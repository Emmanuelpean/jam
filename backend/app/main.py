"""Main script"""

from contextlib import asynccontextmanager

import jwt
from fastapi import FastAPI, APIRouter, Request
from fastapi.middleware.cors import CORSMiddleware

from app import database
from app import routers as app_routers
from app.config import settings
from app.core import routers as core_routers
from app.data_tables import routers as data_table_routers
from app.demo import routers as demo_routers
from app.demo.setup import setup_demo_schema
from app.emails import routers as email_routers
from app.external_service_monitoring import routers as external_service_monitoring_routers
from app.geolocation import routers as geolocation_routers
from app.job_email_scraping import routers as job_email_scraping_routers
from app.job_rating import routers as job_rating_routers
from app.payments import routers as payment_routers
from app.service.routers.service_error import service_error_router
from app.service.scheduler import service_scheduler
from app.service.routers.service import service_router
from app.service.routers.service_log import service_log_router
from app.service.routers.scheduler import scheduler_router

# Import the service modules so they register their run callables with SERVICE_REGISTRY.
from app.job_email_scraping import email_scraper  # noqa: F401
from app.job_rating import scraped_job_rating  # noqa: F401
from app.external_service_monitoring.service import sync  # noqa: F401


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Application lifespan event handler."""

    setup_demo_schema()
    if settings.scheduler:
        service_scheduler.start()
    yield
    if settings.scheduler:
        service_scheduler.stop()


app = FastAPI(title="JAM", version=settings.app_version, lifespan=lifespan)


def get_allowed_origins() -> list[str]:
    """Get allowed CORS origins based on environment"""

    # In test mode, allow all origins
    if settings.test_mode:
        return ["*"]

    # In production, allow only the frontend URL
    else:
        return [settings.frontend_url, "http://localhost:3000"]


app.add_middleware(
    CORSMiddleware,  # type: ignore[arg-type]
    allow_origins=get_allowed_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def demo_schema_middleware(request: Request, call_next):
    """Detect demo tokens and set demo_mode context variable."""

    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    if token:
        try:
            payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
            if payload.get("is_demo"):
                database.demo_mode.set(True)
        except jwt.PyJWTError:
            pass
    response = await call_next(request)
    database.demo_mode.set(False)
    return response


# Data table routers
app.include_router(data_table_routers.company_router)
app.include_router(data_table_routers.person_router)
app.include_router(data_table_routers.job_router)
app.include_router(data_table_routers.aggregator_router)
app.include_router(data_table_routers.interview_router)
app.include_router(data_table_routers.keyword_router)
app.include_router(data_table_routers.file_router)
app.include_router(data_table_routers.job_application_update_router)
app.include_router(data_table_routers.speculative_application_update_router)

# Job Scraping routers
app.include_router(job_email_scraping_routers.scraped_job_router)
app.include_router(job_email_scraping_routers.job_alert_email_router)
app.include_router(job_email_scraping_routers.scraping_filter_router)
app.include_router(job_email_scraping_routers.scraping_favourite_filter_router)
app.include_router(job_email_scraping_routers.forwarding_confirmation_router)

# Job Rating routers
app.include_router(job_rating_routers.job_rating_router)

# External service monitoring routers
app.include_router(external_service_monitoring_routers.external_service_monitoring_history_router)

# Service errors and scheduled services
app.include_router(service_error_router)
app.include_router(service_router)
app.include_router(service_log_router)
app.include_router(scheduler_router)

# User routers
app.include_router(core_routers.user_router)
app.include_router(core_routers.current_user_router)
app.include_router(core_routers.user_qualification_router)

# Auth routers
app.include_router(core_routers.login_router)
app.include_router(core_routers.register_router)
app.include_router(core_routers.password_router)

# Export router
app.include_router(app_routers.export_router)

# Settings router
app.include_router(core_routers.settings_router)

# Email admin
app.include_router(email_routers.email_template_router)

# Others
app.include_router(app_routers.other_router)
app.include_router(app_routers.config_router)
app.include_router(app_routers.tour_router)
app.include_router(geolocation_routers.router)

# Demo
app.include_router(demo_routers.demo_router)

# Stripe
app.include_router(payment_routers.payment_router)

# Testing (routes are protected by their own test_mode checks)
app.include_router(email_routers.email_test_router)
app.include_router(payment_routers.payment_test_router)


@app.get("/")
def read_root() -> dict:
    """Root endpoint"""

    return {"message": "Welcome to the JAM API"}


health_router = APIRouter(prefix="/health", tags=["health"])


@app.get("/health")
def health_check() -> dict:
    """Health check endpoint"""

    return {"status": "ok"}
