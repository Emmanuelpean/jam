from sqlalchemy import Column, Date, Float, ForeignKey, Integer, UniqueConstraint

from app.base_models import CommonBase
from app.database import Base


class AnthropicDailyUsage(CommonBase, Base):
    """One day of Anthropic organisation spend (USD)."""

    date = Column(Date, nullable=False)
    usage_usd = Column(Float, nullable=False)
    service_log_id = Column(
        Integer, ForeignKey("provider_monitoring_service_log.id", ondelete="SET NULL"), nullable=True
    )

    __table_args__ = (UniqueConstraint("date", name="anthropic_usage_history_date_uq"),)
