"""add parsed_location to scraped_job

Revision ID: b2c3d4e5f6a7
Revises: 51c98247435c
Create Date: 2026-02-17 00:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "b2c3d4e5f6a7"
down_revision: Union[str, None] = "51c98247435c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("scraped_job", sa.Column("parsed_location", sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column("scraped_job", "parsed_location")
