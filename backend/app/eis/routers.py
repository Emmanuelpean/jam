"""FastAPI routers for the email ingestion service (EIS) endpoints.

Provides REST API endpoints for managing job alert emails, scraped job postings,
and service execution logs with CRUD operations and admin access controls."""

from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from starlette.requests import Request

from app import models as app_models
from app.database import get_db
from app.eis import models, schemas
from app.eis.job_scraper import LinkedinJobScraper, IndeedJobScraper, VeganJobsScraper
from app.models import User
from app.oauth2 import get_current_user
from app.routers import generate_data_table_crud_router, filter_query, filter_owned_relationships

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


scrapedjob_router = APIRouter(prefix="/scraped_jobs", tags=["scraped_jobs"])


@scrapedjob_router.get("/", response_model=list[schemas.ScrapedJobOut])
def get_all(
    request: Request,
    db: Session = Depends(get_db),
    current_user: app_models.User = Depends(get_current_user),
    limit: int | None = None,
):
    """Retrieve all scraped jobs for the current user that have not been imported, are active and successfully scraped.
    :param request: FastAPI request object to access query parameters
    :param db: Database session.
    :param current_user: Authenticated user.
    :param limit: Maximum number of entries to return.
    :return: List of entries."""

    query = (
        db.query(models.ScrapedJob)
        .filter(models.ScrapedJob.owner_id == current_user.id)
        .filter(models.ScrapedJob.is_scraped)
        .filter(models.ScrapedJob.is_imported.is_(False))
        .filter(models.ScrapedJob.is_active)
    )
    filter_params = dict(request.query_params)
    filter_params.pop("limit", None)
    query = filter_query(query, models.ScrapedJob, filter_params)

    results = query.limit(limit).all()
    filtered_results = [filter_owned_relationships(result, current_user.id) for result in results]
    return filtered_results


@scrapedjob_router.put("/{entry_id}", response_model=schemas.ScrapedJobOut)
def update_scraped_job(
    entry_id: int,
    item: schemas.ScrapedJobUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Mark a scraped job as imported.
    :param entry_id: ID of the scraped job to update
    :param item: update data
    :param current_user: Current authenticated user
    :param db: Database session"""

    query = db.query(models.ScrapedJob).filter(models.ScrapedJob.id == entry_id)
    scraped_job = query.first()

    if not scraped_job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scraped job not found")

    if scraped_job.owner_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorised to update this job")

    # Extract the item data
    item_dict = item.model_dump(exclude_unset=True)

    if not item_dict:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No fields provided for update")

    print(item_dict)

    query.update(item.model_dump(exclude_unset=True))

    db.commit()

    return filter_owned_relationships(query.first(), current_user.id)


# -------------------------------------------------- EIS SERVICE LOGS --------------------------------------------------


# Email Ingestion Service Log router
eis_servicelog_router = APIRouter(prefix="/eis_service_logs", tags=["eis_service_logs"])


@eis_servicelog_router.get("/", response_model=list[schemas.EisServiceLogOut])
def get_service_logs_by_date_range(
    start_date: datetime | None = Query(None, description="Start date for filtering (ISO format)"),
    end_date: datetime | None = Query(None, description="End date for filtering (ISO format)"),
    delta_days: int | None = Query(None, description="Number of days to go back in time"),
    limit: int | None = Query(None, description="Maximum number of logs to return"),
    current_user: User = Depends(get_current_user),
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

    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")

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


@scraper_router.get("/linkedin/{job_id}")
def scrape_job(
    job_id: str,
    current_user: User = Depends(get_current_user),
):
    """Trigger scraping of a job posting from LinkedIn by job ID.
    :param job_id: LinkedIn job ID to scrape
    :param current_user: Current authenticated user
    :return: Success message or error"""

    if not current_user.toast_active:
        raise AssertionError("You are not allowed to use TOAST")

    scraper = LinkedinJobScraper(job_id)
    return scraper.scrape_job()


@scraper_router.get("/indeed/{job_id}")
def scrape_job(
    job_id: str,
    current_user: User = Depends(get_current_user),
):
    """Trigger scraping of a job posting from Indeed by job ID.
    :param job_id: Indeed job ID to scrape
    :param current_user: Current authenticated user
    :return: Success message or error"""

    if not current_user.toast_active:
        raise AssertionError("You are not allowed to use TOAST")

    scraper = IndeedJobScraper(job_id)
    return scraper.scrape_job()


@scraper_router.get("/veganjobs/{job_id}")
def scrape_job(
    job_id: str,
    current_user: User = Depends(get_current_user),
):
    """Trigger scraping of a job posting from LinkedIn by job ID.
    :param job_id: LinkedIn job ID to scrape
    :param current_user: Current authenticated user
    :return: Success message or error"""

    if not current_user.toast_active:
        raise AssertionError("You are not allowed to use TOAST")

    scraper = VeganJobsScraper(job_id)
    return scraper.scrape_job()
