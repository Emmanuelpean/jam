import datetime as dt

from dateutil.relativedelta import relativedelta


def current_month_window() -> tuple[dt.datetime, dt.datetime]:
    """Return (period_start, period_end) — start of the current UTC month and start of the next."""
    period_start = dt.datetime.now(dt.timezone.utc).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    return period_start, period_start + relativedelta(months=1)


def to_iso_z(t: dt.datetime) -> str:
    """Format a UTC datetime as RFC3339 with trailing Z (the format the Anthropic Admin API expects)."""
    return t.strftime("%Y-%m-%dT%H:%M:%SZ")
