"""service scheduler config table

Adds the ``service`` table that drives the database-backed :class:`ServiceScheduler`. Each row is the
configuration and schedule for one background service (name -> registry key, period, parameters,
enabled flag, last/next run). The rows themselves are created at runtime by
``app.service.registry.sync_services_to_db`` (run on scheduler startup) from each service's
registration defaults, so this migration only creates the table.

Revision ID: f3b9c2d1e0a4
Revises: e7f8a9b0c1d2
Create Date: 2026-06-24 00:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "f3b9c2d1e0a4"
down_revision: Union[str, None] = "e7f8a9b0c1d2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "service",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("modified_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("display_name", sa.String(), nullable=False),
        sa.Column("run_period_hours", sa.Float(), nullable=False),
        sa.Column("parameters", sa.JSON(), server_default="{}", nullable=False),
        sa.Column("is_enabled", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("is_running", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("last_run_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("next_run_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_service_name", "service", ["name"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_service_name", table_name="service")
    op.drop_table("service")
