"""Pydantic output schemas for the external service monitoring endpoints."""

from app.service.schemas import ServiceLogOut


class ServiceMonitoringServiceLogOut(ServiceLogOut):
    """One run of the service-monitoring sync."""
