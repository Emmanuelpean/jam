"""Tests for BrightdataJobScraper base class."""

from unittest.mock import patch, MagicMock

import pytest

from app.job_email_scraping.schemas import JobInfo, JobResult
from app.job_email_scraping.job_scrapers.brightdata import BrightdataJobScraper


class ConcreteBrightdataJobScraper(BrightdataJobScraper):
    """Minimal concrete subclass for testing the base class workflow."""

    base_url = "https://example.com/job/"
    name = "example"

    def _process_job_data(self, job_data: dict) -> JobResult:
        return JobResult(
            company=job_data.get("company"),
            job=JobInfo(title=job_data.get("title")),
            raw=str(job_data),
        )


def _mock_response(status_code: int, json_data=None, text: str = "") -> MagicMock:
    """Create a mock requests.Response with the given status, body, and text."""
    resp = MagicMock()
    resp.status_code = status_code
    resp.json.return_value = json_data
    resp.text = text
    return resp


@pytest.fixture
def mock_brightdata():
    """Patches requests and settings, yields the requests module mock."""
    with (
        patch("app.job_email_scraping.job_scrapers.brightdata.requests") as mock_requests,
        patch("app.job_email_scraping.job_scrapers.brightdata.settings") as mock_settings,
    ):
        mock_settings.brightdata_api_key = "test_api_key"
        mock_settings.brightdata_example_dataset_id = "ds_example"
        yield mock_requests


class TestInit:
    """Tests for BrightdataJobScraper.__init__"""

    def test_single_string_job_id_wrapped_in_list(self, mock_brightdata) -> None:
        """Single string job_id is converted to a single-element list."""
        scraper = ConcreteBrightdataJobScraper("job123")
        assert scraper.job_ids == ["job123"]

    def test_list_job_ids_preserved(self, mock_brightdata) -> None:
        """List of job_ids is stored as-is."""
        scraper = ConcreteBrightdataJobScraper(["job1", "job2", "job3"])
        assert scraper.job_ids == ["job1", "job2", "job3"]

    def test_urls_constructed_from_base_url(self, mock_brightdata) -> None:
        """job_urls are built by concatenating base_url with each job_id."""
        scraper = ConcreteBrightdataJobScraper(["abc", "def"])
        assert scraper.job_urls == ["https://example.com/job/abc", "https://example.com/job/def"]

    def test_max_attempts_scaled_by_job_count(self, mock_brightdata) -> None:
        """max_attempts is multiplied by the number of job_ids."""
        scraper = ConcreteBrightdataJobScraper(["a", "b", "c"])
        assert scraper.max_attempts == 60 * 3

    def test_api_key_and_dataset_id_loaded_from_settings(self, mock_brightdata) -> None:
        """api_key and dataset_id are read from settings using the scraper name."""
        scraper = ConcreteBrightdataJobScraper("job1")
        assert scraper.api_key == "test_api_key"
        assert scraper.dataset_id == "ds_example"


class TestGetSnapshot:
    """Tests for BrightdataJobScraper._get_snapshot"""

    def test_returns_snapshot_id(self, mock_brightdata) -> None:
        """Returns the snapshot_id from a successful trigger response."""
        mock_brightdata.post.return_value = _mock_response(200, {"snapshot_id": "snap_abc"})

        scraper = ConcreteBrightdataJobScraper(["job1"])
        assert scraper._get_snapshot() == "snap_abc"

    def test_posts_with_correct_headers_params_and_body(self, mock_brightdata) -> None:
        """Sends Bearer auth, dataset_id param, and job URLs as the request body."""
        mock_brightdata.post.return_value = _mock_response(200, {"snapshot_id": "snap_abc"})

        ConcreteBrightdataJobScraper(["job1", "job2"])._get_snapshot()

        mock_brightdata.post.assert_called_once_with(
            "https://api.brightdata.com/datasets/v3/trigger",
            headers={
                "Authorization": "Bearer test_api_key",
                "Content-Type": "application/json",
            },
            params={"dataset_id": "ds_example", "include_errors": "true"},
            json=[
                {"url": "https://example.com/job/job1"},
                {"url": "https://example.com/job/job2"},
            ],
        )

    def test_raises_on_non_200_status(self, mock_brightdata) -> None:
        """Raises Exception when the trigger endpoint returns non-200."""
        mock_brightdata.post.return_value = _mock_response(500, text="Internal Server Error")

        with pytest.raises(Exception, match="Failed to trigger dataset"):
            ConcreteBrightdataJobScraper("job1")._get_snapshot()

    def test_raises_when_no_snapshot_id_in_response(self, mock_brightdata) -> None:
        """Raises Exception when trigger response body has no snapshot_id."""
        mock_brightdata.post.return_value = _mock_response(200, {})

        with pytest.raises(Exception, match="No snapshot_id"):
            ConcreteBrightdataJobScraper("job1")._get_snapshot()


