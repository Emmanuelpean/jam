"""Unit tests for app/job_email_scraping/job_scrapers/nhs.py"""

import datetime as dt
from unittest.mock import MagicMock, patch

import pytest

from app.job_email_scraping.job_scrapers.nhs import NhsJobScraper


# --------------------------------------------------- HELPERS --------------------------------------------------


def make_apify_mock(items: list[dict]) -> MagicMock:
    """Return a patched ApifyClient mock that yields the given items from the dataset."""
    mock_client = MagicMock()
    mock_client.actor.return_value.start.return_value = {"id": "run-123", "defaultDatasetId": "dataset-123"}
    mock_client.run.return_value.get.return_value = {"status": "SUCCEEDED"}
    mock_client.dataset.return_value.list_items.return_value.items = items
    return mock_client


BASE_JOB: dict = {
    "title": "Community Nurse - District Nursing",
    "employer": "Aneurin Bevan University Health Board",
    "employerAddress": ["Tredegar District Nursing Team", "Park Row", "Tredegar", "NP22 3NG"],
    "closingDate": "29 March 2026",
    "salary": "£31,516 to £38,364 a year per annum, pro rata",
    "jobSummaryText": "The district nursing service is fundamental.",
    "mainDutiesText": "To care for patients and their families.",
    "aboutUsText": "Aneurin Bevan University Health Board is a multi-award-winning NHS organisation.",
}


def make_job(**overrides) -> dict:
    """Return a job dict with the given overrides merged in."""
    return {**BASE_JOB, **overrides}


# --------------------------------------------------- FIXTURES -------------------------------------------------


@pytest.fixture
def mock_apify_cls():
    """Patches ApifyClient and settings for NhsJobScraper (via the base class module)."""
    with (
        patch("app.job_email_scraping.job_scrapers.apify.ApifyClient") as mock_cls,
        patch("app.job_email_scraping.job_scrapers.apify.settings") as mock_settings,
    ):
        mock_settings.apify_api_key = "test_key"
        yield mock_cls


# ---------------------------------------------------- INIT ----------------------------------------------------


class TestInit:

    def test_single_string_id_wrapped_in_list(self) -> None:
        scraper = NhsJobScraper("ABC-123")
        assert scraper.job_ids == ["ABC-123"]

    def test_list_of_ids_preserved(self) -> None:
        scraper = NhsJobScraper(["ABC-123", "DEF-456"])
        assert scraper.job_ids == ["ABC-123", "DEF-456"]

    def test_job_urls_built_from_base_url(self) -> None:
        scraper = NhsJobScraper(["ABC-123", "DEF-456"])
        assert scraper.job_urls == [
            "https://beta.jobs.nhs.uk/candidate/jobadvert/ABC-123",
            "https://beta.jobs.nhs.uk/candidate/jobadvert/DEF-456",
        ]


# ------------------------------------------------- SCRAPE JOB -------------------------------------------------


class TestScrapeJob:

    def test_returns_list_of_job_results(self, mock_apify_cls) -> None:
        mock_apify_cls.return_value = make_apify_mock([make_job()])
        scraper = NhsJobScraper("H9040-26-0303")
        results = scraper.scrape_job()
        assert len(results) == 1

    def test_raises_when_no_job_data(self, mock_apify_cls) -> None:
        mock_apify_cls.return_value = make_apify_mock([])
        scraper = NhsJobScraper("H9040-26-0303")
        with pytest.raises(Exception, match="No data returned from actor run"):
            scraper.scrape_job()

    def test_apify_client_called_with_correct_urls(self, mock_apify_cls) -> None:
        mock_client = make_apify_mock([make_job()])
        mock_apify_cls.return_value = mock_client

        scraper = NhsJobScraper("H9040-26-0303")
        scraper.scrape_job()

        call_kwargs = mock_client.actor.return_value.start.call_args
        run_input = call_kwargs.kwargs["run_input"]
        assert run_input["startUrls"] == [{"url": url} for url in scraper.job_urls]

    def test_apify_actor_id_is_correct(self, mock_apify_cls) -> None:
        mock_client = make_apify_mock([make_job()])
        mock_apify_cls.return_value = mock_client

        scraper = NhsJobScraper("H9040-26-0303")
        scraper.scrape_job()

        mock_client.actor.assert_called_once_with("memo23/nhs-scraper")

    def test_multiple_jobs_all_returned(self, mock_apify_cls) -> None:
        mock_apify_cls.return_value = make_apify_mock([make_job(), make_job(title="Another Job")])
        scraper = NhsJobScraper(["A", "B"])
        results = scraper.scrape_job()
        assert len(results) == 2


