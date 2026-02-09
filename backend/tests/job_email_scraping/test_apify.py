"""Tests for ApifyJobScraper base class."""

from unittest.mock import patch

import pytest

from app.job_email_scraping.schemas import JobInfo, JobResult
from app.job_email_scraping.job_scrapers.apify import ApifyJobScraper


class ConcreteApifyJobScraper(ApifyJobScraper):
    """Minimal concrete subclass for testing the base class workflow."""

    base_url = "https://example.com/job/"
    name = "example"
    actor_id = "test/actor"

    def _process_job_data(self, job_data: dict) -> JobResult:
        return JobResult(
            company=job_data.get("company"),
            job=JobInfo(title=job_data.get("title")),
            raw=str(job_data),
        )


@pytest.fixture
def mock_apify():
    """Patches ApifyClient and settings, yields the ApifyClient class mock."""
    with (
        patch("app.job_email_scraping.job_scrapers.apify.ApifyClient") as mock_cls,
        patch("app.job_email_scraping.job_scrapers.apify.settings") as mock_settings,
    ):
        mock_settings.apify_api_key = "test_key"
        yield mock_cls


class TestInit:
    """Tests for ApifyJobScraper.__init__"""

    def test_single_string_job_id_wrapped_in_list(self, mock_apify) -> None:
        """Single string job_id is converted to a single-element list."""
        scraper = ConcreteApifyJobScraper("job123")
        assert scraper.job_ids == ["job123"]

    def test_list_job_ids_preserved(self, mock_apify) -> None:
        """List of job_ids is stored as-is."""
        scraper = ConcreteApifyJobScraper(["job1", "job2", "job3"])
        assert scraper.job_ids == ["job1", "job2", "job3"]

    def test_urls_constructed_from_base_url(self, mock_apify) -> None:
        """job_urls are built by concatenating base_url with each job_id."""
        scraper = ConcreteApifyJobScraper(["abc", "def"])
        assert scraper.job_urls == ["https://example.com/job/abc", "https://example.com/job/def"]

    def test_max_attempts_scaled_by_job_count(self, mock_apify) -> None:
        """max_attempts is multiplied by the number of job_ids."""
        scraper = ConcreteApifyJobScraper(["a", "b", "c"])
        assert scraper.max_attempts == 60 * 3

    def test_client_initialised_with_api_key(self, mock_apify) -> None:
        """ApifyClient is created with the API key from settings."""
        ConcreteApifyJobScraper("job1")
        mock_apify.assert_called_once_with("test_key")


class TestStartActorRun:
    """Tests for ApifyJobScraper._start_actor_run"""

    def test_starts_actor_with_correct_input(self, mock_apify) -> None:
        """Actor is started with startUrls from job_urls and residential proxy config."""
        mock_run = {"id": "run_123", "defaultDatasetId": "ds_456"}
        mock_apify.return_value.actor.return_value.start.return_value = mock_run

        scraper = ConcreteApifyJobScraper(["job1", "job2"])
        result = scraper._start_actor_run()

        mock_apify.return_value.actor.assert_called_with("test/actor")
        mock_apify.return_value.actor.return_value.start.assert_called_once_with(
            run_input={
                "startUrls": [
                    {"url": "https://example.com/job/job1"},
                    {"url": "https://example.com/job/job2"},
                ],
                "proxy": {"useApifyProxy": True, "apifyProxyGroups": ["RESIDENTIAL"]},
            }
        )
        assert result == mock_run


