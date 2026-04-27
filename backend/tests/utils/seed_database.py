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
    create_companies,
    create_people,
    create_jobs,
    create_files,
    create_interviews,
    create_job_application_updates,
    create_speculative_applications,
)
from tests.utils.create_data.job_rating import (
    create_job_rating_service_logs,
    create_job_ratings,
)
from tests.utils.create_data.job_scraping import (
    create_job_scraping_service_logs,
    create_job_scraping_platform_stats,
    create_job_scraping_service_errors,
    create_job_alert_emails,
    create_scraping_filters,
    create_scraping_favourite_filters,
    create_scraped_jobs,
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


def create_database_data(db, includes=None, excludes=None, **kwargs) -> None:
    """Create sample data for the database
    :param db: database session
    :param includes: list of tables to include (if None, include all)
    :param excludes: list of tables to exclude (if None, exclude none)
    :param kwargs: pre-created entities to use instead of generating (e.g. users=my_users)"""

    def should_create(table_name: str) -> bool:
        """Check if a table should be created based on includes/excludes"""
        if excludes and table_name in excludes:
            return False
        if includes and table_name not in includes:
            return False
        return True

    # Core dependencies (always needed)
    if "users" in kwargs:
        users = kwargs["users"]
    elif should_create("users"):
        users = create_users(db, None, 12)
    else:
        users = None

    if should_create("settings") and "settings" not in kwargs:
        create_settings(db)

    if "ai_prompts" in kwargs:
        ai_prompts = kwargs["ai_prompts"]
    elif should_create("ai_prompts"):
        ai_prompts = create_ai_prompts(db)
    else:
        ai_prompts = None

    # Table data
    if "keywords" in kwargs:
        keywords = kwargs["keywords"]
    elif should_create("keywords") and users:
        keywords = create_keywords(db, users)
    else:
        keywords = None

    if "aggregators" in kwargs:
        aggregators = kwargs["aggregators"]
    elif should_create("aggregators") and users:
        aggregators = create_aggregators(db, users)
    else:
        aggregators = None

    if "geolocations" in kwargs:
        geolocations = kwargs["geolocations"]
    elif should_create("geolocations"):
        geolocations = create_geolocations(db)
    else:
        geolocations = None

    if "companies" in kwargs:
        companies = kwargs["companies"]
    elif should_create("companies") and users:
        companies = create_companies(db, users)
    else:
        companies = None

    if "people" in kwargs:
        people = kwargs["people"]
    elif should_create("people") and users and companies:
        people = create_people(db, users, companies)
    else:
        people = None

    if "files" in kwargs:
        files = kwargs["files"]
    elif should_create("files") and users:
        files = create_files(db, users)
    else:
        files = None

    if "jobs" in kwargs:
        jobs = kwargs["jobs"]
    elif should_create("jobs") and all([keywords, people, users, companies, aggregators, files, geolocations]):
        jobs = create_jobs(db, keywords, people, users, companies, aggregators, files, geolocations)
    else:
        jobs = None

    if should_create("interviews") and "interviews" not in kwargs and all([people, users, jobs, geolocations]):
        create_interviews(db, people, users, jobs, geolocations)

    if should_create("job_application_updates") and "job_application_updates" not in kwargs and users and jobs:
        create_job_application_updates(db, users, jobs)

    if "user_qualifications" in kwargs:
        user_qualifications = kwargs["user_qualifications"]
    elif should_create("user_qualifications") and users:
        user_qualifications = create_user_qualifications(db, users)
    else:
        user_qualifications = None

    if should_create("speculative_applications") and "speculative_applications" not in kwargs and users and people:
        create_speculative_applications(db, users, people)

    # Job Scraping data
    if "job_scraping_service_logs" in kwargs:
        service_logs = kwargs["job_scraping_service_logs"]
    elif should_create("job_scraping_service_logs"):
        service_logs = create_job_scraping_service_logs(db)
    else:
        service_logs = None

    if should_create("job_scraping_platform_stats") and "job_scraping_platform_stats" not in kwargs and service_logs:
        create_job_scraping_platform_stats(db, service_logs)

    if should_create("job_scraping_service_errors") and "job_scraping_service_errors" not in kwargs and service_logs:
        create_job_scraping_service_errors(db, service_logs)

    if "job_alert_emails" in kwargs:
        alert_emails = kwargs["job_alert_emails"]
    elif should_create("job_alert_emails") and users and service_logs:
        alert_emails = create_job_alert_emails(db, users, service_logs)
    else:
        alert_emails = None

    if "scraping_filters" in kwargs:
        scraping_filters = kwargs["scraping_filters"]
    elif should_create("scraping_filters") and users:
        scraping_filters = create_scraping_filters(db, users)
    else:
        scraping_filters = None

    if "scraping_favourite_filters" in kwargs:
        pass
    elif should_create("scraping_favourite_filters") and users:
        create_scraping_favourite_filters(db, users)

    if "scraped_jobs" in kwargs:
        scraped_jobs = kwargs["scraped_jobs"]
    elif should_create("scraped_jobs") and all([alert_emails, users, scraping_filters, geolocations]):
        scraped_jobs = create_scraped_jobs(db, alert_emails, users, scraping_filters, geolocations)
    else:
        scraped_jobs = None

    # Job Rating data
    if "job_rating_service_logs" in kwargs:
        job_rating_service_logs = kwargs["job_rating_service_logs"]
    elif should_create("job_rating_service_logs"):
        job_rating_service_logs = create_job_rating_service_logs(db)
    else:
        job_rating_service_logs = None

    if (
        should_create("job_ratings")
        and "job_ratings" not in kwargs
        and all([users, scraped_jobs, user_qualifications, job_rating_service_logs, ai_prompts])
    ):
        create_job_ratings(db, users, scraped_jobs, user_qualifications, job_rating_service_logs, ai_prompts)


def seed_database() -> None:
    """Main function to seed the database"""
    print("Starting database seeding...")

    # Reset the database
    reset_database(engine)

    # Create a database session
    db = session_local()

    try:
        create_database_data(db)

    except Exception as e:
        print(f"Error during seeding: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
