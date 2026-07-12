"""Shared fixtures for the Apify job-scraper tests."""

from unittest.mock import patch, MagicMock

import pytest
from apify_client._models import Run  # noqa


def make_run(run_id: str = "run-123", dataset_id: str = "dataset-123") -> Run:
    """Build a Run object mimicking the return of ApifyClient.actor(...).start()."""
    return Run.model_construct(id=run_id, default_dataset_id=dataset_id)


def make_run_status(status: str) -> Run:
    """Build a Run object mimicking the return of ApifyClient.run(...).get() with the given status."""
    return Run.model_construct(status=status)


@pytest.fixture
def mock_apify_cls():
    """Patch ApifyClient and settings for the Apify scrapers (via the base class module).
    Yields the patched ApifyClient class mock so tests can drive its return values and assert calls."""
    with (
        patch("app.job_email_scraping.job_scrapers.apify.ApifyClient") as mock_cls,
        patch("app.job_email_scraping.job_scrapers.apify.settings") as mock_settings,
    ):
        mock_settings.apify_api_key = "test_key"
        yield mock_cls


@pytest.fixture
def mock_brightdata():
    """Patches requests and settings, yields the requests module mock."""
    with (
        patch("app.job_email_scraping.job_scrapers.brightdata.requests") as mock_requests,
        patch("app.job_email_scraping.job_scrapers.brightdata.settings") as mock_settings,
    ):
        mock_settings.brightdata_api_key = "test_api_key"
        yield mock_requests


def make_apify_mock(items: list[dict]) -> MagicMock:
    """Build an ApifyClient instance mock whose actor run succeeds and whose dataset yields `items`."""
    client = MagicMock()
    client.actor.return_value.start.return_value = make_run()
    client.run.return_value.get.return_value = make_run_status("SUCCEEDED")
    client.dataset.return_value.list_items.return_value.items = items
    return client
