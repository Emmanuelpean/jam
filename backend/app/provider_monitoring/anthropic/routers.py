import datetime as dt

from fastapi import Depends, Query
from sqlalchemy.orm import Session

from app import models
from app.core.oauth2 import get_current_user
from app.database import get_db
from app.provider_monitoring import provider_monitoring_history_router
from app.provider_monitoring.anthropic.schemas import AnthropicDailyUsageOut
from app.routers.utility import assert_admin, filter_by_date


@provider_monitoring_history_router.get("/anthropic", response_model=list[AnthropicDailyUsageOut])
def get_anthropic_history(
    start_date: dt.date | None = Query(None),
    end_date: dt.date | None = Query(None),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Daily Anthropic spend (USD), oldest first."""

    assert_admin(current_user)
    return filter_by_date(db.query(models.AnthropicDailyUsage), models.AnthropicDailyUsage, start_date, end_date).all()
