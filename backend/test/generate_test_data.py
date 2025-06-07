# backend/seed_database.py
"""
Database seeding script for development.
This script will drop all data and repopulate with hard-coded sample data.
"""

import os
import sys
from datetime import datetime

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import engine, SessionLocal, Base
from app.models import User, Person, Company, Job, Location, Aggregator, Interview, JobApplication, Keyword


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
    users_data = [
        {
            "email": "emmanuel.pean@gmail.com",
            "password": "$2b$12$Dwf3QPkI2SSbcXkqw3gxkOTr9WZxVjSEkBfOLR4KuzW9zX/xfBjmW",
        },
        {"email": "jane.smith@example.com", "password": "$2b$12$hashed_password_here"},
        {"email": "mike.johnson@example.com", "password": "$2b$12$hashed_password_here"},
        {"email": "sarah.wilson@example.com", "password": "$2b$12$hashed_password_here"},
        {"email": "admin@example.com", "password": "$2b$12$hashed_password_here"},
    ]

    users = []
    for user_data in users_data:
        user = User(**user_data)
        users.append(user)
        db.add(user)

    db.commit()
    print(f"Created {len(users)} users")
    return users


def create_companies(db, users):
    """Create sample companies"""
    print("Creating companies...")
    companies_data = [
        {
            "name": "Google",
            "description": "Global technology company specializing in Internet-related services and products",
            "url": "https://google.com",
            "owner_id": users[0].id,
        },
        {
            "name": "Microsoft",
            "description": "Multinational technology corporation developing computer software, consumer electronics, and personal computers",
            "url": "https://microsoft.com",
            "owner_id": users[0].id,
        },
        {
            "name": "Apple",
            "description": "American multinational technology company that designs and develops consumer electronics, computer software, and online services",
            "url": "https://apple.com",
            "owner_id": users[0].id,
        },
        {
            "name": "Meta",
            "description": "Social technology company that builds tools to help people connect, find communities, and grow businesses",
            "url": "https://meta.com",
            "owner_id": users[0].id,
        },
        {
            "name": "Amazon",
            "description": "Multinational technology company focusing on e-commerce, cloud computing, digital streaming, and artificial intelligence",
            "url": "https://amazon.com",
            "owner_id": users[0].id,
        },
    ]

    companies = []
    for company_data in companies_data:
        company = Company(**company_data)
        companies.append(company)
        db.add(company)

    db.commit()
    print(f"Created {len(companies)} companies")
    return companies


def create_locations(db, users):
    """Create sample locations"""
    print("Creating locations...")
    locations_data = [
        {
            "postcode": "94043",
            "city": "Mountain View",
            "country": "United States",
            "remote": False,
            "owner_id": users[0].id,
        },
        {"postcode": "98052", "city": "Redmond", "country": "United States", "remote": False, "owner_id": users[0].id},
        {"postcode": "10001", "city": "New York", "country": "United States", "remote": False, "owner_id": users[0].id},
        {
            "postcode": "SW1A 1AA",
            "city": "London",
            "country": "United Kingdom",
            "remote": False,
            "owner_id": users[0].id,
        },
        {"postcode": None, "city": "Remote", "country": "Global", "remote": True, "owner_id": users[0].id},
    ]

    locations = []
    for location_data in locations_data:
        location = Location(**location_data)
        locations.append(location)
        db.add(location)

    db.commit()
    print(f"Created {len(locations)} locations")
    return locations


def create_aggregators(db, users):
    """Create sample aggregators"""
    print("Creating aggregators...")
    aggregators_data = [
        {"name": "LinkedIn", "url": "https://linkedin.com/jobs", "owner_id": users[0].id},
        {"name": "Indeed", "url": "https://indeed.com", "owner_id": users[0].id},
        {"name": "Glassdoor", "url": "https://glassdoor.com", "owner_id": users[0].id},
        {"name": "AngelList", "url": "https://angel.co", "owner_id": users[0].id},
        {"name": "Stack Overflow Jobs", "url": "https://stackoverflow.com/jobs", "owner_id": users[0].id},
    ]

    aggregators = []
    for aggregator_data in aggregators_data:
        aggregator = Aggregator(**aggregator_data)
        aggregators.append(aggregator)
        db.add(aggregator)

    db.commit()
    print(f"Created {len(aggregators)} aggregators")
    return aggregators


