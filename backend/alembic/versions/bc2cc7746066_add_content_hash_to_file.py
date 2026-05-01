"""add_content_hash_to_file

Revision ID: bc2cc7746066
Revises: e5f6a7b8c9d0
Create Date: 2026-05-01 20:32:58.985532

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bc2cc7746066'
down_revision: Union[str, None] = 'e5f6a7b8c9d0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("file", sa.Column("content_hash", sa.String(), nullable=True))
    op.create_index("ix_file_content_hash", "file", ["content_hash"])


def downgrade() -> None:
    op.drop_index("ix_file_content_hash", table_name="file")
    op.drop_column("file", "content_hash")
