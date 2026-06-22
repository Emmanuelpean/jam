"""Service runner shared models: the ServiceLog base class and the unified Error table."""

import traceback as _traceback

from sqlalchemy import Column, String, Float, Boolean, TIMESTAMP, Integer, ForeignKey
from sqlalchemy.orm import Session, relationship
from sqlalchemy.sql import expression

from app.base_models import CommonBase
from app.database import Base


class ServiceLog(object):
    """Base class for service logs.

    Attributes:
    -----------
    - `run_duration` (float, optional): Duration of the service run.
    - `run_datetime` (datetime): Date and time of the service run.
    - `is_success` (bool): Indicates whether the service run was successful.
    - `error_message` (str, optional): Error message if the service run failed."""

    run_duration = Column(Float, nullable=True)
    run_datetime = Column(TIMESTAMP(timezone=True), nullable=False)
    is_success = Column(Boolean, nullable=True)
    error_message = Column(String, nullable=True)


class Error(CommonBase, Base):
    """Unified record of an error raised during a service run.

    Covers run-level failures (e.g. an unexpected exception in the run loop) and per-item
    failures (e.g. a single job that could not be scraped or rated). The error is linked to the
    run that produced it via the service-specific service-log foreign key (exactly one is set),
    and to the relevant ScrapedJob via `scraped_job_id` for per-job failures.

    Attributes:
    -----------
    - `error_type` (str): Type/class name of the error (e.g. "TimeoutError").
    - `message` (str): Error message.
    - `traceback` (str, optional): Full traceback of the error, if available.
    - `is_acknowledged` (bool): Whether an admin has acknowledged the error.

    Foreign keys
    ------------
    - `scraped_job_id` (int, optional): ScrapedJob the error relates to, for per-job failures
      (scraping / rating). Null for run-level errors not tied to a specific job.
    - `job_email_scraping_service_log_id` (int, optional): Job email scraping run.
    - `job_rating_service_log_id` (int, optional): Job rating run.
    - `external_service_monitoring_service_log_id` (int, optional): Monitoring run.

    Relationships:
    --------------
    - `scraped_job` (ScrapedJob, optional): the ScrapedJob the error relates to.
    - `job_email_scraping_service_log` / `job_rating_service_log` /
      `external_service_monitoring_service_log`: the run that produced the error."""

    error_type = Column(String, nullable=False)
    message = Column(String, nullable=False)
    traceback = Column(String, nullable=True)
    is_acknowledged = Column(Boolean, nullable=False, server_default=expression.false())

    # Foreign keys
    scraped_job_id = Column(
        Integer,
        ForeignKey("scraped_job.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    job_email_scraping_service_log_id = Column(
        Integer,
        ForeignKey("job_email_scraping_service_log.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    job_rating_service_log_id = Column(
        Integer,
        ForeignKey("job_rating_service_log.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    external_service_monitoring_service_log_id = Column(
        Integer,
        ForeignKey("external_service_monitoring_service_log.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )

    # Relationships
    scraped_job = relationship("ScrapedJob", back_populates="scraping_errors")
    job_email_scraping_service_log = relationship("JobEmailScrapingServiceLog", back_populates="service_errors")
    job_rating_service_log = relationship("JobRatingServiceLog", back_populates="service_errors")
    external_service_monitoring_service_log = relationship(
        "ExternalServiceMonitoringServiceLog", back_populates="service_errors"
    )


def record_error(
    db: Session,
    exc: Exception | str,
    message: str | None = None,
    scraped_job_id: int | None = None,
    job_email_scraping_service_log_id: int | None = None,
    job_rating_service_log_id: int | None = None,
    external_service_monitoring_service_log_id: int | None = None,
) -> Error:
    """Create and persist an Error for a caught exception (or a plain error string).
    Captures the current traceback via `traceback.format_exc()`, so call this from within the
    `except` block that handled the error. Pass the service-log id for the originating service.
    :param db: Database session.
    :param exc: The caught exception or an error message string.
    :param message: Optional explicit message; defaults to ``str(exc)``.
    :param scraped_job_id: ScrapedJob the error relates to, for per-job failures.
    :param job_email_scraping_service_log_id: Job email scraping run id, if applicable.
    :param job_rating_service_log_id: Job rating run id, if applicable.
    :param external_service_monitoring_service_log_id: Monitoring run id, if applicable.
    :return: The persisted Error instance."""

    error = Error(
        error_type=type(exc).__name__ if isinstance(exc, BaseException) else "Error",
        message=message if message is not None else str(exc),
        traceback=_traceback.format_exc(),
        scraped_job_id=scraped_job_id,
        job_email_scraping_service_log_id=job_email_scraping_service_log_id,
        job_rating_service_log_id=job_rating_service_log_id,
        external_service_monitoring_service_log_id=external_service_monitoring_service_log_id,
    )
    db.add(error)
    db.commit()
    db.refresh(error)
    return error
