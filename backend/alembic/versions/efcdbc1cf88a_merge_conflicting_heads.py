"""merge conflicting heads

Revision ID: efcdbc1cf88a
Revises: 8a882611d98c, 99db4c2aaf82
Create Date: 2025-12-15 23:02:05.148453

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'efcdbc1cf88a'
down_revision: Union[str, None] = ('8a882611d98c', '99db4c2aaf82')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
