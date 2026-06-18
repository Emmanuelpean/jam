from app.base_models import CommonBase
from app.database import Base
from sqlalchemy import Column, Date, Float, UniqueConstraint


class AnthropicDailyUsage(CommonBase, Base):
    """One day of Anthropic organisation spend (USD)."""

    date = Column(Date, nullable=False)
    usage_usd = Column(Float, nullable=False)

    __table_args__ = (UniqueConstraint("date", name="anthropic_usage_history_date_uq"),)
