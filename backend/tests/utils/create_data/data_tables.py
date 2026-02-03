"""Functions for creating data table test data (companies, jobs, interviews, etc.)."""

from app import models
from tests.utils.test_data import data_tables
from tests.utils.test_data import utils as test_data_utils
from tests.utils.create_data.utils import add_to_db, override_entries_properties


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