def create_keywords(db, users):
    """Create sample keywords"""
    print("Creating keywords...")
    keywords_data = [
        {"name": "Python", "owner_id": users[0].id},
        {"name": "JavaScript", "owner_id": users[0].id},
        {"name": "React", "owner_id": users[0].id},
        {"name": "Node.js", "owner_id": users[0].id},
        {"name": "AWS", "owner_id": users[0].id},
    ]

    keywords = []
    for keyword_data in keywords_data:
        keyword = Keyword(**keyword_data)
        keywords.append(keyword)
        db.add(keyword)

    db.commit()
    print(f"Created {len(keywords)} keywords")
    return keywords


def create_people(db, users, companies):
    """Create sample people"""
    print("Creating people...")
    people_data = [
        {
            "first_name": "John",
            "last_name": "Smith",
            "email": "john.smith@google.com",
            "phone": "+1-555-0101",
            "linkedin_url": "https://linkedin.com/in/johnsmith",
            "company_id": companies[0].id,
            "owner_id": users[0].id,
        },
        {
            "first_name": "Emily",
            "last_name": "Johnson",
            "email": "emily.johnson@microsoft.com",
            "phone": "+1-555-0102",
            "linkedin_url": "https://linkedin.com/in/emilyjohnson",
            "company_id": companies[1].id,
            "owner_id": users[0].id,
        },
        {
            "first_name": "Michael",
            "last_name": "Brown",
            "email": "michael.brown@apple.com",
            "phone": "+1-555-0103",
            "linkedin_url": "https://linkedin.com/in/michaelbrown",
            "company_id": companies[2].id,
            "owner_id": users[0].id,
        },
        {
            "first_name": "Sarah",
            "last_name": "Davis",
            "email": "sarah.davis@meta.com",
            "phone": "+1-555-0104",
            "linkedin_url": "https://linkedin.com/in/sarahdavis",
            "company_id": companies[3].id,
            "owner_id": users[0].id,
        },
        {
            "first_name": "David",
            "last_name": "Wilson",
            "email": "david.wilson@amazon.com",
            "phone": "+1-555-0105",
            "linkedin_url": "https://linkedin.com/in/davidwilson",
            "company_id": companies[4].id,
            "owner_id": users[0].id,
        },
    ]

    people = []
    for person_data in people_data:
        person = Person(**person_data)
        people.append(person)
        db.add(person)

    db.commit()
    print(f"Created {len(people)} people")
    return people


def create_jobs(db, users, companies, locations):
    """Create sample jobs"""
    print("Creating jobs...")
    jobs_data = [
        {
            "title": "Senior Software Engineer",
            "description": "We are looking for a senior software engineer to join our team and work on large-scale distributed systems. You will be responsible for designing, developing, and maintaining high-performance applications.",
            "salary_min": 150000.0,
            "salary_max": 200000.0,
            "url": "https://careers.google.com/jobs/123456",
            "personal_rating": 9,
            "company_id": companies[0].id,
            "location_id": locations[0].id,
            "owner_id": users[0].id,
        },
        {
            "title": "Frontend Developer",
            "description": "Join our frontend team to build amazing user experiences with React and TypeScript. You will work closely with designers and backend engineers to create responsive web applications.",
            "salary_min": 120000.0,
            "salary_max": 160000.0,
            "url": "https://careers.microsoft.com/jobs/234567",
            "personal_rating": 8,
            "company_id": companies[1].id,
            "location_id": locations[1].id,
            "owner_id": users[0].id,
        },
        {
            "title": "Full Stack Developer",
            "description": "We are seeking a full stack developer to work on both frontend and backend systems. Experience with Node.js, React, and cloud platforms is required.",
            "salary_min": 130000.0,
            "salary_max": 170000.0,
            "url": "https://jobs.apple.com/en-us/details/345678",
            "personal_rating": 7,
            "company_id": companies[2].id,
            "location_id": locations[2].id,
            "owner_id": users[0].id,
        },
        {
            "title": "DevOps Engineer",
            "description": "Join our infrastructure team to help scale our platform. You will work with Kubernetes, AWS, and CI/CD pipelines to ensure reliable deployments.",
            "salary_min": 140000.0,
            "salary_max": 180000.0,
            "url": "https://www.metacareers.com/jobs/456789",
            "personal_rating": 8,
            "company_id": companies[3].id,
            "location_id": locations[3].id,
            "owner_id": users[0].id,
        },
        {
            "title": "Data Scientist",
            "description": "We are looking for a data scientist to help us make data-driven decisions. You will work with machine learning models and large datasets to extract insights.",
            "salary_min": 135000.0,
            "salary_max": 175000.0,
            "url": "https://amazon.jobs/en/jobs/567890",
            "personal_rating": 6,
            "company_id": companies[4].id,
            "location_id": locations[4].id,
            "owner_id": users[0].id,
        },
    ]

    jobs = []
    for job_data in jobs_data:
        job = Job(**job_data)
        jobs.append(job)
        db.add(job)

    db.commit()
    print(f"Created {len(jobs)} jobs")
    return jobs