class TestWaitForData:
    """Tests for BrightdataJobScraper._wait_for_data"""

    @patch("app.job_email_scraping.job_scrapers.brightdata.time.sleep")
    def test_returns_on_ready(self, mock_sleep, mock_brightdata) -> None:
        """Returns without sleeping when the first poll returns ready."""
        mock_brightdata.get.return_value = _mock_response(200, {"status": "ready"})

        ConcreteBrightdataJobScraper("job1")._wait_for_data("snap_123")

        mock_sleep.assert_not_called()

    @patch("app.job_email_scraping.job_scrapers.brightdata.time.sleep")
    def test_ready_status_is_case_insensitive(self, _mock_sleep, mock_brightdata) -> None:
        """Accepts mixed-case 'Ready' as a valid ready status."""
        mock_brightdata.get.return_value = _mock_response(200, {"status": "Ready"})

        ConcreteBrightdataJobScraper("job1")._wait_for_data("snap_123")  # Should not raise

    @patch("app.job_email_scraping.job_scrapers.brightdata.time.sleep")
    def test_polls_until_ready(self, mock_sleep, mock_brightdata) -> None:
        """Sleeps between polls and stops as soon as ready is returned."""
        mock_brightdata.get.side_effect = [
            _mock_response(202, {"status": "pending"}),
            _mock_response(200, {"status": "processing"}),
            _mock_response(200, {"status": "ready"}),
        ]

        ConcreteBrightdataJobScraper("job1")._wait_for_data("snap_123")

        assert mock_sleep.call_count == 2

    @patch("app.job_email_scraping.job_scrapers.brightdata.time.sleep")
    def test_raises_on_failed_status(self, _mock_sleep, mock_brightdata) -> None:
        """Raises Exception immediately when status is failed."""
        mock_brightdata.get.return_value = _mock_response(200, {"status": "failed"})

        with pytest.raises(Exception, match="processing failed"):
            ConcreteBrightdataJobScraper("job1")._wait_for_data("snap_123")

    @patch("app.job_email_scraping.job_scrapers.brightdata.time.sleep")
    def test_raises_on_unexpected_http_status(self, _mock_sleep, mock_brightdata) -> None:
        """Raises Exception when progress endpoint returns a status other than 200/202."""
        mock_brightdata.get.return_value = _mock_response(500, text="Server Error")

        with pytest.raises(Exception, match="Failed to get snapshot status"):
            ConcreteBrightdataJobScraper("job1")._wait_for_data("snap_123")

    @patch("app.job_email_scraping.job_scrapers.brightdata.time.sleep")
    def test_raises_timeout_when_max_attempts_exceeded(self, mock_sleep, mock_brightdata) -> None:
        """Raises TimeoutError after exhausting all polling attempts without ready."""
        mock_brightdata.get.return_value = _mock_response(200, {"status": "processing"})

        with pytest.raises(TimeoutError, match="not ready"):
            ConcreteBrightdataJobScraper("job1")._wait_for_data("snap_123")

        assert mock_sleep.call_count == 60


class TestRetrieveData:
    """Tests for BrightdataJobScraper._retrieve_data"""

    def test_returns_data_on_immediate_200(self, mock_brightdata) -> None:
        """Returns json data when the first GET returns 200."""
        data = [{"company": "Acme", "title": "Engineer"}]
        mock_brightdata.get.return_value = _mock_response(200, data)

        assert ConcreteBrightdataJobScraper("job1")._retrieve_data("snap_123") == data

    def test_retries_on_202_then_returns_data(self, mock_brightdata) -> None:
        """Retries while receiving 202 and returns data once 200 arrives."""
        data = [{"company": "Acme"}]
        mock_brightdata.get.side_effect = [
            _mock_response(202),
            _mock_response(202),
            _mock_response(200, data),
        ]

        assert ConcreteBrightdataJobScraper("job1")._retrieve_data("snap_123") == data
        assert mock_brightdata.get.call_count == 3

    def test_raises_when_202_persists_beyond_retry_limit(self, mock_brightdata) -> None:
        """Raises Exception when 202 persists past the 10-retry limit (11 GETs total)."""
        mock_brightdata.get.return_value = _mock_response(202, text="Still processing")

        with pytest.raises(Exception, match="Failed to get snapshot data"):
            ConcreteBrightdataJobScraper("job1")._retrieve_data("snap_123")

        assert mock_brightdata.get.call_count == 11

    def test_raises_on_error_code_in_response(self, mock_brightdata) -> None:
        """Raises Exception when the 200 response body contains an error_code."""
        mock_brightdata.get.return_value = _mock_response(200, [{"error_code": "NOT_FOUND"}])

        with pytest.raises(Exception, match="Failed to get snapshot data"):
            ConcreteBrightdataJobScraper("job1")._retrieve_data("snap_123")

    def test_raises_on_non_200_non_202_status(self, mock_brightdata) -> None:
        """Raises Exception on a status that is neither 200 nor 202."""
        mock_brightdata.get.return_value = _mock_response(404, text="Not Found")

        with pytest.raises(Exception, match="Failed to get snapshot data"):
            ConcreteBrightdataJobScraper("job1")._retrieve_data("snap_123")


class TestProcessJobData:
    """Tests for BrightdataJobScraper._process_job_data"""

    def test_raises_on_base_class(self, mock_brightdata) -> None:
        """Base class raises AssertionError, enforcing subclass implementation."""
        scraper = BrightdataJobScraper("job1")
        with pytest.raises(AssertionError):
            scraper._process_job_data({})


class TestScrapeJob:
    """Tests for BrightdataJobScraper.scrape_job full workflow."""

    @patch("app.job_email_scraping.job_scrapers.brightdata.time.sleep")
    def test_orchestrates_full_scrape_workflow(self, _mock_sleep, mock_brightdata) -> None:
        """Chains get_snapshot → wait → retrieve → process and returns JobResults."""
        data = [
            {"company": "Acme", "title": "Engineer"},
            {"company": "Globex", "title": "Designer"},
        ]
        mock_brightdata.post.return_value = _mock_response(200, {"snapshot_id": "snap_abc"})
        mock_brightdata.get.side_effect = [
            _mock_response(200, {"status": "ready"}),  # _wait_for_data
            _mock_response(200, data),  # _retrieve_data
        ]

        results = ConcreteBrightdataJobScraper(["job1"]).scrape_job()

        assert len(results) == 2
        assert all(isinstance(r, JobResult) for r in results)
        assert results[0].company == "Acme"
        assert results[0].job.title == "Engineer"
        assert results[1].company == "Globex"
        assert results[1].job.title == "Designer"
