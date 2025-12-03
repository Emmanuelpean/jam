"""Email Ingestion System (EIS) Database Models

Defines SQLAlchemy ORM models for email-based job scraping functionality.
Includes models for job alert emails, extracted job IDs, and scraped job data
with associated companies and locations from external sources."""

from sqlalchemy import Column, String, Boolean, ForeignKey, Integer, Float, TIMESTAMP, Table, UniqueConstraint
from sqlalchemy.dialects.postgresql import ARRAY as PG_ARRAY
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from sqlalchemy.sql import expression

from app.models import Base, CommonBase, Owned

# ------------------------------------------------------ MAPPINGS ------------------------------------------------------


jobalertemail_scrapedjob_mapping = Table(
    "jobalertemail_scrapedjob_mapping",
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
    - 'job_found_n' (int): Number of jobs found in the email
    - `platform` (str): Platform from which the email was received (LinkedIn, Indeed, etc.).
    - `body` (str): Body of the email message.

    Foreign keys:
    -------------
    - `service_log_id` (int, optional): Identifier for the EisServiceLog associated with the email.

    Relationships:
    --------------
    - `jobs` (list of ScrapedJob): List of scraped jobs associated with the email.
    - `service_log` (EisServiceLog): EisServiceLog object associated with the email.

    Constraints:
    ------------
    - Unique constraint on the combination of `external_email_id` and `owner_id` to ensure uniqueness per user."""

    external_email_id = Column(String, unique=True, nullable=False)
    subject = Column(String, nullable=False)
    sender = Column(String, nullable=False)
    date_received = Column(TIMESTAMP(timezone=True), nullable=False)
    job_found_n = Column(Integer, nullable=False, default=0)
    platform = Column(String, nullable=False)
    body = Column(String, nullable=False)

    # Foreign keys
    service_log_id = Column(Integer, ForeignKey("eis_service_log.id", ondelete="SET NULL"), nullable=False)

    # Relationships
    jobs = relationship("ScrapedJob", secondary=jobalertemail_scrapedjob_mapping, back_populates="emails")
    service_log = relationship("EisServiceLog", back_populates="emails")

    __table_args__ = (UniqueConstraint("external_email_id", "owner_id", name="unique_email_per_owner"),)


class ScrapedJob(Owned, Base):
    """Represents scraped job postings from external sources with additional metadata.

    Attributes:
    -----------
    - `external_job_id` (str): Unique identifier for the job posting.
    - `platform` (str): Platform from which the job was scraped (LinkedIn, Indeed, etc.).
    - `is_scraped` (bool): Indicates whether the job has been scraped.
    - `is_failed` (bool): Indicates whether the job scraping failed.
    - `scrape_error` (str, optional): Error message if the job scraping failed.
    - `scrape_datetime` (datetime, optional): Date and time when the job was scraped.
    - `is_active` (bool): Indicates whether the job is active
    - `is_imported` (bool): Indicates whether the job was imported into a job.

    # Job data
    - `title` (str, optional): Title of the job.
    - `description` (str, optional): Description of the job.
    - `salary_min` (float, optional): Minimum salary of the job.
    - `salary_max` (float, optional): Maximum salary of the job.
    - `salary_currency` (str, optional): Salary currency
    - `url` (str, optional): URL to the job posting.
    - `raw_url` (str, optional): Raw URL to the job posting.
    - `deadline` (datetime, optional): Deadline for the job.
    - `company` (str, optional): Company name of the job.
    - `location_postcode` (str, optional): Postcode of the job location.
    - `location_city` (str, optional): City of the job location.
    - `location_country` (str, optional): Country of the job location.
    - `attendance_type` (str, optional): Attendance type of the job (e.g., remote, on-site).

    Relationships:
    --------------
    - `emails` (list of JobAlertEmail): List of email messages associated with the job.

    Constraints:
    ------------
    - Unique constraint on the combination of `external_job_id` and `owner_id` to ensure uniqueness per user."""

    external_job_id = Column(String, nullable=False)
    platform = Column(String, nullable=False)
    is_scraped = Column(Boolean, nullable=False, server_default=expression.false())
    is_failed = Column(Boolean, nullable=False, server_default=expression.false())
    scrape_error = Column(String, nullable=True)
    scrape_datetime = Column(TIMESTAMP(timezone=True), nullable=True)
    is_active = Column(Boolean, nullable=False, server_default=expression.true())
    is_imported = Column(Boolean, nullable=False, server_default=expression.false())

    # Job data
    title = Column(String, nullable=True)
    description = Column(String, nullable=True)
    salary_min = Column(Float, nullable=True)
    salary_max = Column(Float, nullable=True)
    salary_currency = Column(String, nullable=True)
    url = Column(String, nullable=True)
    raw_url = Column(String, nullable=True)
    deadline = Column(TIMESTAMP(timezone=True), nullable=True)
    company = Column(String, nullable=True)
    location = Column(String, nullable=True)
    location_postcode = Column(String, nullable=True)
    location_city = Column(String, nullable=True)
    location_country = Column(String, nullable=True)
    attendance_type = Column(String, nullable=True)

    # Foreign keys
    service_log_id = Column(Integer, ForeignKey("eis_service_log.id", ondelete="SET NULL"), nullable=False)

    # Relationships
    emails = relationship("JobAlertEmail", secondary=jobalertemail_scrapedjob_mapping, back_populates="jobs")
    service_log = relationship("EisServiceLog", back_populates="scraped_jobs")

    # Constraints
    __table_args__ = (UniqueConstraint("external_job_id", "owner_id", name="unique_job_per_owner"),)


class EisServiceLog(CommonBase, Base):
    """Represents logs of service operations and their status.

    Attributes:
    -----------
    - `run_duration` (float, optional): Duration of the service run.
    - `run_datetime` (datetime): Date and time of the service run.
    - `is_success` (bool): Indicates whether the service run was successful.
    - `error_message` (str, optional): Error message if the service run failed.
    - `user_found_ids` (list of int): List of user IDs found during the service run.
    - `user_processed_ids` (list of int): List of user IDs processed during the service run.

    Relationships:
    --------------
    - `emails` (list of JobAlertEmail): List of email messages associated with the service.
    - `scraped_jobs` (list of ScrapedJob): List of scraped jobs associated with the service.
    - `platform_stats` (list of PlatformStat): List of platform statistics associated with the service.
    - `errors` (list of EisServiceError): List of errors associated with the service.

    Properties:
    -----------
    - `job_scrape_succeeded_n` (int): Total successfully scraped jobs across all platforms.
    - `job_scrape_failed_n` (int): Total failed scraped jobs across all platforms.
    - `job_scrape_copied_n` (int): Total copied scraped jobs found across all platforms.
    - `job_found_n` (int): Total jobs found (copied + skipped) across all platforms.
    - `email_saved_n` (int): Total emails saved across all platforms.
    - `email_skipped_n` (int): Total emails skipped across all platforms."""

    run_duration = Column(Float, nullable=True)
    run_datetime = Column(TIMESTAMP(timezone=True), nullable=False)
    is_success = Column(Boolean, nullable=True)
    error_message = Column(String, nullable=True)

    # Users
    user_found_ids = Column(PG_ARRAY(Integer), server_default="{}", nullable=False)
    user_processed_ids = Column(PG_ARRAY(Integer), server_default="{}", nullable=False)

    # Relationships
    emails = relationship("JobAlertEmail", back_populates="service_log")
    scraped_jobs = relationship("ScrapedJob", back_populates="service_log")
    platform_stats = relationship("PlatformStat", back_populates="service_log")
    errors = relationship("EisServiceError", back_populates="service_log")

    def __init__(self, **kwargs):
        """Initialise array fields with empty lists if not provided"""
        kwargs.setdefault("user_found_ids", [])
        kwargs.setdefault("user_processed_ids", [])
        super().__init__(**kwargs)

    @hybrid_property
    def job_scrape_succeeded_n(self) -> int:
        """Total successfully scraped jobs across all platforms."""
        return sum(len(stat.job_scrape_succeeded_ids) for stat in self.platform_stats)

    @hybrid_property
    def job_scrape_failed_n(self) -> int:
        """Total failed scraped jobs across all platforms."""
        return sum(len(stat.job_scrape_failed_ids) for stat in self.platform_stats)

    @hybrid_property
    def job_scrape_copied_n(self) -> int:
        """Total copied scraped jobs found across all platforms."""
        return sum(len(stat.job_scrape_copied_ids) for stat in self.platform_stats)

    @hybrid_property
    def job_scrape_skipped_n(self) -> int:
        """Total skipped scraped jobs found across all platforms."""
        return sum(len(stat.job_scrape_skipped_ids) for stat in self.platform_stats)

    @hybrid_property
    def job_found_n(self) -> int:
        """Total jobs copied/skipped across all platforms."""
        return sum(len(stat.job_found_ids) for stat in self.platform_stats)

    @hybrid_property
    def email_saved_n(self) -> int:
        """Total emails saved across all platforms."""
        return sum(len(stat.email_saved_ids) for stat in self.platform_stats)

    @hybrid_property
    def email_skipped_n(self) -> int:
        """Total emails saved across all platforms."""
        return sum(len(stat.email_skipped_ids) for stat in self.platform_stats)


class PlatformStat(CommonBase, Base):
    """Per-platform stats for a service run linked to an EisServiceLog.

    Attributes:
    -----------
    - `name` (str): Platform name (e.g. LinkedIn, Indeed).

    # Emails
    - `email_saved_ids` (list of int): List of saved email IDs.
    - `email_skipped_ids` (list of int): List of skipped email IDs.

    # Jobs
    - `job_found_ids` (list of int): List of found job IDs from the emails.
    - `job_scrape_failed_ids` (list of int): List of failed job scrape IDs.
    - `job_scrape_success_ids` (list of int): List of successful job scrape IDs.
    - `job_scrape_copied_ids` (list of int): List of copied job scrape IDs.

    # Service Log
    - `service_log_id` (int): Foreign key to the associated EisServiceLog.
    - `service_log` (EisServiceLog): Relationship to the associated EisServiceLog.

    Constraints:
    ------------
    - Unique constraint on the combination of `service_log_id` and `name` to ensure uniqueness per platform per service log.
    """

    name = Column(String, nullable=False)

    # Emails
    email_saved_ids = Column(PG_ARRAY(Integer), server_default="{}", nullable=False)
    email_skipped_ids = Column(PG_ARRAY(Integer), server_default="{}", nullable=False)

    # Jobs
    job_found_ids = Column(PG_ARRAY(Integer), server_default="{}", nullable=False)
    job_scrape_failed_ids = Column(PG_ARRAY(Integer), server_default="{}", nullable=False)
    job_scrape_succeeded_ids = Column(PG_ARRAY(Integer), server_default="{}", nullable=False)
    job_scrape_copied_ids = Column(PG_ARRAY(Integer), server_default="{}", nullable=False)
    job_scrape_skipped_ids = Column(PG_ARRAY(Integer), server_default="{}", nullable=False)

    service_log_id = Column(Integer, ForeignKey("eis_service_log.id", ondelete="CASCADE"), nullable=False)
    service_log = relationship("EisServiceLog", back_populates="platform_stats")

    __table_args__ = (UniqueConstraint("service_log_id", "name", name="unique_platform_per_service_log"),)

    def __init__(self, **kwargs):
        """Initialise array fields with empty lists if not provided"""
        kwargs.setdefault("email_saved_ids", [])
        kwargs.setdefault("email_skipped_ids", [])
        kwargs.setdefault("job_found_ids", [])
        kwargs.setdefault("job_scrape_failed_ids", [])
        kwargs.setdefault("job_scrape_succeeded_ids", [])
        kwargs.setdefault("job_scrape_copied_ids", [])
        kwargs.setdefault("job_scrape_skipped_ids", [])
        super().__init__(**kwargs)


class EisServiceError(CommonBase, Base):
    """Records unexpected/unhandled errors raised during a service run.

    Fields:
    - error_type: short label/class name of the error
    - message: error message
    - traceback: full traceback / details
    - occurred_at: timestamp when the error occurred
    - service_log_id: FK to EisServiceLog
    """

    error_type = Column(String, nullable=False)
    message = Column(String, nullable=True)
    traceback = Column(String, nullable=True)

    service_log_id = Column(Integer, ForeignKey("eis_service_log.id", ondelete="CASCADE"), nullable=False)
    service_log = relationship("EisServiceLog", back_populates="errors")
