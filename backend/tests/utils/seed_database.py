"""
Database seeding script for development.
This script will drop all data and repopulate with hard-coded sample data.
"""

import os
import sys

from sqlalchemy import text, inspect

from app.database import engine, session_local, Base
from tests.utils.create_data import (
    create_users,
    create_companies,
    create_locations,
    create_aggregators,
    create_keywords,
    create_people,
    create_jobs,
    create_files,
    create_job_applications,
    create_interviews,
    create_job_alert_emails,
    create_scraped_jobs,
    create_service_logs,
)

sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def reset_database(db_engine) -> None:
    """Drop ALL tables in the database (including orphaned ones) and recreate from models"""
    print("Dropping ALL tables in the database...")

    with db_engine.connect() as conn:
        # Get the database inspector to find all existing tables
        inspector = inspect(db_engine)
        table_names = inspector.get_table_names()

        # For PostgreSQL: Drop tables with CASCADE to handle foreign key constraints
        for table_name in table_names:
            print(f"Dropping table: {table_name}")
            conn.execute(text(f'DROP TABLE IF EXISTS "{table_name}" CASCADE'))

        conn.commit()

    print("Creating all tables from models...")
    Base.metadata.create_all(bind=db_engine)
    print("Database reset complete - all tables deleted and recreated from models!")


def seed_database() -> None:
    """Main function to seed the database"""
    print("Starting database seeding...")

    # Reset the database
    reset_database(engine)

    # Create a database session
    db = session_local()

    try:
        # Create data in order of dependencies
        users = create_users(db)
        companies = create_companies(db)
        locations = create_locations(db)
        aggregators = create_aggregators(db)
        keywords = create_keywords(db)
        people = create_people(db)
        jobs = create_jobs(db, keywords, people)
        files = create_files(db)
        applications = create_job_applications(db)
        interviews = create_interviews(db, people)
        alert_emails = create_job_alert_emails(db)
        scraped_jobs = create_scraped_jobs(db, alert_emails)
        service_logs = create_service_logs(db)

        print("\n" + "=" * 50)
        print("DATABASE SEEDING COMPLETED SUCCESSFULLY!")
        print("=" * 50)
        print(f"Users: {len(users)}")
        print(f"Companies: {len(companies)}")
        print(f"Locations: {len(locations)}")
        print(f"Aggregators: {len(aggregators)}")
        print(f"Keywords: {len(keywords)}")
        print(f"People: {len(people)}")
        print(f"Jobs: {len(jobs)}")
        print(f"Files: {len(files)}")
        print(f"Job Applications: {len(applications)}")
        print(f"Interviews: {len(interviews)}")
        print(f"Job Alert Emails: {len(alert_emails)}")
        print(f"Scraped Jobs: {len(scraped_jobs)}")
        print(f"Service Logs: {len(service_logs)}")
        print("=" * 50)

    except Exception as e:
        print(f"Error during seeding: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
