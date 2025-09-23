"""Functions for creating test data in the database"""

import copy
import random

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


def create_users(db, user_data: list[dict] = None) -> list[models.User]:
    """Create sample users and return them with non-hashed passwords but with database IDs"""

    print("Creating users...")
    users_hash = []
    original_passwords = []
    if not user_data:
        user_data = USER_DATA

    # Store the original password and hash it for database storage
    for user in user_data:
        user_dict = user.copy()
        original_passwords.append(user_dict["password"])  # Store original password
        user_dict["password"] = utils.hash_password(user_dict["password"])
        # noinspection PyArgumentList
        users_hash.append(models.User(**user_dict))

    users_hash = add_to_db(db, users_hash)

    # Create new user objects that won't become detached with the original passwords and database attributes
    result_users = []
    for i, user in enumerate(users_hash):
        user_dict = {key: value for key, value in user.__dict__.items() if key != "_sa_instance_state"}
        user_dict["password"] = original_passwords[i]
        # noinspection PyArgumentList
        new_user = models.User(**user_dict)
        result_users.append(new_user)

    return result_users


def delete_user(db, user_email: str) -> None:
    """Delete a user by email and return the deleted user
    :param db: database session
    :param user_email: user email address"""

    user = db.query(models.User).filter(models.User.email == user_email).first()
    if user:
        db.delete(user)
        db.commit()


def override_entries_properties(data: list[dict], *args) -> list[dict]:
    """Override the owner_id in a list of dictionaries
    :param data: list of model entries to override
    :param args: tuples of (key to override, list of models to get new IDs from)"""

    data = copy.deepcopy(data)
    for entry in data:
        for arg in args:
            key, values = arg
            if entry.get(key, None) is not None:
                try:
                    current_id = entry[key] - 1
                    new_id = values[current_id].id
                    entry[key] = new_id
                except IndexError:
                    data.remove(entry)
                    break
    return data


def add_to_db(db, items: list[models.CommonBase]) -> list:
    """Add a list of items to the database and commit"""

    db.add_all(items)
    db.commit()
    for item in items:
        db.refresh(item)
    return items


def create_keywords(db, users: list[models.User]) -> list[models.Keyword]:
    """Create sample keywords"""

    print("Creating keywords...")
    # noinspection PyArgumentList
    keywords = [
        models.Keyword(**keyword)
        for keyword in override_entries_properties(
            KEYWORD_DATA,
            ("owner_id", users),
        )
    ]
    return add_to_db(db, keywords)


def create_aggregators(db, users: list[models.User]) -> list[models.Aggregator]:
    """Create sample aggregators"""

    print("Creating aggregators...")
    # noinspection PyArgumentList
    aggregators = [
        models.Aggregator(**aggregator)
        for aggregator in override_entries_properties(
            AGGREGATOR_DATA,
            ("owner_id", users),
        )
    ]
    return add_to_db(db, aggregators)


def create_companies(db, users: list[models.User]) -> list[models.Company]:
    """Create sample companies"""

    print("Creating companies...")
    # noinspection PyArgumentList
    companies = [
        models.Company(**company)
        for company in override_entries_properties(
            COMPANY_DATA,
            ("owner_id", users),
        )
    ]
    return add_to_db(db, companies)


def create_locations(db, users: list[models.User]) -> list[models.Location]:
    """Create sample locations"""

    print("Creating locations...")
    # noinspection PyArgumentList
    locations = [
        models.Location(**location)
        for location in override_entries_properties(
            LOCATION_DATA,
            ("owner_id", users),
        )
    ]
    return add_to_db(db, locations)


def create_people(db, users: list[models.User], companies: list[models.Company]) -> list[models.Person]:
    """Create sample people"""

    print("Creating people...")
    # noinspection PyArgumentList
    persons = [
        models.Person(**person)
        for person in override_entries_properties(
            PERSON_DATA,
            ("owner_id", users),
            ("company_id", companies),
        )
    ]
    return add_to_db(db, persons)


