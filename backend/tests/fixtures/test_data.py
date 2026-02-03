"""Test data fixtures for various models."""

import datetime as dt

import pytest

from app import models
from tests.utils.create_data.core import create_settings, create_ai_prompts
from tests.utils.create_data.data_tables import (
    create_keywords,
    create_aggregators,
    create_geolocations,
    create_locations,
    create_companies,
    create_people,
    create_jobs,
    create_files,
    create_interviews,
    create_job_application_updates,
    create_speculative_applications,
)
from tests.utils.create_data.job_scraping import (
    create_scraped_jobs,
    create_job_scraping_service_logs,
    create_job_scraping_platform_stats,
    create_job_scraping_service_errors,
    create_job_alert_emails,
    create_scraping_filters,
)
from tests.utils.create_data.job_rating import (
    create_job_rating_service_logs,
    create_job_ratings,
)


def find_non_owned_entry(entries: list, owner_id: int) -> int:
    """Find an entry not owned by the specified owner_id."""
    for entry in entries:
        if entry.owner_id != owner_id:
            return entry.id
    raise AssertionError("No non-owned entry found")


# -------------------------------------------------------- OTHER -------------------------------------------------------


@pytest.fixture
def test_settings(session) -> list[models.Setting]:
    """Create test settings data"""
    return create_settings(session)


@pytest.fixture
def test_ai_prompts(session) -> tuple[models.AiSystemPrompt, models.AiJobPromptTemplate]:
    """Create test AI prompts for job rating"""
    return create_ai_prompts(session)


# ------------------------------------------------------ TEST DATA -----------------------------------------------------


@pytest.fixture
def test_keywords(session, test_users) -> list[models.Keyword]:
    """Create test keyword data"""
    return create_keywords(session, test_users)


@pytest.fixture
def test_aggregators(session, test_users) -> list[models.Aggregator]:
    """Create test aggregator data"""
    return create_aggregators(session, test_users)


@pytest.fixture
def test_geolocations(session) -> list[models.Geolocation]:
    """Create test geolocation data"""
    return create_geolocations(session)


@pytest.fixture
def test_locations(session, test_users, test_geolocations) -> list[models.Location]:
    """Create test location data"""
    return create_locations(session, test_users)


@pytest.fixture
def test_companies(session, test_users) -> list[models.Company]:
    """Create test company data"""
    return create_companies(session, test_users)


@pytest.fixture
def test_persons(session, test_users, test_companies) -> list[models.Person]:
    """Create test person data"""
    return create_people(session, test_users, test_companies)


@pytest.fixture
def persons_unauthorised_data(test_companies) -> tuple[list[dict], int]:
    """Create test person data with incorrect company_id for access control testing"""
    owner_id = 1
    company_id = find_non_owned_entry(test_companies, owner_id)
    return [{"first_name": "A", "last_name": "B", "company_id": company_id, "owner_id": owner_id}], owner_id


@pytest.fixture
def test_persons_unauthorised(
    session, test_users, test_companies, persons_unauthorised_data
) -> tuple[list[models.Person], int]:
    """Create test person data with incorrect company_id for access control testing"""
    data, owner_id = persons_unauthorised_data
    return create_people(session, test_users, test_companies, data), owner_id


@pytest.fixture
def test_files(session, test_users) -> list[models.File]:
    """Create test files for job applications"""
    return create_files(session, test_users)


@pytest.fixture
def test_jobs(
    session, test_users, test_companies, test_locations, test_keywords, test_persons, test_aggregators, test_files
) -> list[models.Job]:
    """Create test job data"""
    return create_jobs(
        session, test_keywords, test_persons, test_users, test_companies, test_locations, test_aggregators, test_files
    )


@pytest.fixture
def jobs_unauthorised_data(
    session, test_users, test_companies, test_locations, test_keywords, test_persons, test_aggregators, test_files
) -> tuple[list[dict], int, list[dict], list[dict]]:
    """Create test person data with incorrect company_id, location_id, keyword ids and person ids for access control testing"""
    owner_id = 1
    company_id = find_non_owned_entry(test_companies, owner_id)
    location_id = find_non_owned_entry(test_locations, owner_id)
    job_keyword_mapping = [{"job_id": 1, "keyword_ids": [find_non_owned_entry(test_keywords, owner_id)]}]
    job_contact_mapping = [{"job_id": 1, "person_ids": [find_non_owned_entry(test_persons, owner_id)]}]
    data = [
        {
            "title": "A",
            "company_id": company_id,
            "location_id": location_id,
            "owner_id": owner_id,
        }
    ]
    return data, owner_id, job_keyword_mapping, job_contact_mapping


@pytest.fixture
def test_jobs_unauthorised(
    session,
    test_users,
    test_companies,
    test_locations,
    test_keywords,
    test_persons,
    test_aggregators,
    test_files,
    jobs_unauthorised_data,
) -> tuple[list[models.Job], int]:
    """Create test person data with incorrect company_id, location_id, keyword ids and person ids for access control testing"""
    data, owner_id, job_keyword_mapping, job_contact_mapping = jobs_unauthorised_data
    jobs = create_jobs(
        session,
        test_keywords,
        test_persons,
        test_users,
        test_companies,
        test_locations,
        test_aggregators,
        test_files,
        data,
        job_keyword_mapping,
        job_contact_mapping,
    )
    return jobs, owner_id


