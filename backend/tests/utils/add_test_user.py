"""
Database seeding script for development.
This script will drop all data and repopulate with hard-coded sample data.
"""

import os
import sys

from app.database import session_local
from tests.utils.create_data import (
    delete_user,
    create_users,
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
    create_service_logs,
    create_job_application_updates,
)

sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def seed_database() -> None:
    """Main function to seed the database"""
    print("Starting database seeding...")

    # Create a database session
    db = session_local()

    try:
        delete_user(db, "test_user@test.com")
        users = create_users(
            db,
            [
                {
                    "email": "test_user@test.com",
                    "password": "test_password",
                }
            ],
        )
        keywords = create_keywords(db, users)
        aggregators = create_aggregators(db, users)
        locations = create_locations(db, users)
        companies = create_companies(db, users)
        people = create_people(db, users, companies)
        files = create_files(db, users)
        jobs = create_jobs(db, keywords, people, users, companies, locations, aggregators, files)
        interviews = create_interviews(db, people, users, locations, jobs)
        job_application_updates = create_job_application_updates(db, users, jobs)
        service_logs = create_service_logs(db)
        alert_emails = create_job_alert_emails(db, users, service_logs)
        scraped_jobs = create_scraped_jobs(db, alert_emails, users)

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
        print(f"Interviews: {len(interviews)}")
        print(f"Job Application Updates: {len(job_application_updates)}")
        print(f"Service Logs: {len(service_logs)}")
        print(f"Job Alert Emails: {len(alert_emails)}")
        print(f"Scraped Jobs: {len(scraped_jobs)}")

        print("=" * 50)

    except Exception as e:
        print(f"Error during seeding: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