def create_job_applications(db, users, jobs):
    """Create sample job applications"""
    print("Creating job applications...")
    applications_data = [
        {
            "date": datetime(2024, 1, 15, 10, 30),
            "url": "https://careers.google.com/applications/12345",
            "job_id": jobs[0].id,
            "rejected": False,
            "note": "Applied through company website. Waiting for response.",
            "owner_id": users[0].id,
        },
        {
            "date": datetime(2024, 1, 20, 14, 15),
            "url": "https://careers.microsoft.com/applications/23456",
            "job_id": jobs[1].id,
            "rejected": None,
            "note": "Applied via LinkedIn. Got confirmation email.",
            "owner_id": users[0].id,
        },
        {
            "date": datetime(2024, 1, 25, 9, 45),
            "url": "https://jobs.apple.com/applications/34567",
            "job_id": jobs[2].id,
            "rejected": False,
            "note": "Submitted application with portfolio. Fingers crossed!",
            "owner_id": users[0].id,
        },
        {
            "date": datetime(2024, 2, 1, 16, 20),
            "url": "https://metacareers.com/applications/45678",
            "job_id": jobs[3].id,
            "rejected": True,
            "note": "Unfortunately rejected after initial screening.",
            "owner_id": users[0].id,
        },
        {
            "date": datetime(2024, 2, 5, 11, 10),
            "url": "https://amazon.jobs/applications/56789",
            "job_id": jobs[4].id,
            "rejected": None,
            "note": "Applied through recruiter referral. Hope it helps!",
            "owner_id": users[0].id,
        },
    ]

    applications = []
    for app_data in applications_data:
        application = JobApplication(**app_data)
        applications.append(application)
        db.add(application)

    db.commit()
    print(f"Created {len(applications)} job applications")
    return applications


def create_interviews(db, users, jobs, locations):
    """Create sample interviews"""
    print("Creating interviews...")
    interviews_data = [
        {
            "date": datetime(2024, 2, 20, 14, 0),
            "location_id": locations[0].id,
            "job_id": jobs[0].id,
            "note": "Technical interview with the engineering team. Prepare for coding questions.",
            "owner_id": users[0].id,
        },
        {
            "date": datetime(2024, 2, 22, 10, 30),
            "location_id": locations[4].id,  # Remote interview
            "job_id": jobs[1].id,
            "note": "Video call interview with hiring manager. Discuss experience and projects.",
            "owner_id": users[0].id,
        },
        {
            "date": datetime(2024, 2, 25, 15, 15),
            "location_id": locations[2].id,
            "job_id": jobs[2].id,
            "note": "On-site interview at NYC office. System design round.",
            "owner_id": users[0].id,
        },
        {
            "date": datetime(2024, 3, 1, 13, 45),
            "location_id": locations[4].id,  # Remote interview
            "job_id": jobs[3].id,
            "note": "Final round with VP of Engineering. Behavioral questions expected.",
            "owner_id": users[0].id,
        },
        {
            "date": datetime(2024, 3, 5, 11, 0),
            "location_id": locations[4].id,  # Remote interview
            "job_id": jobs[4].id,
            "note": "Data science case study presentation. 45 minutes allocated.",
            "owner_id": users[0].id,
        },
    ]

    interviews = []
    for interview_data in interviews_data:
        interview = Interview(**interview_data)
        interviews.append(interview)
        db.add(interview)

    db.commit()
    print(f"Created {len(interviews)} interviews")
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
        applications = create_job_applications(db, users, jobs)
        interviews = create_interviews(db, users, jobs, locations)

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
    # Check if user wants to proceed
    print("This will DELETE ALL DATA in the database and replace it with sample data.")
    confirm = input("Are you sure you want to continue? (yes/no): ")

    if confirm.lower() in ["yes", "y"]:
        seed_database()
    else:
        print("Seeding cancelled.")
