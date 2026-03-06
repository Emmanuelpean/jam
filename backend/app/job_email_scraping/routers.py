"""FastAPI routers for the job email scraping service endpoints.

Provides REST API endpoints for managing job alert emails, scraped job postings,
and service execution logs with CRUD operations and admin access controls."""

import datetime as dt
import json
from typing import Literal

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy import asc, desc, or_, and_
from sqlalchemy.orm import Session, joinedload
from starlette import status

from app import models as models
from app.core.oauth2 import get_current_user
from app.database import get_db
from app.job_email_scraping import schemas
from app.job_email_scraping.email_scraper import job_scraping_service_runner, SERVICE_NAME
from app.job_email_scraping.job_scrapers.indeed import IndeedBrightdataJobScraper
from app.job_email_scraping.job_scrapers.linkedin import LinkedinBrightdataJobScraper
from app.job_email_scraping.job_scrapers.nhs import NhsJobScraper
from app.job_email_scraping.job_scrapers.veganjobs import VeganJobsJobScraper
from app.routers import generate_data_table_crud_router, NOT_ALLOWED_EXCEPTION
from app.service_runner import routers

# --------------------------------------------------- JOB ALERT EMAILS --------------------------------------------------


# GET endpoint for admin user to get all job alert emails
job_alert_email_router = generate_data_table_crud_router(
    table_model=models.JobEmail,
    out_schema=schemas.JobEmailOut,
    endpoint="job-alert-emails",
    not_found_msg="Job alert email not found",
    allowed_actions=["get_all"],
    admin_only=True,
)


# ---------------------------------------------------- SCRAPED JOBS ----------------------------------------------------


# GET endpoint for admin user to get all scraped jobs
scraped_job_router = generate_data_table_crud_router(
    table_model=models.ScrapedJob,
    out_schema=schemas.ScrapedJobOut,
    endpoint="scraped-jobs",
    not_found_msg="Scraped Job not found",
    allowed_actions=["get_all"],
    admin_only=True,
)


@scraped_job_router.get("/paged", response_model=schemas.PaginatedScrapedJobResponse)
def get_all(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
    page: int = 0,
    page_size: int = 10,
    sort_by: str = "scrape_datetime",
    sort_direction: Literal["asc", "desc"] = "desc",
    show_past_deadline: bool = False,
    since_last_login: bool = False,
    search: str | None = None,
    filters: str | None = None,
) -> dict:
    """Retrieve paginated scraped jobs for the current user that have not been imported, are active and successfully scraped.
    :param db: Database session
    :param current_user: Current user
    :param page: Page number
    :param page_size: Page size
    :param sort_by: sort key
    :param sort_direction: sort direction
    :param show_past_deadline: Show scraped jobs with past deadlines
    :param since_last_login: Only show jobs created since last login
    :param search: Search term"""

    # Base query with eager loading of job_rating
    # noinspection PyComparisonWithNone
    query = (
        db.query(models.ScrapedJob)
        .options(joinedload(models.ScrapedJob.job_rating))  # Always load rating
        .filter(models.ScrapedJob.owner_id == current_user.id)
        .filter(models.ScrapedJob.is_imported.is_(False))
        .filter(models.ScrapedJob.is_active.is_(True))
        .filter(models.ScrapedJob.exclusion_filter_id == None)
    )

    if not show_past_deadline:
        query = query.filter(
            or_(
                models.ScrapedJob.deadline.is_(None),
                models.ScrapedJob.deadline >= dt.datetime.now(dt.timezone.utc),
            )
        )

    if since_last_login and current_user.previous_login:
        query = query.filter(models.ScrapedJob.created_at >= current_user.previous_login)

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

    # Determine if we need a JobRating join (for filters or sorting)
    needs_rating_join = sort_by.startswith("job_rating.")
    filter_conditions = []

    # Parse JSON column filters
    if filters:
        filter_dict = json.loads(filters)
        for key, fval in filter_dict.items():
            ftype = fval.get("type")

            # Resolve the SQLAlchemy column
            if key.startswith("job_rating."):
                attr_name = key.split(".", 1)[1]
                if not hasattr(models.JobRating, attr_name):
                    continue
                col = getattr(models.JobRating, attr_name)
                needs_rating_join = True
            elif hasattr(models.ScrapedJob, key):
                col = getattr(models.ScrapedJob, key)
            else:
                continue

            if ftype == "text":
                value = (fval.get("value") or "").strip()
                if value:
                    filter_conditions.append(col.ilike(f"%{value}%"))

            elif ftype == "select":
                selected = fval.get("selected", [])
                if selected:
                    filter_conditions.append(col.in_(selected))

            elif ftype == "number":
                min_val = fval.get("min")
                max_val = fval.get("max")
                null_filter = fval.get("nullFilter")

                if null_filter == "null":
                    filter_conditions.append(col.is_(None))
                elif null_filter == "not_null":
                    filter_conditions.append(col.isnot(None))
                    if min_val is not None:
                        filter_conditions.append(col >= min_val)
                    if max_val is not None:
                        filter_conditions.append(col <= max_val)
                else:
                    if min_val is not None:
                        filter_conditions.append(col >= min_val)
                    if max_val is not None:
                        filter_conditions.append(col <= max_val)

            elif ftype == "date":
                from_val = fval.get("from")
                to_val = fval.get("to")
                if from_val:
                    filter_conditions.append(col >= from_val)
                if to_val:
                    filter_conditions.append(col <= to_val + "T23:59:59")

            elif ftype == "reference":
                selected_ids = fval.get("selectedIds", [])
                if selected_ids:
                    filter_conditions.append(col.in_([int(sid) for sid in selected_ids]))

    # Apply the join once if needed
    if needs_rating_join:
        query = query.outerjoin(models.JobRating)

    # Apply all filter conditions
    for cond in filter_conditions:
        query = query.filter(cond)

    # Apply sorting
    if sort_by.startswith("job_rating."):
        rating_attribute = sort_by.split(".", 1)[1]

        if hasattr(models.JobRating, rating_attribute):
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
        .filter(models.ScrapedJob.is_imported.is_(False))
        .filter(models.ScrapedJob.is_active.is_(True))
        .filter(models.ScrapedJob.exclusion_filter_id == None)
        .count()
    )
    return {"count": count}


