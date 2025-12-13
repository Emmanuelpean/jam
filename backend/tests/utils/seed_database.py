"""Database seeding script for development.
This script will drop all data and repopulate with hard-coded sample data."""

import os
import sys

from sqlalchemy import text, inspect

from app.database import engine, session_local, Base
from tests.utils.create_data import (
    create_users,
    create_settings,
    create_companies,
    create_locations,
    create_aggregators,
    create_keywords,
    create_people,
    create_jobs,
    create_files,
    create_interviews,
    create_job_alert_emails,
    create_scraped_jobs,
    create_job_scraping_service_logs,
    create_job_application_updates,
    create_job_scraping_platform_stats,
    create_job_scraping_service_errors,
    create_user_qualifications,
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
        users = create_users(db)
        settings = create_settings(db)

        # Table data
        keywords = create_keywords(db, users)
        aggregators = create_aggregators(db, users)
        locations = create_locations(db, users)
        companies = create_companies(db, users)
        people = create_people(db, users, companies)
        files = create_files(db, users)
        jobs = create_jobs(db, keywords, people, users, companies, locations, aggregators, files)
        interviews = create_interviews(db, people, users, locations, jobs)
        job_application_updates = create_job_application_updates(db, users, jobs)
        user_qualifications = create_user_qualifications(db, users)

        # EIS data
        service_logs = create_job_scraping_service_logs(db)
        platform_stats = create_job_scraping_platform_stats(db, service_logs)
        eis_service_errors = create_job_scraping_service_errors(db, service_logs)
        alert_emails = create_job_alert_emails(db, users, service_logs)
        scraped_jobs = create_scraped_jobs(db, alert_emails, users)
        job_ratings = create_job_ratings(db, users, scraped_jobs, user_qualifications)

        print("\n" + "=" * 50)
        print("DATABASE SEEDING COMPLETED SUCCESSFULLY!")
        print("=" * 50)
        print(f"Users: {len(users)}")
        print(f"Settings: {len(settings)}")
        print(f"Companies: {len(companies)}")
        print(f"Locations: {len(locations)}")
        print(f"Aggregators: {len(aggregators)}")
        print(f"Keywords: {len(keywords)}")
        print(f"People: {len(people)}")
        print(f"Jobs: {len(jobs)}")
        print(f"Files: {len(files)}")
        print(f"Interviews: {len(interviews)}")
        print(f"Service Logs: {len(service_logs)}")
        print(f"Job Alert Emails: {len(alert_emails)}")
        print(f"Scraped Jobs: {len(scraped_jobs)}")
        print(f"Job Application Updates: {len(job_application_updates)}")
        print(f"Platform Stats: {len(platform_stats)}")
        print(f"EIS Service Errors: {len(eis_service_errors)}")
        print(f"User Qualifications: {len(user_qualifications)}")
        print(f"Job Ratings: {len(job_ratings)}")
        print("=" * 50)

    except Exception as e:
        print(f"Error during seeding: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
