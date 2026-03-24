"""Tests for IndeedBrightdataJobScraper and IndeedApifyJobScraper._process_job_data."""

from unittest.mock import patch, MagicMock

import pytest

from app.job_email_scraping.job_scrapers.indeed import IndeedBrightdataJobScraper, IndeedApifyJobScraper
from app.job_email_scraping.schemas import JobResult


# ================================================ BRIGHTDATA ================================================

BRIGHTDATA_FULL_JOB = {
    "company_name": "Acme Corp",
    "company_url": "https://www.indeed.com/cmp/acme-corp",
    "location": "London, UK",
    "job_title": "Software Engineer",
    "description_text": "Build great things.",
    "url": "https://www.indeed.com/viewjob?jk=abc123",
    "salary_formatted": "£45,000 - £65,000 a year",
}


@pytest.fixture
def brightdata_scraper():
    with (
        patch("app.job_email_scraping.job_scrapers.brightdata.settings") as mock_settings,
        patch("app.job_email_scraping.job_scrapers.brightdata.requests"),
    ):
        mock_settings.brightdata_api_key = "key"
        mock_settings.brightdata_indeed_dataset_id = "ds_indeed"
        yield IndeedBrightdataJobScraper(["abc123"])


class TestIndeedBrightdataInit:

    def test_base_url_is_indeed(self, brightdata_scraper) -> None:
        assert brightdata_scraper.base_url == "https://www.indeed.com/viewjob?jk="

    def test_name_is_indeed(self, brightdata_scraper) -> None:
        assert brightdata_scraper.name == "indeed"

    def test_job_url_constructed_correctly(self, brightdata_scraper) -> None:
        assert brightdata_scraper.job_urls == ["https://www.indeed.com/viewjob?jk=abc123"]


class TestIndeedBrightdataProcessJobData:

    def test_returns_job_result(self, brightdata_scraper) -> None:
        result = brightdata_scraper._process_job_data(BRIGHTDATA_FULL_JOB)
        assert isinstance(result, JobResult)

    def test_company_name_mapped(self, brightdata_scraper) -> None:
        result = brightdata_scraper._process_job_data(BRIGHTDATA_FULL_JOB)
        assert result.company == "Acme Corp"

    def test_company_url_mapped_to_company_id(self, brightdata_scraper) -> None:
        result = brightdata_scraper._process_job_data(BRIGHTDATA_FULL_JOB)
        assert result.company_id == "https://www.indeed.com/cmp/acme-corp"

    def test_location_mapped(self, brightdata_scraper) -> None:
        result = brightdata_scraper._process_job_data(BRIGHTDATA_FULL_JOB)
        assert result.location == "London, UK"

    def test_job_title_mapped(self, brightdata_scraper) -> None:
        result = brightdata_scraper._process_job_data(BRIGHTDATA_FULL_JOB)
        assert result.job.title == "Software Engineer"

    def test_url_mapped(self, brightdata_scraper) -> None:
        result = brightdata_scraper._process_job_data(BRIGHTDATA_FULL_JOB)
        assert result.job.url == "https://www.indeed.com/viewjob?jk=abc123"

    def test_description_mapped(self, brightdata_scraper) -> None:
        result = brightdata_scraper._process_job_data(BRIGHTDATA_FULL_JOB)
        assert result.job.description == "Build great things."

    def test_raw_is_str_of_job_data(self, brightdata_scraper) -> None:
        result = brightdata_scraper._process_job_data(BRIGHTDATA_FULL_JOB)
        assert result.raw == str(BRIGHTDATA_FULL_JOB)

    def test_description_strips_show_more_show_less(self, brightdata_scraper) -> None:
        # NOTE: str.strip(chars) strips individual characters from both ends, so the test
        # text must not start with any character in "Show more Show less" (S,h,o,w, ,m,r,e,l,s).
        data = {**BRIGHTDATA_FULL_JOB, "description_text": "Build great things.Show more Show less"}
        result = brightdata_scraper._process_job_data(data)
        assert result.job.description == "Build great things."

    def test_description_only_show_more_show_less_gives_none(self, brightdata_scraper) -> None:
        data = {**BRIGHTDATA_FULL_JOB, "description_text": "Show more Show less"}
        result = brightdata_scraper._process_job_data(data)
        assert result.job.description is None

    def test_missing_description_gives_none(self, brightdata_scraper) -> None:
        data = {k: v for k, v in BRIGHTDATA_FULL_JOB.items() if k != "description_text"}
        result = brightdata_scraper._process_job_data(data)
        assert result.job.description is None


