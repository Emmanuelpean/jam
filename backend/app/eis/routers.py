"""FastAPI routers for the email ingestion service (EIS) endpoints.

Provides REST API endpoints for managing job alert emails, scraped job postings,
and service execution logs with CRUD operations and admin access controls."""

from datetime import datetime, timedelta
from typing import Literal

from fastapi import APIRouter, Depends, Query
from sqlalchemy import asc, desc
from sqlalchemy.orm import Session
from starlette.requests import Request

from app import models as app_models
from app.database import get_db
from app.eis import models, schemas
from app.eis.job_scraper import LinkedinBrightdataJobScraper, IndeedBrightdataJobScraper, VeganJobsJobScraper
from app.oauth2 import get_current_user
from app.routers import (
    generate_data_table_crud_router,
    filter_query,
    assert_admin,
    NOT_ALLOWED_EXCEPTION,
)

# --------------------------------------------------- JOB ALERT EMAILS --------------------------------------------------


email_router = generate_data_table_crud_router(
    table_model=models.JobAlertEmail,
    create_schema=schemas.JobAlertEmailCreate,
    update_schema=schemas.JobAlertEmailUpdate,
    out_schema=schemas.JobAlertEmailOut,
    endpoint="job_alert_emails",
    not_found_msg="Job alert email not found",
    allowed_actions=["get"],
)


# ---------------------------------------------------- SCRAPED JOBS ----------------------------------------------------


scrapedjob_router = generate_data_table_crud_router(
    table_model=models.ScrapedJob,
    create_schema=schemas.ScrapedJobCreate,
    update_schema=schemas.ScrapedJobUpdate,
    out_schema=schemas.ScrapedJobOut,
    endpoint="scraped_jobs",
    not_found_msg="Scraped Job not found",
    allowed_actions=["get_one", "put"],
)


@scrapedjob_router.get("/", response_model=schemas.PaginatedScrapedJobResponse)
def get_all(
    request: Request,
    db: Session = Depends(get_db),
    current_user: app_models.User = Depends(get_current_user),
    page: int = 0,
    page_size: int = 10,
    sort_by: str = "scrape_datetime",
    sort_direction: Literal["asc", "desc"] = "desc",
):
    """Retrieve paginated scraped jobs for the current user that have not been imported, are active and successfully scraped.
    :param request: FastAPI request object to access query parameters
    :param db: Database session.
    :param current_user: Authenticated user.
    :param page: Page number (0-indexed).
    :param page_size: Number of items per page.
    :param sort_by: Column name to sort by.
    :param sort_direction: Sort direction (asc or desc).
    :return: Paginated response with items and metadata."""

    # Base query
    query = (
        db.query(models.ScrapedJob)
        .filter(models.ScrapedJob.owner_id == current_user.id)
        .filter(models.ScrapedJob.is_scraped)
        .filter(models.ScrapedJob.is_imported.is_(False))
        .filter(models.ScrapedJob.is_active)
    )

    # Apply filters
    filter_params = dict(request.query_params)
    filter_params.pop("page", None)
    filter_params.pop("page_size", None)
    filter_params.pop("sort_by", None)
    filter_params.pop("sort_direction", None)
    query = filter_query(query, models.ScrapedJob, filter_params)

    # Apply sorting
    if hasattr(models.ScrapedJob, sort_by):
        sort_column = getattr(models.ScrapedJob, sort_by)
        if sort_direction == "desc":
            query = query.order_by(desc(sort_column).nulls_last())
        else:
            query = query.order_by(asc(sort_column).nulls_last())
    else:
        # Default sorting if invalid column
        query = query.order_by(desc(models.ScrapedJob.scrape_datetime).nulls_last())

    # Get total count before pagination
    total = query.count()

    # Calculate pagination
    offset = page * page_size
    total_pages = (total + page_size - 1) // page_size if total > 0 else 1

    # Apply pagination
    results = query.offset(offset).limit(page_size).all()

    return {
        "items": results,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
    }


# -------------------------------------------------- EIS SERVICE LOGS --------------------------------------------------


# Email Ingestion Service Log router
eis_servicelog_router = APIRouter(prefix="/eis_service_logs", tags=["eis_service_logs"])


@eis_servicelog_router.get("/", response_model=list[schemas.EisServiceLogOut])
def get_service_logs_by_date_range(
    start_date: datetime | None = Query(None, description="Start date for filtering (ISO format)"),
    end_date: datetime | None = Query(None, description="End date for filtering (ISO format)"),
    delta_days: int | None = Query(None, description="Number of days to go back in time"),
    limit: int | None = Query(None, description="Maximum number of logs to return"),
    current_user: app_models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get service logs within a specified date range. Admin access required.
    :param start_date: Optional start date filter (inclusive)
    :param end_date: Optional end date filter (inclusive)
    :param limit: Optional limit for number of logs to return
    :param delta_days: Optional number of days to go back in time
    :param current_user: Current authenticated admin user
    :param db: Database session
    :return: list of service logs within the date range ordered by run_datetime descending"""

    assert_admin(current_user)

    query = db.query(models.EisServiceLog)

    # Apply date filters
    if start_date:
        query = query.filter(models.EisServiceLog.run_datetime >= start_date)
    if end_date:
        query = query.filter(models.EisServiceLog.run_datetime <= end_date)
    if delta_days:
        start_date = datetime.now() - timedelta(days=delta_days)
        query = query.filter(models.EisServiceLog.run_datetime >= start_date)

    # Order by run_datetime descending (most recent first)
    query = query.order_by(models.EisServiceLog.run_datetime.desc())

    # Apply limit if specified
    if limit:
        query = query.limit(limit)

    return query.all()


# ------------------------------------------------------ SCRAPING ------------------------------------------------------


scraper_router = APIRouter(prefix="/scraper", tags=["scraper"])


@scraper_router.get("/linkedin/{external_job_id}")
def scrape_job(
    external_job_id: str,
    current_user: app_models.User = Depends(get_current_user),
):
    """Trigger scraping of a job posting from LinkedIn by job ID.
    :param external_job_id: LinkedIn job ID to scrape
    :param current_user: Current authenticated user"""

    if not current_user.toast_active:
        raise NOT_ALLOWED_EXCEPTION

    scraper = LinkedinBrightdataJobScraper(external_job_id)
    return scraper.scrape_job()


@scraper_router.get("/indeed/{external_job_id}")
def scrape_job(
    external_job_id: str,
    current_user: app_models.User = Depends(get_current_user),
):
    """Trigger scraping of a job posting from Indeed by job ID.
    :param external_job_id: Indeed job ID to scrape
    :param current_user: Current authenticated user"""

    if not current_user.toast_active:
        raise NOT_ALLOWED_EXCEPTION

    scraper = IndeedBrightdataJobScraper(external_job_id)
    return scraper.scrape_job()


@scraper_router.get("/veganjobs/{external_job_id}")
def scrape_job(
    external_job_id: str,
    current_user: app_models.User = Depends(get_current_user),
):
    """Trigger scraping of a job posting from Vegan Jobs by job ID.
    :param external_job_id: LinkedIn job ID to scrape
    :param current_user: Current authenticated user
    :return: Success message or error"""

    if not current_user.toast_active:
        raise NOT_ALLOWED_EXCEPTION

    scraper = VeganJobsJobScraper(external_job_id)
    return scraper.scrape_job()
