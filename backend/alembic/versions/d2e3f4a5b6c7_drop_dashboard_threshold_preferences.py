"""drop dashboard threshold preferences (chase_threshold, deadline_threshold, update_limit)

These settings are now configured per dashboard widget instead of per user.

Revision ID: d2e3f4a5b6c7
Revises: c1d2e3f4a5b6
Create Date: 2026-06-11 00:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision: str = "d2e3f4a5b6c7"
down_revision: Union[str, None] = "c1d2e3f4a5b6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column("user_preferences", "chase_threshold")
    op.drop_column("user_preferences", "deadline_threshold")
    op.drop_column("user_preferences", "update_limit")


def downgrade() -> None:
    op.add_column(
        "user_preferences",
        sa.Column("update_limit", sa.Integer(), server_default="10", nullable=False),
    )
    op.add_column(
        "user_preferences",
        sa.Column("deadline_threshold", sa.Integer(), server_default="7", nullable=False),
    )
    op.add_column(
        "user_preferences",
        sa.Column("chase_threshold", sa.Integer(), server_default="14", nullable=False),
    )
