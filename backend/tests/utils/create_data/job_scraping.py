"""Functions for creating job scraping service test data."""

import random

from app import models
from tests.utils.test_data import job_scraping_service
from tests.utils.test_data import utils as test_data_utils
from tests.utils.create_data.utils import add_to_db, override_entries_properties


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
    db, emails, users: list[models.User], filters: list[models.ScrapingExclusionFilter]
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


def create_scraping_filters(db, users: list[models.User]) -> list[models.ScrapingExclusionFilter]:
    """Create sample job filters"""

    print("Creating job filters...")
    # noinspection PyArgumentList
    filters = [
        models.ScrapingExclusionFilter(**filter_data)
        for filter_data in override_entries_properties(
            job_scraping_service.SCRAPING_FILTER_DATA,
            ("owner_id", users),
        )
    ]
    return add_to_db(db, filters)