def create_jobs(
    db,
    keywords,
    persons,
    users: list[models.User],
    companies: list[models.Company],
    locations: list[models.Location],
    aggregators: list[models.Aggregator],
    files: list[models.File],
) -> list[models.Job]:
    """Create sample jobs"""

    print("Creating jobs...")
    # noinspection PyArgumentList
    jobs = [
        models.Job(**job)
        for job in override_entries_properties(
            JOB_DATA,
            ("owner_id", users),
            ("company_id", companies),
            ("location_id", locations),
            ("source_id", aggregators),
            ("application_aggregator_id", aggregators),
            ("cv_id", files),
            ("cover_letter_id", files),
        )
    ]

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

    return add_to_db(db, jobs)


def create_files(db, users: list[models.User]) -> list[models.File]:
    """Create sample files (CVs and cover letters)"""

    print("Creating files...")
    # noinspection PyArgumentList
    files = [models.File(**file) for file in override_entries_properties(FILE_DATA, ("owner_id", users))]
    return add_to_db(db, files)


def create_interviews(
    db,
    persons,
    users: list[models.User],
    locations: list[models.Location],
    jobs: list[models.Job],
) -> list[models.Interview]:
    """Create sample interviews"""

    print("Creating interviews...")
    # noinspection PyArgumentList
    interviews = [
        models.Interview(**interview)
        for interview in override_entries_properties(
            INTERVIEW_DATA,
            ("owner_id", users),
            ("location_id", locations),
            ("job_id", jobs),
        )
    ]

    # Add interviewers to interviews
    add_mappings(
        primary_data=interviews,
        secondary_data=persons,
        mapping_data=INTERVIEW_INTERVIEWER_MAPPINGS,
        primary_key="interview_id",
        secondary_key="person_ids",
        relationship_attr="interviewers",
    )

    return add_to_db(db, interviews)


def create_job_application_updates(
    db,
    users: list[models.User],
    jobs: list[models.Job],
) -> list[models.JobApplicationUpdate]:
    """Create sample job application updates"""

    print("Creating job application updates...")
    # noinspection PyArgumentList
    updates = [
        models.JobApplicationUpdate(**update)
        for update in override_entries_properties(
            JOB_APPLICATION_UPDATE_DATA,
            ("owner_id", users),
            ("job_id", jobs),
        )
    ]

    return add_to_db(db, updates)


def create_job_alert_emails(
    db, users: list[models.User], service_logs: list[eis_models.EisServiceLog]
) -> list[eis_models.JobAlertEmail]:
    """Create sample job alert emails"""

    print("Creating job alert emails...")
    # noinspection PyArgumentList
    emails = [
        eis_models.JobAlertEmail(**email)
        for email in override_entries_properties(
            JOB_ALERT_EMAIL_DATA,
            ("owner_id", users),
            ("service_log_id", service_logs),
        )
    ]
    for email in emails:
        email.external_email_id += str(random.random())  # Ensure uniqueness

    return add_to_db(db, emails)


def create_scraped_jobs(db, emails, users: list[models.User]) -> list[eis_models.ScrapedJob]:
    """Create sample scraped jobs - some with scraped data, some without"""

    print("Creating scraped jobs...")
    # noinspection PyArgumentList
    scraped_jobs = [
        eis_models.ScrapedJob(**job_data)
        for job_data in override_entries_properties(
            JOB_SCRAPED_DATA,
            ("owner_id", users),
        )
    ]

    # Add email mappings to scraped jobs
    add_mappings(
        primary_data=emails,
        secondary_data=scraped_jobs,
        mapping_data=EMAIL_SCRAPEDJOB_MAPPINGS,
        primary_key="email_id",
        secondary_key="scraped_job_ids",
        relationship_attr="jobs",
    )

    return add_to_db(db, scraped_jobs)


def create_service_logs(db) -> list[eis_models.EisServiceLog]:
    """Create sample service logs"""

    print("Creating service logs...")
    # noinspection PyArgumentList
    logs = [eis_models.EisServiceLog(**log) for log in SERVICE_LOG_DATA]

    return add_to_db(db, logs)
