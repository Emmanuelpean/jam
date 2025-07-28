"""Email Ingestion System (EIS) Database Models

Defines SQLAlchemy ORM models for email-based job scraping functionality.
Includes models for job alert emails, extracted job IDs, and scraped job data
with associated companies and locations from external sources."""

from sqlalchemy import Column, String, Boolean, ForeignKey, Integer, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import expression

from app.models import (
    CommonBase,
    Base,
    JobMixin,
    CompanyMixin,
    LocationMixin,
    get_job_constraints,
    get_location_constraints,
)


class JobAlertEmail(CommonBase, Base):
    """Represents email messages containing job information like LinkedIn and Indeed job alerts"""

    external_email_id = Column(String, unique=True, nullable=False)
    subject = Column(String)
    sender = Column(String)
    date_received = Column(DateTime)
    platform = Column(String)
    body = Column(String)

    # Many-to-many relationship with job entries
    job_entries = relationship("JobAlertEmailJob", back_populates="email")


class JobAlertEmailJob(CommonBase, Base):
    """Represents individual job IDs extracted from emails with scraping status"""

    external_job_id = Column(String, nullable=False)
    is_scraped = Column(Boolean, nullable=False, server_default=expression.false())
    is_failed = Column(Boolean, nullable=False, server_default=expression.false())
    scrape_error = Column(String, nullable=True)
    email_id = Column(Integer, ForeignKey("jobalertemail.id", ondelete="CASCADE"), nullable=False)

    # Relationships
    email = relationship("JobAlertEmail", back_populates="job_entries")


class JobScraped(CommonBase, Base, JobMixin):
    """Represents scraped job postings from external sources with additional metadata."""

    __table_args__ = get_job_constraints("scraped_")

    # Foreign key relationships to scraped tables
    company_id = Column(Integer, ForeignKey("companyscraped.id", ondelete="SET NULL"), nullable=True, index=True)
    location_id = Column(Integer, ForeignKey("locationscraped.id", ondelete="SET NULL"), nullable=True, index=True)

    # Relationships to scraped models only
    company = relationship("CompanyScraped", back_populates="jobscraped")
    location = relationship("LocationScraped", back_populates="jobscraped")


class CompanyScraped(CommonBase, Base, CompanyMixin):
    """Represents scraped companies from external sources."""

    # Relationships
    jobscraped = relationship("JobScraped", back_populates="company")


class LocationScraped(CommonBase, Base, LocationMixin):
    """Represents scraped locations from external sources."""

    __table_args__ = get_location_constraints("scraped_")

    # Relationships
    jobscraped = relationship("JobScraped", back_populates="location")
