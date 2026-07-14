import datetime as dt

from app.base_schemas import Out


class StripeDailyIncomeOut(Out):
    """One day of Stripe income (GBP) — gross charges and net (post-fees, refunds applied)."""

    date: dt.date
    gross_gbp: float
    net_gbp: float
