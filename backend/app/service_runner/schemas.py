"""Schemas for the shared service-runner Error model and the base service-log output."""

import datetime as dt

from pydantic import Field, computed_field

from app.base_schemas import Out, BaseModel
from app.service_runner.models import ErrorLevel


class ErrorOut(Out):
    """Service Error output schema"""

    error_type: str
    message: str
    traceback: str | None = None
    is_acknowledged: bool
    level: str | None = None
    scraped_job_id: int | None = None
    job_rating_id: int | None = None
    job_email_scraping_service_log_id: int | None = None
    job_rating_service_log_id: int | None = None
    external_service_monitoring_service_log_id: int | None = None


class ServiceLogOut(Out):
    """Base output schema for service logs."""

    run_datetime: dt.datetime | None = None
    run_duration: float | None = None
    service_errors: list[ErrorOut] = Field(default=[], exclude=True)

    @computed_field
    @property
    def is_success(self) -> bool:
        """True if the run completed (has a ``run_datetime``) with no critical errors."""

        if self.run_datetime is None:
            return False
        return not any(error.level == ErrorLevel.CRITICAL for error in self.service_errors)


class ErrorAcknowledgeRequest(BaseModel):
    """Request schema for acknowledging service errors"""

    ids: list[int]
    is_acknowledged: bool = True
