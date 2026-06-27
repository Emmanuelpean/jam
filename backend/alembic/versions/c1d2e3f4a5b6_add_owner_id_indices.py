"""add owner_id indices to all owned tables and job_application_update.job_id index

Revision ID: c1d2e3f4a5b6
Revises: 84de93787471
Create Date: 2026-06-06 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'c1d2e3f4a5b6'
down_revision: Union[str, None] = '84de93787471'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

OWNED_TABLES = [
    'aggregator',
    'company',
    'file',
    'forwarding_confirmation_link',
    'interview',
    'job',
    'job_application_update',
    'job_email',
    'job_rating',
    'keyword',
    'person',
    'scraped_job',
    'scraping_exclusion_filter',
    'scraping_favourite_filter',
    'speculative_application',
]


def upgrade() -> None:
    for table in OWNED_TABLES:
        op.create_index(op.f(f'ix_{table}_owner_id'), table, ['owner_id'], unique=False)
    op.create_index(
        op.f('ix_job_application_update_job_id'), 'job_application_update', ['job_id'], unique=False
    )


def downgrade() -> None:
    for table in OWNED_TABLES:
        op.drop_index(op.f(f'ix_{table}_owner_id'), table_name=table)
    op.drop_index(op.f('ix_job_application_update_job_id'), table_name='job_application_update')
