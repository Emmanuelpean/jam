"""unified service errors and scheduler

Consolidated migration for the service-error / scheduler rework (replaces the four step migrations
b1c2d3e4f5a6 -> e7f8a9b0c1d2 -> f3b9c2d1e0a4 -> a1b2c3d4e5f6). Net effect over a
database at a7b8c9d0e1f2:

* Replaces the per-service error stores (job_email_scraping_service_error,
  scraped_job.scrape_error, job_rating.error and the error_message columns on the
  service-log tables) with a single service_error table. Existing errors are migrated across.
* service_error.level records severity; run-level failures are service_error rows (with a
  *_service_log_id set) rather than error_message / is_success on the log, which are
  dropped (success is now derived).
* Rating errors are owned by their JobRating via service_error.job_rating_id; the rating retry
  bookkeeping (rating_retry_count / rating_next_retry_at) lives on job_rating.
* Renames the scrape retry fields on scraped_job (retry_count -> scraping_retry_count,
  next_retry_at -> scraping_next_retry_at).
* Adds the service table that drives the database-backed scheduler (rows are created at runtime).

Revision ID: b7c8d9e0f1a2
Revises: a7b8c9d0e1f2
Create Date: 2026-06-27 00:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "b7c8d9e0f1a2"
down_revision: Union[str, None] = "a7b8c9d0e1f2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Pre-existing service-log tables (carrying legacy error_message / is_success columns) with the
# matching foreign-key column on service_error.
_LOGS = [
    ("job_email_scraping_service_log", "job_email_scraping_service_log_id"),
    ("job_rating_service_log", "job_rating_service_log_id"),
    ("provider_monitoring_service_log", "provider_monitoring_service_log_id"),
]

# Service-log tables that gain is_tour now that it lives on the shared ServiceLog base
# (job_email_scraping_service_log already has it, added by 84de93787471).
_LOGS_NEEDING_IS_TOUR = [
    "job_rating_service_log",
    "provider_monitoring_service_log",
]


# Columns provided by CommonBase — id PK, created_at, modified_at — shared by every table.
def _common_columns() -> list:
    return [
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("modified_at", sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False),
    ]


def upgrade() -> None:
    # --- Rename the monitoring service-log table (created under its old name by a7b8c9d0e1f2) ---
    op.rename_table("external_service_monitoring_service_log", "provider_monitoring_service_log")

    # --- Unified service_error table ---
    op.create_table(
        "service_error",
        *_common_columns(),
        sa.Column("error_type", sa.String(), nullable=False),
        sa.Column("message", sa.String(), nullable=False),
        sa.Column("traceback", sa.String(), nullable=True),
        sa.Column("is_acknowledged", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("level", sa.String(), nullable=True),
        sa.Column("scraped_job_id", sa.Integer(), nullable=True),
        sa.Column("job_rating_id", sa.Integer(), nullable=True),
        sa.Column("job_email_scraping_service_log_id", sa.Integer(), nullable=True),
        sa.Column("job_rating_service_log_id", sa.Integer(), nullable=True),
        sa.Column("provider_monitoring_service_log_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["scraped_job_id"], ["scraped_job.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["job_rating_id"], ["job_rating.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["job_email_scraping_service_log_id"], ["job_email_scraping_service_log.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["job_rating_service_log_id"], ["job_rating_service_log.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["provider_monitoring_service_log_id"],
            ["provider_monitoring_service_log.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_service_error_scraped_job_id", "service_error", ["scraped_job_id"])
    op.create_index("ix_service_error_job_rating_id", "service_error", ["job_rating_id"])
    op.create_index(
        "ix_service_error_job_email_scraping_service_log_id", "service_error", ["job_email_scraping_service_log_id"]
    )
    op.create_index("ix_service_error_job_rating_service_log_id", "service_error", ["job_rating_service_log_id"])
    op.create_index(
        "ix_service_error_provider_monitoring_service_log_id",
        "service_error",
        ["provider_monitoring_service_log_id"],
    )

    # --- Rename scrape retry fields and add rating retry fields ---
    op.alter_column("scraped_job", "retry_count", new_column_name="scraping_retry_count")
    op.alter_column("scraped_job", "next_retry_at", new_column_name="scraping_next_retry_at")
    op.add_column("job_rating", sa.Column("rating_retry_count", sa.Integer(), server_default="0", nullable=False))
    op.add_column("job_rating", sa.Column("rating_next_retry_at", sa.TIMESTAMP(timezone=True), nullable=True))

    # --- Add is_tour to the service-log tables that don't yet have it ---
    for table in _LOGS_NEEDING_IS_TOUR:
        op.add_column(table, sa.Column("is_tour", sa.Boolean(), server_default=sa.text("false"), nullable=False))

    # --- Migrate run-level scraping errors (not tied to a specific job) ---
    op.execute("""
        INSERT INTO service_error (created_at, modified_at, error_type, message, traceback,
                                   is_acknowledged, scraped_job_id, job_email_scraping_service_log_id)
        SELECT created_at, modified_at, error_type, message, traceback,
               false, NULL, service_log_id
        FROM job_email_scraping_service_error
        """)

    # --- Migrate per-job scrape errors (JSONB array of {datetime, error}) ---
    op.execute("""
        INSERT INTO service_error (created_at, modified_at, error_type, message, traceback,
                                   is_acknowledged, scraped_job_id, job_email_scraping_service_log_id)
        SELECT
            COALESCE((elem->>'datetime')::timestamptz, now()),
            now(),
            'Error',
            elem->>'error',
            elem->>'error',
            false,
            sj.id,
            sj.service_log_id
        FROM scraped_job sj, jsonb_array_elements(sj.scrape_error) AS elem
        WHERE jsonb_typeof(sj.scrape_error) = 'array'
        """)

    # --- Migrate per-job rating errors (kept linked to the ScrapedJob; run is unknown) ---
    op.execute("""
        INSERT INTO service_error (created_at, modified_at, error_type, message, traceback,
                                   is_acknowledged, scraped_job_id)
        SELECT created_at, modified_at, 'Error', error, error, false, scraped_job_id
        FROM job_rating
        WHERE error IS NOT NULL
        """)

    # --- Migrate run-level error_message values from the service logs ---
    for table, fk_column in _LOGS:
        op.execute(f"""
            INSERT INTO service_error (created_at, modified_at, error_type, message, traceback,
                                       is_acknowledged, {fk_column})
            SELECT now(), now(), 'Error', error_message, error_message, false, id
            FROM {table}
            WHERE error_message IS NOT NULL
            """)

    # --- Drop the now-migrated legacy stores ---
    op.drop_column("scraped_job", "scrape_error")
    op.drop_column("job_rating", "error")
    op.drop_table("job_email_scraping_service_error")
    for table, _fk_column in _LOGS:
        op.drop_column(table, "error_message")
        op.drop_column(table, "is_success")

    # --- Service scheduler config table ---
    op.create_table(
        "service",
        *_common_columns(),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("display_name", sa.String(), nullable=False),
        sa.Column("run_period_hours", sa.Float(), nullable=False),
        sa.Column("parameters", sa.JSON(), server_default="{}", nullable=False),
        sa.Column("is_enabled", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("is_running", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("last_run_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("next_run_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_service_name", "service", ["name"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_service_name", table_name="service")
    op.drop_table("service")

    # --- Restore service-log error columns ---
    for table, fk_column in _LOGS:
        op.add_column(table, sa.Column("error_message", sa.String(), nullable=True))
        op.add_column(table, sa.Column("is_success", sa.Boolean(), nullable=True))
        op.execute(f"""
            UPDATE {table} t
            SET error_message = se.message
            FROM service_error se
            WHERE se.{fk_column} = t.id AND se.scraped_job_id IS NULL AND se.job_rating_id IS NULL
            """)

    # --- Restore scraped_job.scrape_error and retry field names ---
    op.add_column("scraped_job", sa.Column("scrape_error", postgresql.JSONB(), nullable=True))
    op.execute("UPDATE scraped_job SET scrape_error = '[]'::jsonb")
    op.execute("ALTER TABLE scraped_job ALTER COLUMN scrape_error SET NOT NULL")
    op.execute("ALTER TABLE scraped_job ALTER COLUMN scrape_error SET DEFAULT '[]'")
    op.alter_column("scraped_job", "scraping_next_retry_at", new_column_name="next_retry_at")
    op.alter_column("scraped_job", "scraping_retry_count", new_column_name="retry_count")

    # --- Restore job_rating.error and drop rating retry bookkeeping ---
    op.add_column("job_rating", sa.Column("error", sa.String(), nullable=True))
    op.execute("""
        UPDATE job_rating jr
        SET error = se.message
        FROM service_error se
        WHERE se.scraped_job_id = jr.scraped_job_id
          AND se.job_email_scraping_service_log_id IS NULL
        """)
    op.drop_column("job_rating", "rating_next_retry_at")
    op.drop_column("job_rating", "rating_retry_count")

    for table in _LOGS_NEEDING_IS_TOUR:
        op.drop_column(table, "is_tour")

    # --- Recreate the legacy job email scraping error store ---
    op.create_table(
        "job_email_scraping_service_error",
        *_common_columns(),
        sa.Column("error_type", sa.String(), nullable=False),
        sa.Column("message", sa.String(), nullable=False),
        sa.Column("traceback", sa.String(), nullable=False),
        sa.Column("service_log_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["service_log_id"], ["job_email_scraping_service_log.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.execute("""
        INSERT INTO job_email_scraping_service_error (created_at, modified_at, error_type, message,
                                                      traceback, service_log_id)
        SELECT created_at, modified_at, error_type, message, COALESCE(traceback, ''),
               job_email_scraping_service_log_id
        FROM service_error
        WHERE job_email_scraping_service_log_id IS NOT NULL
        """)

    # --- Drop the unified error table ---
    op.drop_index("ix_service_error_provider_monitoring_service_log_id", table_name="service_error")
    op.drop_index("ix_service_error_job_rating_service_log_id", table_name="service_error")
    op.drop_index("ix_service_error_job_email_scraping_service_log_id", table_name="service_error")
    op.drop_index("ix_service_error_job_rating_id", table_name="service_error")
    op.drop_index("ix_service_error_scraped_job_id", table_name="service_error")
    op.drop_table("service_error")

    # --- Restore the monitoring service-log table to its original name ---
    op.rename_table("provider_monitoring_service_log", "external_service_monitoring_service_log")
