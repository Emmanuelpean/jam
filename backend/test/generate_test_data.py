"""
Database seeding script for development.
This script will drop all data and repopulate with hard-coded sample data.
"""

import os
import sys
from datetime import datetime

from app.database import engine, SessionLocal, Base
from app.models import User, Person, Company, Job, Location, Aggregator, Interview, JobApplication, Keyword, File

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
        {
            # Incomplete company - minimal data
            "name": "TechStartup Inc",
            "description": None,
            "url": None,
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
        {
            # Incomplete location - only city
            "postcode": None,
            "city": "Berlin",
            "country": None,
            "owner_id": users[0].id,
        },
        {
            # Incomplete location - only country
            "postcode": None,
            "city": None,
            "country": "Canada",
            "owner_id": users[0].id,
        },
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
        {"name": "Docker", "owner_id": users[0].id},
        {"name": "Kubernetes", "owner_id": users[0].id},
        {"name": "Machine Learning", "owner_id": users[0].id},
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
            "role": "Senior Engineering Manager",
            "company_id": companies[0].id,
            "owner_id": users[0].id,
        },
        {
            "first_name": "Emily",
            "last_name": "Johnson",
            "email": "emily.johnson@microsoft.com",
            "phone": "+1-555-0102",
            "linkedin_url": "https://linkedin.com/in/emilyjohnson",
            "role": "Product Manager",
            "company_id": companies[1].id,
            "owner_id": users[0].id,
        },
        {
            "first_name": "Michael",
            "last_name": "Brown",
            "email": "michael.brown@apple.com",
            "phone": "+1-555-0103",
            "linkedin_url": "https://linkedin.com/in/michaelbrown",
            "role": "Lead Developer",
            "company_id": companies[2].id,
            "owner_id": users[0].id,
        },
        {
            "first_name": "Sarah",
            "last_name": "Davis",
            "email": "sarah.davis@meta.com",
            "phone": "+1-555-0104",
            "linkedin_url": "https://linkedin.com/in/sarahdavis",
            "role": "DevOps Engineer",
            "company_id": companies[3].id,
            "owner_id": users[0].id,
        },
        {
            "first_name": "David",
            "last_name": "Wilson",
            "email": "david.wilson@amazon.com",
            "phone": "+1-555-0105",
            "linkedin_url": "https://linkedin.com/in/davidwilson",
            "role": "Data Science Manager",
            "company_id": companies[4].id,
            "owner_id": users[0].id,
        },
        {
            # Incomplete person - minimal data, no company
            "first_name": "Anonymous",
            "last_name": "Recruiter",
            "email": None,
            "phone": None,
            "linkedin_url": None,
            "role": None,
            "company_id": None,
            "owner_id": users[0].id,
        },
        {
            # Incomplete person - no contact details
            "first_name": "Jane",
            "last_name": "Doe",
            "email": None,
            "phone": None,
            "linkedin_url": None,
            "role": "HR Representative",
            "company_id": companies[5].id,
            "owner_id": users[0].id,
        },
        {
            # Incomplete person - only basic info
            "first_name": "Tech",
            "last_name": "Recruiter",
            "email": "recruiter@techstartup.com",
            "phone": None,
            "linkedin_url": None,
            "role": "Talent Acquisition",
            "company_id": companies[5].id,
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
            "personal_rating": 3,
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
            "personal_rating": 4,
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
            "personal_rating": 5,
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
            "personal_rating": 2,
            "company_id": companies[4].id,
            "location_id": locations[4].id,
            "owner_id": users[0].id,
        },
        {
            # Incomplete job - no company
            "title": "Backend Developer",
            "description": "Looking for a backend developer with Python experience.",
            "salary_min": None,
            "salary_max": None,
            "url": None,
            "personal_rating": None,
            "company_id": None,
            "location_id": locations[4].id,
            "owner_id": users[0].id,
        },
        {
            # Incomplete job - no location
            "title": "Software Engineer Intern",
            "description": "Summer internship opportunity for computer science students.",
            "salary_min": None,
            "salary_max": None,
            "url": "https://techstartup.com/careers/intern",
            "personal_rating": 3,
            "company_id": companies[5].id,
            "location_id": None,
            "owner_id": users[0].id,
        },
        {
            # Incomplete job - minimal information
            "title": "Developer Position",
            "description": None,
            "salary_min": None,
            "salary_max": None,
            "url": None,
            "personal_rating": None,
            "company_id": companies[5].id,
            "location_id": locations[5].id,
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


def create_files(db, users):
    """Create sample files (CVs and cover letters)"""
    print("Creating files...")

    # Sample file contents
    sample_cv_content = b"""John Doe - Software Engineer

EXPERIENCE:
- Senior Software Developer at TechCorp (2019-2024)
- Full Stack Developer at StartupXYZ (2017-2019)
- Junior Developer at WebSolutions (2015-2017)

SKILLS:
- Python, JavaScript, React, Node.js
- AWS, Docker, Kubernetes
- PostgreSQL, MongoDB
- Git, CI/CD, Agile methodologies

EDUCATION:
- B.S. Computer Science, University of Technology (2015)

CERTIFICATIONS:
- AWS Certified Solutions Architect
- Certified Kubernetes Administrator
"""

    sample_cover_letter_content = b"""Dear Hiring Manager,

I am writing to express my strong interest in the Software Engineer position at your company. With over 8 years of experience in full-stack development and a proven track record of delivering scalable solutions, I am excited about the opportunity to contribute to your team.

In my current role at TechCorp, I have:
- Led a team of 5 developers in building microservices architecture
- Implemented CI/CD pipelines that reduced deployment time by 60%
- Designed and developed RESTful APIs serving 1M+ requests daily
- Mentored junior developers and conducted code reviews

I am particularly drawn to your company's mission and would love to discuss how my experience with Python, React, and cloud technologies can help drive your projects forward.

Thank you for considering my application. I look forward to hearing from you.

Best regards,
John Doe
"""

    sample_portfolio_content = b"""John Doe - Portfolio

PROJECT 1: E-commerce Platform
- Built with React, Node.js, PostgreSQL
- Handles 10k+ daily transactions
- Implemented real-time inventory management
- GitHub: github.com/johndoe/ecommerce

PROJECT 2: Data Analytics Dashboard
- Python, Flask, D3.js visualization
- Processes 1TB+ data daily
- Real-time streaming with Apache Kafka
- Deployed on AWS with auto-scaling

PROJECT 3: Mobile App Backend
- RESTful API with Node.js and Express
- JWT authentication and rate limiting
- Integrated with payment gateways
- 99.9% uptime SLA achieved
"""

    files_data = [
        {
            "filename": "john_doe_cv_2024.pdf",
            "content": sample_cv_content,
            "type": "application/pdf",
            "size": len(sample_cv_content),
            "owner_id": users[0].id,
        },
        {
            "filename": "cover_letter_google.pdf",
            "content": sample_cover_letter_content,
            "type": "application/pdf",
            "size": len(sample_cover_letter_content),
            "owner_id": users[0].id,
        },
        {
            "filename": "cover_letter_microsoft.pdf",
            "content": sample_cover_letter_content,
            "type": "application/pdf",
            "size": len(sample_cover_letter_content),
            "owner_id": users[0].id,
        },
        {
            "filename": "john_doe_portfolio.pdf",
            "content": sample_portfolio_content,
            "type": "application/pdf",
            "size": len(sample_portfolio_content),
            "owner_id": users[0].id,
        },
        {
            "filename": "resume_v2.docx",
            "content": sample_cv_content,
            "type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "size": len(sample_cv_content),
            "owner_id": users[0].id,
        },
        {
            "filename": "technical_cover_letter.txt",
            "content": b"Brief cover letter for technical positions focusing on coding skills and experience.",
            "type": "text/plain",
            "size": 85,
            "owner_id": users[0].id,
        },
    ]

    files = []
    for file_data in files_data:
        file_obj = File(**file_data)
        files.append(file_obj)
        db.add(file_obj)

    db.commit()
    print(f"Created {len(files)} files")
    return files


def create_job_applications(db, users, jobs, files):
    """Create sample job applications"""
    print("Creating job applications...")

    applications_data = [
        {
            "date": datetime(2024, 1, 15, 10, 30),
            "url": "https://careers.google.com/applications/12345",
            "job_id": jobs[0].id,
            "status": "Applied",
            "note": "Applied through company website. Waiting for response.",
            "cv_id": files[0].id,  # john_doe_cv_2024.pdf
            "cover_letter_id": files[1].id,  # cover_letter_google.pdf
            "owner_id": users[0].id,
        },
        {
            "date": datetime(2024, 1, 20, 14, 15),
            "url": "https://careers.microsoft.com/applications/23456",
            "job_id": jobs[1].id,
            "status": "Interview",
            "note": "Applied via LinkedIn. Got confirmation email.",
            "cv_id": files[0].id,  # john_doe_cv_2024.pdf
            "cover_letter_id": files[2].id,  # cover_letter_microsoft.pdf
            "owner_id": users[0].id,
        },
        {
            "date": datetime(2024, 1, 25, 9, 45),
            "url": "https://jobs.apple.com/applications/34567",
            "job_id": jobs[2].id,
            "status": "Applied",
            "note": "Submitted application with portfolio. Fingers crossed!",
            "cv_id": files[3].id,  # john_doe_portfolio.pdf (used as CV)
            "cover_letter_id": files[5].id,  # technical_cover_letter.txt
            "owner_id": users[0].id,
        },
        {
            "date": datetime(2024, 2, 1, 16, 20),
            "url": "https://metacareers.com/applications/45678",
            "job_id": jobs[3].id,
            "status": "Rejected",
            "note": "Unfortunately rejected after initial screening.",
            "cv_id": files[4].id,  # resume_v2.docx
            "cover_letter_id": files[1].id,  # cover_letter_google.pdf (reused)
            "owner_id": users[0].id,
        },
        {
            "date": datetime(2024, 2, 5, 11, 10),
            "url": "https://amazon.jobs/applications/56789",
            "job_id": jobs[4].id,
            "status": "Applied",
            "note": "Applied through recruiter referral. Hope it helps!",
            "cv_id": files[0].id,  # john_doe_cv_2024.pdf
            "cover_letter_id": files[5].id,  # technical_cover_letter.txt
            "owner_id": users[0].id,
        },
        {
            # Application with only CV, no cover letter
            "date": datetime(2024, 2, 10, 13, 30),
            "url": None,
            "job_id": jobs[5].id,
            "status": "Applied",
            "note": "Quick application through company form. No cover letter required.",
            "cv_id": files[4].id,  # resume_v2.docx
            "cover_letter_id": None,  # No cover letter
            "owner_id": users[0].id,
        },
        {
            # Application with only cover letter, no CV
            "date": datetime(2024, 2, 12, 15, 45),
            "url": "https://techstartup.com/apply/67890",
            "job_id": jobs[6].id,
            "status": "Applied",
            "note": "Startup prefers cover letters over formal CVs.",
            "cv_id": None,  # No CV
            "cover_letter_id": files[2].id,  # cover_letter_microsoft.pdf
            "owner_id": users[0].id,
        },
        {
            # Minimal application - no files attached
            "date": datetime(2024, 2, 15, 11, 20),
            "url": None,
            "job_id": jobs[7].id,
            "status": "Applied",
            "note": "Applied through internal referral. Files sent separately.",
            "cv_id": None,  # No CV
            "cover_letter_id": None,  # No cover letter
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


def create_interviews(db, users, applications, locations):
    """Create sample interviews"""
    print("Creating interviews...")
    interviews_data = [
        {
            "date": datetime(2024, 2, 20, 14, 0),
            "location_id": locations[0].id,
            "jobapplication_id": applications[0].id,
            "note": "Technical interview with the engineering team. Prepare for coding questions.",
            "owner_id": users[0].id,
        },
        {
            "date": datetime(2024, 2, 22, 10, 30),
            "location_id": locations[4].id,  # Remote interview
            "jobapplication_id": applications[1].id,
            "note": "Video call interview with hiring manager. Discuss experience and projects.",
            "owner_id": users[0].id,
        },
        {
            "date": datetime(2024, 2, 25, 15, 15),
            "location_id": locations[2].id,
            "jobapplication_id": applications[2].id,
            "note": "On-site interview at NYC office. System design round.",
            "owner_id": users[0].id,
        },
        {
            "date": datetime(2024, 3, 1, 13, 45),
            "location_id": locations[4].id,  # Remote interview
            "jobapplication_id": applications[1].id,  # Same application as interview 2
            "note": "Final round with VP of Engineering. Behavioral questions expected.",
            "owner_id": users[0].id,
        },
        {
            "date": datetime(2024, 3, 5, 11, 0),
            "location_id": locations[4].id,  # Remote interview
            "jobapplication_id": applications[4].id,
            "note": "Data science case study presentation. 45 minutes allocated.",
            "owner_id": users[0].id,
        },
        {
            # Incomplete interview - no location specified
            "date": datetime(2024, 3, 10, 16, 0),
            "location_id": None,
            "jobapplication_id": applications[5].id,
            "note": "Phone screening with recruiter. Location TBD.",
            "owner_id": users[0].id,
        },
        {
            # Incomplete interview - minimal information
            "date": datetime(2024, 3, 15, 9, 0),
            "location_id": locations[6].id,  # Only country specified
            "jobapplication_id": applications[1].id,
            "note": None,
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


def assign_keywords_to_jobs(db, jobs, keywords):
    """Assign keywords to jobs (many-to-many)"""
    print("Assigning keywords to jobs...")

    # Assign specific keywords to each job
    keyword_assignments = [
        (jobs[0], [keywords[0], keywords[4]]),  # Senior Software Engineer: Python, AWS
        (jobs[1], [keywords[1], keywords[2]]),  # Frontend Developer: JavaScript, React
        (jobs[2], [keywords[0], keywords[1], keywords[3]]),  # Full Stack: Python, JavaScript, Node.js
        (jobs[3], [keywords[4], keywords[5], keywords[6]]),  # DevOps: AWS, Docker, Kubernetes
        (jobs[4], [keywords[0], keywords[7]]),  # Data Scientist: Python, Machine Learning
        (jobs[5], [keywords[0]]),  # Backend Developer: Python
        (jobs[6], [keywords[0], keywords[1]]),  # Intern: Python, JavaScript
        # jobs[7] gets no keywords (incomplete data)
    ]

    for job, job_keywords in keyword_assignments:
        job.keywords = job_keywords
        db.add(job)

    db.commit()
    print("Assigned keywords to jobs.")


def assign_interviewers_to_interviews(db, interviews, people):
    """Assign interviewers to interviews (many-to-many)"""
    print("Assigning interviewers to interviews...")

    # Assign specific interviewers to each interview
    interviewer_assignments = [
        (interviews[0], [people[0]]),  # John Smith
        (interviews[1], [people[1]]),  # Emily Johnson
        (interviews[2], [people[2], people[0]]),  # Michael Brown + John Smith
        (interviews[3], [people[1]]),  # Emily Johnson
        (interviews[4], [people[4]]),  # David Wilson
        (interviews[5], [people[5]]),  # Anonymous Recruiter
        # interviews[6] gets no interviewers (incomplete data)
    ]

    for interview, interview_people in interviewer_assignments:
        interview.interviewers = interview_people
        db.add(interview)

    db.commit()
    print("Assigned interviewers to interviews.")


def assign_contacts_to_jobs(db, jobs, people):
    """Assign contacts to jobs (many-to-many relationship)"""
    print("Assigning contacts to jobs...")

    # Assign specific contacts to each job
    contact_assignments = [
        (jobs[0], [people[0]]),  # Google job: John Smith
        (jobs[1], [people[1]]),  # Microsoft job: Emily Johnson
        (jobs[2], [people[2]]),  # Apple job: Michael Brown
        (jobs[3], [people[3]]),  # Meta job: Sarah Davis
        (jobs[4], [people[4]]),  # Amazon job: David Wilson
        (jobs[5], [people[5], people[7]]),  # Backend job: Anonymous Recruiter + Tech Recruiter
        (jobs[6], [people[6], people[7]]),  # Intern job: Jane Doe + Tech Recruiter
        # jobs[7] gets no contacts (incomplete data)
    ]

    for job, job_contacts in contact_assignments:
        job.contacts = job_contacts
        db.add(job)

    db.commit()
    print("Assigned contacts to jobs.")


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
        assign_keywords_to_jobs(db, jobs, keywords)
        assign_interviewers_to_interviews(db, interviews, people)
        assign_contacts_to_jobs(db, jobs, people)

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
