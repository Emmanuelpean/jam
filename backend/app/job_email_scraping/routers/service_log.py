"""FastAPI routers for the job email scraping service endpoints.

Provides REST API endpoints for managing job alert emails, scraped job postings,
and service execution logs with CRUD operations and admin access controls."""

import datetime as dt

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app import models
from app.core.oauth2 import get_current_user
from app.database import get_db
from app.job_email_scraping import schemas
from app.service_runner import routers


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
