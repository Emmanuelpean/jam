"""Pydantic schemas for the email ingestion service.
Contains data models for job alert emails, scraped job postings, and service logs
used in the external job scraping and notification system."""

from datetime import datetime

from app.schemas import BaseModel, OwnedOut, Out


# --------------------------------------------------- JOB ALERT EMAIL --------------------------------------------------


class JobAlertEmailCreate(BaseModel):
    external_email_id: str
    subject: str | None = None
    sender: str | None = None
    date_received: datetime | None = None
    platform: str | None = None
    body: str | None = None
    service_log_id: int | None = None


class JobAlertEmailUpdate(JobAlertEmailCreate):
    external_email_id: str | None = None


class JobAlertEmailOut(JobAlertEmailCreate, OwnedOut):
    jobs: list["ScrapedJobOut"]


# ----------------------------------------------------- SCRAPED JOB ----------------------------------------------------


class ScrapedJobCreate(BaseModel):
    external_job_id: str
    is_scraped: bool = False
    is_failed: bool = False
    scrape_error: str | None = None
    is_active: bool = True

    # Job data
    title: str | None = None
    description: str | None = None
    salary_min: float | None = None
    salary_max: float | None = None
    url: str | None = None
    deadline: datetime | None = None
    company: str | None = None
    location: str | None = None


class ScrapedJobUpdate(ScrapedJobCreate):
    """Represents scraped job postings from external sources with additional metadata."""

    external_job_id: str | None = None


class ScrapedJobOut(ScrapedJobCreate, OwnedOut):
    """Represents scraped job postings from external sources with additional metadata."""

    pass
    # emails: list[JobAlertEmailOut]


# ----------------------------------------------------- SERVICE LOG ----------------------------------------------------


class EisServiceLogCreate(BaseModel):
    """Represents a log of a service run."""

    name: str
    run_datetime: datetime
    run_duration: float | None = None
    is_success: bool | None = None
    error_message: str | None = None
    job_success_n: int | None = None
    job_fail_n: int | None = None


class EisServiceLogUpdate(EisServiceLogCreate):
    """Represents a log of a service run."""

    name: str | None = None


class EisServiceLogOut(EisServiceLogCreate, Out):
    """Represents a log of a service run."""

    emails: list[JobAlertEmailOut]
