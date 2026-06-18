"""usage history caches (per-API, daily)

Revision ID: a7b8c9d0e1f2
Revises: d2e3f4a5b6c7
Create Date: 2026-06-16 00:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "a7b8c9d0e1f2"
down_revision: Union[str, None] = "d2e3f4a5b6c7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# Common columns provided by CommonBase — id PK, created_at, modified_at — plus the
# daily `date` column shared by every history table.
def _common_columns() -> list:
    return [
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("modified_at", sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
    ]


def upgrade() -> None:
    op.create_table(
        "anthropic_usage_history",
        *_common_columns(),
        sa.Column("usage_usd", sa.Float(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("date", name="anthropic_usage_history_date_uq"),
    )
    op.create_table(
        "apify_usage_history",
        *_common_columns(),
        sa.Column("usage_usd", sa.Float(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("date", name="apify_usage_history_date_uq"),
    )
    op.create_table(
        "apify_balance_snapshot",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("modified_at", sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("limit_usd", sa.Float(), nullable=True),
        sa.Column("used_usd", sa.Float(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "brightdata_usage_history",
        *_common_columns(),
        sa.Column("dataset", sa.String(), nullable=False),
        sa.Column("usage_usd", sa.Float(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("date", "dataset", name="brightdata_usage_history_date_dataset_uq"),
    )
    op.create_table(
        "brightdata_balance_snapshot",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("modified_at", sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("balance_usd", sa.Float(), nullable=True),
        sa.Column("pending_costs_usd", sa.Float(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "stripe_income_history",
        *_common_columns(),
        sa.Column("gross_gbp", sa.Float(), nullable=False),
        sa.Column("net_gbp", sa.Float(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("date", name="stripe_income_history_date_uq"),
    )
    op.create_table(
        "service_monitoring_service_log",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("modified_at", sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("run_duration", sa.Float(), nullable=True),
        sa.Column("run_datetime", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("is_success", sa.Boolean(), nullable=True),
        sa.Column("error_message", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("service_monitoring_service_log")
    op.drop_table("stripe_income_history")
    op.drop_table("brightdata_balance_snapshot")
    op.drop_table("brightdata_usage_history")
    op.drop_table("apify_balance_snapshot")
    op.drop_table("apify_usage_history")
    op.drop_table("anthropic_usage_history")
