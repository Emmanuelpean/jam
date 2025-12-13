"""Pytest fixtures for Job Rating tests"""

import pytest

import app.job_rating.scraped_job_rating as rating
from tests.job_rating.test_ai_rating import ai_score_job_mock


@pytest.fixture(autouse=True)
def mock_ai_score(monkeypatch) -> None:
    """Mock ai_score_job for all tests"""

    monkeypatch.setattr(rating, "ai_score_job", ai_score_job_mock, raising=False)
