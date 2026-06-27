"""Aggregates all provider-monitoring routers under a single import."""

from app.provider_monitoring import provider_monitoring_history_router  # noqa: F401
from app.provider_monitoring.anthropic import routers as _anthropic  # noqa: F401
from app.provider_monitoring.apify import routers as _apify  # noqa: F401
from app.provider_monitoring.brightdata import routers as _brightdata  # noqa: F401
from app.provider_monitoring.stripe import routers as _stripe  # noqa: F401
