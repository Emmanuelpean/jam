import datetime as dt

from app.base_schemas import Out


class BrightdataDailyUsageOut(Out):
    """One day of Bright Data spend (USD) for a single dataset."""

    date: dt.date
    dataset: str
    usage_usd: float


class BrightdataBalanceOut(Out):
    """Most recent Bright Data balance snapshot."""

    balance_usd: float | None = None
    pending_costs_usd: float | None = None
