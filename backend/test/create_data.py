import copy

from app import models, utils
from table_data import (
    USERS_DATA,
    COMPANIES_DATA,
    LOCATIONS_DATA,
    AGGREGATORS_DATA,
    KEYWORDS_DATA,
    PERSONS_DATA,
    JOBS_DATA,
    add_mappings,
    JOB_KEYWORD_MAPPINGS,
    JOB_CONTACT_MAPPINGS,
    FILES_DATA,
    JOB_APPLICATIONS_DATA,
    INTERVIEWS_DATA,
    INTERVIEW_INTERVIEWER_MAPPINGS,
)


def create_users(db):
    """Create sample users and return them with non-hashed passwords but with database IDs"""

    print("Creating users...")
    users_hash = []
    original_passwords = []

    for user_data in USERS_DATA:
        user_dict = user_data.copy()
        original_passwords.append(user_dict["password"])  # Store original password
        user_dict["password"] = utils.hash_password(user_dict["password"])
        users_hash.append(models.User(**user_dict))

    db.add_all(users_hash)
    db.commit()

    for user in users_hash:
        db.refresh(user)

    # Create new user objects that won't become detached with the original passwords and database attributes
    result_users = []
    for i, user in enumerate(users_hash):
        user_dict = {key: value for key, value in user.__dict__.items() if key != "_sa_instance_state"}
        user_dict["password"] = original_passwords[i]
        new_user = models.User(**user_dict)
        result_users.append(new_user)

    return result_users


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


def create_jobs(db, keywords, persons):
    """Create sample jobs"""

    print("Creating jobs...")
    jobs = [models.Job(**job) for job in JOBS_DATA]

    # Add keywords to jobs
    add_mappings(
        primary_data=jobs,
        secondary_data=keywords,
        mapping_data=JOB_KEYWORD_MAPPINGS,
        primary_key="job_id",
        secondary_key="keyword_ids",
        relationship_attr="keywords",
    )

    # Add contacts to jobs
    add_mappings(
        primary_data=jobs,
        secondary_data=persons,
        mapping_data=JOB_CONTACT_MAPPINGS,
        primary_key="job_id",
        secondary_key="person_ids",
        relationship_attr="contacts",
    )

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


def create_interviews(db, persons):
    """Create sample interviews"""

    print("Creating interviews...")
    interviews = [models.Interview(**interview) for interview in INTERVIEWS_DATA]

    # Add interviewers to interviews
    add_mappings(
        primary_data=interviews,
        secondary_data=persons,
        mapping_data=INTERVIEW_INTERVIEWER_MAPPINGS,
        primary_key="interview_id",
        secondary_key="person_ids",
        relationship_attr="interviewers",
    )

    db.add_all(interviews)
    db.commit()
    return interviews
