"""rename error table to service_error

Renames the unified ``error`` table to ``service_error`` (the model was renamed ``Error`` ->
``ServiceError``) and renames its indexes to match, so a migrated database matches a freshly
created one. Foreign-key and primary-key constraint names keep their ``error_*`` prefixes — they
remain valid after the table rename and are not load-bearing.

Revision ID: a1b2c3d4e5f6
Revises: f3b9c2d1e0a4
Create Date: 2026-06-24 00:00:00.000000

"""

from typing import Sequence, Union

from alembic import op

revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, None] = "f3b9c2d1e0a4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Indexed columns on the error table -> their index suffix.
_INDEXED_COLUMNS = [
    "scraped_job_id",
    "job_rating_id",
    "job_email_scraping_service_log_id",
    "job_rating_service_log_id",
    "external_service_monitoring_service_log_id",
]


def upgrade() -> None:
    op.rename_table("error", "service_error")
    for column in _INDEXED_COLUMNS:
        op.execute(f"ALTER INDEX ix_error_{column} RENAME TO ix_service_error_{column}")


def downgrade() -> None:
    for column in _INDEXED_COLUMNS:
        op.execute(f"ALTER INDEX ix_service_error_{column} RENAME TO ix_error_{column}")
    op.rename_table("service_error", "error")
