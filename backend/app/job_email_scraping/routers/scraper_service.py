"""FastAPI routers for the job email scraping service endpoints.

Provides REST API endpoints for managing job alert emails, scraped job postings,
and service execution logs with CRUD operations and admin access controls."""

from fastapi import APIRouter, Depends, Query

from app import models
from app.core.oauth2 import get_current_user
from app.job_email_scraping import schemas
from app.job_email_scraping.email_scraper import job_scraping_service_runner, SERVICE_NAME
from app.service_runner import routers

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
