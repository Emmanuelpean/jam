from sqlalchemy import Column, String, Float, Boolean, Table, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from sqlalchemy.sql import expression

from app.models import CommonBase, Base

email_jobs = Table(
    "email_jobs",
    Base.metadata,
    Column("jobemail_id", Integer, ForeignKey("jobemails.id", ondelete="CASCADE"), primary_key=True),
    Column("job_entry_id", Integer, ForeignKey("jobemailjobs.id", ondelete="CASCADE"), primary_key=True),
)


class JobEmailJobs(CommonBase, Base):
    """Represents individual job IDs extracted from emails with scraping status"""

    external_job_id = Column(String, nullable=False)
    platform = Column(String, nullable=False)
    is_scraped = Column(Boolean, nullable=False, server_default=expression.false())
    is_failed = Column(Boolean, nullable=False, server_default=expression.false())
    scrape_error = Column(String, nullable=True)

    # Many-to-many relationship with emails
    emails = relationship("JobEmails", secondary=email_jobs, back_populates="job_entries")

    __table_args__ = (UniqueConstraint("external_job_id", "platform", "owner_id", name="unique_job_per_platform"),)

    @hybrid_property
    def email_count(self) -> int:
        """Get count of emails containing this job"""
        return len(self.emails) if self.emails else 0


class JobEmails(CommonBase, Base):
    """Represents email messages containing job information"""

    external_email_id = Column(String, unique=True, nullable=False)
    subject = Column(String)
    sender = Column(String)
    date_received = Column(String)
    platform = Column(String)

    # Many-to-many relationship with job entries
    job_entries = relationship("JobEmailJobs", secondary=email_jobs, back_populates="emails")


class JobscraperSettings(Base):
    """Represents settings for the jobscraper"""

    __tablename__ = "jobscrapersettings"

    id = Column(Integer, primary_key=True, nullable=False)
    period = Column(Float, nullable=False)
