"""Functions for creating test data in the database"""

import copy
import random

from app import model_registry as models, utils
from tests.utils.test_data import basics
from tests.utils.test_data import data_tables
from tests.utils.test_data import job_rating_service
from tests.utils.test_data import job_scraping_service
from tests.utils.test_data import utils as test_data_utils


def create_settings(db) -> list[models.Setting]:
    """Create sample settings"""

    print("Creating settings...")
    # noinspection PyArgumentList
    settings = [models.Setting(**data) for data in basics.SETTINGS_DATA]
    db.add_all(settings)
    db.commit()
    return db.query(models.Setting).all()


def create_users(db, user_data: list[dict] | None = None, rounds=4) -> list[models.User]:
    """Create sample users and return them attached to the session"""

    print("Creating users...")
    users = []
    original_passwords = []
    if not user_data:
        user_data = basics.USER_DATA

    # Store the original password and hash it for database storage
    for user in user_data:
        user_dict = user.copy()
        original_passwords.append(user_dict["password"])  # Store original password
        user_dict["password"] = utils.hash_password(user_dict["password"], rounds)
        # noinspection PyArgumentList
        users.append(models.User(**user_dict))

    users = add_to_db(db, users)

    # Add the plain password as an attribute for test convenience
    for i, user in enumerate(users):
        user.plain_password = original_passwords[i]

    return users


def delete_user(db, user_email: str) -> None:
    """Delete a user by email and return the deleted user
    :param db: database session
    :param user_email: user email address"""

    user = db.query(models.User).filter(models.User.email == user_email).first()
    if user:
        db.delete(user)
        db.commit()


def create_user_qualifications(db, users) -> list[models.UserQualification]:
    """Create sample user qualifications"""

    print("Creating user qualifications...")
    # noinspection PyArgumentList
    keywords = [
        models.UserQualification(**kwargs)
        for kwargs in override_entries_properties(basics.USER_QUALIFICATION_DATA, ("owner_id", users))
    ]
    return add_to_db(db, keywords)


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
        for keyword in override_entries_properties(data_tables.KEYWORD_DATA, ("owner_id", users))
    ]
    return add_to_db(db, keywords)


def create_aggregators(db, users: list[models.User]) -> list[models.Aggregator]:
    """Create sample aggregators"""

    print("Creating aggregators...")
    # noinspection PyArgumentList
    aggregators = [
        models.Aggregator(**aggregator)
        for aggregator in override_entries_properties(data_tables.AGGREGATOR_DATA, ("owner_id", users))
    ]
    return add_to_db(db, aggregators)


def create_companies(db, users: list[models.User]) -> list[models.Company]:
    """Create sample companies"""

    print("Creating companies...")
    # noinspection PyArgumentList
    companies = [
        models.Company(**company)
        for company in override_entries_properties(data_tables.COMPANY_DATA, ("owner_id", users))
    ]
    return add_to_db(db, companies)


def create_locations(db, users: list[models.User]) -> list[models.Location]:
    """Create sample locations"""

    print("Creating locations...")
    # noinspection PyArgumentList
    locations = [
        models.Location(**location)
        for location in override_entries_properties(data_tables.LOCATION_DATA, ("owner_id", users))
    ]
    return add_to_db(db, locations)


def create_geolocations(db) -> list[models.Geolocation]:
    """Create sample geolocations"""

    print("Creating geolocations...")
    # noinspection PyArgumentList
    geolocations = [models.Geolocation(**geo) for geo in data_tables.GEOLOCATION_DATA]
    return add_to_db(db, geolocations)


