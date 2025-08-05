"""Email Ingestion System (EIS) Database Models

Defines SQLAlchemy ORM models for email-based job scraping functionality.
Includes models for job alert emails, extracted job IDs, and scraped job data
with associated companies and locations from external sources."""

from sqlalchemy import Column, String, Boolean, ForeignKey, Integer, DateTime, Float, TIMESTAMP, Table, text, func
from sqlalchemy.orm import relationship
from sqlalchemy.sql import expression

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
    jobs = relationship("ScrapedJob", secondary=email_scrapedjob_mapping, back_populates="emails")


class ScrapedJob(CommonBase, Base):
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
    created_at = Column(TIMESTAMP(timezone=True), server_default=text("now()"), nullable=False)
    modified_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
