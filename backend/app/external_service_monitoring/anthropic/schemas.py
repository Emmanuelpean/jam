"""Pydantic output schemas for the external service monitoring endpoints."""

import datetime as dt

from app.base_schemas import Out


class AnthropicDailyUsageOut(Out):
    """One day of Anthropic spend (USD)."""

    date: dt.date
    usage_usd: float
