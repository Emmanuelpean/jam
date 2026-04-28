"""Pydantic schemas for the Job Email Scraping.
Contains data models for job alert emails, scraped job postings, and service logs
used in the external job scraping and notification system."""

import datetime as dt
from datetime import datetime

from pydantic import field_validator, Field

from app.base_schemas import BaseModel, OwnedOut, Out, serialise_relationships
from app.data_tables.schemas import GeolocationOut
from app.job_rating.schemas import JobRatingOut


class Salary(BaseModel):
    min_amount: float | None = None
    max_amount: float | None = None
    currency: str | None = None


class JobInfo(BaseModel):
    title: str | None = None
    description: str | None = None
    url: str | None = None
    raw_url: str | None = None
    deadline: dt.datetime | None = None
    salary: Salary = Field(default_factory=Salary)
    is_closed: bool = False


class JobResult(BaseModel):
    platform: str | None = None
    job_id: str | None = None
    company: str | None = None
    company_id: str | None = None
    location: str | None = None
    raw: str | None = None
    job: JobInfo


# --------------------------------------------------- JOB ALERT EMAIL --------------------------------------------------


class JobEmail(BaseModel):
    """Job Alert Email base schema"""

    external_email_id: str | None
    subject: str | None = None
    sender: str | None = None
    date_received: datetime | None = None
    platform: str | None = None
    body: str | None = None
    service_log_id: int | None = None
    job_found_n: int | None = 0
    alert_name: str | None = None


class JobEmailUpdate(JobEmail):
    """Job Alert Email update schema"""

    pass


class JobEmailOut(JobEmail, OwnedOut):
    """Job Alert Email output schema"""

    jobs: list[int]

    @field_validator("jobs", mode="before")
    @classmethod
    def serialize_relationships(cls, value) -> list[int]:
        """Serialize relationships to list of IDs"""

        return serialise_relationships(value)


# ----------------------------------------------------- SCRAPED JOB ----------------------------------------------------


class ScrapedJob(BaseModel):
    """Scraped Job base schema"""

    external_job_id: str
    platform: str
    service_log_id: int
    is_processed: bool = False
    is_scraped: bool = False
    is_failed: bool = False
    scrape_datetime: datetime | None = None
    scrape_error: list[dict] = []
    is_active: bool = True
    is_imported: bool = False
    is_skipped: bool = False
    skip_reason: str | None = None
    retry_count: int = 0
    next_retry_at: datetime | None = None
    read_at: datetime | None = None

    # Job data
    title: str | None = None
    description: str | None = None
    salary_min: float | None = None
    salary_max: float | None = None
    salary_currency: str | None = None
    url: str | None = None
    deadline: datetime | None = None
    location: str | None = None
    attendance_type: str | None = None
    is_closed: bool = False
    raw_location: str | None = None
    company: str | None = None


class ScrapedJobUpdate(BaseModel):
    """Scraped Job update schema"""

    is_active: bool | None = None
    is_imported: bool | None = None
    read_at: datetime | None = None


class ScrapedJobOut(ScrapedJob, OwnedOut):
    """Scraped Job output schema"""

    emails: list[int]
    job_rating: JobRatingOut | None
    geolocation: GeolocationOut | None

    @field_validator("emails", mode="before")
    @classmethod
    def serialize_relationships(cls, value) -> list[int]:
        """Serialize relationships to list of IDs"""

        return serialise_relationships(value)


class PaginatedScrapedJobResponse(BaseModel):
    """Paginated Scraped Job response schema"""

    items: list[ScrapedJobOut]
    total: int
    total_filtered: int
    page: int
    page_size: int
    total_pages: int


class PaginatedJobEmailResponse(BaseModel):
    """Paginated Job Email response schema"""

    items: list[JobEmailOut]
    total: int
    total_filtered: int
    page: int
    page_size: int
    total_pages: int


class PaginatedScrapedJobIdsResponse(BaseModel):
    """Paginated Scraped Job IDs-only response schema"""

    items: list[int]
    total: int
    page: int
    page_size: int
    total_pages: int


