"""JAM V1.2

Revision ID: 53e3869239aa
Revises: 5a49153b049a
Create Date: 2026-02-09 22:58:25.657941

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

from app.job_rating.prompts import SYSTEM_PROMPT_V1, JOB_PROMPT_TEMPLATE_V1

# revision identifiers, used by Alembic.
revision: str = "53e3869239aa"
down_revision: Union[str, None] = "5a49153b049a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "ai_job_prompt_template",
        sa.Column("prompt", sa.String(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("modified_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "ai_system_prompt",
        sa.Column("prompt", sa.String(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("modified_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "geolocation",
        sa.Column("query", sa.String(), nullable=False),
        sa.Column("latitude", sa.Float(), nullable=False),
        sa.Column("longitude", sa.Float(), nullable=False),
        sa.Column("postcode", sa.String(), nullable=True),
        sa.Column("suburb", sa.String(), nullable=True),
        sa.Column("city", sa.String(), nullable=True),
        sa.Column("county", sa.String(), nullable=True),
        sa.Column("state", sa.String(), nullable=True),
        sa.Column("country", sa.String(), nullable=True),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("modified_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_geolocation_query"), "geolocation", ["query"], unique=True)
    op.create_table(
        "forwarding_confirmation_link",
        sa.Column("email_external_id", sa.String(), nullable=False),
        sa.Column("url", sa.String(), nullable=False),
        sa.Column("platform", sa.String(), nullable=False),
        sa.Column("is_used", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("owner_id", sa.Integer(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("modified_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["owner_id"], ["user.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "premium_settings",
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("job_scraping_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("job_rating_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("owner_id", sa.Integer(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("modified_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["owner_id"], ["user.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "scraping_exclusion_filter",
        sa.Column("type", sa.String(), nullable=False),
        sa.Column("operator", sa.String(), nullable=False),
        sa.Column("value", sa.String(), nullable=False),
        sa.Column("case_sensitive", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("owner_id", sa.Integer(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("modified_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint(
            "operator IN ('contains', 'equals', 'starts_with', 'ends_with', 'less_than', 'greater_than', 'not_contains', 'not_equals')",
            name="valid_filter_operator",
        ),
        sa.CheckConstraint(
            "type IN ('title', 'company', 'location', 'location_city', 'location_country', 'salary_min', 'salary_max', 'attendance_type')",
            name="valid_filter_type",
        ),
        sa.ForeignKeyConstraint(["owner_id"], ["user.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "scraping_favourite_filter",
        sa.Column("type", sa.String(), nullable=False),
        sa.Column("operator", sa.String(), nullable=False),
        sa.Column("value", sa.String(), nullable=False),
        sa.Column("case_sensitive", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("owner_id", sa.Integer(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("modified_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint(
            "operator IN ('contains', 'equals', 'starts_with', 'ends_with', 'less_than', 'greater_than', 'not_contains', 'not_equals')",
            name="valid_filter_operator",
        ),
        sa.CheckConstraint(
            "type IN ('title', 'company', 'location', 'location_city', 'location_country', 'salary_min', 'salary_max', 'attendance_type')",
            name="valid_filter_type",
        ),
        sa.ForeignKeyConstraint(["owner_id"], ["user.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "stripe_details",
        sa.Column("customer_id", sa.String(), nullable=True),
        sa.Column("subscription_id", sa.String(), nullable=True),
        sa.Column("subscription_status", sa.String(), nullable=True),
        sa.Column("trial_end_date", sa.Integer(), nullable=True),
        sa.Column("owner_id", sa.Integer(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("modified_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["owner_id"], ["user.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "user_preferences",
        sa.Column("theme", sa.String(), server_default="mixed-berry", nullable=False),
        sa.Column("dark_mode", sa.String(), server_default="system", nullable=False),
        sa.Column("chase_threshold", sa.Integer(), server_default="14", nullable=False),
        sa.Column("deadline_threshold", sa.Integer(), server_default="7", nullable=False),
        sa.Column("update_limit", sa.Integer(), server_default="10", nullable=False),
        sa.Column("default_currency", sa.String(), server_default="GBP", nullable=False),
        sa.Column("owner_id", sa.Integer(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("modified_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["owner_id"], ["user.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "user_token",
        sa.Column("token", sa.String(), nullable=False),
        sa.Column("token_type", sa.String(), nullable=False),
        sa.Column("pending_email", sa.String(), nullable=True),
        sa.Column("owner_id", sa.Integer(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("modified_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["owner_id"], ["user.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_user_token_token"), "user_token", ["token"], unique=True)
    op.create_table(
        "speculative_application",
        sa.Column("date", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("note", sa.String(), nullable=True),
        sa.Column("contact_email", sa.String(), nullable=True),
        sa.Column("company_id", sa.Integer(), nullable=False),
        sa.Column("owner_id", sa.Integer(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("modified_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["company_id"], ["company.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["owner_id"], ["user.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "speculative_application_contact_mapping",
        sa.Column("speculative_application_id", sa.Integer(), nullable=False),
        sa.Column("person_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["person_id"], ["person.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["speculative_application_id"], ["speculative_application.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("speculative_application_id", "person_id"),
    )
    op.add_column("job", sa.Column("source_type", sa.String(), nullable=True))
    op.add_column("job", sa.Column("source_aggregator_id", sa.Integer(), nullable=True))
    op.add_column("job", sa.Column("recruiter_id", sa.Integer(), nullable=True))
    op.add_column("job", sa.Column("recruitment_company_id", sa.Integer(), nullable=True))
    op.drop_index(op.f("ix_job_source_id"), table_name="job")
    op.create_index(op.f("ix_job_recruiter_id"), "job", ["recruiter_id"], unique=False)
    op.create_index(op.f("ix_job_recruitment_company_id"), "job", ["recruitment_company_id"], unique=False)
    op.create_index(op.f("ix_job_source_aggregator_id"), "job", ["source_aggregator_id"], unique=False)
    op.drop_constraint(op.f("job_source_id_fkey"), "job", type_="foreignkey")
    op.create_foreign_key(None, "job", "person", ["recruiter_id"], ["id"], ondelete="SET NULL")
    op.create_foreign_key(None, "job", "company", ["recruitment_company_id"], ["id"], ondelete="SET NULL")
    op.create_foreign_key(None, "job", "aggregator", ["source_aggregator_id"], ["id"], ondelete="SET NULL")
    # Transfer source_id data to source_aggregator_id before dropping
    op.execute("UPDATE job SET source_aggregator_id = source_id WHERE source_id IS NOT NULL")
    op.drop_column("job", "source_id")
    op.add_column(
        "job_email_scraping_platform_stat",
        sa.Column("job_to_process_ids", postgresql.ARRAY(sa.Integer()), server_default="{}", nullable=False),
    )
    op.add_column(
        "job_email_scraping_platform_stat",
        sa.Column("job_scrape_filtered_ids", postgresql.ARRAY(sa.Integer()), server_default="{}", nullable=False),
    )
    # Transfer job_to_scrape_ids data to job_to_process_ids before dropping
    op.execute("""
        UPDATE job_email_scraping_platform_stat
        SET job_to_process_ids = job_to_scrape_ids
        WHERE job_to_scrape_ids != '{}'
    """)
    op.drop_column("job_email_scraping_platform_stat", "job_to_scrape_ids")
    op.add_column("job_rating", sa.Column("job_prompt", sa.String(), nullable=True))
    op.add_column("job_rating", sa.Column("system_prompt_id", sa.Integer(), nullable=True))
    op.add_column("job_rating", sa.Column("job_prompt_template_id", sa.Integer(), nullable=True))
    op.create_foreign_key(
        None, "job_rating", "ai_job_prompt_template", ["job_prompt_template_id"], ["id"], ondelete="SET NULL"
    )
    op.create_foreign_key(None, "job_rating", "ai_system_prompt", ["system_prompt_id"], ["id"], ondelete="SET NULL")
    op.drop_column("job_rating", "script_version")
    op.add_column("location", sa.Column("geolocation_id", sa.Integer(), nullable=True))
    op.create_foreign_key(None, "location", "geolocation", ["geolocation_id"], ["id"], ondelete="SET NULL")
    op.add_column("person", sa.Column("is_recruiter", sa.Boolean(), server_default=sa.text("false"), nullable=False))
    op.add_column(
        "scraped_job", sa.Column("is_processed", sa.Boolean(), server_default=sa.text("false"), nullable=False)
    )
    op.execute("UPDATE scraped_job SET is_processed = true")
    op.add_column("scraped_job", sa.Column("is_skipped", sa.Boolean(), server_default=sa.text("false"), nullable=False))
    op.add_column("scraped_job", sa.Column("skip_reason", sa.String(), nullable=True))
    op.add_column("scraped_job", sa.Column("exclusion_filter_id", sa.Integer(), nullable=True))
    op.add_column("scraped_job", sa.Column("favourite_filter_id", sa.Integer(), nullable=True))
    op.add_column("scraped_job", sa.Column("geolocation_id", sa.Integer(), nullable=True))
    op.create_foreign_key(None, "scraped_job", "geolocation", ["geolocation_id"], ["id"], ondelete="SET NULL")
    op.create_foreign_key(
        None, "scraped_job", "scraping_exclusion_filter", ["exclusion_filter_id"], ["id"], ondelete="SET NULL"
    )
    op.create_foreign_key(
        None, "scraped_job", "scraping_favourite_filter", ["favourite_filter_id"], ["id"], ondelete="SET NULL"
    )
    # Migrate user data to subtables before dropping columns
    op.execute("""
        INSERT INTO user_preferences (owner_id, theme, chase_threshold, deadline_threshold, update_limit, default_currency)
        SELECT id, theme, chase_threshold, deadline_threshold, update_limit, default_currency
        FROM "user"
    """)
    op.execute("""
        INSERT INTO stripe_details (owner_id)
        SELECT id FROM "user"
    """)
    op.execute("""
        INSERT INTO premium_settings (owner_id, is_active)
        SELECT id, toast_active FROM "user"
    """)
    # Migrate verification tokens
    op.execute("""
        INSERT INTO user_token (owner_id, token, token_type)
        SELECT id, verification_token, 'verification'
        FROM "user"
        WHERE verification_token IS NOT NULL
    """)
    # Migrate password reset tokens
    op.execute("""
        INSERT INTO user_token (owner_id, token, token_type)
        SELECT id, password_reset_token, 'password_reset'
        FROM "user"
        WHERE password_reset_token IS NOT NULL
    """)
    # Migrate email change tokens
    op.execute("""
        INSERT INTO user_token (owner_id, token, token_type, pending_email)
        SELECT id, email_change_token, 'email_change', pending_email
        FROM "user"
        WHERE email_change_token IS NOT NULL
    """)

    op.add_column("user", sa.Column("previous_login", sa.TIMESTAMP(timezone=True), nullable=True))
    op.add_column("user", sa.Column("app_version", sa.String(), nullable=True))
    op.execute("UPDATE \"user\" SET app_version = '1.10.0'")  # Add version number
    op.add_column("user", sa.Column("first_name", sa.String(), nullable=True))
    op.add_column("user", sa.Column("last_name", sa.String(), nullable=True))
    op.drop_constraint(op.f("user_password_reset_token_key"), "user", type_="unique")
    op.drop_column("user", "email_change_token_created_at")
    op.drop_column("user", "theme")
    op.drop_column("user", "update_limit")
    op.drop_column("user", "email_change_token")
    op.drop_column("user", "chase_threshold")
    op.drop_column("user", "password_reset_token")
    op.drop_column("user", "deadline_threshold")
    op.drop_column("user", "pending_email")
    op.drop_column("user", "default_currency")
    op.drop_column("user", "password_reset_token_created_at")
    op.drop_column("user", "verification_token_created_at")
    op.drop_column("user", "toast_active")
    op.drop_column("user", "verification_token")
    op.drop_column("user_qualification", "is_active")
    op.drop_constraint("valid_applied_via_values", "job", type_="check")
    op.create_check_constraint(
        "valid_applied_via_values",
        "job",
        "applied_via IN ('aggregator', 'email', 'company_website', 'phone', 'other')",
    )

    # Seed AI prompts
    op.execute(sa.text("INSERT INTO ai_system_prompt (prompt) VALUES (:prompt)").bindparams(prompt=SYSTEM_PROMPT_V1))
    op.execute(
        sa.text("INSERT INTO ai_job_prompt_template (prompt) VALUES (:prompt)").bindparams(
            prompt=JOB_PROMPT_TEMPLATE_V1
        )
    )


def downgrade() -> None:
    op.add_column(
        "user_qualification",
        sa.Column("is_active", sa.BOOLEAN(), server_default=sa.text("true"), autoincrement=False, nullable=False),
    )
    op.add_column("user", sa.Column("verification_token", sa.VARCHAR(), autoincrement=False, nullable=True))
    op.add_column(
        "user",
        sa.Column("toast_active", sa.BOOLEAN(), server_default=sa.text("false"), autoincrement=False, nullable=False),
    )
    op.add_column(
        "user",
        sa.Column(
            "verification_token_created_at", postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True
        ),
    )
    op.add_column(
        "user",
        sa.Column(
            "password_reset_token_created_at", postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True
        ),
    )
    op.add_column(
        "user",
        sa.Column(
            "default_currency",
            sa.VARCHAR(),
            server_default=sa.text("'GBP'::character varying"),
            autoincrement=False,
            nullable=False,
        ),
    )
    op.add_column("user", sa.Column("pending_email", sa.VARCHAR(), autoincrement=False, nullable=True))
    op.add_column(
        "user",
        sa.Column("deadline_threshold", sa.INTEGER(), server_default=sa.text("7"), autoincrement=False, nullable=False),
    )
    op.add_column("user", sa.Column("password_reset_token", sa.VARCHAR(), autoincrement=False, nullable=True))
    op.add_column(
        "user",
        sa.Column("chase_threshold", sa.INTEGER(), server_default=sa.text("14"), autoincrement=False, nullable=False),
    )
    op.add_column("user", sa.Column("email_change_token", sa.VARCHAR(), autoincrement=False, nullable=True))
    op.add_column(
        "user",
        sa.Column("update_limit", sa.INTEGER(), server_default=sa.text("10"), autoincrement=False, nullable=False),
    )
    op.add_column(
        "user",
        sa.Column(
            "theme",
            sa.VARCHAR(),
            server_default=sa.text("'mixed-berry'::character varying"),
            autoincrement=False,
            nullable=False,
        ),
    )
    op.add_column(
        "user",
        sa.Column(
            "email_change_token_created_at", postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True
        ),
    )

    # Restore user data from subtables before dropping them
    op.execute("""
        UPDATE "user" u
        SET theme = up.theme,
            chase_threshold = up.chase_threshold,
            deadline_threshold = up.deadline_threshold,
            update_limit = up.update_limit,
            default_currency = up.default_currency
        FROM user_preferences up
        WHERE u.id = up.owner_id
    """)
    # Restore toast_active from premium_settings.is_active
    op.execute("""
        UPDATE "user" u
        SET toast_active = ps.is_active
        FROM premium_settings ps
        WHERE u.id = ps.owner_id
    """)
    # Restore verification tokens
    op.execute("""
        UPDATE "user" u
        SET verification_token = ut.token
        FROM user_token ut
        WHERE u.id = ut.owner_id AND ut.token_type = 'verification'
    """)
    # Restore password reset tokens
    op.execute("""
        UPDATE "user" u
        SET password_reset_token = ut.token
        FROM user_token ut
        WHERE u.id = ut.owner_id AND ut.token_type = 'password_reset'
    """)
    # Restore email change tokens
    op.execute("""
        UPDATE "user" u
        SET email_change_token = ut.token, pending_email = ut.pending_email
        FROM user_token ut
        WHERE u.id = ut.owner_id AND ut.token_type = 'email_change'
    """)

    op.create_unique_constraint(
        op.f("user_password_reset_token_key"), "user", ["password_reset_token"], postgresql_nulls_not_distinct=False
    )
    op.drop_column("user", "last_name")
    op.drop_column("user", "first_name")
    op.drop_column("user", "app_version")
    op.drop_column("user", "previous_login")
    op.drop_constraint(op.f("scraped_job_geolocation_id_fkey"), "scraped_job", type_="foreignkey")
    op.drop_constraint(op.f("scraped_job_favourite_filter_id_fkey"), "scraped_job", type_="foreignkey")
    op.drop_constraint(op.f("scraped_job_exclusion_filter_id_fkey"), "scraped_job", type_="foreignkey")
    op.drop_column("scraped_job", "geolocation_id")
    op.drop_column("scraped_job", "favourite_filter_id")
    op.drop_column("scraped_job", "exclusion_filter_id")
    op.drop_column("scraped_job", "skip_reason")
    op.drop_column("scraped_job", "is_skipped")
    op.drop_column("scraped_job", "is_processed")
    op.drop_column("person", "is_recruiter")
    op.drop_constraint(op.f("location_geolocation_id_fkey"), "location", type_="foreignkey")
    op.drop_column("location", "geolocation_id")
    op.add_column("job_rating", sa.Column("script_version", sa.INTEGER(), autoincrement=False, nullable=True))
    op.drop_constraint(op.f("job_rating_job_prompt_template_id_fkey"), "job_rating", type_="foreignkey")
    op.drop_constraint(op.f("job_rating_system_prompt_id_fkey"), "job_rating", type_="foreignkey")
    op.drop_column("job_rating", "job_prompt_template_id")
    op.drop_column("job_rating", "system_prompt_id")
    op.drop_column("job_rating", "job_prompt")
    op.add_column(
        "job_email_scraping_platform_stat",
        sa.Column(
            "job_to_scrape_ids",
            postgresql.ARRAY(sa.INTEGER()),
            server_default=sa.text("'{}'::integer[]"),
            autoincrement=False,
            nullable=False,
        ),
    )
    # Transfer job_to_process_ids data back to job_to_scrape_ids before dropping
    op.execute("""
        UPDATE job_email_scraping_platform_stat
        SET job_to_scrape_ids = job_to_process_ids
        WHERE job_to_process_ids != '{}'
    """)
    op.drop_column("job_email_scraping_platform_stat", "job_scrape_filtered_ids")
    op.drop_column("job_email_scraping_platform_stat", "job_to_process_ids")
    op.add_column("job", sa.Column("source_id", sa.INTEGER(), autoincrement=False, nullable=True))
    # Transfer source_aggregator_id data back to source_id before dropping
    op.execute("UPDATE job SET source_id = source_aggregator_id WHERE source_aggregator_id IS NOT NULL")
    op.drop_constraint(op.f("job_source_aggregator_id_fkey"), "job", type_="foreignkey")
    op.drop_constraint(op.f("job_recruitment_company_id_fkey"), "job", type_="foreignkey")
    op.drop_constraint(op.f("job_recruiter_id_fkey"), "job", type_="foreignkey")
    op.create_foreign_key(op.f("job_source_id_fkey"), "job", "aggregator", ["source_id"], ["id"], ondelete="SET NULL")
    op.drop_index(op.f("ix_job_source_aggregator_id"), table_name="job")
    op.drop_index(op.f("ix_job_recruitment_company_id"), table_name="job")
    op.drop_index(op.f("ix_job_recruiter_id"), table_name="job")
    op.create_index(op.f("ix_job_source_id"), "job", ["source_id"], unique=False)
    op.drop_column("job", "recruitment_company_id")
    op.drop_column("job", "recruiter_id")
    op.drop_column("job", "source_aggregator_id")
    op.drop_column("job", "source_type")
    op.drop_table("speculative_application_contact_mapping")
    op.drop_table("speculative_application")
    op.drop_index(op.f("ix_user_token_token"), table_name="user_token")
    op.drop_table("user_token")
    op.drop_table("user_preferences")
    op.drop_table("stripe_details")
    op.drop_table("scraping_favourite_filter")
    op.drop_table("scraping_exclusion_filter")
    op.drop_table("premium_settings")
    op.drop_table("forwarding_confirmation_link")
    op.drop_index(op.f("ix_geolocation_query"), table_name="geolocation")
    op.drop_table("geolocation")
    op.drop_table("ai_system_prompt")
    op.drop_table("ai_job_prompt_template")
    op.drop_constraint("valid_applied_via_values", "job", type_="check")
    op.create_check_constraint(
        "valid_applied_via_values", "job", "applied_via IN ('aggregator', 'email', 'phone', 'other')"
    )
