"""Job Email Scraper Database Models

Defines SQLAlchemy ORM models for email-based job scraping functionality.
Includes models for job alert emails, extracted job IDs, and scraped job data
with associated companies and locations from external sources."""

from sqlalchemy import (
    Column,
    String,
    Boolean,
    ForeignKey,
    Integer,
    Float,
    TIMESTAMP,
    Table,
    UniqueConstraint,
    CheckConstraint,
)
from sqlalchemy.dialects.postgresql import ARRAY as PG_ARRAY
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from sqlalchemy.sql import expression

from app.models import Base, CommonBase, Owned, ServiceLog

# ------------------------------------------------------ MAPPINGS ------------------------------------------------------


jobemail_scrapedjob_mapping = Table(
    "jobemail_scrapedjob_mapping",
    Base.metadata,
    Column("email_id", Integer, ForeignKey("job_email.id", ondelete="CASCADE"), primary_key=True),
    Column("job_id", Integer, ForeignKey("scraped_job.id", ondelete="CASCADE"), primary_key=True),
)


# -------------------------------------------------------- DATA --------------------------------------------------------


class JobEmail(Owned, Base):
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
    - `alert_name` (str, optional): Name of the job alert associated with the email.

    Foreign keys:
    -------------
    - `service_log_id` (int, optional): Identifier for the JobEmailScrapingServiceLog associated with the email.

    Relationships:
    --------------
    - `jobs` (list of ScrapedJob): List of scraped jobs associated with the email.
    - `service_log` (JobEmailScrapingServiceLog): JobEmailScrapingServiceLog object associated with the email.

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
    alert_name = Column(String, nullable=True)

    # Foreign keys
    service_log_id = Column(
        Integer, ForeignKey("job_email_scraping_service_log.id", ondelete="SET NULL"), nullable=False
    )

    # Relationships
    jobs = relationship("ScrapedJob", secondary=jobemail_scrapedjob_mapping, back_populates="emails")
    service_log = relationship("JobEmailScrapingServiceLog", back_populates="emails")

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

    Foreign keys:
    -------------
    - `service_log_id` (int): Identifier for the JobEmailScrapingServiceLog associated with the job.

    Relationships:
    --------------
    - `emails` (list of JobEmail): List of email messages associated with the job.
    - `service_log` (JobEmailScrapingServiceLog): JobEmailScrapingServiceLog object associated with the job.
    - `job_rating` (JobRating): JobRating object associated with the job.

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
    service_log_id = Column(
        Integer, ForeignKey("job_email_scraping_service_log.id", ondelete="SET NULL"), nullable=False
    )

    # Relationships
    emails = relationship("JobEmail", secondary=jobemail_scrapedjob_mapping, back_populates="jobs")
    service_log = relationship("JobEmailScrapingServiceLog", back_populates="scraped_jobs")
    job_rating = relationship("JobRating", back_populates="scraped_job", uselist=False)

    # Constraints
    __table_args__ = (UniqueConstraint("external_job_id", "owner_id", name="unique_job_per_owner"),)


class JobEmailScrapingServiceLog(ServiceLog, CommonBase, Base):
    """Represents logs of service operations and their status.

    Attributes:
    -----------
    - `user_found_ids` (list of int): List of user IDs found during the service run.
    - `user_processed_ids` (list of int): List of user IDs processed during the service run.
    - `email_found_n` (int): Number of emails found during the service run.

    Relationships:
    --------------
    - `emails` (list of JobEmail): List of email messages associated with the service log.
    - `scraped_jobs` (list of ScrapedJob): List of scraped jobs associated with the service log.
    - `platform_stats` (list of JobEmailScrapingPlatformStat): List of platform statistics associated with the service log.
    - `errors` (list of JobEmailScrapingServiceError): List of errors associated with the service log.

    Properties:
    -----------
    - `job_scrape_succeeded_n` (int): Total successfully scraped jobs across all platforms.
    - `job_scrape_failed_n` (int): Total failed scraped jobs across all platforms.
    - `job_scrape_copied_n` (int): Total copied scraped jobs found across all platforms.
    - `job_scrape_skipped_n` (int): Total skipped scraped jobs found across all platforms.
    - `job_found_n` (int): Total jobs found (copied + skipped) across all platforms.
    - `email_saved_n` (int): Total emails saved across all platforms.
    - `email_skipped_n` (int): Total emails skipped across all platforms."""

    # Users
    user_found_ids = Column(PG_ARRAY(Integer), server_default="{}", nullable=False)
    user_processed_ids = Column(PG_ARRAY(Integer), server_default="{}", nullable=False)

    # Emails
    email_found_n = Column(Integer, nullable=False, default=0)

    # Relationships
    emails = relationship("JobEmail", back_populates="service_log")
    scraped_jobs = relationship("ScrapedJob", back_populates="service_log")
    platform_stats = relationship("JobEmailScrapingPlatformStat", back_populates="service_log")
    service_errors = relationship("JobEmailScrapingServiceError", back_populates="service_log")

    def __init__(self, **kwargs) -> None:
        """Initialise array fields with empty lists if not provided"""
        kwargs.setdefault("user_found_ids", [])
        kwargs.setdefault("user_processed_ids", [])
        super().__init__(**kwargs)

    @hybrid_property
    def job_to_scrape_n(self) -> int:
        """Total jobs to scrape across all platforms."""
        return sum(len(stat.job_to_scrape_ids) for stat in self.platform_stats)

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

    @hybrid_property
    def job_scrape_filtered_n(self) -> int:
        """Total filtered scraped jobs across all platforms."""
        return sum(len(stat.job_scrape_filtered_ids) for stat in self.platform_stats)


