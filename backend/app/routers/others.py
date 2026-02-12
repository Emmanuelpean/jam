"""Router for miscellaneous endpoints like currencies and countries."""

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

import database
from app import models
from app.config import settings
from app.job_email_scraping.email_parsers import PLATFORM_SENDER_EMAILS
from app.utils import open_json

other_router = APIRouter(prefix="/others", tags=["others"])


@other_router.get("/currencies/", response_class=JSONResponse)
def get_currencies() -> list[dict]:
    """Get the list of currencies."""

    currencies = open_json("app/data/currencies.json")
    return currencies


@other_router.get("/countries/", response_class=JSONResponse)
def get_countries() -> list[dict]:
    """Get the list of countries."""

    countries = open_json("app/data/countries.json")
    return countries


config_router = APIRouter(prefix="/config", tags=["config"])


def get_demo_credentials(db) -> str:
    """Get the demo user for testing purposes."""

    user = db.query(models.User).filter(models.User.is_demo).first()
    if not user:
        raise AssertionError("No demo user found in database.")
    return user.email


@config_router.get("/")
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
    }
