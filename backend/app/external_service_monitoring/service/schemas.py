"""Pydantic output schemas for the external service monitoring endpoints."""

import datetime as dt

from app.base_schemas import Out


class ServiceMonitoringServiceLogOut(Out):
    """One run of the service-monitoring sync."""

    run_datetime: dt.datetime | None = None
    run_duration: float | None = None
    is_success: bool | None = None
    error_message: str | None = None
