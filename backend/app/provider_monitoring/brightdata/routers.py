import datetime as dt

from fastapi import Depends, Query
from sqlalchemy.orm import Session

from app import models
from app.core.oauth2 import get_current_user
from app.database import get_db
from app.provider_monitoring import provider_monitoring_history_router
from app.provider_monitoring.brightdata.schemas import BrightdataBalanceOut, BrightdataDailyUsageOut
from app.routers.utility import assert_admin, filter_by_date


@provider_monitoring_history_router.get("/brightdata", response_model=list[BrightdataDailyUsageOut])
def get_brightdata_history(
    start_date: dt.date | None = Query(None),
    end_date: dt.date | None = Query(None),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Daily Bright Data spend (USD), one row per (date, dataset), oldest first."""

    assert_admin(current_user)
    table = models.BrightdataDailyUsage
    return filter_by_date(db.query(table), table, start_date, end_date).all()


@provider_monitoring_history_router.get("/brightdata/balance", response_model=BrightdataBalanceOut | None)
def get_brightdata_balance(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Latest Bright Data balance snapshot (or null if the sync hasn't run yet)."""

    assert_admin(current_user)
    return db.query(models.BrightdataBalance).order_by(models.BrightdataBalance.created_at.desc()).first()
