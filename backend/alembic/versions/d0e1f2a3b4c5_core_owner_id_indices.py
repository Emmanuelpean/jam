"""add owner_id indices to the core owned tables

Revision ID: d0e1f2a3b4c5
Revises: b8c9d0e1f2a3
Create Date: 2026-08-31 00:00:00.000000

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "d0e1f2a3b4c5"
down_revision: Union[str, None] = "b8c9d0e1f2a3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

OWNED_TABLES = [
    "premium_settings",
    "stripe_details",
    "user_preferences",
    "user_qualification",
    "user_token",
]


def upgrade() -> None:
    for table in OWNED_TABLES:
        op.create_index(op.f(f"ix_{table}_owner_id"), table, ["owner_id"], unique=False)


def downgrade() -> None:
    for table in OWNED_TABLES:
        op.drop_index(op.f(f"ix_{table}_owner_id"), table_name=table)
