"""Pytest fixtures for Job Rating tests"""

import pytest

import app.job_rating.ai_rating
from tests.job_rating.test_ai_rating import ai_score_job_mock


@pytest.fixture(scope="session", autouse=True)
def mock_linkedin_job_scrapers(monkeypatch) -> None:
    """Mock LinkedinJobScraper for all tests"""

    monkeypatch.setattr(app.job_rating.ai_rating, "ai_score_job", ai_score_job_mock, raising=False)
