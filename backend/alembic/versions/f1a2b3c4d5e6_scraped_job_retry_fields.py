"""scraped_job retry fields

Revision ID: f1a2b3c4d5e6
Revises: 77b1a20511b7
Create Date: 2026-03-11 00:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "f1a2b3c4d5e6"
down_revision: Union[str, None] = "77b1a20511b7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("scraped_job", sa.Column("retry_count", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("scraped_job", sa.Column("next_retry_at", sa.TIMESTAMP(timezone=True), nullable=True))
    op.execute("""
        ALTER TABLE scraped_job
        ALTER COLUMN scrape_error TYPE JSONB
        USING CASE
            WHEN scrape_error IS NULL THEN '[]'::jsonb
            ELSE jsonb_build_array(jsonb_build_object('datetime', scrape_datetime::text, 'error', scrape_error))
        END
        """)
    op.execute("ALTER TABLE scraped_job ALTER COLUMN scrape_error SET NOT NULL")
    op.execute("ALTER TABLE scraped_job ALTER COLUMN scrape_error SET DEFAULT '[]'")
    op.add_column("scraped_job", sa.Column("is_closed", sa.BOOLEAN, nullable=False, server_default="false"))


def downgrade() -> None:
    op.drop_column("scraped_job", "retry_count")
    op.drop_column("scraped_job", "next_retry_at")
    op.execute("""
        ALTER TABLE scraped_job
        ALTER COLUMN scrape_error TYPE VARCHAR
        USING CASE
            WHEN jsonb_array_length(scrape_error) = 0 THEN NULL
            ELSE (SELECT string_agg(elem->>'error', E'\\n\\n') FROM jsonb_array_elements(scrape_error) AS elem)
        END
        """)
    op.execute("ALTER TABLE scraped_job ALTER COLUMN scrape_error DROP NOT NULL")
    op.execute("ALTER TABLE scraped_job ALTER COLUMN scrape_error DROP DEFAULT")
    op.drop_column("scraped_job", "is_closed")
