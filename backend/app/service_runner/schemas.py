"""Schemas for the shared service-runner Error model."""

from app.base_schemas import Out, BaseModel


class ErrorOut(Out):
    """Service Error output schema"""

    error_type: str
    message: str
    traceback: str | None = None
    is_acknowledged: bool
    scraped_job_id: int | None = None
    job_email_scraping_service_log_id: int | None = None
    job_rating_service_log_id: int | None = None
    external_service_monitoring_service_log_id: int | None = None


class ErrorAcknowledgeRequest(BaseModel):
    """Request schema for acknowledging service errors"""

    ids: list[int]
    is_acknowledged: bool = True
