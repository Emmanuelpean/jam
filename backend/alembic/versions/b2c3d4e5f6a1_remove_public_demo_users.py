"""remove demo users and the is_demo column

The "Try JAM" button now logs in with a configured address (DEMO_USER_EMAIL) that no user row backs;
every demo account lives in the demo schema and is created on login. Demo accounts seeded into the
public schema are unreachable from that point on, so they are deleted along with whatever data they
own (cascade), and the column that flagged them goes with them: a session is a demo session when its
JWT carries the demo claim, which is what selects the demo schema in the first place.

The deleted rows cannot be recovered; the downgrade only restores the column.

Revision ID: b2c3d4e5f6a1
Revises: a1b2c3d4e5f6
Create Date: 2026-09-06 00:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy import text

revision: str = "b2c3d4e5f6a1"
down_revision: Union[str, None] = "a1b2c3d4e5f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.get_bind().execute(text('DELETE FROM "user" WHERE is_demo'))
    op.drop_column("user", "is_demo")


def downgrade() -> None:
    op.add_column(
        "user",
        sa.Column("is_demo", sa.Boolean(), nullable=False, server_default=sa.text("false")),
    )
