"""service error monitoring schema changes

Consolidates the service-monitoring error model changes:

* Run-level failures are now ``error`` rows (with the relevant ``*_service_log_id`` set and no
  ``scraped_job_id``) rather than ``error_message`` stored on the service log. Existing non-null
  ``error_message`` values are migrated into ``error`` before the columns are dropped.
* Adds ``error.level`` severity (``critical`` for run-level failures, ``error`` for a single failed
  operation in an otherwise-continuing run, null for per-item scraping / rating failures).
* Adds ``error.job_rating_id`` (ondelete CASCADE) so rating errors are owned solely by their
  JobRating, backfilled from the matching scraped job, then clears ``scraped_job_id`` on those
  rating errors so they no longer surface under ScrapedJob.scraping_errors.
* Moves the rating retry bookkeeping (``rating_retry_count`` / ``rating_next_retry_at``) from
  ``scraped_job`` to ``job_rating``, since the JobRating row is now created up front (pending).
* Drops ``is_success`` from the service-log tables; it is now derived in the output schema (a run is
  successful when it has a ``run_datetime`` and recorded no critical ``error`` rows).

Revision ID: e7f8a9b0c1d2
Revises: b1c2d3e4f5a6
Create Date: 2026-06-24 00:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "e7f8a9b0c1d2"
down_revision: Union[str, None] = "b1c2d3e4f5a6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# (service-log table, the matching foreign-key column on the error table)
_LOGS = [
    ("job_email_scraping_service_log", "job_email_scraping_service_log_id"),
    ("job_rating_service_log", "job_rating_service_log_id"),
    ("external_service_monitoring_service_log", "external_service_monitoring_service_log_id"),
]


def upgrade() -> None:
    # Migrate run-level error_message values into the error table, then drop the columns.
    for table, fk_column in _LOGS:
        op.execute(f"""
            INSERT INTO error (created_at, modified_at, error_type, message, traceback,
                               is_acknowledged, {fk_column})
            SELECT now(), now(), 'Error', error_message, error_message, false, id
            FROM {table}
            WHERE error_message IS NOT NULL
            """)
        op.drop_column(table, "error_message")

    # Severity level for service-level errors.
    op.add_column("error", sa.Column("level", sa.String(), nullable=True))

    # Link rating errors to their JobRating.
    op.add_column("error", sa.Column("job_rating_id", sa.Integer(), nullable=True))
    op.create_index("ix_error_job_rating_id", "error", ["job_rating_id"])
    op.create_foreign_key(
        "error_job_rating_id_fkey", "error", "job_rating", ["job_rating_id"], ["id"], ondelete="CASCADE"
    )
    # Backfill job_rating_id from the matching scraped job, then drop scraped_job_id on rating
    # errors so they are linked only via job_rating_id.
    op.execute("""
        UPDATE error e
        SET job_rating_id = jr.id
        FROM job_rating jr
        WHERE e.scraped_job_id = jr.scraped_job_id
          AND e.job_rating_service_log_id IS NOT NULL
        """)
    op.execute("UPDATE error SET scraped_job_id = NULL WHERE job_rating_service_log_id IS NOT NULL")

    # Move rating retry bookkeeping from scraped_job to job_rating.
    op.add_column("job_rating", sa.Column("rating_retry_count", sa.Integer(), server_default="0", nullable=False))
    op.add_column("job_rating", sa.Column("rating_next_retry_at", sa.TIMESTAMP(timezone=True), nullable=True))
    op.execute("""
        UPDATE job_rating jr
        SET rating_retry_count = sj.rating_retry_count,
            rating_next_retry_at = sj.rating_next_retry_at
        FROM scraped_job sj
        WHERE jr.scraped_job_id = sj.id
        """)
    op.drop_column("scraped_job", "rating_retry_count")
    op.drop_column("scraped_job", "rating_next_retry_at")

    # is_success is now derived, not stored.
    for table, _fk_column in _LOGS:
        op.drop_column(table, "is_success")


def downgrade() -> None:
    for table, _fk_column in _LOGS:
        op.add_column(table, sa.Column("is_success", sa.Boolean(), nullable=True))

    op.add_column("scraped_job", sa.Column("rating_retry_count", sa.Integer(), server_default="0", nullable=False))
    op.add_column("scraped_job", sa.Column("rating_next_retry_at", sa.TIMESTAMP(timezone=True), nullable=True))
    op.execute("""
        UPDATE scraped_job sj
        SET rating_retry_count = jr.rating_retry_count,
            rating_next_retry_at = jr.rating_next_retry_at
        FROM job_rating jr
        WHERE jr.scraped_job_id = sj.id
        """)
    op.drop_column("job_rating", "rating_next_retry_at")
    op.drop_column("job_rating", "rating_retry_count")

    # Best-effort: restore scraped_job_id from the linked JobRating before dropping job_rating_id.
    op.execute("""
        UPDATE error e
        SET scraped_job_id = jr.scraped_job_id
        FROM job_rating jr
        WHERE e.job_rating_id = jr.id AND e.job_rating_service_log_id IS NOT NULL
        """)
    op.drop_constraint("error_job_rating_id_fkey", "error", type_="foreignkey")
    op.drop_index("ix_error_job_rating_id", table_name="error")
    op.drop_column("error", "job_rating_id")

    op.drop_column("error", "level")

    for table, _fk_column in _LOGS:
        op.add_column(table, sa.Column("error_message", sa.String(), nullable=True))
