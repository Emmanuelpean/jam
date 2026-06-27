"""Pytantic models for Apify."""

import datetime as dt

from app.base_schemas import Out


class ApifyDailyUsageOut(Out):
    """One day of Apify usage (USD)."""

    date: dt.date
    usage_usd: float


class ApifyBalanceOut(Out):
    """Most recent Apify cycle balance snapshot."""

    limit_usd: float | None = None
