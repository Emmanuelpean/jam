"""FastAPI routers for the email ingestion service (EIS) endpoints.

Provides REST API endpoints for managing job alert emails, scraped job postings,
and service execution logs with CRUD operations and admin access controls."""

from datetime import datetime
from typing import Literal

from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy import asc, desc, or_
from sqlalchemy.orm import Session, joinedload
from starlette import status
from starlette.requests import Request

from app import model_registry as models
from app import service_runner
from app.database import get_db
from app.job_email_scraping import schemas
from app.job_email_scraping.email_scraper import scraper_service, SERVICE_NAME
from app.job_email_scraping.job_scrapers.indeed import IndeedBrightdataJobScraper
from app.job_email_scraping.job_scrapers.linkedin import LinkedinBrightdataJobScraper
from app.job_email_scraping.job_scrapers.nhs import NhsJobScraper
from app.job_email_scraping.job_scrapers.veganjobs import VeganJobsJobScraper
from app.oauth2 import get_current_user
from app.routers import (
    generate_data_table_crud_router,
    filter_query,
    NOT_ALLOWED_EXCEPTION,
)

# --------------------------------------------------- JOB ALERT EMAILS --------------------------------------------------


# GET endpoint for admin user to get all job alert emails
job_alert_email_router = generate_data_table_crud_router(
    table_model=models.JobEmail,
    out_schema=schemas.JobEmailOut,
    endpoint="job_alert_emails",
    not_found_msg="Job alert email not found",
    allowed_actions=["get_all"],
    admin_only=True,
)


# ---------------------------------------------------- SCRAPED JOBS ----------------------------------------------------


# GET endpoint for admin user to get all scraped jobs
scraped_job_router = generate_data_table_crud_router(
    table_model=models.ScrapedJob,
    out_schema=schemas.ScrapedJobOut,
    endpoint="scraped_jobs",
    not_found_msg="Scraped Job not found",
    allowed_actions=["get_all"],
    admin_only=True,
)


@scraped_job_router.get("/paged", response_model=schemas.PaginatedScrapedJobResponse)
def get_all(
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
    page: int = 0,
    page_size: int = 10,
    sort_by: str = "scrape_datetime",
    sort_direction: Literal["asc", "desc"] = "desc",
    search: str | None = None,
):
    """Retrieve paginated scraped jobs for the current user that have not been imported, are active and successfully scraped."""

    # Base query with eager loading of job_rating
    # noinspection PyComparisonWithNone
    query = (
        db.query(models.ScrapedJob)
        .options(joinedload(models.ScrapedJob.job_rating))  # Always load rating
        .filter(models.ScrapedJob.owner_id == current_user.id)
        .filter(models.ScrapedJob.is_scraped)
        .filter(models.ScrapedJob.is_imported.is_(False))
        .filter(models.ScrapedJob.is_active)
        .filter(models.ScrapedJob.filter_id == None)
    )

    # Apply search filter
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                models.ScrapedJob.title.ilike(search_term),
                models.ScrapedJob.company.ilike(search_term),
                models.ScrapedJob.location.ilike(search_term),
                models.ScrapedJob.description.ilike(search_term),
                models.ScrapedJob.platform.ilike(search_term),
            )
        )

    # Apply filters
    filter_params = dict(request.query_params)
    filter_params.pop("page", None)
    filter_params.pop("page_size", None)
    filter_params.pop("sort_by", None)
    filter_params.pop("sort_direction", None)
    filter_params.pop("search", None)
    query = filter_query(query, models.ScrapedJob, filter_params)

    # Apply sorting
    if sort_by.startswith("job_rating."):
        # Handle sorting by job_rating relationship attributes
        rating_attribute = sort_by.split(".", 1)[1]  # e.g., "overall_score"

        if hasattr(models.JobRating, rating_attribute):
            # Need explicit join for ORDER BY to work
            query = query.outerjoin(models.JobRating)
            sort_column = getattr(models.JobRating, rating_attribute)

            if sort_direction == "desc":
                query = query.order_by(desc(sort_column).nulls_last())
            else:
                query = query.order_by(asc(sort_column).nulls_last())
        else:
            # Default sorting if invalid column
            query = query.order_by(desc(models.ScrapedJob.scrape_datetime).nulls_last())
    elif hasattr(models.ScrapedJob, sort_by):
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


