"""Test data fixtures for various models."""

import pytest

from app import models
from tests.utils.create_data.job_scraping import (
    create_scraped_jobs,
    create_job_scraping_service_logs,
    create_job_scraping_platform_stats,
    create_job_scraping_service_errors,
    create_job_alert_emails,
    create_scraping_filters,
    create_scraping_favourite_filters,
)


@pytest.fixture
def test_scraped_jobs(
    session, test_users, test_job_alert_emails, test_scraping_filters, test_geolocations
) -> list[models.ScrapedJob]:
    """Create test job alert email jobs"""
    return create_scraped_jobs(session, test_job_alert_emails, test_users, test_scraping_filters, test_geolocations)


@pytest.fixture
def test_job_scraping_service_logs(session) -> list[models.JobEmailScrapingServiceLog]:
    """Create test service logs"""
    return create_job_scraping_service_logs(session)


@pytest.fixture
def test_platform_stats(session, test_job_scraping_service_logs) -> list[models.JobEmailScrapingPlatformStat]:
    """Create test platform stats"""
    return create_job_scraping_platform_stats(session, test_job_scraping_service_logs)


@pytest.fixture
def test_job_scraping_service_errors(
    session, test_job_scraping_service_logs
) -> list[models.JobEmailScrapingServiceError]:
    """Create test job_email_scraping service errors"""
    return create_job_scraping_service_errors(session, test_job_scraping_service_logs)


@pytest.fixture
def test_job_alert_emails(session, test_users, test_job_scraping_service_logs) -> list[models.JobEmail]:
    """Create test job alert emails"""
    return create_job_alert_emails(session, test_users, test_job_scraping_service_logs)


@pytest.fixture
def test_scraping_filters(session, test_users) -> list[models.ScrapingExclusionFilter]:
    """Create test scraped job filter data"""
    return create_scraping_filters(session, test_users)


@pytest.fixture
def test_scraping_favourite_filters(session, test_users) -> list[models.ScrapingFavouriteFilter]:
    """Create test scraped job favourite filter data"""
    return create_scraping_favourite_filters(session, test_users)
