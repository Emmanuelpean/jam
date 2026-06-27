"""Pydantic output schemas for the provider monitoring endpoints."""

from app.service.schemas import ServiceLogOut


class ProviderMonitoringServiceLogOut(ServiceLogOut):
    """One run of the service-monitoring sync."""