# GET endpoint for regular user to get the number of scraped jobs
@scraped_job_router.get("/count")
def get_scraped_job_count(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get the count of scraped jobs for the current user that are scraped, not imported, and active.
    :param current_user: Current authenticated user
    :param db: Database session
    :return: Count of scraped jobs"""

    # noinspection PyComparisonWithNone
    count = (
        db.query(models.ScrapedJob)
        .filter(models.ScrapedJob.owner_id == current_user.id)
        .filter(models.ScrapedJob.is_scraped)
        .filter(models.ScrapedJob.is_imported.is_(False))
        .filter(models.ScrapedJob.is_active)
        .filter(models.ScrapedJob.filter_id == None)
        .count()
    )
    return {"count": count}


@scraped_job_router.get("/filtered_by_filter/{filter_id}", response_model=list[schemas.ScrapedJobOut])
def get_scraped_jobs_filtered_by_filter(
    filter_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get scraped jobs associated with a specific filter for the current user.
    :param filter_id: ID of the filter
    :param current_user: Current authenticated user
    :param db: Database session
    :return: List of scraped jobs associated with the filter"""

    scraped_jobs = (
        db.query(models.ScrapedJob)
        .filter(models.ScrapedJob.owner_id == current_user.id)
        .filter(models.ScrapedJob.filter_id == filter_id)
        .all()
    )
    return scraped_jobs


# PUT endpoint for regular users to update the entries
generate_data_table_crud_router(
    table_model=models.ScrapedJob,
    update_schema=schemas.ScrapedJobUpdate,
    out_schema=schemas.ScrapedJobOut,
    endpoint="scraped_jobs",
    not_found_msg="Scraped Job not found",
    allowed_actions=["put"],
    router=scraped_job_router,
)


# -------------------------------------------------- EIS SERVICE LOGS --------------------------------------------------


# Email Ingestion Service Log router
eis_service_log_router = APIRouter(prefix="/eis_service_logs", tags=["eis_service_logs"])


# GET endpoint for admins to get the service logs
@eis_service_log_router.get("/", response_model=list[schemas.JobEmailScrapingServiceLogOut])
def get_service_logs_by_date_range(
    start_date: datetime | None = Query(None, description="Start date for filtering (ISO format)"),
    end_date: datetime | None = Query(None, description="End date for filtering (ISO format)"),
    delta_days: int | None = Query(None, description="Number of days to go back in time"),
    limit: int | None = Query(None, description="Maximum number of logs to return"),
    current_user: models.User = Depends(get_current_user),
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

    return service_runner.get_service_logs_by_date_range(
        start_date,
        end_date,
        delta_days,
        limit,
        current_user,
        db,
        models.JobEmailScrapingServiceLog,
    )


# GET endpoint for admin user to get the latest service log
@eis_service_log_router.get("/latest", response_model=schemas.JobEmailScrapingServiceLogOut)
def get_latest(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get the latest service log entry. Admin access required.
    :param current_user: Current authenticated admin user
    :param db: Database session
    :return: Latest service log entry"""

    return service_runner.get_latest(current_user, db, models.JobEmailScrapingServiceLog)


# ------------------------------------------------------ SCRAPING ------------------------------------------------------


scraper_router = APIRouter(prefix="/scraper", tags=["scraper"])


@scraper_router.get("/linkedin/{external_job_id}")
def scrape_job(
    external_job_id: str,
    current_user: models.User = Depends(get_current_user),
):
    """Trigger scraping of a job posting from LinkedIn by job ID.
    :param external_job_id: LinkedIn job ID to scrape
    :param current_user: Current authenticated user"""

    if not current_user.toast_active:
        raise NOT_ALLOWED_EXCEPTION

    scraper = LinkedinBrightdataJobScraper(external_job_id)
    return scraper.scrape_job()[0]


@scraper_router.get("/indeed/{external_job_id}")
def scrape_job(
    external_job_id: str,
    current_user: models.User = Depends(get_current_user),
):
    """Trigger scraping of a job posting from Indeed by job ID.
    :param external_job_id: Indeed job ID to scrape
    :param current_user: Current authenticated user"""

    if not current_user.toast_active:
        raise NOT_ALLOWED_EXCEPTION

    scraper = IndeedBrightdataJobScraper(external_job_id)
    return scraper.scrape_job()[0]


@scraper_router.get("/veganjobs/{external_job_id}")
def scrape_job(
    external_job_id: str,
    current_user: models.User = Depends(get_current_user),
):
    """Trigger scraping of a job posting from Vegan Jobs by job ID.
    :param external_job_id: LinkedIn job ID to scrape
    :param current_user: Current authenticated user
    :return: Success message or error"""

    if not current_user.toast_active:
        raise NOT_ALLOWED_EXCEPTION

    scraper = VeganJobsJobScraper(external_job_id)
    return scraper.scrape_job()[0]


@scraper_router.get("/nhs/{external_job_id}")
def scrape_job(
    external_job_id: str,
    current_user: models.User = Depends(get_current_user),
):
    """Trigger scraping of a job posting from the NHS website by job ID.
    :param external_job_id: LinkedIn job ID to scrape
    :param current_user: Current authenticated user
    :return: Success message or error"""

    if not current_user.toast_active:
        raise NOT_ALLOWED_EXCEPTION

    scraper = NhsJobScraper(external_job_id)
    return scraper.scrape_job()[0]


# ------------------------------------------------ EMAIL SCRAPER SERVICE -----------------------------------------------


email_scraper_service_router = APIRouter(prefix="/email_scraper_service", tags=["email_scraper_service"])


@email_scraper_service_router.post("/start")
def start_scraper(
    request: schemas.JobEmailScrapingStartRequest,
    current_user: models.User = Depends(get_current_user),
) -> dict:
    """Start the service runner with the specified period.
    :param request: StartRequest object containing period_hours
    :param current_user: Current authenticated user"""

    return service_runner.start_scraper(scraper_service, current_user, request.period_hours)


@email_scraper_service_router.post("/stop")
def stop_scraper(current_user: models.User = Depends(get_current_user)) -> dict:
    """Stop the service runner.
    :param current_user: Current authenticated user"""

    return service_runner.stop_scraper(scraper_service, current_user)


@email_scraper_service_router.get("/status")
def scraper_status(
    current_user: models.User = Depends(get_current_user),
) -> dict:
    """Get the current status of the service.
    :param current_user: Current authenticated user"""

    return service_runner.scraper_status(scraper_service, current_user)


@email_scraper_service_router.get("/logs")
def get_scraper_logs(
    lines: int = Query(100, ge=1, le=10000),
    current_user: models.User = Depends(get_current_user),
):
    """Get the last N lines from the service log file
    :param lines: Number of lines to retrieve (default 100, max 10000)
    :param current_user: Current authenticated user"""

    return service_runner.get_service_logs(SERVICE_NAME, lines, current_user)


# ------------------------------------------------- SCRAPED JOB FILTERS ------------------------------------------------


scraped_job_filter_router = generate_data_table_crud_router(
    table_model=models.ScrapedJobFilter,
    create_schema=schemas.ScrapedJobFilterCreate,
    update_schema=schemas.ScrapedJobFilterUpdate,
    out_schema=schemas.ScrapedJobFilterOut,
    endpoint="scraped_job_filters",
    not_found_msg="Scraped Job Filter not found",
    allowed_actions=["get_all", "get_one"],
)


@scraped_job_filter_router.post("/", response_model=schemas.ScrapedJobFilterOut)
def create_scraped_job_filter(
    filter_data: schemas.ScrapedJobFilterCreate,
    response: Response,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new scraped job filter. If the type, operator and value are the same as an existing filter, use that
    new filter and update it with the data.
    :param filter_data: Data for the new filter
    :param response: Response for the new filter
    :param current_user: Current authenticated user
    :param db: Database session
    :return: New job filter or existing one"""

    # If an existing filter with the same parameters exists for the user, return it instead of creating a new one
    existing_filter = (
        db.query(models.ScrapedJobFilter)
        .filter_by(owner_id=current_user.id)
        .filter_by(type=filter_data.type)
        .filter_by(operator=filter_data.operator)
        .filter_by(value=filter_data.value)
        .filter_by(case_sensitive=filter_data.case_sensitive)
        .first()
    )
    if existing_filter:
        for key, value in filter_data.model_dump().items():
            setattr(existing_filter, key, value)
        db.commit()
        db.refresh(existing_filter)
        response.status_code = status.HTTP_200_OK
        return existing_filter

    else:
        # noinspection PyArgumentList
        filter_obj = models.ScrapedJobFilter(
            **filter_data.model_dump(),
            owner_id=current_user.id,
        )
        db.add(filter_obj)
        db.commit()
        db.refresh(filter_obj)
        response.status_code = status.HTTP_201_CREATED
        return filter_obj


@scraped_job_filter_router.delete("/{filter_id}", response_model=schemas.ScrapedJobFilterOut)
def delete_scraped_job_filter(
    filter_id: int,
    response: Response,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a scraped job filter by ID.
    :param filter_id: ID of the filter to delete
    :param response: FastAPI response object
    :param current_user: Current authenticated user
    :param db: Database session
    :return: The deleted or deactivated filter object"""

    # Fetch the filter to ensure it exists and belongs to the current user
    filter_obj = (
        db.query(models.ScrapedJobFilter)
        .filter(models.ScrapedJobFilter.id == filter_id)
        .filter(models.ScrapedJobFilter.owner_id == current_user.id)
        .first()
    )
    filter_data = filter_obj.model_dump()

    if not filter_obj:
        raise NOT_ALLOWED_EXCEPTION

    if filter_obj.filtered_jobs:
        filter_obj.is_active = False
        db.commit()
        db.refresh(filter_obj)
        response.status_code = status.HTTP_200_OK
    else:
        db.delete(filter_obj)
        db.commit()
        response.status_code = status.HTTP_204_NO_CONTENT

    return filter_data


@scraped_job_filter_router.put("/{filter_id}")
def update_scraped_job_filter(
    filter_id: int,
    update_data: schemas.ScrapedJobFilterUpdate,
    response: Response,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update a scraped job filter by ID.
    :param filter_id: ID of the filter to update
    :param update_data: Update data for the filter
    :param response: FastAPI response object
    :param current_user: Current authenticated user
    :param db: Database session"""

    # Fetch the filter to ensure it exists and belongs to the current user. Inactive filters cannot be updated
    filter_obj = (
        db.query(models.ScrapedJobFilter)
        .filter(models.ScrapedJobFilter.id == filter_id)
        .filter(models.ScrapedJobFilter.owner_id == current_user.id)
        .filter(models.ScrapedJobFilter.is_active)
        .first()
    )

    if not filter_obj:
        raise NOT_ALLOWED_EXCEPTION

    # If the filter previously filtered jobs, create a new filter
    if filter_obj.filtered_jobs:
        filter_dict = {
            "type": filter_obj.type,
            "operator": filter_obj.operator,
            "value": filter_obj.value,
            "case_sensitive": filter_obj.case_sensitive,
            "is_enabled": filter_obj.is_enabled,
            "is_active": filter_obj.is_active,
            "owner_id": filter_obj.owner_id,
        }
        filter_dict.update(update_data.model_dump(exclude_unset=True))
        # noinspection PyArgumentList
        filter_obj = models.ScrapedJobFilter(**filter_dict)
        db.add(filter_obj)
        response.status_code = status.HTTP_201_CREATED

    # If the filter was never used, update it
    else:
        for key, value in update_data.model_dump(exclude_unset=True).items():
            setattr(filter_obj, key, value)
        response.status_code = status.HTTP_200_OK

    db.commit()
    db.refresh(filter_obj)
    return filter_obj
