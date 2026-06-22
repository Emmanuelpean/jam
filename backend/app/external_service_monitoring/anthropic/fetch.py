"""Module for Anthropic service monitoring."""

import datetime as dt

from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.config import settings
from app.external_service_monitoring import logger
from app.external_service_monitoring.anthropic import models
from app.utilities.database import upsert
from app.utilities.datetime import current_month_window, to_iso_z
from app.utilities.http import request_with_retry


class AnthropicDailyUsage(BaseModel):
    """One day of Anthropic organisation spend in USD."""

    date: dt.date
    usage_usd: float


def sum_bucket_amount(bucket: dict) -> float:
    """Sum the `amount` field across the results of a single cost_report bucket, returning USD.
    :param bucket: A single cost_report bucket."""

    total_cents = 0.0
    for item in bucket.get("results") or []:
        amount = item.get("amount")
        try:
            total_cents += float(amount)
        except (TypeError, ValueError):
            continue
    return total_cents / 100.0


def fetch_anthropic_daily_usage(db: Session | None = None) -> list[AnthropicDailyUsage]:
    """Fetch per-day Anthropic organisation cost for the current calendar month.

    The Admin API's cost_report endpoint returns daily buckets by default, so each bucket
    maps to one day in the returned list. Pagination requires re-sending the original
    window — `page` alone returns 400."""

    period_start, period_end = current_month_window()
    headers = {
        "x-api-key": settings.anthropic_admin_key,
        "anthropic-version": "2023-06-01",
    }
    base_params: dict = {
        "starting_at": to_iso_z(period_start),
        "ending_at": to_iso_z(period_end),
        "limit": 31,
    }

    buckets: list[dict] = []
    page_token: str | None = None
    while True:
        params = {**base_params, **({"page": page_token} if page_token else {})}
        resp = request_with_retry(
            "GET",
            "https://api.anthropic.com/v1/organizations/cost_report",
            service="anthropic",
            headers=headers,
            params=params,
            timeout=10,
            logger=logger,
        )
        resp.raise_for_status()
        payload = resp.json()
        buckets.extend(payload.get("data") or [])
        if not payload.get("has_more") or not payload.get("next_page"):
            break
        page_token = payload["next_page"]

    entries = [
        AnthropicDailyUsage(
            date=dt.date.fromisoformat(bucket["starting_at"][:10]),
            usage_usd=sum_bucket_amount(bucket),
        )
        for bucket in buckets
    ]
    if db:
        upsert(db, models.AnthropicDailyUsage, entries, ["date"])
    return entries