class TestIndeedBrightdataSalary:

    def test_yearly_salary_extracted_with_commas(self, brightdata_scraper) -> None:
        result = brightdata_scraper._process_job_data(BRIGHTDATA_FULL_JOB)
        assert result.job.salary.min_amount == 45000.0
        assert result.job.salary.max_amount == 65000.0
        assert result.job.salary.currency == "GBP"

    def test_salary_with_per_annum_wording(self, brightdata_scraper) -> None:
        data = {**BRIGHTDATA_FULL_JOB, "salary_formatted": "£30,000 - £50,000 per annum"}
        result = brightdata_scraper._process_job_data(data)
        assert result.job.salary.min_amount == 30000.0
        assert result.job.salary.max_amount == 50000.0

    def test_salary_with_en_dash(self, brightdata_scraper) -> None:
        data = {**BRIGHTDATA_FULL_JOB, "salary_formatted": "£40,000 – £60,000 a year"}
        result = brightdata_scraper._process_job_data(data)
        assert result.job.salary.min_amount == 40000.0
        assert result.job.salary.max_amount == 60000.0

    def test_salary_without_commas(self, brightdata_scraper) -> None:
        data = {**BRIGHTDATA_FULL_JOB, "salary_formatted": "£45000 - £65000 a year"}
        result = brightdata_scraper._process_job_data(data)
        assert result.job.salary.min_amount == 45000.0
        assert result.job.salary.max_amount == 65000.0

    def test_missing_salary_formatted_gives_none(self, brightdata_scraper) -> None:
        data = {k: v for k, v in BRIGHTDATA_FULL_JOB.items() if k != "salary_formatted"}
        result = brightdata_scraper._process_job_data(data)
        assert result.job.salary.min_amount is None
        assert result.job.salary.max_amount is None
        assert result.job.salary.currency is None

    def test_non_yearly_salary_gives_none(self, brightdata_scraper) -> None:
        data = {**BRIGHTDATA_FULL_JOB, "salary_formatted": "£3,000 - £5,000 a month"}
        result = brightdata_scraper._process_job_data(data)
        assert result.job.salary.min_amount is None
        assert result.job.salary.currency is None

    def test_unrecognised_salary_format_gives_none(self, brightdata_scraper) -> None:
        data = {**BRIGHTDATA_FULL_JOB, "salary_formatted": "Competitive salary"}
        result = brightdata_scraper._process_job_data(data)
        assert result.job.salary.min_amount is None

    def test_empty_dict_does_not_raise(self, brightdata_scraper) -> None:
        result = brightdata_scraper._process_job_data({})
        assert isinstance(result, JobResult)
        assert result.company is None
        assert result.job.salary.min_amount is None


# ================================================== APIFY ===================================================

APIFY_FULL_JOB = {
    "jobInfoModel": {
        "jobInfoHeaderModel": {
            "jobTitle": "Postdoctoral Research Assistant in Physiology of Calcification in phytoplankton",
            "companyName": "University of Oxford",
        },
        "location": {
            "fullAddress": "Wellington Square, Oxford",
        },
        "description": {
            "text": "The Department of Earth Sciences are seeking a highly motivated researcher.",
        },
    }
}


@pytest.fixture
def apify_scraper():
    with (
        patch("app.job_email_scraping.job_scrapers.apify.ApifyClient"),
        patch("app.job_email_scraping.job_scrapers.apify.settings") as mock_settings,
    ):
        mock_settings.apify_api_key = "test_key"
        yield IndeedApifyJobScraper(["758f2768706ab970"])


class TestIndeedApifyInit:

    def test_base_url_is_indeed(self, apify_scraper) -> None:
        assert apify_scraper.base_url == "https://www.indeed.com/viewjob?jk="

    def test_name_is_indeed(self, apify_scraper) -> None:
        assert apify_scraper.name == "indeed"

    def test_actor_id(self, apify_scraper) -> None:
        assert apify_scraper.actor_id == "memo23/apify-indeed-cheerio-ppr"

    def test_job_url_constructed_correctly(self, apify_scraper) -> None:
        assert apify_scraper.job_urls == ["https://www.indeed.com/viewjob?jk=758f2768706ab970"]


class TestIndeedApifyProcessJobData:

    def test_returns_job_result(self, apify_scraper) -> None:
        result = apify_scraper._process_job_data(APIFY_FULL_JOB)
        assert isinstance(result, JobResult)

    def test_job_title_mapped(self, apify_scraper) -> None:
        result = apify_scraper._process_job_data(APIFY_FULL_JOB)
        assert result.job.title == "Postdoctoral Research Assistant in Physiology of Calcification in phytoplankton"

    def test_company_name_mapped(self, apify_scraper) -> None:
        result = apify_scraper._process_job_data(APIFY_FULL_JOB)
        assert result.company == "University of Oxford"

    def test_location_mapped(self, apify_scraper) -> None:
        result = apify_scraper._process_job_data(APIFY_FULL_JOB)
        assert result.location == "Wellington Square, Oxford"

    def test_description_mapped(self, apify_scraper) -> None:
        result = apify_scraper._process_job_data(APIFY_FULL_JOB)
        assert result.job.description == "The Department of Earth Sciences are seeking a highly motivated researcher."

    def test_raw_is_str_of_job_data(self, apify_scraper) -> None:
        result = apify_scraper._process_job_data(APIFY_FULL_JOB)
        assert result.raw == str(APIFY_FULL_JOB)

    def test_missing_job_info_model_raises(self, apify_scraper) -> None:
        with pytest.raises(KeyError):
            apify_scraper._process_job_data({})

    def test_missing_job_title_raises(self, apify_scraper) -> None:
        data = {
            "jobInfoModel": {
                "jobInfoHeaderModel": {"companyName": "Acme"},
                "location": {"fullAddress": "London"},
                "description": {"text": "Some text"},
            }
        }
        with pytest.raises(KeyError):
            apify_scraper._process_job_data(data)

    def test_scrape_job_end_to_end(self, apify_scraper) -> None:
        """scrape_job chains Apify workflow and returns processed JobResults."""
        client = apify_scraper.client
        client.actor.return_value.start.return_value = {"id": "run_1", "defaultDatasetId": "ds_1"}
        client.run.return_value.get.return_value = {"status": "SUCCEEDED"}
        client.dataset.return_value.list_items.return_value.items = [APIFY_FULL_JOB]

        with patch("app.job_email_scraping.job_scrapers.apify.time.sleep"):
            results = apify_scraper.scrape_job()

        assert len(results) == 1
        assert results[0].company == "University of Oxford"
        assert results[0].job.title == "Postdoctoral Research Assistant in Physiology of Calcification in phytoplankton"
        assert results[0].location == "Wellington Square, Oxford"
