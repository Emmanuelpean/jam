"""Add is_tour column to all Owned models

Revision ID: a2b3c4d5e6f7
Revises: e5f6a7b8c9d0
Create Date: 2026-05-16 00:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a2b3c4d5e6f7"
down_revision: Union[str, tuple, None] = "e5f6a7b8c9d0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_OWNED_TABLES = [
    "aggregator",
    "company",
    "file",
    "forwarding_confirmation_link",
    "interview",
    "job",
    "job_application_update",
    "job_email",
    "job_rating",
    "keyword",
    "person",
    "premium_settings",
    "scraped_job",
    "scraping_exclusion_filter",
    "scraping_favourite_filter",
    "speculative_application",
    "stripe_details",
    "user_preferences",
    "user_qualification",
    "user_token",
]


def upgrade() -> None:
    for table in _OWNED_TABLES:
        op.add_column(table, sa.Column("is_tour", sa.Boolean(), nullable=False, server_default=sa.text("false")))


def downgrade() -> None:
    for table in _OWNED_TABLES:
        op.drop_column(table, "is_tour")
