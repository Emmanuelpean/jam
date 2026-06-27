"""Aggregates all external-service-monitoring routers under a single import."""

from app.external_service_monitoring import external_service_monitoring_history_router  # noqa: F401
from app.external_service_monitoring.anthropic import routers as _anthropic  # noqa: F401
from app.external_service_monitoring.apify import routers as _apify  # noqa: F401
from app.external_service_monitoring.brightdata import routers as _brightdata  # noqa: F401
from app.external_service_monitoring.stripe import routers as _stripe  # noqa: F401
