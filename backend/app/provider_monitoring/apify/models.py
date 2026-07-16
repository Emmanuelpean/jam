"""Sqlalchemy models for Apify."""

from sqlalchemy import Column, Date, Float, ForeignKey, Integer, UniqueConstraint

from app.base_models import CommonBase
from app.database import Base


class ApifyDailyUsage(CommonBase, Base):
    """One day of Apify usage (USD), summed across services for that day."""

    date = Column(Date, nullable=False)
    usage_usd = Column(Float, nullable=False)
    service_log_id = Column(
        Integer, ForeignKey("provider_monitoring_service_log.id", ondelete="SET NULL"), nullable=True
    )

    __table_args__ = (UniqueConstraint("date", name="apify_usage_history_date_uq"),)


class ApifyBalance(CommonBase, Base):
    """Point-in-time snapshot of the Apify cycle balance."""

    limit_usd = Column(Float, nullable=True)
    service_log_id = Column(
        Integer, ForeignKey("provider_monitoring_service_log.id", ondelete="SET NULL"), nullable=True
    )
