"""Database seeding script for development.
This script will drop all data and repopulate with hard-coded sample data."""

import os
import sys

from sqlalchemy import text, inspect

from app.database import engine, session_local, Base
import tests.utils.create_data as crd

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
        users = crd.create_users(db, None, 12)
        settings = crd.create_settings(db)

        # Table data
        keywords = crd.create_keywords(db, users)
        aggregators = crd.create_aggregators(db, users)
        geolocations = crd.create_geolocations(db)
        locations = crd.create_locations(db, users)
        companies = crd.create_companies(db, users)
        people = crd.create_people(db, users, companies)
        files = crd.create_files(db, users)
        jobs = crd.create_jobs(db, keywords, people, users, companies, locations, aggregators, files)
        interviews = crd.create_interviews(db, people, users, locations, jobs)
        job_application_updates = crd.create_job_application_updates(db, users, jobs)
        user_qualifications = crd.create_user_qualifications(db, users)
        speculative_applications = crd.create_speculative_applications(db, users, people)

        # EIS data
        service_logs = crd.create_job_scraping_service_logs(db)
        platform_stats = crd.create_job_scraping_platform_stats(db, service_logs)
        eis_service_errors = crd.create_job_scraping_service_errors(db, service_logs)
        alert_emails = crd.create_job_alert_emails(db, users, service_logs)
        scraping_filters = crd.create_scraping_filters(db, users)
        scraped_jobs = crd.create_scraped_jobs(db, alert_emails, users, scraping_filters)

        # Job Ratings data
        job_rating_service_logs = crd.create_job_scraping_service_logs(db)
        job_ratings = crd.create_job_ratings(db, users, scraped_jobs, user_qualifications, job_rating_service_logs)

        print("\n" + "=" * 50)
        print("DATABASE SEEDING COMPLETED SUCCESSFULLY!")
        print("=" * 50)
        print(f"Users: {len(users)}")
        print(f"Settings: {len(settings)}")
        print(f"Companies: {len(companies)}")
        print(f"Geolocations: {len(geolocations)}")
        print(f"Locations: {len(locations)}")
        print(f"Aggregators: {len(aggregators)}")
        print(f"Keywords: {len(keywords)}")
        print(f"People: {len(people)}")
        print(f"Jobs: {len(jobs)}")
        print(f"Files: {len(files)}")
        print(f"Interviews: {len(interviews)}")
        print(f"Speculative Applications: {len(speculative_applications)}")
        print(f"Service Logs: {len(service_logs)}")
        print(f"Job Alert Emails: {len(alert_emails)}")
        print(f"Scraped Jobs: {len(scraped_jobs)}")
        print(f"Job Application Updates: {len(job_application_updates)}")
        print(f"Platform Stats: {len(platform_stats)}")
        print(f"EIS Service Errors: {len(eis_service_errors)}")
        print(f"Job Filters: {len(scraping_filters)}")
        print(f"User Qualifications: {len(user_qualifications)}")
        print(f"Job Rating Service Logs: {len(job_rating_service_logs)}")
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
