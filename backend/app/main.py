"""Main script"""

from contextlib import asynccontextmanager

import jwt
from fastapi import FastAPI, APIRouter, Request
from fastapi.middleware.cors import CORSMiddleware

from app import database
from app.config import settings
from app.core.routers import auth as auth_routers
from app.core.routers import settings as settings_routers
from app.core.routers import user as user_routers
from app.data_tables import routers as data_table_routers
from app.demo.router import demo_router
from app.demo.setup import setup_demo_schema
from app.emails.routers import templates as email_template_router
from app.emails.routers import tests as email_test_router
from app.job_email_scraping import routers as job_scraping_routers
from app.job_rating import routers as job_rating_routers
from app.payments import routers as payment_router
from app.payments import test_routers as payment_test_routers
from app.routers import export as export_routers
from app.routers import others as other_routers
from app.geolocation import routers as geolocation_routers


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Application lifespan event handler."""

    setup_demo_schema()
    yield


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
    CORSMiddleware,
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
        except Exception:
            pass
    response = await call_next(request)
    database.demo_mode.set(False)
    return response


# Data table routers
app.include_router(data_table_routers.company_router)
app.include_router(data_table_routers.person_router)
app.include_router(data_table_routers.location_router)
app.include_router(data_table_routers.job_router)
app.include_router(data_table_routers.aggregator_router)
app.include_router(data_table_routers.interview_router)
app.include_router(data_table_routers.keyword_router)
app.include_router(data_table_routers.file_router)
app.include_router(data_table_routers.job_application_update_router)
app.include_router(data_table_routers.speculative_application_update_router)

# Job Scraping routers
app.include_router(job_scraping_routers.scraped_job_router)
app.include_router(job_scraping_routers.job_alert_email_router)
app.include_router(job_scraping_routers.job_scraping_service_log_router)
app.include_router(job_scraping_routers.scraper_router)
app.include_router(job_scraping_routers.email_scraper_service_router)
app.include_router(job_scraping_routers.scraping_filter_router)
app.include_router(job_scraping_routers.forwarding_confirmation_router)

# Job Rating routers
app.include_router(job_rating_routers.ai_system_prompt_router)
app.include_router(job_rating_routers.job_rating_router)
app.include_router(job_rating_routers.job_rating_service_log_router)
app.include_router(job_rating_routers.job_rating_service_router)

# User routers
app.include_router(user_routers.user_router)
app.include_router(user_routers.current_user_router)
app.include_router(user_routers.user_qualification_router)

# Auth routers
app.include_router(auth_routers.login_router)
app.include_router(auth_routers.register_router)
app.include_router(auth_routers.password_router)

# Export router
app.include_router(export_routers.router)

# Settings router
app.include_router(settings_routers.settings_router)

# Email admin
app.include_router(email_template_router.router)

# Others
app.include_router(other_routers.other_router)
app.include_router(other_routers.config_router)
app.include_router(geolocation_routers.router)

# Demo
app.include_router(demo_router)

# Stripe
app.include_router(payment_router.payment_router)

# Testing
if settings.test_mode:
    app.include_router(email_test_router.router)
    app.include_router(payment_test_routers.test_router)


@app.get("/")
def read_root() -> dict:
    """Root endpoint"""

    return {"message": "Welcome to the JAM API"}


health_router = APIRouter(prefix="/health", tags=["health"])


@app.get("/health")
def health_check() -> dict:
    """Health check endpoint"""

    return {"status": "ok"}
