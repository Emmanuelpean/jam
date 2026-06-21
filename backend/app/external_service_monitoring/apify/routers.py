import datetime as dt

from fastapi import Depends, Query
from sqlalchemy.orm import Session

from app import models
from app.core.oauth2 import get_current_user
from app.database import get_db
from app.external_service_monitoring import external_service_monitoring_history_router
from app.external_service_monitoring.apify.schemas import ApifyBalanceOut
from app.external_service_monitoring.apify.schemas import ApifyDailyUsageOut
from app.routers.utility import assert_admin, filter_by_date


@external_service_monitoring_history_router.get("/apify", response_model=list[ApifyDailyUsageOut])
def get_apify_history(
    start_date: dt.date | None = Query(None),
    end_date: dt.date | None = Query(None),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Daily Apify usage (USD), oldest first."""

    assert_admin(current_user)
    return filter_by_date(db.query(models.ApifyDailyUsage), models.ApifyDailyUsage, start_date, end_date).all()


@external_service_monitoring_history_router.get("/apify/balance", response_model=ApifyBalanceOut | None)
def get_apify_balance(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Latest Apify cycle balance snapshot (or null if the sync hasn't run yet)."""

    assert_admin(current_user)
    return db.query(models.ApifyBalance).order_by(models.ApifyBalance.created_at.desc()).first()
