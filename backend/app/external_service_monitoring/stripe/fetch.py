"""Module for Stripe service monitoring."""

import datetime as dt

from sqlalchemy.orm import Session

from app.payments import stripe
from pydantic import BaseModel

from app.external_service_monitoring.stripe import models
from app.utilities.datetime import current_month_window
from app.utilities.database import upsert

STRIPE_INCOME_CURRENCY = "gbp"
STRIPE_INCOME_TXN_TYPES = ("charge", "refund")


class StripeDailyIncome(BaseModel):
    """One day of Stripe income in GBP — gross charges and net (post-fees, refunds applied)."""

    date: dt.date
    gross_gbp: float
    net_gbp: float


def fetch_stripe_daily_income(db: Session | None = None) -> list[StripeDailyIncome]:
    """Fetch per-day Stripe income for the current calendar month.

    Iterates balance transactions and groups by UTC date. `gross_gbp` counts only `charge`
    amounts; `net_gbp` includes fees and refunds, matching what hits the bank. Non-GBP
    transactions are skipped to keep the chart in a single currency."""

    period_start, period_end = current_month_window()
    gross_pence: dict[dt.date, int] = {}
    net_pence: dict[dt.date, int] = {}
    for txn_type in STRIPE_INCOME_TXN_TYPES:
        for txn in stripe.BalanceTransaction.list(
            created={
                "gte": int(period_start.timestamp()),
                "lt": int(period_end.timestamp()),
            },
            type=txn_type,
            limit=100,
        ).auto_paging_iter():
            if (txn.currency or "").lower() != STRIPE_INCOME_CURRENCY:
                continue
            day = dt.datetime.fromtimestamp(txn.created, tz=dt.timezone.utc).date()
            if txn_type == "charge":
                gross_pence[day] = gross_pence.get(day, 0) + txn.amount
            net_pence[day] = net_pence.get(day, 0) + txn.net

    days = sorted(set(gross_pence) | set(net_pence))
    entries = [
        StripeDailyIncome(
            date=day,
            gross_gbp=gross_pence.get(day, 0) / 100.0,
            net_gbp=net_pence.get(day, 0) / 100.0,
        )
        for day in days
    ]
    if db:
        upsert(db, models.StripeDailyIncome, entries, ["date"])
    return entries
