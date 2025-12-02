"""Pydantic schemas for the email ingestion service.
Contains data models for job alert emails, scraped job postings, and service logs
used in the external job scraping and notification system."""

from datetime import datetime

from pydantic import field_validator

from app.schemas import BaseModel, OwnedOut, Out, serialize_relationships


# --------------------------------------------------- JOB ALERT EMAIL --------------------------------------------------


class JobAlertEmail(BaseModel):
    """Job Alert Email base schema"""

    external_email_id: str | None
    subject: str | None = None
    sender: str | None = None
    date_received: datetime | None = None
    platform: str | None = None
    body: str | None = None
    service_log_id: int | None = None
    job_found_n: int | None = 0


class JobAlertEmailUpdate(JobAlertEmail):
    """Job Alert Email update schema"""

    pass


class JobAlertEmailOut(JobAlertEmail, OwnedOut):
    """Job Alert Email output schema"""

    jobs: list[int]

    @field_validator("jobs", mode="before")
    @classmethod
    def serialize_relationships(cls, value) -> list[int]:
        """Serialize relationships to list of IDs"""

        return serialize_relationships(value)


# ----------------------------------------------------- SCRAPED JOB ----------------------------------------------------


class ScrapedJob(BaseModel):
    """Scraped Job base schema"""

    external_job_id: str
    platform: str
    service_log_id: int
    is_scraped: bool = False
    is_failed: bool = False
    scrape_datetime: datetime | None = None
    scrape_error: str | None = None
    is_active: bool = True
    is_imported: bool = False

    # Job data
    title: str | None = None
    description: str | None = None
    salary_min: float | None = None
    salary_max: float | None = None
    salary_currency: str | None = None
    url: str | None = None
    deadline: datetime | None = None
    attendance_type: str | None = None
    location: str | None = None
    location_city: str | None = None
    location_postcode: str | None = None
    location_country: str | None = None
    company: str | None = None


class ScrapedJobUpdate(BaseModel):
    """Scraped Job update schema"""

    is_active: bool | None = None
    is_imported: bool | None = None


class ScrapedJobOut(ScrapedJob, OwnedOut):
    """Scraped Job output schema"""

    emails: list[int]

    @field_validator("emails", mode="before")
    @classmethod
    def serialize_relationships(cls, value) -> list[int]:
        """Serialize relationships to list of IDs"""

        return serialize_relationships(value)


class PaginatedScrapedJobResponse(BaseModel):
    """Paginated Scraped Job response schema"""

    items: list[ScrapedJobOut]
    total: int
    page: int
    page_size: int
    total_pages: int


# ----------------------------------------------------- SERVICE LOG ----------------------------------------------------


class EisServiceLogOut(Out):
    """EIS Service Log output schema"""

    run_datetime: datetime | None = None
    run_duration: float | None = None
    is_success: bool | None = None
    error_message: str | None = None

    # Users
    user_found_n: int = 0
    user_processed_n: int = 0

    # Emails
    email_found_n: int = 0
    email_saved_n: int = 0
    email_skipped_n: int = 0

    # Relationships
    emails: list[int]
    scraped_jobs: list[int]
    platform_stats: list["PlatformStatOut"]

    # Dynamic fields
    jobs_found_n: int = 0
    jobs_scraped_n: int = 0
    jobs_failed_n: int = 0
    jobs_copied_n: int = 0

    @field_validator("emails", "scraped_jobs", mode="before")
    @classmethod
    def serialize_relationships(cls, value) -> list[int]:
        """Serialize relationships to list of IDs"""

        return serialize_relationships(value)


# --------------------------------------------------- PLATFORM STATS ---------------------------------------------------


class PlatformStatOut(Out):
    """Platform Stat output schema"""

    name: str | None = None

    # Jobs
    job_found_n: int = 0
    job_scraped_n: int = 0
    job_failed_n: int = 0
    job_copied_n: int = 0

    # Emails
    email_saved_n: int = 0
    email_skipped_n: int = 0

    service_log_id: int | None = None


# ------------------------------------------------ EMAIL SCRAPER SERVICE -----------------------------------------------


class StartRequest(BaseModel):
    """Start Request schema for email scraper service"""

    period_hours: float | None = 3.0
    timedelta_days: int | None = 1
