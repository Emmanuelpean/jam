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
    op.add_column("user_preferences", sa.Column("dashboard_layout", sa.JSON(), nullable=True))


def downgrade() -> None:
    op.drop_column("user_preferences", "dashboard_layout")
