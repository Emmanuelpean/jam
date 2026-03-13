"""FastAPI routers for the job email scraping service endpoints.

Provides REST API endpoints for managing job alert emails, scraped job postings,
and service execution logs with CRUD operations and admin access controls."""

from typing import Literal

from fastapi import Depends, HTTPException
from fastapi.routing import APIRouter
from sqlalchemy import asc, desc, or_
from sqlalchemy.orm import Session
from starlette import status

from app import models
from app.core.oauth2 import get_current_user
from app.database import get_db
from app.job_email_scraping import schemas

job_alert_email_router = APIRouter(
    prefix="/job-alert-emails",
    tags=["job-alert-emails"],
)


@job_alert_email_router.get("/paged", response_model=schemas.PaginatedJobEmailResponse)
def get_job_emails_paged(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
    page: int = 0,
    page_size: int = 10,
    sort_by: str = "date_received",
    sort_direction: Literal["asc", "desc"] = "desc",
    search: str | None = None,
) -> dict:
    """Retrieve paginated job alert emails for the current user.
    :param db: Database session
    :param current_user: Current authenticated user
    :param page: Page number
    :param page_size: Page size
    :param sort_by: Sort key
    :param sort_direction: Sort direction
    :param search: Search term"""

    query = db.query(models.JobEmail).filter(models.JobEmail.owner_id == current_user.id)

    total = query.count()

    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                models.JobEmail.subject.ilike(search_term),
                models.JobEmail.sender.ilike(search_term),
                models.JobEmail.platform.ilike(search_term),
                models.JobEmail.alert_name.ilike(search_term),
            )
        )

    if hasattr(models.JobEmail, sort_by):
        sort_column = getattr(models.JobEmail, sort_by)
        if sort_direction == "desc":
            query = query.order_by(desc(sort_column).nulls_last())
        else:
            query = query.order_by(asc(sort_column).nulls_last())
    else:
        query = query.order_by(desc(models.JobEmail.date_received).nulls_last())

    total_filtered = query.count()
    offset = page * page_size
    total_pages = (total_filtered + page_size - 1) // page_size if total_filtered > 0 else 1
    results = query.offset(offset).limit(page_size).all()

    return {
        "items": results,
        "total": total,
        "total_filtered": total_filtered,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
    }


@job_alert_email_router.get("/by-scraped-job/{job_id}", response_model=list[schemas.JobEmailOut])
def get_job_emails_by_scraped_job(
    job_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get job emails associated with a specific scraped job for the current user.
    :param job_id: ID of the scraped job
    :param current_user: Current authenticated user
    :param db: Database session
    :return: List of job emails linked to the scraped job"""

    job = (
        db.query(models.ScrapedJob)
        .filter(models.ScrapedJob.id == job_id)
        .filter(models.ScrapedJob.owner_id == current_user.id)
        .first()
    )
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scraped job not found")
    return job.emails
