"""FastAPI routers for the job email scraping service endpoints.

Provides REST API endpoints for managing job alert emails, scraped job postings,
and service execution logs with CRUD operations and admin access controls."""

import datetime as dt
from typing import Literal

from fastapi import Depends, HTTPException
from sqlalchemy import asc, desc, or_
from sqlalchemy.orm import Session, joinedload
from starlette import status
from starlette.requests import Request

from app import models
from app.core.oauth2 import get_current_user
from app.database import get_db
from app.job_email_scraping import schemas
from app.routers.utility import generate_data_table_crud_router, filter_query


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
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
    page: int = 0,
    page_size: int = 10,
    sort_by: str = "scrape_datetime",
    sort_direction: Literal["asc", "desc"] = "desc",
    show_past_deadline: bool = False,
    since_last_login: bool = False,
    search: str | None = None,
) -> dict:
    """Retrieve paginated scraped jobs for the current user that have not been imported, are active and successfully scraped.
    :param request: Request
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

    total = query.count()

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

    # Apply filters
    filter_params = dict(request.query_params)
    filter_params.pop("page", None)
    filter_params.pop("page_size", None)
    filter_params.pop("sort_by", None)
    filter_params.pop("sort_direction", None)
    filter_params.pop("search", None)
    filter_params.pop("show_past_deadline", None)
    filter_params.pop("since_last_login", None)
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
    total_filtered = query.count()

    # Calculate pagination
    offset = page * page_size
    total_pages = (total_filtered + page_size - 1) // page_size if total_filtered > 0 else 1

    # Apply pagination
    results = query.offset(offset).limit(page_size).all()

    return {
        "items": results,
        "total": total,
        "total_filtered": total_filtered,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
    }


@scraped_job_router.get("/by-email/{email_id}", response_model=list[schemas.ScrapedJobOut])
def get_scraped_jobs_by_email(
    email_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get scraped jobs associated with a specific job email for the current user.
    :param email_id: ID of the job email
    :param current_user: Current authenticated user
    :param db: Database session
    :return: List of scraped jobs linked to the email"""

    email = (
        db.query(models.JobEmail)
        .filter(models.JobEmail.id == email_id)
        .filter(models.JobEmail.owner_id == current_user.id)
        .first()
    )
    if not email:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job email not found")
    return email.jobs


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
