"""Functions for creating data table test data (companies, jobs, interviews, etc.)."""

from app import models
from tests.utils.create_data.utils import create_db_entries, override_properties
from tests.utils.test_data import data_tables
from tests.utils.test_data import utils as test_data_utils


def create_keywords(db, users: list[models.User]) -> list[models.Keyword]:
    """Create sample keywords"""

    data = override_properties(data_tables.KEYWORD_DATA, ("owner_id", users))
    print(f"Creating {len(data)} Keywords...")
    return create_db_entries(db, models.Keyword, data)


def create_aggregators(db, users: list[models.User]) -> list[models.Aggregator]:
    """Create sample aggregators"""

    data = override_properties(data_tables.AGGREGATOR_DATA, ("owner_id", users))
    print(f"Creating {len(data)} Aggregators...")
    return create_db_entries(db, models.Aggregator, data)


def create_companies(db, users: list[models.User]) -> list[models.Company]:
    """Create sample companies"""

    data = override_properties(data_tables.COMPANY_DATA, ("owner_id", users))
    print(f"Creating {len(data)} Companies...")
    return create_db_entries(db, models.Company, data)


def create_locations(db, users: list[models.User]) -> list[models.Location]:
    """Create sample locations"""

    data = override_properties(data_tables.LOCATION_DATA, ("owner_id", users))
    print(f"Creating {len(data)} Locations...")
    return create_db_entries(db, models.Location, data)


def create_geolocations(db) -> list[models.Geolocation]:
    """Create sample geolocations"""

    data = data_tables.GEOLOCATION_DATA
    print(f"Creating {len(data)} Geolocations...")
    return create_db_entries(db, models.Geolocation, data)


def create_people(
    db,
    users: list[models.User],
    companies: list[models.Company],
    data: list[dict] | None = None,
) -> list[models.Person]:
    """Create sample people"""

    if not data:
        data = data_tables.PERSON_DATA
    data = override_properties(data, ("owner_id", users), ("company_id", companies))
    print(f"Creating {len(data)} People...")
    return create_db_entries(db, models.Person, data)


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

    if job_data is None:
        job_data = data_tables.JOB_DATA
    data = override_properties(
        job_data,
        ("owner_id", users),
        ("company_id", companies),
        ("location_id", locations),
        ("source_id", aggregators),
        ("application_aggregator_id", aggregators),
        ("cv_id", files),
        ("cover_letter_id", files),
    )
    print(f"Creating {len(data)} Jobs...")
    jobs = create_db_entries(db, models.Job, data)

    # Add job/keyword mapping
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

    # Add job/contact mapping
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

    db.commit()
    return jobs


def create_files(db, users: list[models.User]) -> list[models.File]:
    """Create sample files (CVs and cover letters)"""

    data = override_properties(data_tables.FILE_DATA, ("owner_id", users))
    print(f"Creating {len(data)} Files...")
    return create_db_entries(db, models.File, data)


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

    if interview_data is None:
        interview_data = data_tables.INTERVIEW_DATA
    data = override_properties(interview_data, ("owner_id", users), ("location_id", locations), ("job_id", jobs))
    print(f"Creating {len(data)} Interviews...")
    interviews = create_db_entries(db, models.Interview, data)

    # Add interview/interviewer mapping
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

    db.commit()
    return interviews


def create_job_application_updates(
    db,
    users: list[models.User],
    jobs: list[models.Job],
    update_data: list[dict] | None = None,
) -> list[models.JobApplicationUpdate]:
    """Create sample job application updates"""

    if update_data is None:
        update_data = data_tables.JOB_APPLICATION_UPDATE_DATA
    data = override_properties(update_data, ("owner_id", users), ("job_id", jobs))
    print(f"Creating {len(data)} Job Application Updates...")
    return create_db_entries(db, models.JobApplicationUpdate, data)


def create_speculative_applications(
    db,
    users: list[models.User],
    persons: list[models.Person],
):
    """Create sample speculative applications"""

    data = override_properties(data_tables.SPECULATIVE_APPLICATION_DATA, ("owner_id", users))
    print(f"Creating {len(data)} Speculative Applications...")
    applications = create_db_entries(db, models.SpeculativeApplication, data)

    # Add Application/Contact mapping
    test_data_utils.add_mappings(
        primary_data=applications,
        secondary_data=persons,
        mapping_data=data_tables.SPECULATIVE_APPLICATION_CONTACTS_MAPPING,
        primary_key="speculative_application_id",
        secondary_key="contact_ids",
        relationship_attr="contacts",
    )
    db.commit()
    return applications
