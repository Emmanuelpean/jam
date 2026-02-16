"""removed non-null on latitude and longitude columns in Geolocation table

Revision ID: 51c98247435c
Revises: 53e3869239aa
Create Date: 2026-02-15 18:22:20.608099

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '51c98247435c'
down_revision: Union[str, None] = '53e3869239aa'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column("geolocation", "latitude", existing_type=sa.Float(), nullable=True)
    op.alter_column("geolocation", "longitude", existing_type=sa.Float(), nullable=True)


def downgrade() -> None:
    op.alter_column("geolocation", "longitude", existing_type=sa.Float(), nullable=False)
    op.alter_column("geolocation", "latitude", existing_type=sa.Float(), nullable=False)