class TestWaitForData:
    """Tests for ApifyJobScraper._wait_for_data"""

    @patch("app.job_email_scraping.job_scrapers.apify.time.sleep")
    def test_returns_immediately_on_succeeded(self, mock_sleep, mock_apify) -> None:
        """Returns without sleeping when the first poll returns SUCCEEDED."""
        mock_apify.return_value.run.return_value.get.return_value = {"status": "SUCCEEDED"}

        scraper = ConcreteApifyJobScraper("job1")
        scraper._wait_for_data("run_123")

        mock_apify.return_value.run.assert_called_with("run_123")
        mock_sleep.assert_not_called()

    @patch("app.job_email_scraping.job_scrapers.apify.time.sleep")
    def test_polls_until_succeeded(self, mock_sleep, mock_apify) -> None:
        """Sleeps between polls and stops as soon as SUCCEEDED is returned."""
        mock_apify.return_value.run.return_value.get.side_effect = [
            {"status": "READY"},
            {"status": "RUNNING"},
            {"status": "SUCCEEDED"},
        ]

        scraper = ConcreteApifyJobScraper("job1")
        scraper._wait_for_data("run_123")

        assert mock_sleep.call_count == 2

    @pytest.mark.parametrize("failed_status", ["FAILED", "ABORTED", "TIMED-OUT"])
    @patch("app.job_email_scraping.job_scrapers.apify.time.sleep")
    def test_raises_on_terminal_failure(self, _mock_sleep, mock_apify, failed_status) -> None:
        """Raises Exception immediately on FAILED, ABORTED, or TIMED-OUT status."""
        mock_apify.return_value.run.return_value.get.return_value = {"status": failed_status}

        scraper = ConcreteApifyJobScraper("job1")
        with pytest.raises(Exception, match=failed_status.lower()):
            scraper._wait_for_data("run_123")

    @patch("app.job_email_scraping.job_scrapers.apify.time.sleep")
    def test_raises_timeout_when_max_attempts_exceeded(self, mock_sleep, mock_apify) -> None:
        """Raises TimeoutError after exhausting all polling attempts without SUCCEEDED."""
        mock_apify.return_value.run.return_value.get.return_value = {"status": "RUNNING"}

        scraper = ConcreteApifyJobScraper("job1")
        with pytest.raises(TimeoutError, match="not complete"):
            scraper._wait_for_data("run_123")

        assert mock_sleep.call_count == 60


class TestRetrieveData:
    """Tests for ApifyJobScraper._retrieve_data"""

    def test_returns_items_from_dataset(self, mock_apify) -> None:
        """Returns the list of items from the specified Apify dataset."""
        items = [{"title": "Job 1"}, {"title": "Job 2"}]
        mock_apify.return_value.dataset.return_value.list_items.return_value.items = items

        scraper = ConcreteApifyJobScraper("job1")
        result = scraper._retrieve_data("ds_123")

        mock_apify.return_value.dataset.assert_called_once_with("ds_123")
        assert result == items

    def test_raises_when_dataset_empty(self, mock_apify) -> None:
        """Raises Exception when the dataset returns no items."""
        mock_apify.return_value.dataset.return_value.list_items.return_value.items = []

        scraper = ConcreteApifyJobScraper("job1")
        with pytest.raises(Exception, match="No data"):
            scraper._retrieve_data("ds_123")


class TestProcessJobData:
    """Tests for ApifyJobScraper._process_job_data"""

    def test_raises_on_base_class(self, mock_apify) -> None:
        """Base class raises AssertionError, enforcing subclass implementation."""
        scraper = ApifyJobScraper("job1")
        with pytest.raises(AssertionError):
            scraper._process_job_data({})


class TestScrapeJob:
    """Tests for ApifyJobScraper.scrape_job full workflow."""

    @patch("app.job_email_scraping.job_scrapers.apify.time.sleep")
    def test_orchestrates_full_scrape_workflow(self, _mock_sleep, mock_apify) -> None:
        """Chains start → wait → retrieve → process and returns processed JobResults."""
        client = mock_apify.return_value
        client.actor.return_value.start.return_value = {"id": "run_abc", "defaultDatasetId": "ds_xyz"}
        client.run.return_value.get.return_value = {"status": "SUCCEEDED"}
        client.dataset.return_value.list_items.return_value.items = [
            {"company": "Acme", "title": "Engineer"},
            {"company": "Globex", "title": "Designer"},
        ]

        results = ConcreteApifyJobScraper(["job1"]).scrape_job()

        assert len(results) == 2
        assert all(isinstance(r, JobResult) for r in results)
        assert results[0].company == "Acme"
        assert results[0].job.title == "Engineer"
        assert results[1].company == "Globex"
        assert results[1].job.title == "Designer"

    def test_raises_when_no_run_id(self, mock_apify) -> None:
        """Raises Exception when actor start returns no run ID."""
        mock_apify.return_value.actor.return_value.start.return_value = {"defaultDatasetId": "ds_xyz"}

        with pytest.raises(Exception, match="No run_id"):
            ConcreteApifyJobScraper("job1").scrape_job()

    def test_raises_when_no_dataset_id(self, mock_apify) -> None:
        """Raises Exception when actor start returns no dataset ID."""
        mock_apify.return_value.actor.return_value.start.return_value = {"id": "run_abc"}

        with pytest.raises(Exception, match="No defaultDatasetId"):
            ConcreteApifyJobScraper("job1").scrape_job()
