"""add service_log_id to job_rating

Gives each JobRating a direct FK to the rating run that created it, instead of relying on the
``JobRatingServiceLog.job_found_ids`` array (which a retried job appears in for every run that
attempted it). Mirrors ``ScrapedJob.service_log_id``.

Backfill: the earliest rating run whose ``job_found_ids`` contains the rating's scraped-job id — the
run that first picked the (then unrated) job up, i.e. the one that created the rating.

Revision ID: d4e5f6a7b8c9
Revises: c3d4e5f6a7b8
Create Date: 2026-07-15 00:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "d4e5f6a7b8c9"
down_revision: Union[str, None] = "c3d4e5f6a7b8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("job_rating", sa.Column("service_log_id", sa.Integer(), nullable=True))
    op.create_foreign_key(None, "job_rating", "job_rating_service_log", ["service_log_id"], ["id"], ondelete="SET NULL")
    op.execute("""
        UPDATE job_rating jr
        SET service_log_id = (
            SELECT l.id
            FROM job_rating_service_log l
            WHERE jr.scraped_job_id = ANY(l.job_found_ids)
            ORDER BY l.run_datetime ASC NULLS LAST, l.id ASC
            LIMIT 1
        )
        """)


def downgrade() -> None:
    op.drop_column("job_rating", "service_log_id")
