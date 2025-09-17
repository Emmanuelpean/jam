import app.eis.models as eis_models
from app import models, utils
from tests.utils.table_data import (
    USER_DATA,
    SETTINGS_DATA,
    COMPANY_DATA,
    LOCATION_DATA,
    AGGREGATOR_DATA,
    KEYWORD_DATA,
    PERSON_DATA,
    JOB_DATA,
    add_mappings,
    JOB_KEYWORD_MAPPINGS,
    JOB_CONTACT_MAPPINGS,
    FILE_DATA,
    INTERVIEW_DATA,
    INTERVIEW_INTERVIEWER_MAPPINGS,
    JOB_ALERT_EMAIL_DATA,
    JOB_SCRAPED_DATA,
    EMAIL_SCRAPEDJOB_MAPPINGS,
    SERVICE_LOG_DATA,
    JOB_APPLICATION_UPDATE_DATA,
)


def create_settings(db) -> list[models.Setting]:
    """Create sample settings"""

    print("Creating settings...")
    # noinspection PyArgumentList
    settings = [models.Setting(**data) for data in SETTINGS_DATA]
    db.add_all(settings)
    db.commit()
    return db.query(models.Setting).all()


def create_users(db) -> list[models.User]:
    """Create sample users and return them with non-hashed passwords but with database IDs"""

    print("Creating users...")
    users_hash = []
    original_passwords = []

    for user_data in USER_DATA:
        user_dict = user_data.copy()
        original_passwords.append(user_dict["password"])  # Store original password
        user_dict["password"] = utils.hash_password(user_dict["password"])
        # noinspection PyArgumentList
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
        # noinspection PyArgumentList
        new_user = models.User(**user_dict)
        result_users.append(new_user)

    return result_users


def create_companies(db) -> list[models.Company]:
    """Create sample companies"""

    print("Creating companies...")
    # noinspection PyArgumentList
    companies = [models.Company(**company) for company in COMPANY_DATA]
    db.add_all(companies)
    db.commit()
    return db.query(models.Company).all()


def create_locations(db) -> list[models.Location]:
    """Create sample locations"""

    print("Creating locations...")
    # noinspection PyArgumentList
    locations = [models.Location(**location) for location in LOCATION_DATA]
    db.add_all(locations)
    db.commit()
    return db.query(models.Location).all()


def create_aggregators(db) -> list[models.Aggregator]:
    """Create sample aggregators"""

    print("Creating aggregators...")
    # noinspection PyArgumentList
    aggregators = [models.Aggregator(**aggregator) for aggregator in AGGREGATOR_DATA]
    db.add_all(aggregators)
    db.commit()
    return db.query(models.Aggregator).all()


def create_keywords(db) -> list[models.Keyword]:
    """Create sample keywords"""

    print("Creating keywords...")
    # noinspection PyArgumentList
    keywords = [models.Keyword(**keyword) for keyword in KEYWORD_DATA]
    db.add_all(keywords)
    db.commit()
    return db.query(models.Keyword).all()


def create_people(db) -> list[models.Person]:
    """Create sample people"""

    print("Creating people...")
    # noinspection PyArgumentList
    persons = [models.Person(**person) for person in PERSON_DATA]
    db.add_all(persons)
    db.commit()
    return db.query(models.Person).all()


def create_jobs(db, keywords, persons) -> list[models.Job]:
    """Create sample jobs"""

    print("Creating jobs...")
    # noinspection PyArgumentList
    jobs = [models.Job(**job) for job in JOB_DATA]

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
    return db.query(models.Job).all()


def create_files(db) -> list[models.File]:
    """Create sample files (CVs and cover letters)"""

    print("Creating files...")
    # noinspection PyArgumentList
    files = [models.File(**file) for file in FILE_DATA]
    db.add_all(files)
    db.commit()
    return db.query(models.File).all()


def create_interviews(db, persons) -> list[models.Interview]:
    """Create sample interviews"""

    print("Creating interviews...")
    # noinspection PyArgumentList
    interviews = [models.Interview(**interview) for interview in INTERVIEW_DATA]

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
    return db.query(models.Interview).all()


def create_job_alert_emails(db) -> list[eis_models.JobAlertEmail]:
    """Create sample job alert emails"""

    print("Creating job alert emails...")
    # noinspection PyArgumentList
    emails = [eis_models.JobAlertEmail(**email) for email in JOB_ALERT_EMAIL_DATA]
    db.add_all(emails)
    db.commit()
    return db.query(eis_models.JobAlertEmail).all()


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
    return db.query(eis_models.ScrapedJob).all()


def create_service_logs(db) -> list[eis_models.EisServiceLog]:
    """Create sample service logs"""

    print("Creating service logs...")
    # noinspection PyArgumentList
    logs = [eis_models.EisServiceLog(**log) for log in SERVICE_LOG_DATA]
    db.add_all(logs)
    db.commit()
    return db.query(eis_models.EisServiceLog).all()


def create_job_application_updates(db) -> list[models.JobApplicationUpdate]:
    """Create sample job application updates"""

    print("Creating job application updates...")
    # noinspection PyArgumentList
    updates = [models.JobApplicationUpdate(**update) for update in JOB_APPLICATION_UPDATE_DATA]
    db.add_all(updates)
    db.commit()
    return db.query(models.JobApplicationUpdate).all()
