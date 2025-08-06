from app import models, utils
import app.eis.eis_models as eis_models
from tests.utils.table_data import (
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
    JOB_ALERT_EMAILS_DATA,
    JOB_SCRAPED_DATA,
    EMAIL_SCRAPEDJOB_MAPPINGS,
    SERVICE_LOGS_DATA,
)


def create_users(db) -> list[models.User]:
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


def create_companies(db) -> list[models.Company]:
    """Create sample companies"""

    print("Creating companies...")
    # noinspection PyArgumentList
    companies = [models.Company(**company) for company in COMPANIES_DATA]
    db.add_all(companies)
    db.commit()
    return companies


def create_locations(db) -> list[models.Location]:
    """Create sample locations"""

    print("Creating locations...")
    # noinspection PyArgumentList
    locations = [models.Location(**location) for location in LOCATIONS_DATA + [{"remote": True, "owner_id": 1}]]
    db.add_all(locations)
    db.commit()
    return locations[:-1]


def create_aggregators(db) -> list[models.Aggregator]:
    """Create sample aggregators"""

    print("Creating aggregators...")
    # noinspection PyArgumentList
    aggregators = [models.Aggregator(**aggregator) for aggregator in AGGREGATORS_DATA]
    db.add_all(aggregators)
    db.commit()
    return aggregators


def create_keywords(db) -> list[models.Keyword]:
    """Create sample keywords"""

    print("Creating keywords...")
    # noinspection PyArgumentList
    keywords = [models.Keyword(**keyword) for keyword in KEYWORDS_DATA]
    db.add_all(keywords)
    db.commit()
    return keywords


def create_people(db) -> list[models.Person]:
    """Create sample people"""

    print("Creating people...")
    # noinspection PyArgumentList
    persons = [models.Person(**person) for person in PERSONS_DATA]
    db.add_all(persons)
    db.commit()
    return persons


def create_jobs(db, keywords, persons) -> list[models.Job]:
    """Create sample jobs"""

    print("Creating jobs...")
    # noinspection PyArgumentList
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


def create_files(db) -> list[models.File]:
    """Create sample files (CVs and cover letters)"""

    print("Creating files...")
    # noinspection PyArgumentList
    files = [models.File(**file) for file in FILES_DATA]
    db.add_all(files)
    db.commit()
    return files


def create_job_applications(db) -> list[models.JobApplication]:
    """Create sample job applications"""

    print("Creating job applications...")
    # noinspection PyArgumentList
    job_applications = [models.JobApplication(**job_application) for job_application in JOB_APPLICATIONS_DATA]
    db.add_all(job_applications)
    db.commit()
    return job_applications


def create_interviews(db, persons) -> list[models.Interview]:
    """Create sample interviews"""

    print("Creating interviews...")
    # noinspection PyArgumentList
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


def create_job_alert_emails(db) -> list[eis_models.JobAlertEmail]:
    """Create sample job alert emails"""

    print("Creating job alert emails...")
    # noinspection PyArgumentList
    emails = [eis_models.JobAlertEmail(**email) for email in JOB_ALERT_EMAILS_DATA]
    db.add_all(emails)
    db.commit()
    return emails


def create_scraped_jobs(db, emails) -> list[eis_models.ScrapedJob]:
    """Create sample scraped jobs - some with scraped data, some without"""

    print("Creating scraped jobs...")
    # noinspection PyArgumentList
    scraped_jobs = [eis_models.ScrapedJob(**job_data) for job_data in JOB_SCRAPED_DATA]

    # Add email mappings to scraped jobs
    add_mappings(
        primary_data=emails,
        secondary_data=scraped_jobs,
        mapping_data=EMAIL_SCRAPEDJOB_MAPPINGS,
        primary_key="email_id",
        secondary_key="scraped_job_ids",
        relationship_attr="jobs",
    )

    db.add_all(scraped_jobs)
    db.commit()
    return scraped_jobs


def create_service_logs(db) -> list[eis_models.ServiceLog]:
    """Create sample service logs"""

    print("Creating service logs...")
    logs = [eis_models.ServiceLog(**log) for log in SERVICE_LOGS_DATA]
    db.add_all(logs)
    db.commit()
    return logs
