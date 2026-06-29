"""Unit tests for app/job_email_scraping/job_scrapers/veganjobs.py"""

from unittest.mock import MagicMock, patch

import pytest

from app.job_email_scraping.job_scrapers.veganjobs import VeganJobsJobScraper


# --------------------------------------------------- HELPERS --------------------------------------------------


def make_response(html: str, status_code: int = 200) -> MagicMock:
    """Build a mock cloudscraper response."""
    mock = MagicMock()
    mock.status_code = status_code
    mock.content = html.encode("utf-8")
    mock.raise_for_status = MagicMock()
    if status_code >= 400:
        mock.raise_for_status.side_effect = Exception(f"HTTP {status_code}")
    return mock


def make_scraper_mock(html: str = "", status_code: int = 200) -> MagicMock:
    """Return a mocked cloudscraper instance whose .get() returns the given HTML."""
    mock_session = MagicMock()
    mock_session.get.return_value = make_response(html, status_code)
    return mock_session


MINIMAL_HTML = """
<html><body>
<h2 class="page-title">Managing Director</h2>
<div class="joblisting-meta-company-name">The Humane League UK</div>
<ul class="job-listing-meta meta">
  <li class="location">Remote (UK)</li>
</ul>
<div class="job_listing-description">About the role. Some duties.</div>
</body></html>
"""

SALARY_HTML = """
<html><body>
<h2 class="page-title">Software Engineer</h2>
<div class="joblisting-meta-company-name">Vegan Corp</div>
<li class="location">London</li>
<div class="job_listing-description">
Job overview text.
Salary: £50,000 per year
Some text after salary.
</div>
</body></html>
"""

OVERWIEW_HTML = """
<html><body>
<h2 class="page-title">Chef</h2>
<div class="job_listing-description">Overwiew
Cook plant-based food.
</div>
</body></html>
"""

MISSING_ELEMENTS_HTML = """
<html><body>
<div class="job_listing-description">Some description.</div>
</body></html>
"""

NO_CONTAINER_HTML = """
<html><body>
<h2 class="page-title">Chef</h2>
</body></html>
"""


@pytest.fixture
def scraper_factory():
    """Factory that patches cloudscraper.create_scraper and returns (VeganJobsJobScraper, mock_session)."""

    def _make(job_ids, html=MINIMAL_HTML, status_code=200):
        mock_session = make_scraper_mock(html, status_code)
        with patch("app.job_email_scraping.job_scrapers.veganjobs.cloudscraper") as mock_cs:
            mock_cs.create_scraper.return_value = mock_session
            scraper = VeganJobsJobScraper(job_ids)
        scraper.scraper = mock_session  # replace instance scraper directly
        return scraper, mock_session

    return _make


# ---------------------------------------------------- INIT ----------------------------------------------------


class TestInit:

    def test_single_string_id_wrapped_in_list(self) -> None:
        with patch("app.job_email_scraping.job_scrapers.veganjobs.cloudscraper"):
            scraper = VeganJobsJobScraper("some-job-slug")
        assert scraper.job_ids == ["some-job-slug"]

    def test_list_of_ids_preserved(self) -> None:
        with patch("app.job_email_scraping.job_scrapers.veganjobs.cloudscraper"):
            scraper = VeganJobsJobScraper(["slug-a", "slug-b"])
        assert scraper.job_ids == ["slug-a", "slug-b"]

    def test_job_urls_built_from_base_url(self) -> None:
        with patch("app.job_email_scraping.job_scrapers.veganjobs.cloudscraper"):
            scraper = VeganJobsJobScraper(["slug-a", "slug-b"])
        assert scraper.job_urls == [
            "https://veganjobs.com/job/slug-a",
            "https://veganjobs.com/job/slug-b",
        ]

    def test_cloudscraper_session_created(self) -> None:
        with patch("app.job_email_scraping.job_scrapers.veganjobs.cloudscraper") as mock_cs:
            VeganJobsJobScraper("slug")
        mock_cs.create_scraper.assert_called_once()


# -------------------------------------------- SCRAPE_JOB_LISTING ---------------------------------------------


