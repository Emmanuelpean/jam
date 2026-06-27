"""Functions for creating job scraping service test data."""

import random

from app import models
from tests.utils.create_data.utils import create_db_entries, override_properties
from tests.utils.test_data import job_scraping
from tests.utils.test_data import utils as test_data_utils


def create_job_alert_emails(
    db,
    users: list[models.User],
    service_logs: list[models.JobEmailScrapingServiceLog],
) -> list[models.JobEmail]:
    """Create sample job alert emails"""

    data = override_properties(
        job_scraping.JOB_EMAIL_DATA,
        ("owner_id", users),
        ("service_log_id", service_logs),
    )
    print(f"Creating {len(data)} Job Alert Emails...")
    emails = create_db_entries(db, models.JobEmail, data)

    # Ensure uniqueness of external_email_id
    for email in emails:
        email.external_email_id += str(random.random())
    db.commit()

    return emails


def create_scraped_jobs(
    db,
    emails,
    users: list[models.User],
    filters: list[models.ScrapingExclusionFilter],
    geolocations: list[models.Geolocation],
) -> list[models.ScrapedJob]:
    """Create sample scraped jobs - some with scraped data, some without"""

    data = override_properties(
        job_scraping.SCRAPED_JOB_DATA,
        ("owner_id", users),
        ("service_log_id", emails),
        ("filter_id", filters),
    )
    for d in data:
        geolocation = [g for g in geolocations if d.get("location") == g.query]
        if geolocation:
            d["geolocation_id"] = geolocation[0].id
    print(f"Creating {len(data)} Scraped Jobs...")
    scraped_jobs = create_db_entries(db, models.ScrapedJob, data)

    # Add email mappings to scraped jobs
    test_data_utils.add_mappings(
        primary_data=emails,
        secondary_data=scraped_jobs,
        mapping_data=job_scraping.EMAIL_SCRAPEDJOB_MAPPINGS,
        primary_key="email_id",
        secondary_key="scraped_job_ids",
        relationship_attr="jobs",
    )

    db.commit()
    return scraped_jobs


def create_job_scraping_service_logs(db) -> list[models.JobEmailScrapingServiceLog]:
    """Create sample scraped job service logs"""

    data = job_scraping.JOB_SCRAPING_SERVICE_LOG_DATA
    print(f"Creating {len(data)} Job Scraping Service Logs...")
    return create_db_entries(db, models.JobEmailScrapingServiceLog, data)


def create_job_scraping_platform_stats(db, service_logs) -> list[models.JobEmailScrapingPlatformStat]:
    """Create sample platform stats"""

    data = override_properties(job_scraping.JOB_SCRAPING_PLATFORM_STAT_DATA, ("service_log_id", service_logs))
    print(f"Creating {len(data)} Platform Stats...")
    return create_db_entries(db, models.JobEmailScrapingPlatformStat, data)


def create_job_scraping_service_errors(db, service_logs) -> list[models.ServiceError]:
    """Create sample Job Scraping service errors as unified Error rows"""

    data = override_properties(job_scraping.JOB_SCRAPING_SERVICE_ERROR_DATA, ("service_log_id", service_logs))
    for entry in data:
        entry["job_email_scraping_service_log_id"] = entry.pop("service_log_id")
    print(f"Creating {len(data)} Job Scraping Service Errors...")
    return create_db_entries(db, models.ServiceError, data)


def create_scraping_filters(db, users: list[models.User]) -> list[models.ScrapingExclusionFilter]:
    """Create sample job filters"""

    data = override_properties(job_scraping.SCRAPING_FILTER_DATA, ("owner_id", users))
    print(f"Creating {len(data)} Scraping Filters...")
    return create_db_entries(db, models.ScrapingExclusionFilter, data)


def create_scraping_favourite_filters(db, users: list[models.User]) -> list[models.ScrapingFavouriteFilter]:
    """Create sample favourite job filters"""

    data = override_properties(job_scraping.SCRAPING_FAVOURITE_FILTER_DATA, ("owner_id", users))
    print(f"Creating {len(data)} Scraping Favourite Filters...")
    return create_db_entries(db, models.ScrapingFavouriteFilter, data)
