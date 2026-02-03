"""Database seeding script for development.
This script will drop all data and repopulate with hard-coded sample data."""

import os
import sys

from sqlalchemy import text, inspect

from app.database import engine, session_local, Base
from tests.utils.create_data.core import (
    create_users,
    create_settings,
    create_ai_prompts,
    create_user_qualifications,
)
from tests.utils.create_data.data_tables import (
    create_keywords,
    create_aggregators,
    create_geolocations,
    create_locations,
    create_companies,
    create_people,
    create_jobs,
    create_files,
    create_interviews,
    create_job_application_updates,
    create_speculative_applications,
)
from tests.utils.create_data.job_scraping import (
    create_job_scraping_service_logs,
    create_job_scraping_platform_stats,
    create_job_scraping_service_errors,
    create_job_alert_emails,
    create_scraping_filters,
    create_scraped_jobs,
)
from tests.utils.create_data.job_rating import (
    create_job_rating_service_logs,
    create_job_ratings,
)

sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def reset_database(db_engine, ask_confirmation: bool = True) -> None:
    """Drop ALL tables in the database (including orphaned ones) and recreate from models"""

    if ask_confirmation:
        ask = input(
            "WARNING: This will DROP ALL DATA in the database. Press Enter 'Yes' continue or anything else to abort."
        )
        if ask.lower() != "yes":
            print("Aborting.")
            sys.exit(0)

    print("Dropping all tables in the database...")

    with db_engine.connect() as conn:
        # Get the database inspector to find all existing tables
        inspector = inspect(db_engine)
        table_names = inspector.get_table_names()

        # For PostgreSQL: Drop tables with CASCADE to handle foreign key constraints
        for table_name in table_names:
            conn.execute(text(f'DROP TABLE IF EXISTS "{table_name}" CASCADE'))

        conn.commit()

    print("Creating all tables from models...")
    Base.metadata.create_all(bind=db_engine)


def seed_database() -> None:
    """Main function to seed the database"""
    print("Starting database seeding...")

    # Reset the database
    reset_database(engine)

    # Create a database session
    db = session_local()

    try:
        # App data
        users = create_users(db, None, 12)
        create_settings(db)
        ai_prompts = create_ai_prompts(db)

        # Table data
        keywords = create_keywords(db, users)
        aggregators = create_aggregators(db, users)
        create_geolocations(db)
        locations = create_locations(db, users)
        companies = create_companies(db, users)
        people = create_people(db, users, companies)
        files = create_files(db, users)
        jobs = create_jobs(db, keywords, people, users, companies, locations, aggregators, files)
        create_interviews(db, people, users, locations, jobs)
        create_job_application_updates(db, users, jobs)
        user_qualifications = create_user_qualifications(db, users)
        create_speculative_applications(db, users, people)

        # Job Scraping data
        service_logs = create_job_scraping_service_logs(db)
        create_job_scraping_platform_stats(db, service_logs)
        create_job_scraping_service_errors(db, service_logs)
        alert_emails = create_job_alert_emails(db, users, service_logs)
        scraping_filters = create_scraping_filters(db, users)
        scraped_jobs = create_scraped_jobs(db, alert_emails, users, scraping_filters)

        # Job Rating data
        job_rating_service_logs = create_job_rating_service_logs(db)
        create_job_ratings(db, users, scraped_jobs, user_qualifications, job_rating_service_logs, ai_prompts)

    except Exception as e:
        print(f"Error during seeding: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