def create_people(
    db,
    users: list[models.User],
    companies: list[models.Company],
    data: list[dict] | None = None,
) -> list[models.Person]:
    """Create sample people"""

    print("Creating people...")
    if not data:
        data = data_tables.PERSON_DATA
    # noinspection PyArgumentList
    persons = [
        models.Person(**person)
        for person in override_entries_properties(
            data,
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
    job_data: list[dict] | None = None,
    job_keyword_mappings: list[dict] | None = None,
    job_contact_mappings: list[dict] | None = None,
) -> list[models.Job]:
    """Create sample jobs"""

    print("Creating jobs...")
    if job_data is None:
        job_data = data_tables.JOB_DATA
    # noinspection PyArgumentList
    jobs = [
        models.Job(**job)
        for job in override_entries_properties(
            job_data,
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
    if job_keyword_mappings is None:
        job_keyword_mappings = data_tables.JOB_KEYWORD_MAPPINGS
    test_data_utils.add_mappings(
        primary_data=jobs,
        secondary_data=keywords,
        mapping_data=job_keyword_mappings,
        primary_key="job_id",
        secondary_key="keyword_ids",
        relationship_attr="keywords",
    )

    # Add contacts to jobs
    if job_contact_mappings is None:
        job_contact_mappings = data_tables.JOB_CONTACT_MAPPINGS
    test_data_utils.add_mappings(
        primary_data=jobs,
        secondary_data=persons,
        mapping_data=job_contact_mappings,
        primary_key="job_id",
        secondary_key="person_ids",
        relationship_attr="contacts",
    )

    return add_to_db(db, jobs)


def create_files(db, users: list[models.User]) -> list[models.File]:
    """Create sample files (CVs and cover letters)"""

    print("Creating files...")
    # noinspection PyArgumentList
    files = [models.File(**file) for file in override_entries_properties(data_tables.FILE_DATA, ("owner_id", users))]
    return add_to_db(db, files)


def create_interviews(
    db,
    persons,
    users: list[models.User],
    locations: list[models.Location],
    jobs: list[models.Job],
    interview_data: list[dict] | None = None,
    interview_interviewer_mappings: list[dict] | None = None,
) -> list[models.Interview]:
    """Create sample interviews"""

    print("Creating interviews...")
    if interview_data is None:
        interview_data = data_tables.INTERVIEW_DATA
    # noinspection PyArgumentList
    interviews = [
        models.Interview(**interview)
        for interview in override_entries_properties(
            interview_data,
            ("owner_id", users),
            ("location_id", locations),
            ("job_id", jobs),
        )
    ]

    # Add interviewers to interviews
    if interview_interviewer_mappings is None:
        interview_interviewer_mappings = data_tables.INTERVIEW_INTERVIEWER_MAPPINGS
    test_data_utils.add_mappings(
        primary_data=interviews,
        secondary_data=persons,
        mapping_data=interview_interviewer_mappings,
        primary_key="interview_id",
        secondary_key="person_ids",
        relationship_attr="interviewers",
    )

    return add_to_db(db, interviews)


def create_job_application_updates(
    db,
    users: list[models.User],
    jobs: list[models.Job],
    update_data: list[dict] | None = None,
) -> list[models.JobApplicationUpdate]:
    """Create sample job application updates"""

    print("Creating job application updates...")
    if update_data is None:
        update_data = data_tables.JOB_APPLICATION_UPDATE_DATA
    # noinspection PyArgumentList
    updates = [
        models.JobApplicationUpdate(**update)
        for update in override_entries_properties(
            update_data,
            ("owner_id", users),
            ("job_id", jobs),
        )
    ]

    return add_to_db(db, updates)


def create_speculative_applications(
    db,
    users: list[models.User],
    persons: list[models.Person],
):
    """Create sample speculative applications"""

    print("Creating speculative applications...")
    # noinspection PyArgumentList
    applications = [
        models.SpeculativeApplication(**data)
        for data in override_entries_properties(
            data_tables.SPECULATIVE_APPLICATION_DATA,
            ("owner_id", users),
        )
    ]

    test_data_utils.add_mappings(
        primary_data=applications,
        secondary_data=persons,
        mapping_data=data_tables.SPECULATIVE_APPLICATION_CONTACTS_MAPPING,
        primary_key="speculative_application_id",
        secondary_key="contact_ids",
        relationship_attr="contacts",
    )
    return add_to_db(db, applications)


# ------------------------------------------------ JOB SCRAPING SERVICE ------------------------------------------------


def create_job_alert_emails(
    db, users: list[models.User], service_logs: list[models.JobEmailScrapingServiceLog]
) -> list[models.JobEmail]:
    """Create sample job alert emails"""

    print("Creating job alert emails...")
    # noinspection PyArgumentList
    emails = [
        models.JobEmail(**email)
        for email in override_entries_properties(
            job_scraping_service.JOB_EMAIL_DATA,
            ("owner_id", users),
            ("service_log_id", service_logs),
        )
    ]
    for email in emails:
        email.external_email_id += str(random.random())  # Ensure uniqueness

    return add_to_db(db, emails)


def create_scraped_jobs(
    db, emails, users: list[models.User], filters: list[models.ScrapingFilter]
) -> list[models.ScrapedJob]:
    """Create sample scraped jobs - some with scraped data, some without"""

    print("Creating scraped jobs...")
    # noinspection PyArgumentList
    scraped_jobs = [
        models.ScrapedJob(**job_data)
        for job_data in override_entries_properties(
            job_scraping_service.SCRAPED_JOB_DATA,
            ("owner_id", users),
            ("service_log_id", emails),
            ("filter_id", filters),
        )
    ]

    # Add email mappings to scraped jobs
    test_data_utils.add_mappings(
        primary_data=emails,
        secondary_data=scraped_jobs,
        mapping_data=job_scraping_service.EMAIL_SCRAPEDJOB_MAPPINGS,
        primary_key="email_id",
        secondary_key="scraped_job_ids",
        relationship_attr="jobs",
    )

    return add_to_db(db, scraped_jobs)


def create_job_scraping_service_logs(db) -> list[models.JobEmailScrapingServiceLog]:
    """Create sample scraped job service logs"""

    print("Creating Job Scraping service logs...")
    # noinspection PyArgumentList
    logs = [models.JobEmailScrapingServiceLog(**log) for log in job_scraping_service.JOB_SCRAPING_SERVICE_LOG_DATA]

    return add_to_db(db, logs)


def create_job_scraping_platform_stats(db, service_logs) -> list[models.JobEmailScrapingPlatformStat]:
    """Create sample platform stats"""

    print("Creating platform stats...")
    # noinspection PyArgumentList
    stats = [
        models.JobEmailScrapingPlatformStat(**data)
        for data in override_entries_properties(
            job_scraping_service.JOB_SCRAPING_PLATFORM_STAT_DATA,
            ("service_log_id", service_logs),
        )
    ]

    return add_to_db(db, stats)


def create_job_scraping_service_errors(db, service_logs) -> list[models.JobEmailScrapingServiceError]:
    """Create sample EIS service errors"""

    print("Creating EIS service errors...")
    # noinspection PyArgumentList
    errors = [
        models.JobEmailScrapingServiceError(**data)
        for data in override_entries_properties(
            job_scraping_service.JOB_SCRAPING_SERVICE_ERROR_DATA,
            ("service_log_id", service_logs),
        )
    ]

    return add_to_db(db, errors)


def create_scraping_filters(db, users: list[models.User]) -> list[models.ScrapingFilter]:
    """Create sample job filters"""

    print("Creating job filters...")
    # noinspection PyArgumentList
    filters = [
        models.ScrapingFilter(**filter_data)
        for filter_data in override_entries_properties(
            job_scraping_service.SCRAPING_FILTER_DATA,
            ("owner_id", users),
        )
    ]
    return add_to_db(db, filters)


# ----------------------------------------------- JOB RATING SERVICE LOGS ----------------------------------------------


def create_job_rating_service_logs(db) -> list[models.JobRatingServiceLog]:
    """Create sample scraped job service logs"""

    print("Creating Job Rating service logs...")
    # noinspection PyArgumentList
    logs = [models.JobRatingServiceLog(**log) for log in job_rating_service.JOB_RATING_SERVICE_LOG_DATA]

    return add_to_db(db, logs)


def create_job_ratings(db, users, use_qualifications, scraped_jobs, service_logs) -> list[models.JobRating]:
    """Create sample job ratings"""

    print("Creating job ratings...")
    # noinspection PyArgumentList
    keywords = [
        models.JobRating(**kwargs)
        for kwargs in override_entries_properties(
            job_rating_service.JOB_RATING_DATA,
            ("owner_id", users),
            ("job_id", scraped_jobs),
            ("user_qualification_id", use_qualifications),
            ("service_log_id", service_logs),
        )
    ]
    return add_to_db(db, keywords)
