"""Sqlalchemy models for Apify."""

from sqlalchemy import Column, Date, Float, UniqueConstraint

from app.base_models import CommonBase
from app.database import Base


class ApifyDailyUsage(CommonBase, Base):
    """One day of Apify usage (USD), summed across services for that day."""

    date = Column(Date, nullable=False)
    usage_usd = Column(Float, nullable=False)

    __table_args__ = (UniqueConstraint("date", name="apify_usage_history_date_uq"),)


class ApifyBalance(CommonBase, Base):
    """Point-in-time snapshot of the Apify cycle balance."""

    limit_usd = Column(Float, nullable=True)
