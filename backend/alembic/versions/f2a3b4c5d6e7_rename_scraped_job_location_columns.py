"""Rename scraped_job location/parsed_location columns and drop location_city/country/postcode

Revision ID: f2a3b4c5d6e7
Revises: e1f2a3b4c5d6, b2c3d4e5f6a7
Create Date: 2026-04-28 00:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "f2a3b4c5d6e7"
down_revision: Union[str, tuple, None] = ("e1f2a3b4c5d6", "b2c3d4e5f6a7")
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column("scraped_job", "location", new_column_name="raw_location")
    op.alter_column("scraped_job", "parsed_location", new_column_name="location")
    op.drop_column("scraped_job", "location_city")
    op.drop_column("scraped_job", "location_country")
    op.drop_column("scraped_job", "location_postcode")
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


def downgrade() -> None:
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
    op.add_column("scraped_job", sa.Column("location_postcode", sa.String(), nullable=True))
    op.add_column("scraped_job", sa.Column("location_country", sa.String(), nullable=True))
    op.add_column("scraped_job", sa.Column("location_city", sa.String(), nullable=True))
    op.alter_column("scraped_job", "location", new_column_name="parsed_location")
    op.alter_column("scraped_job", "raw_location", new_column_name="location")
