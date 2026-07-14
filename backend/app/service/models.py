"""Service shared models: the ServiceLog base class and the unified ServiceError table."""

import datetime as dt
import traceback as _traceback
from enum import StrEnum

from sqlalchemy import Column, String, Float, Boolean, TIMESTAMP, Integer, ForeignKey, JSON
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Session, relationship
from sqlalchemy.sql import expression

from app.base_models import CommonBase
from app.database import Base
from app.utilities.logger import AppLogger


class ServiceLog(CommonBase):
    """Base class for service logs.

    Attributes:
    -----------
    - `run_duration` (float, optional): Duration of the service run.
    - `run_datetime` (datetime): Date and time of the service run.

    Failures are recorded as :class:`ServiceError` rows linked to the run (run-level failures have no
    scraped_job_id), not stored on the log itself. Concrete subclasses must define the service_errors
    relationship (the back-reference FK differs per table)."""

    is_tour = Column(Boolean, nullable=False, server_default=expression.false())
    run_duration = Column(Float, nullable=True)
    run_datetime = Column(TIMESTAMP(timezone=True), nullable=False, default=lambda: dt.datetime.now(dt.timezone.utc))

    service_errors: list["ServiceError"] = []

    def set_run_duration(self) -> None:
        """Set run_duration to the seconds elapsed since run_datetime."""

        self.run_duration = (dt.datetime.now(self.run_datetime.tzinfo) - self.run_datetime).total_seconds()

    @hybrid_property
    def is_finished(self) -> bool:
        """True once the run has completed."""

        return self.run_duration is not None

    @hybrid_property
    def is_success(self) -> bool:
        """True if the run produced no CRITICAL error. Derived from the service_errors relationship defined on each
        concrete service-log subclass."""

        return not any(error.level == ServiceErrorLevel.CRITICAL for error in self.service_errors)


class Service(CommonBase, Base):
    """Configuration and schedule for a periodically-run background service.

    Attributes:
    -----------
    - `name` (str): Registry key; matches the service's service_name.
    - `display_name` (str): Human-readable name for the UI.
    - `run_period_hours` (float): Interval between scheduled runs, in hours.
    - `parameters` (dict): Keyword arguments passed to the service callable.
    - `is_enabled` (bool): Whether the scheduler should run this service.
    - `is_running` (bool): Whether a run is currently in progress (overlap guard).
    - `last_run_at` (datetime, optional): When the service last started running.
    - `next_run_at` (datetime, optional): When the service is next due to run."""

    name = Column(String, unique=True, nullable=False, index=True)
    display_name = Column(String, nullable=False)
    run_period_hours = Column(Float, nullable=False)
    parameters = Column(JSON, nullable=False, server_default="{}")
    is_enabled = Column(Boolean, nullable=False, server_default=expression.false())
    is_running = Column(Boolean, nullable=False, server_default=expression.false())
    last_run_at = Column(TIMESTAMP(timezone=True), nullable=True)
    next_run_at = Column(TIMESTAMP(timezone=True), nullable=True)

    @property
    def last_log(self) -> str | None:
        """The last line of this service's log file, or None if it has no log yet."""

        return AppLogger.read_logger(str(self.name)).get_last_log_line()


class ServiceErrorLevel(StrEnum):
    """Severity of a Service Error"""

    CRITICAL = "critical"
    ERROR = "error"


