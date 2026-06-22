"""unified error table + retry fields

Introduces a single ``error`` table shared by all services. Migrates the existing per-service
error stores (``job_email_scraping_service_error``, ``scraped_job.scrape_error``,
``job_rating.error``) into ``error``, then removes them. Renames the scrape retry fields on
``scraped_job`` and adds rating retry fields.

Revision ID: b1c2d3e4f5a6
Revises: a7b8c9d0e1f2
Create Date: 2026-06-22 00:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "b1c2d3e4f5a6"
down_revision: Union[str, None] = "a7b8c9d0e1f2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# Columns provided by CommonBase — id PK, created_at, modified_at — shared by every table.
def _common_columns() -> list:
    return [
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("modified_at", sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False),
    ]


def upgrade() -> None:
    # --- New unified error table ---
    op.create_table(
        "error",
        *_common_columns(),
        sa.Column("error_type", sa.String(), nullable=False),
        sa.Column("message", sa.String(), nullable=False),
        sa.Column("traceback", sa.String(), nullable=True),
        sa.Column("is_acknowledged", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("scraped_job_id", sa.Integer(), nullable=True),
        sa.Column("job_email_scraping_service_log_id", sa.Integer(), nullable=True),
        sa.Column("job_rating_service_log_id", sa.Integer(), nullable=True),
        sa.Column("external_service_monitoring_service_log_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["scraped_job_id"], ["scraped_job.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["job_email_scraping_service_log_id"], ["job_email_scraping_service_log.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["job_rating_service_log_id"], ["job_rating_service_log.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["external_service_monitoring_service_log_id"],
            ["external_service_monitoring_service_log.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_error_scraped_job_id", "error", ["scraped_job_id"])
    op.create_index("ix_error_job_email_scraping_service_log_id", "error", ["job_email_scraping_service_log_id"])
    op.create_index("ix_error_job_rating_service_log_id", "error", ["job_rating_service_log_id"])
    op.create_index(
        "ix_error_external_service_monitoring_service_log_id",
        "error",
        ["external_service_monitoring_service_log_id"],
    )

    # --- Rename scrape retry fields and add rating retry fields on scraped_job ---
    op.alter_column("scraped_job", "retry_count", new_column_name="scraping_retry_count")
    op.alter_column("scraped_job", "next_retry_at", new_column_name="scraping_next_retry_at")
    op.add_column("scraped_job", sa.Column("rating_retry_count", sa.Integer(), server_default="0", nullable=False))
    op.add_column("scraped_job", sa.Column("rating_next_retry_at", sa.TIMESTAMP(timezone=True), nullable=True))

    # --- Migrate existing run-level scraping errors (not tied to a specific job) ---
    op.execute("""
        INSERT INTO error (created_at, modified_at, error_type, message, traceback,
                                   is_acknowledged, scraped_job_id, job_email_scraping_service_log_id)
        SELECT created_at, modified_at, error_type, message, traceback,
               false, NULL, service_log_id
        FROM job_email_scraping_service_error
        """)

    # --- Migrate per-job scrape errors (JSONB array of {datetime, error}) ---
    op.execute("""
        INSERT INTO error (created_at, modified_at, error_type, message, traceback,
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

    # --- Migrate per-job rating errors (the originating run is unknown, so left null) ---
    op.execute("""
        INSERT INTO error (created_at, modified_at, error_type, message, traceback,
                                   is_acknowledged, scraped_job_id, job_rating_service_log_id)
        SELECT created_at, modified_at, 'Error', error, error, false, scraped_job_id, NULL
        FROM job_rating
        WHERE error IS NOT NULL
        """)

    # --- Drop the now-migrated legacy stores ---
    op.drop_column("scraped_job", "scrape_error")
    op.drop_column("job_rating", "error")
    op.drop_table("job_email_scraping_service_error")


def downgrade() -> None:
    # --- Recreate legacy stores ---
    op.add_column("scraped_job", sa.Column("scrape_error", postgresql.JSONB(), nullable=True))
    op.execute("UPDATE scraped_job SET scrape_error = '[]'::jsonb")
    op.execute("ALTER TABLE scraped_job ALTER COLUMN scrape_error SET NOT NULL")
    op.execute("ALTER TABLE scraped_job ALTER COLUMN scrape_error SET DEFAULT '[]'")

    op.add_column("job_rating", sa.Column("error", sa.String(), nullable=True))

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

    # --- Best-effort restore of scraping errors (run-level + per-job) ---
    op.execute("""
        INSERT INTO job_email_scraping_service_error (created_at, modified_at, error_type, message,
                                                      traceback, service_log_id)
        SELECT created_at, modified_at, error_type, message, COALESCE(traceback, ''),
               job_email_scraping_service_log_id
        FROM error
        WHERE job_email_scraping_service_log_id IS NOT NULL
        """)

    # --- Best-effort restore of per-job rating errors ---
    op.execute("""
        UPDATE job_rating jr
        SET error = se.message
        FROM error se
        WHERE se.job_rating_service_log_id IS NOT NULL AND se.scraped_job_id = jr.scraped_job_id
        """)

    op.drop_column("scraped_job", "rating_next_retry_at")
    op.drop_column("scraped_job", "rating_retry_count")
    op.alter_column("scraped_job", "scraping_next_retry_at", new_column_name="next_retry_at")
    op.alter_column("scraped_job", "scraping_retry_count", new_column_name="retry_count")
    op.drop_index("ix_error_external_service_monitoring_service_log_id", table_name="error")
    op.drop_index("ix_error_job_rating_service_log_id", table_name="error")
    op.drop_index("ix_error_job_email_scraping_service_log_id", table_name="error")
    op.drop_index("ix_error_scraped_job_id", table_name="error")
    op.drop_table("error")
