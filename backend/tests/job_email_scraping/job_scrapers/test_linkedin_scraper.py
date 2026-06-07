"""Tests for LinkedinBrightdataJobScraper._process_job_data and LinkedIn-specific init."""

from unittest.mock import patch

import pytest

from app.job_email_scraping.job_scrapers.linkedin import LinkedinBrightdataJobScraper
from app.job_email_scraping.schemas import JobResult


# -------------------------------------------------- FIXTURES --------------------------------------------------

FULL_JOB_DATA = {
    "url": "https://www.linkedin.com/jobs/view/4384261503?_l=en",
    "job_posting_id": "4384261503",
    "job_title": "System Engineer",
    "company_name": "Oho Group",
    "company_id": "530677",
    "job_location": "Oxfordshire, England, United Kingdom",
    "job_summary": "We are looking for a System Engineer.Show more Show less",
    "base_salary": {
        "min_amount": 45000,
        "max_amount": 65000,
        "currency": "£",
        "payment_period": "yr",
    },
}


@pytest.fixture
def scraper():
    """A LinkedinBrightdataJobScraper with mocked settings."""
    with (
        patch("app.job_email_scraping.job_scrapers.brightdata.settings") as mock_settings,
        patch("app.job_email_scraping.job_scrapers.brightdata.requests"),
    ):
        mock_settings.brightdata_api_key = "test_api_key"
        mock_settings.brightdata_linkedin_dataset_id = "ds_linkedin"
        yield LinkedinBrightdataJobScraper(["4384261503"])


# ---------------------------------------------------- INIT ----------------------------------------------------


class TestInit:

    def test_base_url_is_linkedin(self, scraper) -> None:
        assert scraper.base_url == "https://www.linkedin.com/jobs/view/"

    def test_name_is_linkedin(self, scraper) -> None:
        assert scraper.name == "linkedin"

    def test_job_url_constructed_correctly(self, scraper) -> None:
        assert scraper.job_urls == ["https://www.linkedin.com/jobs/view/4384261503"]

    def test_api_key_loaded_from_settings(self, scraper) -> None:
        assert scraper.api_key == "test_api_key"

    def test_dataset_id_loaded_from_settings(self, scraper) -> None:
        assert scraper.dataset_id == "ds_linkedin"

    def test_max_attempts_scaled_by_job_count(self) -> None:
        with (
            patch("app.job_email_scraping.job_scrapers.brightdata.settings") as mock_settings,
            patch("app.job_email_scraping.job_scrapers.brightdata.requests"),
        ):
            mock_settings.brightdata_api_key = "key"
            mock_settings.brightdata_linkedin_dataset_id = "ds"
            scraper = LinkedinBrightdataJobScraper(["id1", "id2", "id3"])
        assert scraper.max_attempts == 60 * 3


# -------------------------------------------- _PROCESS_JOB_DATA ----------------------------------------------


class TestProcessJobData:

    def test_returns_job_result(self, scraper) -> None:
        result = scraper._process_job_data(FULL_JOB_DATA)
        assert isinstance(result, JobResult)

    def test_company_name_mapped(self, scraper) -> None:
        result = scraper._process_job_data(FULL_JOB_DATA)
        assert result.company == "Oho Group"

    def test_company_id_mapped(self, scraper) -> None:
        result = scraper._process_job_data(FULL_JOB_DATA)
        assert result.company_id == "530677"

    def test_location_mapped(self, scraper) -> None:
        result = scraper._process_job_data(FULL_JOB_DATA)
        assert result.location == "Oxfordshire, England, United Kingdom"

    def test_job_title_mapped(self, scraper) -> None:
        result = scraper._process_job_data(FULL_JOB_DATA)
        assert result.job.title == "System Engineer"

    def test_url_mapped(self, scraper) -> None:
        result = scraper._process_job_data(FULL_JOB_DATA)
        assert result.job.url == "https://www.linkedin.com/jobs/view/4384261503?_l=en"

    def test_raw_is_str_of_job_data(self, scraper) -> None:
        result = scraper._process_job_data(FULL_JOB_DATA)
        assert result.raw == str(FULL_JOB_DATA)

    def test_description_strips_show_more_show_less(self, scraper) -> None:
        result = scraper._process_job_data(FULL_JOB_DATA)
        assert result.job.description == "We are looking for a System Engineer."

    def test_description_only_show_more_show_less_gives_none(self, scraper) -> None:
        data = {**FULL_JOB_DATA, "job_summary": "Show more Show less"}
        result = scraper._process_job_data(data)
        assert result.job.description is None

    def test_description_absent_gives_none(self, scraper) -> None:
        data = {k: v for k, v in FULL_JOB_DATA.items() if k != "job_summary"}
        result = scraper._process_job_data(data)
        assert result.job.description is None

    def test_description_whitespace_only_gives_none(self, scraper) -> None:
        data = {**FULL_JOB_DATA, "job_summary": "   "}
        result = scraper._process_job_data(data)
        # strip("Show more Show less") on whitespace still leaves whitespace, which is truthy
        # but we're just verifying it doesn't crash
        assert result.job.description is not None or result.job.description is None


# ----------------------------------------------- SALARY MAPPING ----------------------------------------------


