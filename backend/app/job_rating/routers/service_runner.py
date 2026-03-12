"""Routers for Job Rating related endpoints."""

from fastapi import APIRouter, Depends, Query

from app import models
from app.core.oauth2 import get_current_user
from app.job_rating import schemas
from app.job_rating.scraped_job_rating import job_rating_service_runner, SERVICE_NAME
from app.service_runner import routers

job_rating_service_router = APIRouter(prefix="/job-rating-service-runner", tags=["job-rating-service-runner"])


@job_rating_service_router.post("/start")
def start_scraper(
    request: schemas.JobRatingServiceLogStartRequest,
    current_user: models.User = Depends(get_current_user),
) -> dict:
    """Start the email scraping service with the specified period.
    :param request: StartRequest object containing period_hours
    :param current_user: Current authenticated user"""

    return routers.start_scraper(job_rating_service_runner, current_user, request.period_hours)


@job_rating_service_router.post("/stop")
def stop_scraper(
    current_user: models.User = Depends(get_current_user),
) -> dict:
    """Stop the email scraping service.
    :param current_user: Current authenticated user"""

    return routers.stop_scraper(job_rating_service_runner, current_user)


@job_rating_service_router.get("/status")
def scraper_status(
    current_user: models.User = Depends(get_current_user),
) -> dict:
    """Get the current status of the email scraping service.
    :param current_user: Current authenticated user"""

    return routers.scraper_status(job_rating_service_runner, current_user)


@job_rating_service_router.get("/logs")
def get_scraper_logs(
    lines: int = Query(100, ge=1, le=10000),
    current_user: models.User = Depends(get_current_user),
):
    """Get the last N lines from the scraper log file
    :param lines: Number of lines to retrieve (default 100, max 10000)
    :param current_user: Current authenticated user"""

    return routers.get_service_logs(SERVICE_NAME, lines, current_user)