# ---------------------------------------------- FIELD MAPPING ------------------------------------------------


class TestFieldMapping:

    def test_employer_mapped_to_company(self, mock_apify_cls) -> None:
        mock_apify_cls.return_value = make_apify_mock([make_job(employer="NHS Trust")])
        result = NhsJobScraper("X").scrape_job()[0]
        assert result.company == "NHS Trust"

    def test_employer_address_joined_as_location(self, mock_apify_cls) -> None:
        mock_apify_cls.return_value = make_apify_mock(
            [make_job(employerAddress=["99 Regents Park Road", "London", "NW1 8UR"])]
        )
        result = NhsJobScraper("X").scrape_job()[0]
        assert result.location == "99 Regents Park Road London NW1 8UR"

    def test_empty_employer_address_gives_none_location(self, mock_apify_cls) -> None:
        mock_apify_cls.return_value = make_apify_mock([make_job(employerAddress=[])])
        result = NhsJobScraper("X").scrape_job()[0]
        assert result.location is None

    def test_title_mapped(self, mock_apify_cls) -> None:
        mock_apify_cls.return_value = make_apify_mock([make_job(title="Practice Nurse")])
        result = NhsJobScraper("X").scrape_job()[0]
        assert result.job.title == "Practice Nurse"

    def test_missing_title_is_none(self, mock_apify_cls) -> None:
        mock_apify_cls.return_value = make_apify_mock([make_job(title=None)])
        result = NhsJobScraper("X").scrape_job()[0]
        assert result.job.title is None

    def test_raw_is_string_of_job_dict(self, mock_apify_cls) -> None:
        job = make_job()
        mock_apify_cls.return_value = make_apify_mock([job])
        result = NhsJobScraper("X").scrape_job()[0]
        assert result.raw == str(job)


# ----------------------------------------------- DESCRIPTION -------------------------------------------------


class TestDescription:

    def test_all_three_sections_joined(self, mock_apify_cls) -> None:
        mock_apify_cls.return_value = make_apify_mock(
            [make_job(jobSummaryText="Summary", mainDutiesText="Duties", aboutUsText="About")]
        )
        result = NhsJobScraper("X").scrape_job()[0]
        assert result.job.description == "Summary\n\nDuties\n\nAbout"

    def test_missing_sections_omitted_from_description(self, mock_apify_cls) -> None:
        mock_apify_cls.return_value = make_apify_mock(
            [make_job(jobSummaryText="Summary", mainDutiesText=None, aboutUsText=None)]
        )
        result = NhsJobScraper("X").scrape_job()[0]
        assert result.job.description == "Summary"

    def test_all_missing_description_is_none(self, mock_apify_cls) -> None:
        mock_apify_cls.return_value = make_apify_mock(
            [make_job(jobSummaryText=None, mainDutiesText=None, aboutUsText=None)]
        )
        result = NhsJobScraper("X").scrape_job()[0]
        assert result.job.description is None


# -------------------------------------------------- DEADLINE --------------------------------------------------