class JobEmailScrapingPlatformStat(CommonBase, Base):
    """Per-platform stats for a service run linked to an JobEmailScrapingServiceLog.

    Attributes:
    -----------
    - `name` (str): Platform name (e.g. LinkedIn, Indeed).

    # Emails
    - `email_saved_ids` (list of int): List of saved email IDs.
    - `email_skipped_ids` (list of int): List of skipped email IDs.

    # Jobs
    - `job_found_ids` (list of int): List of found job IDs from the emails.
    - `job_to_scrape_ids` (list of int): List of job IDs to be scraped.
    - `job_scrape_failed_ids` (list of int): List of failed job scrape IDs.
    - `job_scrape_succeeded_ids` (list of int): List of successful job scrape IDs.
    - `job_scrape_copied_ids` (list of int): List of copied job scrape IDs.
    - `job_scrape_skipped_ids` (list of int): List of skipped job scrape IDs.
    - `job_scrape_filtered_ids` (list of int): List of filtered job scrape IDs.

    Foreign keys:
    -------------
    - `service_log_id` (int): Foreign key to the associated JobEmailScrapingServiceLog.

    Relationships:
    --------------
    - `service_log` (JobEmailScrapingServiceLog): Relationship to the associated JobEmailScrapingServiceLog.

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
    job_to_scrape_ids = Column(PG_ARRAY(Integer), server_default="{}", nullable=False)
    job_scrape_failed_ids = Column(PG_ARRAY(Integer), server_default="{}", nullable=False)
    job_scrape_succeeded_ids = Column(PG_ARRAY(Integer), server_default="{}", nullable=False)
    job_scrape_copied_ids = Column(PG_ARRAY(Integer), server_default="{}", nullable=False)
    job_scrape_skipped_ids = Column(PG_ARRAY(Integer), server_default="{}", nullable=False)
    job_scrape_filtered_ids = Column(PG_ARRAY(Integer), server_default="{}", nullable=False)

    # Foreign keys
    service_log_id = Column(
        Integer, ForeignKey("job_email_scraping_service_log.id", ondelete="CASCADE"), nullable=False
    )

    # Relationships
    service_log = relationship("JobEmailScrapingServiceLog", back_populates="platform_stats")

    # Constraints
    __table_args__ = (UniqueConstraint("service_log_id", "name", name="unique_platform_per_service_log"),)

    def __init__(self, **kwargs) -> None:
        """Initialise array fields with empty lists if not provided"""
        kwargs.setdefault("email_saved_ids", [])
        kwargs.setdefault("email_skipped_ids", [])
        kwargs.setdefault("job_found_ids", [])
        kwargs.setdefault("job_to_scrape_ids", [])
        kwargs.setdefault("job_scrape_failed_ids", [])
        kwargs.setdefault("job_scrape_succeeded_ids", [])
        kwargs.setdefault("job_scrape_copied_ids", [])
        kwargs.setdefault("job_scrape_skipped_ids", [])
        kwargs.setdefault("job_scrape_filtered_ids", [])
        super().__init__(**kwargs)


class JobEmailScrapingServiceError(CommonBase, Base):
    """Records unexpected/unhandled errors raised during a service run.

    Attributes:
    -----------
    - `error_type` (str): Type of the error.
    - `message` (str, optional): Error message.
    - `traceback` (str, optional): Traceback of the error.

    Foreign keys:
    -------------
    - `service_log_id` (int): Foreign key to the associated JobEmailScrapingServiceLog.

    Relationships:
    --------------
    - `service_log` (JobEmailScrapingServiceLog): Relationship to the associated JobEmailScrapingServiceLog"""

    error_type = Column(String, nullable=False)
    message = Column(String, nullable=False)
    traceback = Column(String, nullable=False)

    # Foreign keys
    service_log_id = Column(
        Integer, ForeignKey("job_email_scraping_service_log.id", ondelete="CASCADE"), nullable=False
    )

    # Relationships
    service_log = relationship("JobEmailScrapingServiceLog", back_populates="service_errors")


class ScrapedJobFilter(Owned, Base):
    """Represents user-defined rules to filter out scraped jobs.

    Attributes:
    -----------
    - `type` (str): Type of filter (title, company, location, salary, attendance_type).
    - `operator` (str): Operator for the filter (contains, equals, starts_with, ends_with, less_than, greater_than).
    - `value` (str): Value to match against.
    - `is_active` (bool): Whether this filter rule is currently active.
    - `case_sensitive` (bool): Whether string matching should be case-sensitive.

    Constraints:
    ------------
    - Check constraint to ensure valid filter_type values.
    - Check constraint to ensure valid filter_operator values."""

    type = Column(String, nullable=False)
    operator = Column(String, nullable=False)
    value = Column(String, nullable=False)
    is_active = Column(Boolean, nullable=False, server_default=expression.true())
    case_sensitive = Column(Boolean, nullable=False, server_default=expression.false())

    __table_args__ = (
        CheckConstraint(
            type.in_(
                [
                    "title",
                    "company",
                    "location",
                    "location_city",
                    "location_country",
                    "salary_min",
                    "salary_max",
                    "attendance_type",
                ]
            ),
            name="valid_filter_type",
        ),
        CheckConstraint(
            operator.in_(
                [
                    "contains",
                    "equals",
                    "starts_with",
                    "ends_with",
                    "less_than",
                    "greater_than",
                    "not_contains",
                    "not_equals",
                ]
            ),
            name="valid_filter_operator",
        ),
    )

    @hybrid_property
    def name(self) -> str:
        """Generate a human-readable name for the filter rule."""

        return f"{self.type} {self.operator} '{self.value}'"
