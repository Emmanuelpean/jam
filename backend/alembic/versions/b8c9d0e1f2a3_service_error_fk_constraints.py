"""add service_error FK consistency constraints

Enforces at the DB level the invariants the recorder already upholds:
* a scraped_job_id implies its scraping-run FK,
* a job_rating_id implies its rating-run FK,
* every row is attributed to at least one FK,
* the three service-log FKs are mutually exclusive (an error belongs to one run).

Revision ID: b8c9d0e1f2a3
Revises: f6a7b8c9d0e1
Create Date: 2026-07-15 00:00:03.000000

"""

from typing import Sequence, Union

from alembic import op

revision: str = "b8c9d0e1f2a3"
down_revision: Union[str, None] = "f6a7b8c9d0e1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_CONSTRAINTS = [
    (
        "ck_service_error_scraped_job_requires_scraping_log",
        "scraped_job_id IS NULL OR job_email_scraping_service_log_id IS NOT NULL",
    ),
    (
        "ck_service_error_rating_requires_rating_log",
        "job_rating_id IS NULL OR job_rating_service_log_id IS NOT NULL",
    ),
    (
        "ck_service_error_at_least_one_fk",
        "num_nonnulls(scraped_job_id, job_rating_id, job_email_scraping_service_log_id, "
        "job_rating_service_log_id, provider_monitoring_service_log_id) >= 1",
    ),
    (
        "ck_service_error_single_service_log",
        "num_nonnulls(job_email_scraping_service_log_id, job_rating_service_log_id, "
        "provider_monitoring_service_log_id) <= 1",
    ),
]


def upgrade() -> None:
    for name, condition in _CONSTRAINTS:
        op.create_check_constraint(name, "service_error", condition)


def downgrade() -> None:
    for name, _condition in reversed(_CONSTRAINTS):
        op.drop_constraint(name, "service_error", type_="check")
