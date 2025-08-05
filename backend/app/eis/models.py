"""Email Ingestion System (EIS) Database Models

Defines SQLAlchemy ORM models for email-based job scraping functionality.
Includes models for job alert emails, extracted job IDs, and scraped job data
with associated companies and locations from external sources."""

from sqlalchemy import Column, String, Boolean, ForeignKey, Integer, DateTime, Float, TIMESTAMP, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import expression
from app import schemas
from datetime import datetime
from app.routers.tables import generate_crud_router

from app.models import CommonBase, Base

email_scrapedjob_mapping = Table(
    "email_scrapedjob_mapping",
    Base.metadata,
    Column("email_id", Integer, ForeignKey("jobalertemail.id", ondelete="CASCADE"), primary_key=True),
    Column("job_id", Integer, ForeignKey("jobscraped.id", ondelete="CASCADE"), primary_key=True),
)


class JobAlertEmail(CommonBase, Base):
    """Represents email messages containing job information like LinkedIn and Indeed job alerts"""

    external_email_id = Column(String, unique=True, nullable=False)
    subject = Column(String)
    sender = Column(String)
    date_received = Column(DateTime)
    platform = Column(String)
    body = Column(String)

    # Many-to-many relationship with scraped jobs
    jobs = relationship("JobScraped", secondary=email_scrapedjob_mapping, back_populates="emails")


class Email(schemas.BaseModel):
    """Email model"""

    external_email_id: str
    subject: str | None = None
    sender: str | None = None
    date_received: datetime | None = None
    platform: str | None = None
    body: str | None = None


class EmailUpdate(Email):
    """Email model"""

    external_email_id: str | None = None


class EmailOut(Email, schemas.Out):
    """Email model"""

    jobs: list[schemas.JobOut]


generate_crud_router(
    table_model=JobAlertEmail,
    create_schema=Email,
    update_schema=EmailUpdate,
    out_schema=EmailOut,
    endpoint="jobalertemails",
    not_found_msg="Job alert email not found",
)


class JobScraped(CommonBase, Base):
    """Represents scraped job postings from external sources with additional metadata."""

    external_job_id = Column(String, nullable=False, unique=True)
    is_scraped = Column(Boolean, nullable=False, server_default=expression.false())
    is_failed = Column(Boolean, nullable=False, server_default=expression.false())
    scrape_error = Column(String, nullable=True)

    # Job data
    title = Column(String, nullable=True)
    description = Column(String, nullable=True)
    salary_min = Column(Float, nullable=True)
    salary_max = Column(Float, nullable=True)
    url = Column(String, nullable=True)
    deadline = Column(TIMESTAMP(timezone=True), nullable=True)
    company = Column(String, nullable=True)
    location = Column(String, nullable=True)

    # Many-to-many relationship with scraped jobs
    emails = relationship("JobAlertEmail", secondary=email_scrapedjob_mapping, back_populates="jobs")


class JobScrape(schemas.BaseModel):

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


class JobScrapeUpdate(JobScrape):
    """Represents scraped job postings from external sources with additional metadata."""

    external_job_id: str | None = None


class JobScrapeOut(JobScrape):
    """Represents scraped job postings from external sources with additional metadata."""

    emails: list[EmailOut]


generate_crud_router(
    table_model=JobScraped,
    create_schema=JobScrape,
    update_schema=JobScrapeUpdate,
    out_schema=JobScrapeOut,
    endpoint="scrapedjobs",
    not_found_msg="Scraped job not found",
)


class ServiceLog(Base):
    """Represents logs of service operations and their status."""

    __tablename__ = "servicelog"

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, nullable=False)
    run_duration = Column(Float)
    run_datetime = Column(DateTime)
    is_success = Column(Boolean, nullable=False)
    error_message = Column(String, nullable=True)
    job_success_n = Column(Integer, nullable=True)
    job_fail_n = Column(Integer, nullable=True)
