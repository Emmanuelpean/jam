"""
Database seeding script for development.
This script will drop all data and repopulate with hard-coded sample data.
"""

import os
import sys

from app.database import engine, SessionLocal, Base
from create_data import (
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
)

sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def reset_database():
    """Drop all tables and recreate them"""
    print("Dropping all tables...")
    Base.metadata.drop_all(bind=engine)
    print("Creating all tables...")
    Base.metadata.create_all(bind=engine)
    print("Database reset complete!")


def seed_database():
    """Main function to seed the database"""
    print("Starting database seeding...")

    # Reset the database
    reset_database()

    # Create a database session
    db = SessionLocal()

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
        print("=" * 50)

    except Exception as e:
        print(f"Error during seeding: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":

    seed_database()