@pytest.fixture
def test_interviews(session, test_users, test_jobs, test_locations, test_persons) -> list[models.Interview]:
    """Create test interview data"""
    return create_interviews(session, test_persons, test_users, test_locations, test_jobs)


@pytest.fixture
def interviews_unauthorised_data(
    session, test_users, test_jobs, test_locations, test_persons
) -> tuple[list[dict], int, list[dict]]:
    """Create test interview data with incorrect job_id for access control testing"""
    owner_id = 1
    job_id = find_non_owned_entry(test_jobs, owner_id)
    data = [{"job_id": job_id, "date": str(dt.datetime.now()), "owner_id": owner_id, "type": "phone"}]
    interview_interviewer_mappings = [{"interview_id": 1, "person_ids": [find_non_owned_entry(test_persons, owner_id)]}]
    return data, owner_id, interview_interviewer_mappings


@pytest.fixture
def test_interviews_unauthorised(
    session, test_users, test_jobs, test_locations, test_persons, interviews_unauthorised_data
) -> tuple[list[models.Interview], int]:
    """Create test interview data with incorrect job_id for access control testing"""
    data, owner_id, interview_interviewer_mappings = interviews_unauthorised_data
    interviews = create_interviews(
        session,
        test_persons,
        test_users,
        test_locations,
        test_jobs,
        data,
        interview_interviewer_mappings,
    )
    return interviews, owner_id


@pytest.fixture
def test_job_application_updates(session, test_users, test_jobs) -> list[models.JobApplicationUpdate]:
    """Create test job application update data"""
    return create_job_application_updates(session, test_users, test_jobs)


@pytest.fixture
def job_application_updates_unauthorised_data(session, test_users, test_jobs) -> tuple[list[dict], int]:
    """Create test job application update data with incorrect job_id for access control testing"""
    owner_id = 1
    job_id = find_non_owned_entry(test_jobs, owner_id)
    data = [
        {
            "job_id": job_id,
            "date": str(dt.datetime.now()),
            "type": "received",
            "owner_id": owner_id,
            "note": "Test note",
        }
    ]
    return data, owner_id


@pytest.fixture
def test_job_application_updates_unauthorised(
    session, test_users, test_jobs, job_application_updates_unauthorised_data
) -> tuple[list[models.JobApplicationUpdate], int]:
    """Create test job application update data with incorrect job_id for access control testing"""
    data, owner_id = job_application_updates_unauthorised_data
    updates = create_job_application_updates(session, test_users, test_jobs, data)
    return updates, owner_id


@pytest.fixture
def test_speculative_applications(
    session, test_users, test_persons, test_companies
) -> list[models.SpeculativeApplication]:
    """Create test speculative application data"""
    return create_speculative_applications(session, test_users, test_persons)


@pytest.fixture
def test_scraped_jobs(
    session, test_users, test_job_alert_emails, test_scraping_filters, test_geolocations
) -> list[models.ScrapedJob]:
    """Create test job alert email jobs"""
    return create_scraped_jobs(session, test_job_alert_emails, test_users, test_scraping_filters)


@pytest.fixture
def test_eis_service_logs(session) -> list[models.JobEmailScrapingServiceLog]:
    """Create test service logs"""
    return create_job_scraping_service_logs(session)


@pytest.fixture
def test_platform_stats(session, test_eis_service_logs) -> list[models.JobEmailScrapingPlatformStat]:
    """Create test platform stats"""
    return create_job_scraping_platform_stats(session, test_eis_service_logs)


@pytest.fixture
def test_eis_service_errors(session, test_eis_service_logs) -> list[models.JobEmailScrapingServiceError]:
    """Create test job_email_scraping service errors"""
    return create_job_scraping_service_errors(session, test_eis_service_logs)


@pytest.fixture
def test_job_alert_emails(session, test_users, test_eis_service_logs) -> list[models.JobEmail]:
    """Create test job alert emails"""
    return create_job_alert_emails(session, test_users, test_eis_service_logs)


@pytest.fixture
def test_job_rating_service_logs(session) -> list[models.JobRatingServiceLog]:
    """Create test job rating service logs"""
    return create_job_rating_service_logs(session)


@pytest.fixture
def test_job_ratings(
    session, test_users, test_scraped_jobs, test_user_qualifications, test_job_rating_service_logs, test_ai_prompts
) -> list[models.JobRating]:
    """Create test job ratings"""
    return create_job_ratings(
        session, test_users, test_scraped_jobs, test_user_qualifications, test_job_rating_service_logs, test_ai_prompts
    )


@pytest.fixture
def test_scraping_filters(session, test_users) -> list[models.ScrapingExclusionFilter]:
    """Create test scraped job filter data"""
    return create_scraping_filters(session, test_users)
