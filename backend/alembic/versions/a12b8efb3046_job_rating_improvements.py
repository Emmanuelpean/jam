"""empty message

Revision ID: a12b8efb3046
Revises: b2c3d4e5f6a7
Create Date: 2026-02-23 21:14:35.206988

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "a12b8efb3046"
down_revision: Union[str, None] = "b2c3d4e5f6a7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("job_rating", sa.Column("is_skipped", sa.Boolean(), server_default=sa.text("false"), nullable=False))
    op.add_column("job_rating", sa.Column("skip_reason", sa.String(), nullable=True))
    op.add_column("job_rating", sa.Column("llm_model", sa.String(), nullable=False))
    op.execute("UPDATE job_rating SET llm_model = 'gpt-4.1-mini'")
    op.add_column("job_rating", sa.Column("notes", postgresql.ARRAY(sa.String()), server_default="{}", nullable=False))
    op.alter_column("job_rating_service_log", "rated_job_found_ids", new_column_name="job_found_ids")
    op.alter_column("job_rating_service_log", "rated_job_succeeded_ids", new_column_name="job_succeeded_ids")
    op.alter_column("job_rating_service_log", "rated_job_failed_ids", new_column_name="job_failed_ids")
    op.add_column(
        "job_rating_service_log",
        sa.Column("job_skipped_ids", postgresql.ARRAY(sa.Integer()), server_default="{}", nullable=False),
    )


def downgrade() -> None:
    op.drop_column("job_rating_service_log", "job_skipped_ids")
    # Rename back
    op.alter_column("job_rating_service_log", "job_found_ids", new_column_name="rated_job_found_ids")
    op.alter_column("job_rating_service_log", "job_succeeded_ids", new_column_name="rated_job_succeeded_ids")
    op.alter_column("job_rating_service_log", "job_failed_ids", new_column_name="rated_job_failed_ids")
    op.drop_column("job_rating", "notes")
    op.drop_column("job_rating", "skip_reason")
    op.drop_column("job_rating", "is_skipped")
    op.drop_column("job_rating", "llm_model")