class PlatformAlertStats(BaseModel):
    """Platform Alert Stats output schema"""

    platform: str
    alert_name: str | None = None
    scraped_count: int
    imported_count: int
    applied_count: int


# ----------------------------------------------------- SERVICE LOG ----------------------------------------------------


class JobEmailScrapingServiceLogOut(Out):
    """Job Email Scraping Service Log output schema"""

    run_datetime: datetime | None = None
    run_duration: float | None = None
    is_success: bool | None = None
    error_message: str | None = None

    # Users
    user_found_ids: list[int] = []
    user_processed_ids: list[int] = []

    # Emails
    email_found_n: int = 0
    email_saved_n: int = 0
    email_skipped_n: int = 0

    # Jobs
    job_found_n: int = 0
    job_to_process_n: int = 0
    job_scrape_succeeded_n: int = 0
    job_scrape_failed_n: int = 0
    job_scrape_copied_n: int = 0
    job_scrape_skipped_n: int = 0

    # Relationships
    emails: list[int]
    scraped_jobs: list[int]
    platform_stats: list["JobEmailScrapingPlatformStatOut"]
    service_errors: list["JobEmailScrapingServiceErrorOut"]

    @field_validator("emails", "scraped_jobs", mode="before")
    @classmethod
    def serialize_relationships(cls, value) -> list[int]:
        """Serialize relationships to list of IDs"""
        return serialise_relationships(value)


# --------------------------------------------------- PLATFORM STATS ---------------------------------------------------


class JobEmailScrapingPlatformStatOut(Out):
    """Job Email Scraping Platform Stat output schema"""

    name: str | None = None

    # Jobs
    job_found_ids: list[int] = []
    job_to_process_ids: list[int] = []
    job_scrape_succeeded_ids: list[int] = []
    job_scrape_failed_ids: list[int] = []
    job_scrape_copied_ids: list[int] = []
    job_scrape_skipped_ids: list[int] = []

    # Emails
    email_saved_ids: list[int] = []
    email_skipped_ids: list[int] = []

    service_log_id: int | None = None


# --------------------------------------------- JOB SCRAPING SERVICE ERROR ---------------------------------------------


class JobEmailScrapingServiceErrorOut(Out):
    """Job Email Scraping Service Error output schema"""

    error_type: str
    message: str
    traceback: str


# ------------------------------------------------ EMAIL SCRAPER SERVICE -----------------------------------------------


class JobEmailScrapingStartRequest(BaseModel):
    """Start Request schema for email scraper service"""

    period_hours: float | None = 3.0
    timedelta_days: int | None = 1


# ------------------------------------------------- SCRAPED JOB FILTER -------------------------------------------------


class ScrapingFilterCreate(BaseModel):
    """Scraped Job Filter creation schema"""

    type: str
    value: str
    operator: str
    is_active: bool = True
    case_sensitive: bool = False


class ScrapingFilterUpdate(ScrapingFilterCreate):
    """Scraped Job Filter update schema"""

    type: str | None = None
    value: str | None = None
    operator: str | None = None


class ScrapingFilterOut(OwnedOut, ScrapingFilterCreate):
    """Scraped Job Filter output schema"""

    filtered_jobs: list[int]

    @field_validator("filtered_jobs", mode="before")
    @classmethod
    def serialize_relationships(cls, value) -> list[int]:
        """Serialize relationships to list of IDs"""
        return serialise_relationships(value)


class ScrapingFavouriteFilterOut(OwnedOut, ScrapingFilterCreate):
    """Scraped Job Favourite Filter output schema"""

    pass


class FilterPreviewResponse(BaseModel):
    """Response schema for filter preview endpoint"""

    items: list[ScrapedJobOut]
    total: int
    total_filtered: int
    page: int
    page_size: int
    total_pages: int


# ------------------------------------------- FORWARDING CONFIRMATION LINK ---------------------------------------------


class ForwardingConfirmationLinkOut(OwnedOut):
    """Forwarding Confirmation Link output schema"""

    url: str
    platform: str


class ForwardingConfirmationLinkUpdate(BaseModel):
    """Forwarding Confirmation Link update schema"""

    is_used: bool
