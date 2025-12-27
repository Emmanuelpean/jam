"""Routers for Job Rating related endpoints."""

from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app import service_runner, models as app_models
from app.database import get_db
from app.job_rating import models, schemas
from app.job_rating.scraped_job_rating import job_rating_service_runner, SERVICE_NAME
from app.oauth2 import get_current_user
from app.routers import generate_data_table_crud_router

# ---------------------------------------------------- SCRAPED JOBS ----------------------------------------------------


job_rating_router = generate_data_table_crud_router(
    table_model=models.JobRating,
    out_schema=schemas.JobRatingOut,
    endpoint="job-ratings",
    not_found_msg="Job Rating not found",
    allowed_actions=["get_all"],
    admin_only=True,
)


# ---------------------------------------------------- SERVICE LOGS ----------------------------------------------------


# Service Log router
job_rating_service_log_router = APIRouter(prefix="/job-rating-service-logs", tags=["job-rating-service-logs"])


# GET endpoint for admins to get the service logs
@job_rating_service_log_router.get("/", response_model=list[schemas.JobRatingServiceLogOut])
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

    return service_runner.get_service_logs_by_date_range(
        start_date,
        end_date,
        delta_days,
        limit,
        current_user,
        db,
        models.JobRatingServiceLog,
    )


# GET endpoint for admin user to get the latest service log
@job_rating_service_log_router.get("/latest", response_model=schemas.JobRatingServiceLogOut)
def get_latest(
    current_user: app_models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get the latest service log entry. Admin access required.
    :param current_user: Current authenticated admin user
    :param db: Database session
    :return: Latest service log entry"""

    return service_runner.get_latest(current_user, db, models.JobRatingServiceLog)


# --------------------------------------------------- SERVICE RUNNER ---------------------------------------------------


job_rating_service_router = APIRouter(prefix="/job_rating_service_runner", tags=["job_rating_service_runner"])


@job_rating_service_router.post("/start")
def start_scraper(
    request: schemas.JobRatingServiceLogStartRequest,
    current_user: app_models.User = Depends(get_current_user),
) -> dict:
    """Start the email scraping service with the specified period.
    :param request: StartRequest object containing period_hours
    :param current_user: Current authenticated user"""

    return service_runner.start_scraper(job_rating_service_runner, current_user, request.period_hours)


@job_rating_service_router.post("/stop")
def stop_scraper(
    current_user: app_models.User = Depends(get_current_user),
) -> dict:
    """Stop the email scraping service.
    :param current_user: Current authenticated user"""

    return service_runner.stop_scraper(job_rating_service_runner, current_user)


@job_rating_service_router.get("/status")
def scraper_status(
    current_user: app_models.User = Depends(get_current_user),
) -> dict:
    """Get the current status of the email scraping service.
    :param current_user: Current authenticated user"""

    return service_runner.scraper_status(job_rating_service_runner, current_user)


@job_rating_service_router.get("/logs")
def get_scraper_logs(
    lines: int = Query(100, ge=1, le=10000),
    current_user: app_models.User = Depends(get_current_user),
):
    """Get the last N lines from the scraper log file
    :param lines: Number of lines to retrieve (default 100, max 10000)
    :param current_user: Current authenticated user"""

    return service_runner.get_service_logs(SERVICE_NAME, lines, current_user)