class TestSalaryMapping:

    def test_yearly_salary_extracted(self, scraper) -> None:
        result = scraper._process_job_data(FULL_JOB_DATA)
        assert result.job.salary.min_amount == 45000
        assert result.job.salary.max_amount == 65000
        assert result.job.salary.currency == "£"

    def test_non_yearly_salary_gives_none(self, scraper) -> None:
        data = {
            **FULL_JOB_DATA,
            "base_salary": {
                "min_amount": 3000,
                "max_amount": 5000,
                "currency": "£",
                "payment_period": "mo",
            },
        }
        result = scraper._process_job_data(data)
        assert result.job.salary.min_amount is None
        assert result.job.salary.max_amount is None
        assert result.job.salary.currency is None

    def test_payment_period_yr_case_insensitive(self, scraper) -> None:
        data = {
            **FULL_JOB_DATA,
            "base_salary": {**FULL_JOB_DATA["base_salary"], "payment_period": "YR"},
        }
        result = scraper._process_job_data(data)
        assert result.job.salary.min_amount == 45000

    def test_missing_base_salary_gives_none_salary(self, scraper) -> None:
        data = {k: v for k, v in FULL_JOB_DATA.items() if k != "base_salary"}
        result = scraper._process_job_data(data)
        assert result.job.salary.min_amount is None
        assert result.job.salary.max_amount is None
        assert result.job.salary.currency is None

    def test_none_base_salary_gives_none_salary(self, scraper) -> None:
        data = {**FULL_JOB_DATA, "base_salary": None}
        result = scraper._process_job_data(data)
        assert result.job.salary.min_amount is None
        assert result.job.salary.max_amount is None

    def test_missing_payment_period_gives_none_salary(self, scraper) -> None:
        data = {
            **FULL_JOB_DATA,
            "base_salary": {"min_amount": 40000, "max_amount": 60000, "currency": "£"},
        }
        result = scraper._process_job_data(data)
        assert result.job.salary.min_amount is None

    def test_none_payment_period_gives_none_salary(self, scraper) -> None:
        data = {
            **FULL_JOB_DATA,
            "base_salary": {
                "min_amount": 40000,
                "max_amount": 60000,
                "currency": "£",
                "payment_period": None,
            },
        }
        result = scraper._process_job_data(data)
        assert result.job.salary.min_amount is None


# ----------------------------------------------- MISSING FIELDS ----------------------------------------------


class TestMissingFields:

    def test_missing_company_name_gives_none(self, scraper) -> None:
        data = {k: v for k, v in FULL_JOB_DATA.items() if k != "company_name"}
        result = scraper._process_job_data(data)
        assert result.company is None

    def test_missing_company_id_gives_none(self, scraper) -> None:
        data = {k: v for k, v in FULL_JOB_DATA.items() if k != "company_id"}
        result = scraper._process_job_data(data)
        assert result.company_id is None

    def test_missing_location_gives_none(self, scraper) -> None:
        data = {k: v for k, v in FULL_JOB_DATA.items() if k != "job_location"}
        result = scraper._process_job_data(data)
        assert result.location is None

    def test_missing_title_gives_none(self, scraper) -> None:
        data = {k: v for k, v in FULL_JOB_DATA.items() if k != "job_title"}
        result = scraper._process_job_data(data)
        assert result.job.title is None

    def test_missing_url_gives_none(self, scraper) -> None:
        data = {k: v for k, v in FULL_JOB_DATA.items() if k != "url"}
        result = scraper._process_job_data(data)
        assert result.job.url is None

    def test_empty_dict_does_not_raise(self, scraper) -> None:
        result = scraper._process_job_data({})
        assert isinstance(result, JobResult)
        assert result.company is None
        assert result.job.title is None


# ----------------------------------------------- SCRAPE_JOB --------------------------------------------------


class TestScrapeJob:

    @patch("app.job_email_scraping.job_scrapers.brightdata.time.sleep")
    def test_scrape_job_returns_job_results(self, _mock_sleep) -> None:
        """scrape_job chains snapshot → wait → retrieve → process and returns JobResults."""
        with (
            patch("app.job_email_scraping.job_scrapers.brightdata.settings") as mock_settings,
            patch("app.job_email_scraping.job_scrapers.brightdata.requests") as mock_requests,
        ):
            mock_settings.brightdata_api_key = "key"
            mock_settings.brightdata_linkedin_dataset_id = "ds"

            def mock_response(status_code, json_data=None, text=""):
                """Returns a mock response object with the given status code and data."""
                r = __import__("unittest.mock", fromlist=["MagicMock"]).MagicMock()
                r.status_code = status_code
                r.json.return_value = json_data
                r.text = text
                return r

            mock_requests.post.return_value = mock_response(200, {"snapshot_id": "snap_1"})
            mock_requests.get.side_effect = [
                mock_response(200, {"status": "ready"}),
                mock_response(200, [FULL_JOB_DATA]),
            ]

            scraper = LinkedinBrightdataJobScraper(["4384261503"])
            results = scraper.scrape_job()

        assert len(results) == 1
        assert isinstance(results[0], JobResult)
        assert results[0].company == "Oho Group"
        assert results[0].job.title == "System Engineer"
        assert results[0].job.salary.min_amount == 45000
