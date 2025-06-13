"""
Database seeding script for development.
This script will drop all data and repopulate with hard-coded sample data.
"""

import os
import sys

from app import models
from app.database import engine, SessionLocal, Base

from test.data import (
    USERS_DATA,
    COMPANIES_DATA,
    LOCATIONS_DATA,
    PERSONS_DATA,
    AGGREGATORS_DATA,
    KEYWORDS_DATA,
    FILES_DATA,
    JOBS_DATA,
    JOB_APPLICATIONS_DATA,
    INTERVIEWS_DATA,
    JOB_KEYWORD_MAPPINGS,
    JOB_CONTACT_MAPPINGS,
    INTERVIEW_INTERVIEWER_MAPPINGS,
)

sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def reset_database():
    """Drop all tables and recreate them"""
    print("Dropping all tables...")
    Base.metadata.drop_all(bind=engine)
    print("Creating all tables...")
    Base.metadata.create_all(bind=engine)
    print("Database reset complete!")


def create_users(db):
    """Create sample users"""

    print("Creating users...")
    users = [models.User(**user) for user in USERS_DATA]
    db.add_all(users)
    db.commit()
    return users


def create_companies(db):
    """Create sample companies"""

    print("Creating companies...")
    companies = [models.Company(**company) for company in COMPANIES_DATA]
    db.add_all(companies)
    db.commit()
    return companies


def create_locations(db):
    """Create sample locations"""

    print("Creating locations...")
    locations = [models.Location(**location) for location in LOCATIONS_DATA]
    db.add_all(locations)
    db.commit()
    return locations


def create_aggregators(db):
    """Create sample aggregators"""

    print("Creating aggregators...")
    aggregators = [models.Aggregator(**aggregator) for aggregator in AGGREGATORS_DATA]
    db.add_all(aggregators)
    db.commit()
    return aggregators


def create_keywords(db):
    """Create sample keywords"""

    print("Creating keywords...")
    keywords = [models.Keyword(**keyword) for keyword in KEYWORDS_DATA]
    db.add_all(keywords)
    db.commit()
    return keywords


def create_people(db):
    """Create sample people"""

    print("Creating people...")
    persons = [models.Person(**person) for person in PERSONS_DATA]
    db.add_all(persons)
    db.commit()
    return persons


def create_jobs(db):
    """Create sample jobs"""

    print("Creating jobs...")
    jobs = [models.Job(**job) for job in JOBS_DATA]

    # Add keywords to jobs
    for d in JOB_KEYWORD_MAPPINGS:
        jobs[d["job_id"]].keywords.append(d["keyword_ids"])

    # Add contacts to jobs (many-to-many relationship)
    for d in JOB_CONTACT_MAPPINGS:
        jobs[d["job_id"]].keywords.append(d["person_ids"])

    db.add_all(jobs)
    db.commit()
    return jobs


def create_files(db):
    """Create sample files (CVs and cover letters)"""

    print("Creating files...")
    files = [models.File(**file) for file in FILES_DATA]
    db.add_all(files)
    db.commit()
    return files


def create_job_applications(db):
    """Create sample job applications"""

    print("Creating job applications...")
    job_applications = [models.JobApplication(**job_application) for job_application in JOB_APPLICATIONS_DATA]
    db.add_all(job_applications)
    db.commit()
    return job_applications


def create_interviews(db):
    """Create sample interviews"""
    interviews = [models.Interview(**interview) for interview in INTERVIEWS_DATA]
    # Add interviewers to interviews using the many-to-many relationship
    for d in INTERVIEW_INTERVIEWER_MAPPINGS:
        interviews[d["interview_id"]].keywords.append(d["person_ids"])
    db.add_all(interviews)
    db.commit()
    return interviews


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
        companies = create_companies(db, users)
        locations = create_locations(db, users)
        aggregators = create_aggregators(db, users)
        keywords = create_keywords(db, users)
        people = create_people(db, users, companies)
        jobs = create_jobs(db, users, companies, locations)
        files = create_files(db, users)
        applications = create_job_applications(db, users, jobs, files)
        interviews = create_interviews(db, users, applications, locations)

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
