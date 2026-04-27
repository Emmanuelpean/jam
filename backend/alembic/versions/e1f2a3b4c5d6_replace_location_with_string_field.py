"""Replace Location entity with string field on Job and Interview

Revision ID: e1f2a3b4c5d6
Revises: d4e5f6a7b8c9
Create Date: 2026-04-26 00:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "e1f2a3b4c5d6"
down_revision: Union[str, None] = "d4e5f6a7b8c9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Step 1: Add new columns to job and interview
    op.add_column("job", sa.Column("location", sa.String(), nullable=True))
    op.add_column(
        "job",
        sa.Column("geolocation_id", sa.Integer(), sa.ForeignKey("geolocation.id", ondelete="SET NULL"), nullable=True),
    )
    op.create_index(op.f("ix_job_geolocation_id"), "job", ["geolocation_id"], unique=False)

    op.add_column("interview", sa.Column("location", sa.String(), nullable=True))
    op.add_column(
        "interview",
        sa.Column(
            "geolocation_id", sa.Integer(), sa.ForeignKey("geolocation.id", ondelete="SET NULL"), nullable=True
        ),
    )
    op.create_index(op.f("ix_interview_geolocation_id"), "interview", ["geolocation_id"], unique=False)

    # Step 2: Migrate existing location data into the new columns
    op.execute(
        """
        UPDATE job
        SET location = CONCAT_WS(', ',
                NULLIF(l.city, ''),
                NULLIF(l.country, ''),
                NULLIF(l.postcode, '')
            ),
            geolocation_id = l.geolocation_id
        FROM location l
        WHERE job.location_id = l.id
        """
    )
    op.execute(
        """
        UPDATE interview
        SET location = CONCAT_WS(', ',
                NULLIF(l.city, ''),
                NULLIF(l.country, ''),
                NULLIF(l.postcode, '')
            ),
            geolocation_id = l.geolocation_id
        FROM location l
        WHERE interview.location_id = l.id
        """
    )

    # Step 3: Drop the old location_id FK columns
    op.drop_index("ix_job_location_id", table_name="job")
    op.drop_constraint("job_location_id_fkey", "job", type_="foreignkey")
    op.drop_column("job", "location_id")

    op.drop_index("ix_interview_location_id", table_name="interview")
    op.drop_constraint("interview_location_id_fkey", "interview", type_="foreignkey")
    op.drop_column("interview", "location_id")

    # Step 4: Drop the location table (all FKs are gone)
    op.drop_table("location")


def downgrade() -> None:
    # Step 1: Recreate the location table
    op.create_table(
        "location",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("modified_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("owner_id", sa.Integer(), nullable=False),
        sa.Column("postcode", sa.String(), nullable=True),
        sa.Column("city", sa.String(), nullable=True),
        sa.Column("country", sa.String(), nullable=True),
        sa.Column("geolocation_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["geolocation_id"], ["geolocation.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["owner_id"], ["user.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint(
            "postcode IS NOT NULL OR city IS NOT NULL OR country IS NOT NULL",
            name="location_data_required",
        ),
        sa.UniqueConstraint("owner_id", "city", "postcode", "country", name="uq_owner_location_unique"),
    )
    op.create_index(op.f("ix_location_id"), "location", ["id"], unique=False)

    # Step 2: Add location_id back to job and interview
    op.add_column(
        "job",
        sa.Column("location_id", sa.Integer(), sa.ForeignKey("location.id", ondelete="SET NULL"), nullable=True),
    )
    op.create_index(op.f("ix_job_location_id"), "job", ["location_id"], unique=False)

    op.add_column(
        "interview",
        sa.Column("location_id", sa.Integer(), sa.ForeignKey("location.id", ondelete="SET NULL"), nullable=True),
    )
    op.create_index(op.f("ix_interview_location_id"), "interview", ["location_id"], unique=False)

    # Step 3: Drop new columns
    op.drop_index(op.f("ix_job_geolocation_id"), table_name="job")
    op.drop_column("job", "geolocation_id")
    op.drop_column("job", "location")

    op.drop_index(op.f("ix_interview_geolocation_id"), table_name="interview")
    op.drop_column("interview", "geolocation_id")
    op.drop_column("interview", "location")
