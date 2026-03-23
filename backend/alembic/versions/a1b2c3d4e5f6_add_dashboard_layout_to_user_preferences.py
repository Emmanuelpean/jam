"""add dashboard_layout to user_preferences

Revision ID: a1b2c3d4e5f6
Revises: 53e3869239aa
Create Date: 2026-02-12 00:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, None] = "53e3869239aa"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("scraped_job", sa.Column("read_at", sa.TIMESTAMP(timezone=True), nullable=True))
    op.add_column("user_preferences", sa.Column("dashboard_layout", sa.String(), nullable=True))
    op.drop_constraint("scraped_job_favourite_filter_id_fkey", "scraped_job", type_="foreignkey")
    op.drop_column("scraped_job", "favourite_filter_id")


def downgrade() -> None:
    op.add_column("scraped_job", sa.Column("favourite_filter_id", sa.Integer(), nullable=True))
    op.create_foreign_key(
        None, "scraped_job", "scraping_favourite_filter", ["favourite_filter_id"], ["id"], ondelete="SET NULL"
    )
    op.drop_column("user_preferences", "dashboard_layout")
    op.drop_column("scraped_job", "read_at")
