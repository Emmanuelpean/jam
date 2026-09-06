"""add table_page_size preference

Adds a JSON ``table_page_size`` column to ``user_preferences`` storing the number of entries per
page chosen for each table. Tables with no entry fit their page size to the available height.

Revision ID: a1b2c3d4e5f6
Revises: d0e1f2a3b4c5
Create Date: 2026-09-06 00:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, None] = "d0e1f2a3b4c5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("user_preferences", sa.Column("table_page_size", sa.JSON(), nullable=True))


def downgrade() -> None:
    op.drop_column("user_preferences", "table_page_size")
