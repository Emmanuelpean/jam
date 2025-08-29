"""Email Ingestion System (EIS) Database Models

Defines SQLAlchemy ORM models for email-based job scraping functionality.
Includes models for job alert emails, extracted job IDs, and scraped job data
with associated companies and locations from external sources."""

from sqlalchemy import Column, String, Boolean, ForeignKey, Integer, DateTime, Float, TIMESTAMP, Table, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import expression

from app.models import Base, CommonBase, Owned


# ------------------------------------------------------ MAPPINGS ------------------------------------------------------


email_scrapedjob_mapping = Table(
    "email_scrapedjob_mapping",
    Base.metadata,
    Column("email_id", Integer, ForeignKey("job_alert_email.id", ondelete="CASCADE"), primary_key=True),
    Column("job_id", Integer, ForeignKey("scraped_job.id", ondelete="CASCADE"), primary_key=True),
)


# -------------------------------------------------------- DATA --------------------------------------------------------


class JobAlertEmail(Owned, Base):
    """Represents email messages containing job information like LinkedIn and Indeed job alerts

    Attributes:
    -----------
    - `external_email_id` (str): Unique identifier for the email message.
    - `subject` (str): Subject of the email message.
    - `sender` (str): Sender of the email message.
    - `date_received` (datetime): Date and time when the email was received.
    - `platform` (str): Platform from which the email was received (LinkedIn, Indeed, etc.).
    - `body` (str): Body of the email message.

    Foreign keys:
    -------------
    - `service_log_id` (int, optional): Identifier for the EisServiceLog associated with the email.

    Relationships:
    --------------
    - `jobs` (list of ScrapedJob): List of scraped jobs associated with the email.
    - `service_log` (EisServiceLog): EisServiceLog object associated with the email."""

    external_email_id = Column(String, unique=True, nullable=False)
    subject = Column(String, nullable=True)
    sender = Column(String, nullable=True)
    date_received = Column(TIMESTAMP(timezone=True), nullable=True)
    platform = Column(String, nullable=True)
    body = Column(String, nullable=True)

    # Foreign keys
    service_log_id = Column(Integer, ForeignKey("eis_service_log.id", ondelete="SET NULL"), nullable=True)

    # Relationships
    jobs = relationship("ScrapedJob", secondary=email_scrapedjob_mapping, back_populates="emails")
    service_log = relationship("EisServiceLog", back_populates="emails")


class ScrapedJob(Owned, Base):
    """Represents scraped job postings from external sources with additional metadata.

    Attributes:
    -----------
    - `external_job_id` (str): Unique identifier for the job posting.
    - `is_scraped` (bool): Indicates whether the job has been scraped.
    - `is_failed` (bool): Indicates whether the job scraping failed.
    - `scrape_error` (str, optional): Error message if the job scraping failed.
    - `is_active` (bool): Indicates whether the job is active
    - `title` (str, optional): Title of the job.
    - `description` (str, optional): Description of the job.
    - `salary_min` (float, optional): Minimum salary of the job.
    - `salary_max` (float, optional): Maximum salary of the job.
    - `url` (str, optional): URL to the job posting.
    - `deadline` (datetime, optional): Deadline for the job.
    - `company` (str, optional): Company name of the job.
    - `location` (str, optional): Location of the job.

    Relationships:
    --------------
    - `emails` (list of JobAlertEmail): List of email messages associated with the job."""

    external_job_id = Column(String, nullable=False)
    is_scraped = Column(Boolean, nullable=False, server_default=expression.false())
    is_failed = Column(Boolean, nullable=False, server_default=expression.false())
    scrape_error = Column(String, nullable=True)
    is_active = Column(Boolean, nullable=False, server_default=expression.true())

    # Job data
    title = Column(String, nullable=True)
    description = Column(String, nullable=True)
    salary_min = Column(Float, nullable=True)
    salary_max = Column(Float, nullable=True)
    url = Column(String, nullable=True)
    deadline = Column(TIMESTAMP(timezone=True), nullable=True)
    company = Column(String, nullable=True)
    location = Column(String, nullable=True)

    # Relationships
    emails = relationship("JobAlertEmail", secondary=email_scrapedjob_mapping, back_populates="jobs")

    # Constraints
    __table_args__ = (
        UniqueConstraint('external_job_id', 'owner_id', name='unique_job_per_owner'),
    )


class EisServiceLog(CommonBase, Base):
    """Represents logs of service operations and their status.

    Attributes:
    -----------
    - `name` (str): Name of the service.
    - `run_duration` (float, optional): Duration of the service run.
    - `run_datetime` (datetime): Date and time of the service run.
    - `is_success` (bool): Indicates whether the service run was successful.
    - `error_message` (str, optional): Error message if the service run failed.
    - `job_success_n` (int, optional): Number of successful jobs scraped.
    - `job_fail_n` (int, optional): Number of failed jobs scraped.
    - `users_processed_n` (int, optional): Number of users processed.
    - `emails_found_n` (int, optional): Number of email messages found.
    - `emails_saved_n` (int, optional): Number of email messages saved.
    - `jobs_extracted_n` (int, optional): Number of jobs extracted.
    - `linkedin_job_n` (int, optional): Number of LinkedIn jobs extracted.
    - `indeed_job_n` (int, optional): Number of Indeed jobs extracted.

    Relationships:
    --------------
    - `emails` (list of JobAlertEmail): List of email messages associated with the service."""

    name = Column(String, nullable=False)
    run_duration = Column(Float, nullable=True)
    run_datetime = Column(DateTime, nullable=False)
    is_success = Column(Boolean, nullable=True)
    error_message = Column(String, nullable=True)
    job_success_n = Column(Integer, nullable=True)
    job_fail_n = Column(Integer, nullable=True)
    users_processed_n = Column(Integer, nullable=True)
    emails_found_n = Column(Integer, nullable=True)
    emails_saved_n = Column(Integer, nullable=True)
    jobs_extracted_n = Column(Integer, nullable=True)
    linkedin_job_n = Column(Integer, nullable=True)
    indeed_job_n = Column(Integer, nullable=True)

    emails = relationship("JobAlertEmail", back_populates="service_log")
