"""add tour_panel_dismissed preference

Adds a boolean ``tour_panel_dismissed`` column to ``user_preferences`` so users can hide the
"Take a Tour" sidebar entry without having to complete every guided tour.

Revision ID: c3d4e5f6a7b8
Revises: b2f4a6c8d0e1
Create Date: 2026-07-14 00:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "c3d4e5f6a7b8"
down_revision: Union[str, None] = "b2f4a6c8d0e1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "user_preferences",
        sa.Column(
            "tour_panel_dismissed", sa.Boolean(), nullable=False, server_default="false"
        ),
    )


def downgrade() -> None:
    op.drop_column("user_preferences", "tour_panel_dismissed")