@scraped_job_router.get("/filtered-by-filter/{filter_id}", response_model=list[schemas.ScrapedJobOut])
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
        .filter(models.ScrapedJob.exclusion_filter_id == filter_id)
        .all()
    )
    return scraped_jobs


# PUT endpoint for regular users to update the entries
generate_data_table_crud_router(
    table_model=models.ScrapedJob,
    update_schema=schemas.ScrapedJobUpdate,
    out_schema=schemas.ScrapedJobOut,
    endpoint="scraped-jobs",
    not_found_msg="Scraped Job not found",
    allowed_actions=["put"],
    router=scraped_job_router,
)


# ---------------------------------------------- JOB SCRAPING SERVICE LOGS ---------------------------------------------


# Email Ingestion Service Log router
job_scraping_service_log_router = APIRouter(prefix="/job-scraping-service-logs", tags=["job-scraping-service-logs"])


# GET endpoint for admins to get the service logs
@job_scraping_service_log_router.get("/", response_model=list[schemas.JobEmailScrapingServiceLogOut])
def get_service_logs_by_date_range(
    start_date: dt.datetime | None = Query(None, description="Start date for filtering (ISO format)"),
    end_date: dt.datetime | None = Query(None, description="End date for filtering (ISO format)"),
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

    return routers.get_service_logs_by_date_range(
        start_date,
        end_date,
        delta_days,
        limit,
        current_user,
        db,
        models.JobEmailScrapingServiceLog,
    )


# GET endpoint for admin user to get the latest service log
@job_scraping_service_log_router.get("/latest", response_model=schemas.JobEmailScrapingServiceLogOut)
def get_latest(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get the latest service log entry. Admin access required.
    :param current_user: Current authenticated admin user
    :param db: Database session
    :return: Latest service log entry"""

    return routers.get_latest(current_user, db, models.JobEmailScrapingServiceLog)


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


email_scraper_service_router = APIRouter(prefix="/job-scraper-service", tags=["job-scraper-service"])


@email_scraper_service_router.post("/start")
def start_scraper(
    request: schemas.JobEmailScrapingStartRequest,
    current_user: models.User = Depends(get_current_user),
) -> dict:
    """Start the service runner with the specified period.
    :param request: StartRequest object containing period_hours
    :param current_user: Current authenticated user"""

    return routers.start_scraper(job_scraping_service_runner, current_user, request.period_hours)


@email_scraper_service_router.post("/stop")
def stop_scraper(
    current_user: models.User = Depends(get_current_user),
) -> dict:
    """Stop the service runner.
    :param current_user: Current authenticated user"""

    return routers.stop_scraper(job_scraping_service_runner, current_user)


@email_scraper_service_router.get("/status")
def scraper_status(
    current_user: models.User = Depends(get_current_user),
) -> dict:
    """Get the current status of the service"""

    return routers.scraper_status(job_scraping_service_runner, current_user)


@email_scraper_service_router.get("/logs")
def get_scraper_logs(
    lines: int = Query(100, ge=1, le=10000),
    current_user: models.User = Depends(get_current_user),
):
    """Get the last N lines from the service log file
    :param lines: Number of lines to retrieve (default 100, max 10000)
    :param current_user: Current authenticated user"""

    return routers.get_service_logs(SERVICE_NAME, lines, current_user)


# ------------------------------------------------- SCRAPED JOB FILTERS ------------------------------------------------


scraping_filter_router = generate_data_table_crud_router(
    table_model=models.ScrapingExclusionFilter,
    create_schema=schemas.ScrapingFilterCreate,
    update_schema=schemas.ScrapingFilterUpdate,
    out_schema=schemas.ScrapingFilterOut,
    endpoint="scraping-filters",
    not_found_msg="Scraped Job Filter not found",
    allowed_actions=["get_all", "get_one", "post"],
)


@scraping_filter_router.put("/{filter_id}", status_code=status.HTTP_200_OK, response_model=schemas.ScrapingFilterOut)
def update_scraping_filter(
    filter_id: int,
    update_data: schemas.ScrapingFilterUpdate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update a scraped job filter by ID.
    :param filter_id: ID of the filter to update
    :param update_data: Update data for the filter
    :param current_user: Current authenticated user
    :param db: Database session"""

    # Fetch the filter to ensure it exists and belongs to the current user.
    filter_obj = (
        db.query(models.ScrapingExclusionFilter)
        .filter(models.ScrapingExclusionFilter.id == filter_id)
        .filter(models.ScrapingExclusionFilter.owner_id == current_user.id)
        .first()
    )

    if not filter_obj:
        raise NOT_ALLOWED_EXCEPTION

    # Get the update fields
    update_dict = update_data.model_dump(exclude_unset=True)
    print(filter_obj.filtered_jobs)
    print(filter_obj.id)

    # If the filter previously filtered jobs, only allow is_active updates
    if filter_obj.filtered_jobs:
        # Check if any fields other than is_active are being updated
        non_active_fields = {k: v for k, v in update_dict.items() if k != "is_active"}
        if non_active_fields:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Cannot update filter fields other than is_active when filter has been used",
            )

    # If the filter was never used, update it
    for key, value in update_data.model_dump(exclude_unset=True).items():
        setattr(filter_obj, key, value)

    db.commit()
    db.refresh(filter_obj)
    return filter_obj


@scraping_filter_router.delete("/{filter_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_scraping_filter(
    filter_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a scraped job filter by ID.
    :param filter_id: ID of the filter to delete
    :param current_user: Current authenticated user
    :param db: Database session
    :return: The deleted or deactivated filter object"""

    # Fetch the filter to ensure it exists and belongs to the current user
    filter_obj = (
        db.query(models.ScrapingExclusionFilter)
        .filter(models.ScrapingExclusionFilter.id == filter_id)
        .filter(models.ScrapingExclusionFilter.owner_id == current_user.id)
        .first()
    )

    if not filter_obj:
        raise NOT_ALLOWED_EXCEPTION

    # If the filter has filtered jobs, do not delete it, just deactivate it
    if filter_obj.filtered_jobs:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT)
    else:
        db.delete(filter_obj)
        db.commit()


# ------------------------------------------- FORWARDING CONFIRMATION LINKS --------------------------------------------


forwarding_confirmation_router = APIRouter(
    prefix="/forwarding-confirmation-links", tags=["forwarding-confirmation-links"]
)


@forwarding_confirmation_router.get("/pending", response_model=schemas.ForwardingConfirmationLinkOut | None)
def get_pending_confirmation_links(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> models.ForwardingConfirmationLink | None:
    """Get all unused forwarding confirmation links for the current user.
    :param current_user: Current authenticated user
    :param db: Database session
    :return: List of pending forwarding confirmation links"""

    entry = (
        db.query(models.ForwardingConfirmationLink)
        .filter(models.ForwardingConfirmationLink.owner_id == current_user.id)
        .order_by(models.ForwardingConfirmationLink.created_at.desc())
        .first()
    )
    if entry and entry.is_used:
        return None
    else:
        return entry


@forwarding_confirmation_router.put("/{link_id}", response_model=schemas.ForwardingConfirmationLinkOut)
def update_confirmation_link(
    link_id: int,
    update_data: schemas.ForwardingConfirmationLinkUpdate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> models.ForwardingConfirmationLink:
    """Update a forwarding confirmation link (mark as used).
    :param link_id: ID of the link to update
    :param update_data: Update data
    :param current_user: Current authenticated user
    :param db: Database session
    :return: Updated forwarding confirmation link"""

    link = (
        db.query(models.ForwardingConfirmationLink)
        .filter(models.ForwardingConfirmationLink.id == link_id)
        .filter(models.ForwardingConfirmationLink.owner_id == current_user.id)
        .first()
    )

    if not link:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Confirmation link not found")

    for key, value in update_data.model_dump(exclude_unset=True).items():
        setattr(link, key, value)

    db.commit()
    db.refresh(link)
    return link
