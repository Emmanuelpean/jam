"""Daily usage history endpoints — one GET per external service. Admin only."""

import datetime as dt

from fastapi import Depends, Query
from sqlalchemy.orm import Session

from app import models
from app.core.oauth2 import get_current_user
from app.database import get_db
from app.provider_monitoring import provider_monitoring_history_router
from app.provider_monitoring.stripe.schemas import StripeDailyIncomeOut
from app.routers.utility import assert_admin, filter_by_date


@provider_monitoring_history_router.get("/stripe", response_model=list[StripeDailyIncomeOut])
def get_stripe_history(
    start_date: dt.date | None = Query(None),
    end_date: dt.date | None = Query(None),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Daily Stripe income (GBP), oldest first."""

    assert_admin(current_user)
    return filter_by_date(db.query(models.StripeDailyIncome), models.StripeDailyIncome, start_date, end_date).all()
