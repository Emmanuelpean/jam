"""Pydantic schemas for the email ingestion service.
Contains data models for job alert emails, scraped job postings, and service logs
used in the external job scraping and notification system."""

from datetime import datetime

from app.schemas import BaseModel, OwnedOut, Out


# --------------------------------------------------- JOB ALERT EMAIL --------------------------------------------------


class JobAlertEmailCreate(BaseModel):
    """Job Alert Email create schema"""

    external_email_id: str
    subject: str | None = None
    sender: str | None = None
    date_received: datetime | None = None
    platform: str | None = None
    body: str | None = None
    service_log_id: int | None = None
    job_found_n: int | None = 0


class JobAlertEmailUpdate(JobAlertEmailCreate):
    """Job Alert Email update schema"""

    external_email_id: str | None = None


class JobAlertEmailOut(JobAlertEmailCreate, OwnedOut):
    """Job Alert Email output schema"""

    jobs: list["ScrapedJobMinOut"]
    service_log: "EisServiceLogMinOut"


class JobAlertEmailMinOut(JobAlertEmailCreate, OwnedOut):
    """Job Alert Email minimal output schema"""

    pass


# ----------------------------------------------------- SCRAPED JOB ----------------------------------------------------


class ScrapedJobCreate(BaseModel):
    """Scraped Job create schema"""

    external_job_id: str
    is_scraped: bool = False
    is_failed: bool = False
    scrape_error: str | None = None
    is_active: bool = True
    is_imported: bool = False

    # Job data
    title: str | None = None
    description: str | None = None
    salary_min: float | None = None
    salary_max: float | None = None
    url: str | None = None
    deadline: datetime | None = None
    attendance_type: str | None = None
    location_name: str | None = None
    location_city: str | None = None
    location_postcode: str | None = None
    location_country: str | None = None
    company: str | None = None


class ScrapedJobUpdate(BaseModel):
    """Scraped Job update schema"""

    is_active: bool | None = None
    is_imported: bool | None = None


class ScrapedJobOut(ScrapedJobCreate, OwnedOut):
    """Scraped Job output schema"""

    emails: list[JobAlertEmailMinOut]


class ScrapedJobMinOut(ScrapedJobCreate, OwnedOut):
    """Scraped Job minimal output schema"""

    pass


# ----------------------------------------------------- SERVICE LOG ----------------------------------------------------


class EisServiceLogCreate(BaseModel):
    """EIS Service Log create schema"""

    run_datetime: datetime
    run_duration: float | None = None
    is_success: bool | None = None
    error_message: str | None = None
    job_success_n: int | None = None
    job_fail_n: int | None = None


class EisServiceLogUpdate(EisServiceLogCreate):
    """EIS Service Log update schema"""

    run_datetime: datetime | None = None


class EisServiceLogOut(EisServiceLogCreate, Out):
    """EIS Service Log output schema"""

    emails: list[JobAlertEmailOut]


class EisServiceLogMinOut(EisServiceLogCreate, Out):
    """EIS Service Log minimal output schema"""

    pass
