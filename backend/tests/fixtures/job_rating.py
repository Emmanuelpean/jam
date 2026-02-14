"""Test data fixtures for various models."""

import pytest

from app import models
from tests.utils.create_data.job_rating import (
    create_job_rating_service_logs,
    create_job_ratings,
)


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
