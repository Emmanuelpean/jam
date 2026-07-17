from sqlalchemy import Date, Column, Float, ForeignKey, Integer, UniqueConstraint

from app.base_models import CommonBase
from app.database import Base


class StripeDailyIncome(CommonBase, Base):
    """One day of Stripe income (GBP) — gross charges and net (post-fees, refunds applied)."""

    date = Column(Date, nullable=False)
    gross_gbp = Column(Float, nullable=False)
    net_gbp = Column(Float, nullable=False)
    service_log_id = Column(
        Integer, ForeignKey("provider_monitoring_service_log.id", ondelete="SET NULL"), nullable=True
    )

    __table_args__ = (UniqueConstraint("date", name="stripe_income_history_date_uq"),)
