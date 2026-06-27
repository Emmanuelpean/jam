"""Schemas for the shared ServiceError model and the base service-log output."""

import datetime as dt

from pydantic import Field, computed_field

from app.base_schemas import Out, BaseModel
from app.service.models import ServiceErrorLevel


class ServiceErrorOut(Out):
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
    provider_monitoring_service_log_id: int | None = None


class ErrorAcknowledgeRequest(BaseModel):
    """Request schema for acknowledging service errors"""

    ids: list[int]
    is_acknowledged: bool = True


class ServiceLogOut(Out):
    """Base output schema for service logs."""

    run_datetime: dt.datetime | None = None
    run_duration: float | None = None
    service_errors: list[ServiceErrorOut] = Field(default=[], exclude=True)

    @computed_field
    @property
    def is_finished(self) -> bool:
        """True if the run completed (has a ``run_datetime``) with no critical errors."""

        return self.run_datetime is not None

    @computed_field
    @property
    def is_success(self) -> bool:
        """True if the run completed (has a ``run_datetime``) without any CRITICAL error."""

        return not any([error.level == ServiceErrorLevel.CRITICAL for error in self.service_errors])


class ServiceOut(Out):
    """Output schema for a scheduled service."""

    name: str
    display_name: str
    run_period_hours: float
    parameters: dict = {}
    is_enabled: bool
    is_running: bool
    last_run_at: dt.datetime | None = None
    next_run_at: dt.datetime | None = None


class ServiceUpdate(BaseModel):
    """Request schema for updating a scheduled service's configuration."""

    is_enabled: bool | None = None
    run_period_hours: float | None = Field(default=None, gt=0)
    parameters: dict | None = None
