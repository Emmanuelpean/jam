from datetime import datetime

from app.schemas import BaseModel, Out, JobOut


class JobAlertEmail(BaseModel):
    """Email model"""

    external_email_id: str
    subject: str | None = None
    sender: str | None = None
    date_received: datetime | None = None
    platform: str | None = None
    body: str | None = None


class EmailUpdate(JobAlertEmail):
    """Email model"""

    external_email_id: str | None = None


class JobAlertEmailOut(JobAlertEmail, Out):
    """Email model"""

    jobs: list[JobOut]


class ScrapedJob(BaseModel):

    external_job_id: str
    is_scraped: bool = False
    is_failed: bool = False
    scrape_error: str | None = None

    title: str | None = None
    description: str | None = None
    salary_min: float | None = None
    salary_max: float | None = None
    url: str | None = None
    deadline: datetime | None = None
    company: str | None = None
    location: str | None = None


class ScrapedJobUpdate(ScrapedJob):
    """Represents scraped job postings from external sources with additional metadata."""

    external_job_id: str | None = None


class ScrapedJobOut(ScrapedJob):
    """Represents scraped job postings from external sources with additional metadata."""

    emails: list[JobAlertEmailOut]


class ServiceLog(BaseModel):
    """Represents a log of a service run."""

    name: str
    run_duration: float
    run_datetime: datetime
    is_success: bool
    error_message: str | None = None
    job_success_n: int | None = None
    job_fail_n: int | None = None


class ServiceLogOut(ServiceLog):
    """Represents a log of a service run."""

    pass


class ServiceLogUpdate(ServiceLog):
    """Represents a log of a service run."""

    id: int | None = None
