from sqlalchemy import Column, Date, Float, ForeignKey, Integer, String, UniqueConstraint

from app.base_models import CommonBase
from app.database import Base


class BrightdataDailyUsage(CommonBase, Base):
    """One day of Bright Data spend (USD) for a single dataset.

    Multiple rows per day — one per dataset. Adding a new dataset doesn't need a schema change."""

    date = Column(Date, nullable=False)
    dataset = Column(String, nullable=False)
    usage_usd = Column(Float, nullable=False)
    service_log_id = Column(
        Integer, ForeignKey("provider_monitoring_service_log.id", ondelete="SET NULL"), nullable=True
    )

    __table_args__ = (UniqueConstraint("date", "dataset", name="brightdata_usage_history_date_dataset_uq"),)


class BrightdataBalance(CommonBase, Base):
    """Point-in-time snapshot of the Bright Data account balance (USD).

    Append-only — each sync run adds a row. Frontend reads the most recent row by `created_at`."""

    balance_usd = Column(Float, nullable=True)
    pending_costs_usd = Column(Float, nullable=True)
    service_log_id = Column(
        Integer, ForeignKey("provider_monitoring_service_log.id", ondelete="SET NULL"), nullable=True
    )
