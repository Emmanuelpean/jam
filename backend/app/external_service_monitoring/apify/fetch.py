"""Module for Apify service monitoring."""

import datetime as dt

import requests
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.config import settings
from app.external_service_monitoring.apify import models
from app.utilities.database import upsert


class ApifyDailyUsage(BaseModel):
    """One day of Apify usage in USD, parsed from `dailyServiceUsages` entries."""

    date: dt.date
    usage_usd: float = Field(validation_alias="totalUsageCreditsUsd")


class ApifyBalance(BaseModel):
    """Apify cycle credit snapshot. Apify has no separate prepaid balance for most plans —
    the limit is the monthly plan cap and used is the current cycle spend."""

    limit_usd: float | None = None


def fetch_apify_balance(db: Session | None = None) -> ApifyBalance:
    """Hit /v2/users/me and return the `plan` dict (used to discover the cycle limit)."""

    headers = {"Authorization": f"Bearer {settings.apify_api_key}"}
    resp = requests.get("https://api.apify.com/v2/users/me", headers=headers, timeout=10)
    resp.raise_for_status()
    plan = resp.json().get("data", {}).get("plan")
    if not plan:
        raise RuntimeError(f"Apify API returned user data without a plan: {resp.json()}")
    limit_usd = plan.get("monthlyUsageCreditsUsd") or plan.get("maxMonthlyUsageUsd")
    entry = ApifyBalance(limit_usd=limit_usd)
    if db:
        db.add(models.ApifyBalance(**entry.model_dump()))
        db.commit()
    return entry


def fetch_apify_daily_usage(db: Session | None = None) -> list[ApifyDailyUsage]:
    """Hit /v2/users/me/usage/monthly and return the `data` dict (used for daily + cycle total)."""

    headers = {"Authorization": f"Bearer {settings.apify_api_key}"}
    resp = requests.get("https://api.apify.com/v2/users/me/usage/monthly", headers=headers, timeout=10)
    resp.raise_for_status()
    data = resp.json().get("data") or {}
    entries = [ApifyDailyUsage.model_validate(entry) for entry in data.get("dailyServiceUsages") or []]
    if db:
        upsert(db, models.ApifyDailyUsage, entries, ["date"])
    return entries
