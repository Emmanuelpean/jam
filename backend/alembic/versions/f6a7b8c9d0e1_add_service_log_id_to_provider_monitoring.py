"""add service_log_id to provider monitoring tables

Gives each provider-monitoring record (daily usage + balance snapshots) a FK to the
ProviderMonitoringServiceLog run that last wrote it, mirroring ScrapedJob/JobRating.service_log_id.
The daily-usage tables are upserted each run, so the FK is refreshed on every write and reflects the
most recent run that touched the row.

Backfill: the most recent run that had started by the time the row was last written
(``provider_monitoring_service_log.created_at <= <row>.modified_at``).

Revision ID: f6a7b8c9d0e1
Revises: e5f6a7b8c9d0
Create Date: 2026-07-15 00:00:02.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "f6a7b8c9d0e1"
down_revision: Union[str, None] = "e5f6a7b8c9d0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_TABLES = [
    "anthropic_daily_usage",
    "apify_daily_usage",
    "apify_balance",
    "brightdata_daily_usage",
    "brightdata_balance",
    "stripe_daily_income",
]


def upgrade() -> None:
    for table in _TABLES:
        op.add_column(table, sa.Column("service_log_id", sa.Integer(), nullable=True))
        op.create_foreign_key(
            None, table, "provider_monitoring_service_log", ["service_log_id"], ["id"], ondelete="SET NULL"
        )
        op.execute(f"""
            UPDATE {table} t
            SET service_log_id = (
                SELECT l.id
                FROM provider_monitoring_service_log l
                WHERE l.created_at <= t.modified_at
                ORDER BY l.created_at DESC
                LIMIT 1
            )
            """)


def downgrade() -> None:
    for table in _TABLES:
        op.drop_column(table, "service_log_id")
