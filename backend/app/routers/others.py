"""Router for miscellaneous endpoints like currencies and countries."""

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from app import models, database
from app.base_schemas import COLUMN_LIMITS
from app.config import settings
from app.core.models import get_setting_value
from app.core.schemas import ConfigOut
from app.job_email_scraping.email_parsers import PLATFORM_SENDER_EMAILS
from app.resources import CURRENCIES

other_router = APIRouter(prefix="/others", tags=["others"])


@other_router.get("/currencies/", response_class=JSONResponse)
def get_currencies() -> list[dict]:
    """Get the list of currencies."""

    return CURRENCIES


config_router = APIRouter(prefix="/config", tags=["config"])


def get_demo_credentials(db) -> str:
    """Get the demo user for testing purposes."""

    user = db.query(models.User).filter(models.User.is_demo).first()
    if not user:
        raise AssertionError("No demo user found in database.")
    return user.email


@config_router.get("/", response_model=ConfigOut)
def get_config(
    db=Depends(database.get_db),
) -> dict:
    """Get the application configuration."""

    return {
        "scraper_email": settings.scraper_email_username,
        "support_email": settings.support_email,
        "platform_sender_emails": {value: key for key, value in PLATFORM_SENDER_EMAILS.items()},
        "min_password_length": settings.min_password_length,
        "app_demo_username": get_demo_credentials(db),
        "scrape_max_retry": settings.scrape_max_retry,
        "max_file_size_mb": settings.max_file_size_mb,
        "monthly_scrape_quota": settings.monthly_scrape_quota,
        "column_limits": COLUMN_LIMITS,
    }


@config_router.get("/status")
def get_status(db=Depends(database.get_db)) -> dict:
    """Get dynamic application status (polled by frontend)."""

    return {
        "maintenance_scheduled_at": get_setting_value(db, "maintenance_scheduled_at", None),
        "test_mode": settings.test_mode,
    }
