"""Tour + locations

Revision ID: a9b8c7d6e5f4
Revises: f1a2b3c4d5e6
Create Date: 2026-05-21

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "a9b8c7d6e5f4"
down_revision: Union[str, None] = "f1a2b3c4d5e6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_OWNED_TABLES = [
    "aggregator",
    "company",
    "file",
    "forwarding_confirmation_link",
    "interview",
    "job",
    "job_application_update",
    "job_email",
    "job_rating",
    "keyword",
    "person",
    "premium_settings",
    "scraped_job",
    "scraping_exclusion_filter",
    "scraping_favourite_filter",
    "speculative_application",
    "stripe_details",
    "user_preferences",
    "user_qualification",
    "user_token",
]


def upgrade() -> None:
    # --- User preferences ---
    op.add_column("user_preferences", sa.Column("dashboard_layout", sa.String(), nullable=True))
    op.add_column("user_preferences", sa.Column("completed_tours", sa.JSON(), nullable=True))

    # --- Scraped job ---
    op.add_column("scraped_job", sa.Column("read_at", sa.TIMESTAMP(timezone=True), nullable=True))
    op.drop_constraint("scraped_job_favourite_filter_id_fkey", "scraped_job", type_="foreignkey")
    op.drop_column("scraped_job", "favourite_filter_id")
    op.alter_column("scraped_job", "location", new_column_name="raw_location")
    op.alter_column("scraped_job", "parsed_location", new_column_name="location")
    op.drop_column("scraped_job", "location_city")
    op.drop_column("scraped_job", "location_country")
    op.drop_column("scraped_job", "location_postcode")

    # --- Scraping filters ---
    op.drop_constraint("valid_filter_type", "scraping_exclusion_filter", type_="check")
    op.drop_constraint("valid_filter_type", "scraping_favourite_filter", type_="check")
    op.create_check_constraint(
        "valid_filter_type",
        "scraping_exclusion_filter",
        "type IN ('title', 'company', 'location', 'salary_min', 'salary_max', 'attendance_type')",
    )
    op.create_check_constraint(
        "valid_filter_type",
        "scraping_favourite_filter",
        "type IN ('title', 'company', 'location', 'salary_min', 'salary_max', 'attendance_type')",
    )

    # --- Location (job / interview) ---
    op.add_column("job", sa.Column("location", sa.String(), nullable=True))
    op.add_column(
        "job",
        sa.Column("geolocation_id", sa.Integer(), sa.ForeignKey("geolocation.id", ondelete="SET NULL"), nullable=True),
    )
    op.create_index(op.f("ix_job_geolocation_id"), "job", ["geolocation_id"], unique=False)

    op.add_column("interview", sa.Column("location", sa.String(), nullable=True))
    op.add_column(
        "interview",
        sa.Column("geolocation_id", sa.Integer(), sa.ForeignKey("geolocation.id", ondelete="SET NULL"), nullable=True),
    )
    op.create_index(op.f("ix_interview_geolocation_id"), "interview", ["geolocation_id"], unique=False)

    op.execute("""
        UPDATE job
        SET location = CONCAT_WS(', ',
                NULLIF(l.city, ''),
                NULLIF(l.country, ''),
                NULLIF(l.postcode, '')
            ),
            geolocation_id = l.geolocation_id
        FROM location l
        WHERE job.location_id = l.id
        """)
    op.execute("""
        UPDATE interview
        SET location = CONCAT_WS(', ',
                NULLIF(l.city, ''),
                NULLIF(l.country, ''),
                NULLIF(l.postcode, '')
            ),
            geolocation_id = l.geolocation_id
        FROM location l
        WHERE interview.location_id = l.id
        """)

    op.drop_index("ix_job_location_id", table_name="job")
    op.drop_constraint("job_location_id_fkey", "job", type_="foreignkey")
    op.drop_column("job", "location_id")

    op.drop_index("ix_interview_location_id", table_name="interview")
    op.drop_constraint("interview_location_id_fkey", "interview", type_="foreignkey")
    op.drop_column("interview", "location_id")

    op.drop_table("location")

    # --- File ---
    op.add_column("file", sa.Column("file_type", sa.String(), nullable=True))
    op.add_column("file", sa.Column("content_hash", sa.String(), nullable=True))
    op.create_index("ix_file_content_hash", "file", ["content_hash"])

    # --- Tour ---
    for table in _OWNED_TABLES:
        op.add_column(table, sa.Column("is_tour", sa.Boolean(), nullable=False, server_default=sa.text("false")))

    op.drop_constraint("uq_owner_keyword_name", "keyword", type_="unique")
    op.create_unique_constraint("uq_owner_keyword_name", "keyword", ["owner_id", "name", "is_tour"])

    op.drop_constraint("uq_owner_aggregator_name", "aggregator", type_="unique")
    op.create_unique_constraint("uq_owner_aggregator_name", "aggregator", ["owner_id", "name", "is_tour"])

    op.drop_constraint("uq_owner_company_name", "company", type_="unique")
    op.create_unique_constraint("uq_owner_company_name", "company", ["owner_id", "name", "is_tour"])


def downgrade() -> None:
    # --- Tour ---
    op.drop_constraint("uq_owner_company_name", "company", type_="unique")
    op.create_unique_constraint("uq_owner_company_name", "company", ["owner_id", "name"])

    op.drop_constraint("uq_owner_aggregator_name", "aggregator", type_="unique")
    op.create_unique_constraint("uq_owner_aggregator_name", "aggregator", ["owner_id", "name"])

    op.drop_constraint("uq_owner_keyword_name", "keyword", type_="unique")
    op.create_unique_constraint("uq_owner_keyword_name", "keyword", ["owner_id", "name"])

    for table in reversed(_OWNED_TABLES):
        op.drop_column(table, "is_tour")

    # --- File ---
    op.drop_index("ix_file_content_hash", table_name="file")
    op.drop_column("file", "content_hash")
    op.drop_column("file", "file_type")

    # --- Location (job / interview) ---
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

    op.drop_index(op.f("ix_job_geolocation_id"), table_name="job")
    op.drop_column("job", "geolocation_id")
    op.drop_column("job", "location")

    op.drop_index(op.f("ix_interview_geolocation_id"), table_name="interview")
    op.drop_column("interview", "geolocation_id")
    op.drop_column("interview", "location")

    # --- Scraping filters ---
    op.drop_constraint("valid_filter_type", "scraping_exclusion_filter", type_="check")
    op.drop_constraint("valid_filter_type", "scraping_favourite_filter", type_="check")
    op.create_check_constraint(
        "valid_filter_type",
        "scraping_exclusion_filter",
        "type IN ('title', 'company', 'location', 'location_city', 'location_country', 'salary_min', 'salary_max', 'attendance_type')",
    )
    op.create_check_constraint(
        "valid_filter_type",
        "scraping_favourite_filter",
        "type IN ('title', 'company', 'location', 'location_city', 'location_country', 'salary_min', 'salary_max', 'attendance_type')",
    )

    # --- Scraped job ---
    op.add_column("scraped_job", sa.Column("location_postcode", sa.String(), nullable=True))
    op.add_column("scraped_job", sa.Column("location_country", sa.String(), nullable=True))
    op.add_column("scraped_job", sa.Column("location_city", sa.String(), nullable=True))
    op.alter_column("scraped_job", "location", new_column_name="parsed_location")
    op.alter_column("scraped_job", "raw_location", new_column_name="location")
    op.add_column("scraped_job", sa.Column("favourite_filter_id", sa.Integer(), nullable=True))
    op.create_foreign_key(
        None, "scraped_job", "scraping_favourite_filter", ["favourite_filter_id"], ["id"], ondelete="SET NULL"
    )
    op.drop_column("scraped_job", "read_at")

    # --- User preferences ---
    op.drop_column("user_preferences", "completed_tours")
    op.drop_column("user_preferences", "dashboard_layout")