class TestDeadline:

    def test_valid_closing_date_parsed(self, mock_apify_cls) -> None:
        mock_apify_cls.return_value = make_apify_mock([make_job(closingDate="29 March 2026")])
        result = NhsJobScraper("X").scrape_job()[0]
        assert result.job.deadline == dt.datetime(2026, 3, 29)

    def test_closed_job_has_no_deadline_and_is_closed(self, mock_apify_cls) -> None:
        mock_apify_cls.return_value = make_apify_mock([make_job(closingDate="THIS JOB IS NOW CLOSED")])
        result = NhsJobScraper("X").scrape_job()[0]
        assert result.job.deadline is None
        assert result.job.is_closed is True

    def test_closed_check_is_case_insensitive(self, mock_apify_cls) -> None:
        mock_apify_cls.return_value = make_apify_mock([make_job(closingDate="this job is now closed")])
        result = NhsJobScraper("X").scrape_job()[0]
        assert result.job.is_closed is True

    def test_unparseable_closing_date_gives_none_deadline(self, mock_apify_cls) -> None:
        mock_apify_cls.return_value = make_apify_mock([make_job(closingDate="not a date")])
        result = NhsJobScraper("X").scrape_job()[0]
        assert result.job.deadline is None
        assert result.job.is_closed is False

    def test_absent_closing_date_gives_none_deadline(self, mock_apify_cls) -> None:
        job = make_job()
        del job["closingDate"]
        mock_apify_cls.return_value = make_apify_mock([job])
        result = NhsJobScraper("X").scrape_job()[0]
        assert result.job.deadline is None


# --------------------------------------------------- SALARY ---------------------------------------------------


class TestSalary:

    def test_annual_salary_parsed(self, mock_apify_cls) -> None:
        mock_apify_cls.return_value = make_apify_mock(
            [make_job(salary="£31,516 to £38,364 a year per annum, pro rata")]
        )
        result = NhsJobScraper("X").scrape_job()[0]
        assert result.job.salary.min_amount == 31516
        assert result.job.salary.max_amount == 38364
        assert result.job.salary.currency == "£"

    def test_per_annum_salary_parsed(self, mock_apify_cls) -> None:
        mock_apify_cls.return_value = make_apify_mock([make_job(salary="£50,000 to £60,000 per annum")])
        result = NhsJobScraper("X").scrape_job()[0]
        assert result.job.salary.min_amount == 50000
        assert result.job.salary.max_amount == 60000

    def test_no_salary_gives_none_fields(self, mock_apify_cls) -> None:
        mock_apify_cls.return_value = make_apify_mock([make_job(salary=None)])
        result = NhsJobScraper("X").scrape_job()[0]
        assert result.job.salary.min_amount is None
        assert result.job.salary.max_amount is None
        assert result.job.salary.currency is None

    def test_unrecognised_salary_format_gives_none_fields(self, mock_apify_cls) -> None:
        mock_apify_cls.return_value = make_apify_mock([make_job(salary="Competitive salary")])
        result = NhsJobScraper("X").scrape_job()[0]
        assert result.job.salary.min_amount is None
        assert result.job.salary.max_amount is None

    def test_salary_without_commas_parsed(self, mock_apify_cls) -> None:
        mock_apify_cls.return_value = make_apify_mock([make_job(salary="£25000 to £30000 a year")])
        result = NhsJobScraper("X").scrape_job()[0]
        assert result.job.salary.min_amount == 25000
        assert result.job.salary.max_amount == 30000


# ------------------------------------------- DOWNTIME / ERROR TITLES -----------------------------------------


class TestDowntime:

    def test_planned_downtime_title_raises(self, mock_apify_cls) -> None:
        mock_apify_cls.return_value = make_apify_mock([make_job(title="NHS Jobs: Planned downtime")])
        with pytest.raises(Exception, match="NHS Jobs: Planned downtime"):
            NhsJobScraper("X").scrape_job()

    def test_service_problem_title_raises(self, mock_apify_cls) -> None:
        mock_apify_cls.return_value = make_apify_mock([make_job(title="Sorry, there is a problem with the service")])
        with pytest.raises(Exception, match="Sorry, there is a problem with the service"):
            NhsJobScraper("X").scrape_job()
