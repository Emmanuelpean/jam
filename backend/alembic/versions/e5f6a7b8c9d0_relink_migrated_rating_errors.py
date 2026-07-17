"""relink migrated job-rating errors to their JobRating

The unified-service-errors migration (b7c8d9e0f1a2) converted the legacy ``job_rating.error``
strings into ``service_error`` rows but linked them via ``scraped_job_id`` (the ScrapedJob) instead
of ``job_rating_id`` (the JobRating) — unlike the ScrapedJob scrape errors, which were linked
correctly. As a result these historical rating errors surfaced as scraping errors and were absent
from ``JobRating.rating_errors``.

This re-links them. The affected rows are the only ``service_error`` rows with a ``scraped_job_id``
but no service-log FK: genuine per-job scrape errors always carry
``job_email_scraping_service_log_id`` (``ScrapedJob.service_log_id`` is NOT NULL). Each is matched to
its JobRating through the shared ``scraped_job_id`` (ScrapedJob ↔ JobRating is 1:1), given
``job_rating_id`` and the rating's own ``service_log_id`` (added in d4e5f6a7b8c9), and cleared of
``scraped_job_id`` to match how the app now records rating errors.

The downgrade reverses this only for rows bearing b7c8d9e0f1a2's fingerprint (``error_type = 'Error'``
with ``context`` NULL and ``traceback`` equal to ``message``), so natively-recorded rating errors —
which carry a real exception type and a full traceback distinct from the message — are left untouched.

Revision ID: e5f6a7b8c9d0
Revises: d4e5f6a7b8c9
Create Date: 2026-07-15 00:00:01.000000

"""

from typing import Sequence, Union

from alembic import op

revision: str = "e5f6a7b8c9d0"
down_revision: Union[str, None] = "d4e5f6a7b8c9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        UPDATE service_error se
        SET job_rating_id = jr.id,
            job_rating_service_log_id = jr.service_log_id,
            scraped_job_id = NULL
        FROM job_rating jr
        WHERE se.scraped_job_id = jr.scraped_job_id
          AND se.job_rating_id IS NULL
          AND se.job_email_scraping_service_log_id IS NULL
          AND se.job_rating_service_log_id IS NULL
          AND se.provider_monitoring_service_log_id IS NULL
        """)


def downgrade() -> None:
    op.execute("""
        UPDATE service_error se
        SET scraped_job_id = jr.scraped_job_id,
            job_rating_id = NULL,
            job_rating_service_log_id = NULL
        FROM job_rating jr
        WHERE se.job_rating_id = jr.id
          AND se.scraped_job_id IS NULL
          AND se.job_email_scraping_service_log_id IS NULL
          AND se.provider_monitoring_service_log_id IS NULL
          AND se.error_type = 'Error'
          AND se.context IS NULL
          AND se.traceback = se.message
        """)
