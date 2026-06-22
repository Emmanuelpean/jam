"""Module for Bright Data service monitoring."""

import datetime as dt

from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.config import settings
from app.external_service_monitoring import logger
from app.external_service_monitoring.brightdata import models
from app.utilities.database import upsert
from app.utilities.http import request_with_retry

DATASET_LABELS: dict[str, str] = {
    settings.brightdata_linkedin_dataset_id: "LinkedIn",
    settings.brightdata_indeed_dataset_id: "Indeed",
}


class BrightdataDailyUsage(BaseModel):
    """One day of Bright Data spend (USD) for a single dataset."""

    date: dt.date
    dataset: str
    usage_usd: float


class BrightdataBalance(BaseModel):
    """Point-in-time Bright Data account balance snapshot (USD)."""

    balance_usd: float | None = None
    pending_costs_usd: float | None = None


def fetch_brightdata_balance(db: Session | None = None) -> BrightdataBalance:
    """Hit /customer/balance and return the current account balance + pending costs."""

    headers = {"Authorization": f"Bearer {settings.brightdata_api_key}"}
    resp = request_with_retry(
        "GET",
        "https://api.brightdata.com/customer/balance",
        service="brightdata",
        headers=headers,
        timeout=10,
        logger=logger,
    )
    resp.raise_for_status()
    payload = resp.json() or {}
    entry = BrightdataBalance(
        balance_usd=payload.get("balance"),
        pending_costs_usd=payload.get("pending_costs"),
    )
    if db:
        db.add(models.BrightdataBalance(**entry.model_dump()))
        db.commit()
    return entry


def fetch_brightdata_daily_usage(db: Session | None = None) -> list[BrightdataDailyUsage]:
    """Hit /costs/export/json for the current calendar month and return one row per (date, dataset).

    Despite the misleading name, `dimension=web_apis` is the dimension that returns a per-dataset
    breakdown — `datasets` and `products` documented elsewhere return 400."""

    today = dt.date.today()
    start = today.replace(day=1)
    # Add 32 days then snap to first of that month — handles December → January cleanly.
    end = (start + dt.timedelta(days=32)).replace(day=1)

    headers = {
        "Authorization": f"Bearer {settings.brightdata_api_key}",
        "Content-Type": "application/json",
    }
    body = {
        "dimension": "web_apis",
        "filters": {},
        "from": start.strftime("%Y-%m-%d"),
        "to": end.strftime("%Y-%m-%d"),
    }
    resp = request_with_retry(
        "POST",
        "https://api.brightdata.com/costs/export/json",
        service="brightdata",
        headers=headers,
        json=body,
        timeout=10,
    )
    resp.raise_for_status()
    payload = resp.json() or {}

    # Response shape: {"YYYY-MM-DD": {"<dataset_id>": <usd>, ...}, ..., "total": {...}}
    entries: list[BrightdataDailyUsage] = []
    for date_key, by_dataset in payload.items():
        if date_key == "total" or not isinstance(by_dataset, dict):
            continue
        try:
            day = dt.datetime.strptime(date_key, "%Y-%m-%d").date()
        except ValueError:
            continue
        for dataset_id, amount in by_dataset.items():
            label = DATASET_LABELS.get(dataset_id)
            if not label:
                continue
            try:
                usage = float(amount)
            except (TypeError, ValueError):
                continue
            entries.append(BrightdataDailyUsage(date=day, dataset=label, usage_usd=usage))

    if db:
        upsert(db, models.BrightdataDailyUsage, entries, ["date", "dataset"])
    return entries
