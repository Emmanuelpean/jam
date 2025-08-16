from datetime import datetime

from app.schemas import BaseModel, OwnedOut, Out, JobOut


# --------------------------------------------------- JOB ALERT EMAIL --------------------------------------------------


class JobAlertEmail(BaseModel):
    """Job Alert Email input model"""

    external_email_id: str
    subject: str | None = None
    sender: str | None = None
    date_received: datetime | None = None
    platform: str | None = None
    body: str | None = None
    service_log_id: int | None = None


class JobAlertEmailUpdate(JobAlertEmail):
    """Job Alert Email output model"""

    external_email_id: str | None = None


class JobAlertEmailOut(JobAlertEmail, OwnedOut):
    """Email model"""

    jobs: list["ScrapedJobOut"]


# ----------------------------------------------------- SCRAPED JOB ----------------------------------------------------


class ScrapedJob(BaseModel):

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


class ScrapedJobUpdate(ScrapedJob):
    """Represents scraped job postings from external sources with additional metadata."""

    external_job_id: str | None = None


class ScrapedJobOut(ScrapedJob, OwnedOut):
    """Represents scraped job postings from external sources with additional metadata."""

    pass
    # emails: list[JobAlertEmailOut]


# ----------------------------------------------------- SERVICE LOG ----------------------------------------------------


class ServiceLog(BaseModel):
    """Represents a log of a service run."""

    name: str
    run_datetime: datetime
    run_duration: float | None = None
    is_success: bool | None = None
    error_message: str | None = None
    job_success_n: int | None = None
    job_fail_n: int | None = None


class ServiceLogUpdate(ServiceLog):
    """Represents a log of a service run."""

    name: str | None = None


class ServiceLogOut(ServiceLog, Out):
    """Represents a log of a service run."""

    emails: list[JobAlertEmailOut]