class ServiceError(CommonBase, Base):
    """Unified record of an error raised during a service run.

    Attributes:
    -----------
    - `error_type` (str): Type/class name of the error (e.g. "TimeoutError").
    - `message` (str): Static message describing the failure. Kept free of runtime values
    - `context` (dict, optional): The runtime values relevant to this occurrence (e.g. {"job_id": "job_42"}).
    - `traceback` (str): Full traceback of the error.
    - `is_acknowledged` (bool): Whether an admin has acknowledged the error.
    - `level` (str): Severity (see :class:`ErrorLevel`); defaults to ERROR.

    Foreign keys
    ------------
    - `scraped_job_id` (int, optional): ScrapedJob the error relates to, for per-job scraping failures.
    - `job_rating_id` (int, optional): JobRating the rating error belongs to, for per-job rating failures.
    - `job_email_scraping_service_log_id` (int, optional): Job email scraping run.
    - `job_rating_service_log_id` (int, optional): Job rating run.
    - `provider_monitoring_service_log_id` (int, optional): Monitoring run.

    Relationships:
    --------------
    - `scraped_job` (ScrapedJob, optional): the ScrapedJob the error relates to.
    - `job_rating` (JobRating, optional): the JobRating the error belongs to.
    - `job_email_scraping_service_log` / `job_rating_service_log` /
      `provider_monitoring_service_log`: the run that produced the error."""

    error_type = Column(String, nullable=False)
    message = Column(String, nullable=False)
    context = Column(JSON, nullable=True)
    traceback = Column(String, nullable=False)
    is_acknowledged = Column(Boolean, nullable=False, server_default=expression.false())
    level = Column(String, nullable=True, default=ServiceErrorLevel.ERROR)

    # Foreign keys
    scraped_job_id = Column(
        Integer,
        ForeignKey("scraped_job.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    job_rating_id = Column(
        Integer,
        ForeignKey("job_rating.id", ondelete="CASCADE"),
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
    provider_monitoring_service_log_id = Column(
        Integer,
        ForeignKey("provider_monitoring_service_log.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )

    # Relationships
    scraped_job = relationship("ScrapedJob", back_populates="scraping_errors")
    job_rating = relationship("JobRating", foreign_keys=[job_rating_id], back_populates="rating_errors")
    job_email_scraping_service_log = relationship("JobEmailScrapingServiceLog", back_populates="service_errors")
    job_rating_service_log = relationship("JobRatingServiceLog", back_populates="service_errors")
    provider_monitoring_service_log = relationship("ProviderMonitoringServiceLog", back_populates="service_errors")


def record_error(
    db: Session,
    exc: Exception,
    message: str,
    context: dict | None = None,
    level: ServiceErrorLevel = ServiceErrorLevel.ERROR,
    scraped_job_id: int | None = None,
    job_rating_id: int | None = None,
    job_email_scraping_service_log_id: int | None = None,
    job_rating_service_log_id: int | None = None,
    provider_monitoring_service_log_id: int | None = None,
) -> ServiceError:
    """Create and persist a ServiceError for a caught exception.
    The stored traceback is formatted from the exception's own `__traceback__`. Pass the service-log id
    for the originating service.
    :param db: Database session.
    :param exc: The caught exception, whose type and traceback are recorded.
    :param message: Static message describing the failure. Kept free of runtime values.
    :param context: The runtime values relevant to this occurrence (e.g. {"job_id": "job_42"}).
    :param level: Error severity.
    :param scraped_job_id: ScrapedJob the error relates to, for per-job failures.
    :param job_rating_id: JobRating the rating error belongs to, if applicable.
    :param job_email_scraping_service_log_id: Job email scraping run id, if applicable.
    :param job_rating_service_log_id: Job rating run id, if applicable.
    :param provider_monitoring_service_log_id: Monitoring run id, if applicable.
    :return: The persisted ServiceError instance."""

    error = ServiceError(
        error_type=type(exc).__name__,
        message=message,
        context=context,
        traceback="".join(_traceback.format_exception(type(exc), exc, exc.__traceback__)),
        level=level,
        scraped_job_id=scraped_job_id,
        job_rating_id=job_rating_id,
        job_email_scraping_service_log_id=job_email_scraping_service_log_id,
        job_rating_service_log_id=job_rating_service_log_id,
        provider_monitoring_service_log_id=provider_monitoring_service_log_id,
    )
    db.add(error)
    db.commit()
    db.refresh(error)
    return error
