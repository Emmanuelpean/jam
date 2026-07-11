"""replace scraped_job / job_rating outcome booleans with a status column

Collapses the per-outcome booleans on scraped_job (is_processed / is_scraped / is_failed /
is_skipped) and job_rating (is_success / is_skipped) into a single VARCHAR ``status`` column holding
a ProcessingStatus value (pending / completed / failed / skipped / filtered). ``filtered`` is
scraping-specific (job matched an exclusion rule); job ratings only ever use the first four.

Revision ID: b2f4a6c8d0e1
Revises: b7c8d9e0f1a2
Create Date: 2026-07-06 00:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "b2f4a6c8d0e1"
down_revision: Union[str, None] = "b7c8d9e0f1a2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- scraped_job ---
    op.add_column("scraped_job", sa.Column("status", sa.String(), nullable=False, server_default="pending"))
    op.execute("""
        UPDATE scraped_job SET status = CASE
            WHEN is_failed  THEN 'failed'
            WHEN is_skipped THEN 'skipped'
            WHEN is_scraped THEN 'completed'
            WHEN is_processed THEN 'filtered'
            ELSE 'pending'
        END
        """)
    op.drop_column("scraped_job", "is_processed")
    op.drop_column("scraped_job", "is_scraped")
    op.drop_column("scraped_job", "is_failed")
    op.drop_column("scraped_job", "is_skipped")

    # --- job_rating ---
    op.add_column("job_rating", sa.Column("status", sa.String(), nullable=False, server_default="pending"))
    op.execute("""
        UPDATE job_rating SET status = CASE
            WHEN is_skipped        THEN 'skipped'
            WHEN is_success IS TRUE  THEN 'completed'
            WHEN is_success IS FALSE THEN 'failed'
            ELSE 'pending'
        END
        """)
    op.drop_column("job_rating", "is_skipped")
    op.drop_column("job_rating", "is_success")


def downgrade() -> None:
    # --- job_rating ---
    op.add_column("job_rating", sa.Column("is_success", sa.Boolean(), nullable=True))
    op.add_column("job_rating", sa.Column("is_skipped", sa.Boolean(), nullable=False, server_default=sa.text("false")))
    op.execute("UPDATE job_rating SET is_skipped = (status = 'skipped')")
    op.execute("""
        UPDATE job_rating SET is_success = CASE
            WHEN status = 'completed' THEN TRUE
            WHEN status = 'failed'    THEN FALSE
            ELSE NULL
        END
        """)
    op.drop_column("job_rating", "status")

    # --- scraped_job ---
    for col in ("is_processed", "is_scraped", "is_failed", "is_skipped"):
        op.add_column("scraped_job", sa.Column(col, sa.Boolean(), nullable=False, server_default=sa.text("false")))
    op.execute("UPDATE scraped_job SET is_processed = (status <> 'pending')")
    op.execute("UPDATE scraped_job SET is_scraped = (status = 'completed')")
    op.execute("UPDATE scraped_job SET is_failed = (status = 'failed')")
    op.execute("UPDATE scraped_job SET is_skipped = (status = 'skipped')")
    op.drop_column("scraped_job", "status")