class TestScrapeJobListing:

    def test_title_extracted(self, scraper_factory) -> None:
        scraper, _ = scraper_factory("slug", MINIMAL_HTML)
        result = scraper.scrape_job_listing("https://veganjobs.com/job/slug")
        assert result.job.title == "Managing Director"

    def test_company_extracted(self, scraper_factory) -> None:
        scraper, _ = scraper_factory("slug", MINIMAL_HTML)
        result = scraper.scrape_job_listing("https://veganjobs.com/job/slug")
        assert result.company == "The Humane League UK"

    def test_location_extracted(self, scraper_factory) -> None:
        scraper, _ = scraper_factory("slug", MINIMAL_HTML)
        result = scraper.scrape_job_listing("https://veganjobs.com/job/slug")
        assert result.location == "Remote (UK)"

    def test_description_extracted(self, scraper_factory) -> None:
        scraper, _ = scraper_factory("slug", MINIMAL_HTML)
        result = scraper.scrape_job_listing("https://veganjobs.com/job/slug")
        assert result.job.description is not None
        assert "About the role" in result.job.description

    def test_raw_is_soup_text(self, scraper_factory) -> None:
        scraper, _ = scraper_factory("slug", MINIMAL_HTML)
        result = scraper.scrape_job_listing("https://veganjobs.com/job/slug")
        assert isinstance(result.raw, str)
        assert "Managing Director" in result.raw

    def test_salary_fields_always_none(self, scraper_factory) -> None:
        """Salary parsing is commented out; fields should always be None."""
        scraper, _ = scraper_factory("slug", MINIMAL_HTML)
        result = scraper.scrape_job_listing("https://veganjobs.com/job/slug")
        assert result.job.salary.min_amount is None
        assert result.job.salary.max_amount is None
        assert result.job.salary.currency is None

    def test_company_id_is_none(self, scraper_factory) -> None:
        scraper, _ = scraper_factory("slug", MINIMAL_HTML)
        result = scraper.scrape_job_listing("https://veganjobs.com/job/slug")
        assert result.company_id is None

    def test_missing_title_tag_gives_none(self, scraper_factory) -> None:
        scraper, _ = scraper_factory("slug", MISSING_ELEMENTS_HTML)
        result = scraper.scrape_job_listing("https://veganjobs.com/job/slug")
        assert result.job.title is None

    def test_missing_company_tag_gives_none(self, scraper_factory) -> None:
        scraper, _ = scraper_factory("slug", MISSING_ELEMENTS_HTML)
        result = scraper.scrape_job_listing("https://veganjobs.com/job/slug")
        assert result.company is None

    def test_missing_location_tag_gives_none(self, scraper_factory) -> None:
        scraper, _ = scraper_factory("slug", MISSING_ELEMENTS_HTML)
        result = scraper.scrape_job_listing("https://veganjobs.com/job/slug")
        assert result.location is None

    def test_missing_description_container_gives_empty_description(self, scraper_factory) -> None:
        scraper, _ = scraper_factory("slug", NO_CONTAINER_HTML)
        result = scraper.scrape_job_listing("https://veganjobs.com/job/slug")
        assert result.job.description == ""

    def test_salary_section_stripped_from_description(self, scraper_factory) -> None:
        """Everything from 'Salary:' onwards is removed from description."""
        scraper, _ = scraper_factory("slug", SALARY_HTML)
        result = scraper.scrape_job_listing("https://veganjobs.com/job/slug")
        assert "Salary:" not in result.job.description
        assert "£50,000" not in result.job.description
        assert result.job.description and "Job overview text" in result.job.description

    def test_overwiew_prefix_stripped_from_description(self, scraper_factory) -> None:
        """'Overwiew' (sic) prefix is stripped from description start."""
        scraper, _ = scraper_factory("slug", OVERWIEW_HTML)
        result = scraper.scrape_job_listing("https://veganjobs.com/job/slug")
        assert result.job.description and not result.job.description.startswith("Overwiew")

    def test_get_called_with_url(self, scraper_factory) -> None:
        url = "https://veganjobs.com/job/some-slug"
        scraper, mock_session = scraper_factory("some-slug", MINIMAL_HTML)
        scraper.scrape_job_listing(url)
        mock_session.get.assert_called_once_with(url)

    def test_raise_for_status_called(self, scraper_factory) -> None:
        scraper, mock_session = scraper_factory("slug", MINIMAL_HTML)
        scraper.scrape_job_listing("https://veganjobs.com/job/slug")
        mock_session.get.return_value.raise_for_status.assert_called_once()

    def test_http_error_propagates(self, scraper_factory) -> None:
        scraper, mock_session = scraper_factory("slug", status_code=404)
        with pytest.raises(Exception):
            scraper.scrape_job_listing("https://veganjobs.com/job/slug")


# ------------------------------------------------- SCRAPE_JOB -------------------------------------------------


class TestScrapeJob:

    def test_returns_list_of_job_results(self, scraper_factory) -> None:
        scraper, _ = scraper_factory("slug", MINIMAL_HTML)
        results = scraper.scrape_job()
        assert len(results) == 1

    def test_multiple_ids_all_scraped(self, scraper_factory) -> None:
        scraper, mock_session = scraper_factory(["slug-a", "slug-b"], MINIMAL_HTML)
        results = scraper.scrape_job()
        assert len(results) == 2

    def test_correct_urls_requested(self, scraper_factory) -> None:
        scraper, mock_session = scraper_factory(["a", "b"], MINIMAL_HTML)
        scraper.scrape_job()
        called_urls = [c.args[0] for c in mock_session.get.call_args_list]
        assert "https://veganjobs.com/job/a" in called_urls
        assert "https://veganjobs.com/job/b" in called_urls

    def test_retries_on_failure_then_succeeds(self) -> None:
        """If scrape_job_listing fails on first attempt and succeeds on second, result is returned."""
        with patch("app.job_email_scraping.job_scrapers.veganjobs.cloudscraper"):
            scraper = VeganJobsJobScraper("slug")

        success_result = MagicMock()
        call_count = 0

        def side_effect(url):
            """Return success_result on first call, raise RuntimeError on second."""
            _ = url
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise RuntimeError("transient error")
            return success_result

        scraper.scrape_job_listing = side_effect
        results = scraper.scrape_job()

        assert results == [success_result]
        assert call_count == 2

    def test_raises_after_50_failures(self) -> None:
        """After 50 consecutive failures, AssertionError is raised."""
        with patch("app.job_email_scraping.job_scrapers.veganjobs.cloudscraper"):
            scraper = VeganJobsJobScraper("slug")

        scraper.scrape_job_listing = MagicMock(side_effect=RuntimeError("always fails"))

        with pytest.raises(AssertionError, match="Failed to scrape job listing"):
            scraper.scrape_job()

        assert scraper.scrape_job_listing.call_count == 50

    def test_stops_retrying_after_success(self) -> None:
        """Exactly one call is made when the first attempt succeeds."""
        with patch("app.job_email_scraping.job_scrapers.veganjobs.cloudscraper"):
            scraper = VeganJobsJobScraper("slug")

        scraper.scrape_job_listing = MagicMock(return_value=MagicMock())
        scraper.scrape_job()

        scraper.scrape_job_listing.assert_called_once()
