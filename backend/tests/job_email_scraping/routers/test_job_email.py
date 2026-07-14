"""Tests for Job Scraping routers."""

import datetime as dt
import json

import pytest
from starlette import status
from starlette.testclient import TestClient

from app import models
from app.job_email_scraping.schemas import JobEmailOut
from tests.base_test import BaseTest
from tests.conftest import make_undefined_method_params
from tests.fixtures.users import FixtureUser


class TestJobEmailsByScrapedJob(BaseTest):
    """Test suite for GET /job-alert-emails/by-scraped-job/{job_id}"""

    endpoint = "/job-alert-emails/by-scraped-job"

    def test_get_emails_for_scraped_job(self, test_regular_user: FixtureUser) -> None:
        """Should return emails linked to a scraped job owned by the user"""

        emails = [test_regular_user.create_job_email(), test_regular_user.create_job_email()]
        job = test_regular_user.create_scraped_job(emails=emails)

        response = test_regular_user.client.get(f"{self.endpoint}/{job.id}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == len(emails)
        self.check_output(emails, data, JobEmailOut)

    def test_not_found_nonexistent_job(self, test_regular_user: FixtureUser) -> None:
        """Should return 404 when scraped job doesn't exist"""

        response = test_regular_user.client.get(f"{self.endpoint}/99999")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_not_found_other_users_job(self, test_regular_user: FixtureUser, test_admin_user: FixtureUser) -> None:
        """Should return 404 when scraped job belongs to another user"""

        admin_job = test_admin_user.create_scraped_job()
        response = test_regular_user.client.get(f"{self.endpoint}/{admin_job.id}")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_unauthenticated(self, client: TestClient, test_regular_user: FixtureUser) -> None:
        """Should return 401 when not authenticated"""

        job = test_regular_user.create_scraped_job()
        response = client.get(f"{self.endpoint}/{job.id}")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestJobAlertEmailsPaged:
    """Test suite for GET /job-alert-emails/paged"""

    endpoint = "/job-alert-emails/paged"

    @pytest.fixture
    def job_emails(self, test_regular_user: FixtureUser, test_admin_user: FixtureUser) -> list[models.JobEmail]:
        """Create the regular user's 4 job alert emails (varied subject/platform/date for the
        search and sort tests), plus emails owned by another user to verify ownership isolation."""

        now = dt.datetime.now(dt.timezone.utc)
        owned = [
            test_regular_user.create_job_email(subject="Python Developer", platform="linkedin", date_received=now),
            test_regular_user.create_job_email(
                subject="Data Analyst", platform="indeed", date_received=now - dt.timedelta(days=1)
            ),
            test_regular_user.create_job_email(
                subject="Backend Engineer", platform="nhs", date_received=now - dt.timedelta(days=2)
            ),
            test_regular_user.create_job_email(
                subject="Frontend Role", platform="linkedin", date_received=now - dt.timedelta(days=3)
            ),
        ]
        # Emails owned by another user must never appear in the regular user's results.
        test_admin_user.create_job_email(subject="Admin Alert One")
        test_admin_user.create_job_email(subject="Admin Alert Two")
        return owned

    def test_get_paged_default_params(self, job_emails: list[models.JobEmail], test_regular_user: FixtureUser) -> None:
        """Should return paginated emails for the current user with default params"""

        response = test_regular_user.client.get(self.endpoint)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 4  # Regular user owns 4 emails
        assert data["page"] == 0
        assert data["page_size"] == 10
        assert len(data["items"]) == 4

    def test_pagination(self, job_emails: list[models.JobEmail], test_regular_user: FixtureUser) -> None:
        """Should respect page and page_size parameters"""

        response = test_regular_user.client.get(self.endpoint, params={"page": 0, "page_size": 2})

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 4
        assert data["page_size"] == 2
        assert len(data["items"]) == 2
        assert data["total_pages"] == 2

    def test_pagination_second_page(self, job_emails: list[models.JobEmail], test_regular_user: FixtureUser) -> None:
        """Should return the correct items for the second page"""

        response = test_regular_user.client.get(self.endpoint, params={"page": 1, "page_size": 2})

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 4
        assert len(data["items"]) == 2
        assert data["page"] == 1

    def test_sort_by_date_received_desc(
        self, job_emails: list[models.JobEmail], test_regular_user: FixtureUser
    ) -> None:
        """Should sort by date_received descending by default"""

        response = test_regular_user.client.get(self.endpoint)

        assert response.status_code == status.HTTP_200_OK
        items = response.json()["items"]
        dates = [item["date_received"] for item in items]
        assert dates == sorted(dates, reverse=True)

    def test_sort_by_date_received_asc(self, job_emails: list[models.JobEmail], test_regular_user: FixtureUser) -> None:
        """Should sort by date_received ascending when specified"""

        response = test_regular_user.client.get(self.endpoint, params={"sort_direction": "asc"})

        assert response.status_code == status.HTTP_200_OK
        items = response.json()["items"]
        dates = [item["date_received"] for item in items]
        assert dates == sorted(dates)

    def test_sort_by_subject(self, job_emails: list[models.JobEmail], test_regular_user: FixtureUser) -> None:
        """Should sort by subject when specified"""

        response = test_regular_user.client.get(self.endpoint, params={"sort_by": "subject", "sort_direction": "asc"})

        assert response.status_code == status.HTTP_200_OK
        items = response.json()["items"]
        subjects = [item["subject"] for item in items]
        assert subjects == sorted(subjects)

    def test_search_by_subject(self, job_emails: list[models.JobEmail], test_regular_user: FixtureUser) -> None:
        """Should filter emails by search term matching subject"""

        response = test_regular_user.client.get(self.endpoint, params={"search": "Python"})

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] >= 1
        for item in data["items"]:
            assert any(
                "python" in (item.get(field) or "").lower() for field in ["subject", "sender", "platform", "alert_name"]
            )

    def test_search_by_platform(self, job_emails: list[models.JobEmail], test_regular_user: FixtureUser) -> None:
        """Should filter emails by search term matching platform"""

        response = test_regular_user.client.get(self.endpoint, params={"search": "indeed"})

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] >= 1
        for item in data["items"]:
            assert any(
                "indeed" in (item.get(field) or "").lower() for field in ["subject", "sender", "platform", "alert_name"]
            )

    def test_search_no_results(self, job_emails: list[models.JobEmail], test_regular_user: FixtureUser) -> None:
        """Should return empty results when search term matches nothing"""

        response = test_regular_user.client.get(self.endpoint, params={"search": "nonexistent_xyz_123"})

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 4
        assert data["total_filtered"] == 0
        assert len(data["items"]) == 0

    def test_only_returns_own_emails(self, job_emails: list[models.JobEmail], test_regular_user: FixtureUser) -> None:
        """Should only return emails belonging to the authenticated user"""

        response = test_regular_user.client.get(self.endpoint, params={"page_size": 100})

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        # Regular user owns 4 emails; the other user's emails must be excluded.
        assert data["total"] == 4

    def test_unauthenticated(self, client: TestClient) -> None:
        """Should return 401 when not authenticated"""

        response = client.get(self.endpoint)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestJobAlertEmailsPagedFilters:
    """Tests for the JSON `filters` query parameter on /job-alert-emails/paged."""

    endpoint = "/job-alert-emails/paged"

    # --------------------------------------------------- TEXT FILTER --------------------------------------------------

    def test_text_filter_on_subject(self, test_regular_user: FixtureUser) -> None:
        """Text filter should match subject via case-insensitive substring."""

        test_regular_user.create_job_email(subject="Python Developer Roles")
        test_regular_user.create_job_email(subject="Java Engineer Openings")
        test_regular_user.create_job_email(subject="Data Scientist Positions")

        filters = json.dumps({"subject": {"type": "text", "value": "python"}})
        response = test_regular_user.client.get(self.endpoint, params={"filters": filters})

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total_filtered"] == 1
        assert data["items"][0]["subject"] == "Python Developer Roles"

    def test_text_filter_on_sender(self, test_regular_user: FixtureUser) -> None:
        """Text filter should match sender address."""

        test_regular_user.create_job_email(sender="jobalerts@linkedin.com")
        test_regular_user.create_job_email(sender="noreply@indeed.com")

        filters = json.dumps({"sender": {"type": "text", "value": "jobalerts"}})
        response = test_regular_user.client.get(self.endpoint, params={"filters": filters})

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["total_filtered"] == 1
        assert response.json()["items"][0]["sender"] == "jobalerts@linkedin.com"

    # -------------------------------------------------- SELECT FILTER -------------------------------------------------

    def test_select_filter_on_platform(self, test_regular_user: FixtureUser) -> None:
        """Select filter should match exact platform values."""

        test_regular_user.create_job_email(platform="linkedin")
        test_regular_user.create_job_email(platform="indeed")
        test_regular_user.create_job_email(platform="nhs")

        filters = json.dumps({"platform": {"type": "select", "selected": ["indeed", "nhs"]}})
        response = test_regular_user.client.get(self.endpoint, params={"filters": filters})

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total_filtered"] == 2
        platforms = {item["platform"] for item in data["items"]}
        assert platforms == {"indeed", "nhs"}

    # -------------------------------------------------- NUMBER FILTER -------------------------------------------------

    def test_number_filter_min_on_job_found_n(self, test_regular_user: FixtureUser) -> None:
        """Number filter with min should return emails with job_found_n >= value."""

        test_regular_user.create_job_email(subject="Few", job_found_n=2)
        test_regular_user.create_job_email(subject="Some", job_found_n=10)
        test_regular_user.create_job_email(subject="Many", job_found_n=50)

        filters = json.dumps({"job_found_n": {"type": "number", "min": 9, "max": None}})
        response = test_regular_user.client.get(self.endpoint, params={"filters": filters})

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total_filtered"] == 2
        subjects = {item["subject"] for item in data["items"]}
        assert subjects == {"Some", "Many"}

    def test_number_filter_range_on_job_found_n(self, test_regular_user: FixtureUser) -> None:
        """Number filter with both min and max should return emails in range."""

        test_regular_user.create_job_email(subject="Low", job_found_n=1)
        test_regular_user.create_job_email(subject="Mid", job_found_n=20)
        test_regular_user.create_job_email(subject="High", job_found_n=100)

        filters = json.dumps({"job_found_n": {"type": "number", "min": 10, "max": 50}})
        response = test_regular_user.client.get(self.endpoint, params={"filters": filters})

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["total_filtered"] == 1
        assert response.json()["items"][0]["subject"] == "Mid"

    # ------------------------------------------ NULL FILTER (nullFilter) ----------------------------------------------

    def test_null_filter_null_shows_only_emails_without_alert_name(self, test_regular_user: FixtureUser) -> None:
        """nullFilter='null' should show only emails with no alert_name."""

        test_regular_user.create_job_email(subject="Named", alert_name="Python jobs")
        test_regular_user.create_job_email(subject="Unnamed", alert_name=None)

        filters = json.dumps({"alert_name": {"type": "number", "min": None, "max": None, "nullFilter": "null"}})
        response = test_regular_user.client.get(self.endpoint, params={"filters": filters})

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total_filtered"] == 1
        assert data["items"][0]["subject"] == "Unnamed"

    def test_null_filter_not_null_excludes_emails_without_alert_name(self, test_regular_user: FixtureUser) -> None:
        """nullFilter='not_null' should exclude emails with no alert_name."""

        test_regular_user.create_job_email(subject="Named", alert_name="Python jobs")
        test_regular_user.create_job_email(subject="Unnamed", alert_name=None)

        filters = json.dumps({"alert_name": {"type": "number", "min": None, "max": None, "nullFilter": "not_null"}})
        response = test_regular_user.client.get(self.endpoint, params={"filters": filters})

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total_filtered"] == 1
        assert data["items"][0]["subject"] == "Named"

    def test_null_filter_all_returns_everything(self, test_regular_user: FixtureUser) -> None:
        """nullFilter='all' should not filter on nullability."""

        test_regular_user.create_job_email(subject="Named", alert_name="Python jobs")
        test_regular_user.create_job_email(subject="Unnamed", alert_name=None)

        filters = json.dumps({"alert_name": {"type": "number", "min": None, "max": None, "nullFilter": "all"}})
        response = test_regular_user.client.get(self.endpoint, params={"filters": filters})

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["total_filtered"] == 2

    # --------------------------------------------------- DATE FILTER --------------------------------------------------

    def test_date_filter_from(self, test_regular_user: FixtureUser) -> None:
        """Date filter with 'from' should exclude emails received before the date."""

        test_regular_user.create_job_email(subject="Old", date_received=dt.datetime(2020, 1, 1, tzinfo=dt.timezone.utc))
        test_regular_user.create_job_email(
            subject="Recent", date_received=dt.datetime(2099, 6, 15, tzinfo=dt.timezone.utc)
        )

        filters = json.dumps({"date_received": {"type": "date", "from": "2025-01-01", "to": None}})
        response = test_regular_user.client.get(self.endpoint, params={"filters": filters})

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total_filtered"] == 1
        assert data["items"][0]["subject"] == "Recent"

    def test_date_filter_range(self, test_regular_user: FixtureUser) -> None:
        """Date filter with from and to should return emails within the range."""

        test_regular_user.create_job_email(
            subject="Early", date_received=dt.datetime(2025, 3, 1, tzinfo=dt.timezone.utc)
        )
        test_regular_user.create_job_email(
            subject="Mid", date_received=dt.datetime(2025, 3, 15, tzinfo=dt.timezone.utc)
        )
        test_regular_user.create_job_email(
            subject="Late", date_received=dt.datetime(2025, 4, 10, tzinfo=dt.timezone.utc)
        )

        filters = json.dumps({"date_received": {"type": "date", "from": "2025-03-10", "to": "2025-03-31"}})
        response = test_regular_user.client.get(self.endpoint, params={"filters": filters})

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total_filtered"] == 1
        assert data["items"][0]["subject"] == "Mid"

    # -------------------------------------------- MULTIPLE FILTERS COMBINED -------------------------------------------

    def test_multiple_filters_combined(self, test_regular_user: FixtureUser) -> None:
        """Multiple filters should be combined with AND logic."""

        test_regular_user.create_job_email(subject="Python on LinkedIn", platform="linkedin")
        test_regular_user.create_job_email(subject="Python on Indeed", platform="indeed")
        test_regular_user.create_job_email(subject="Java on LinkedIn", platform="linkedin")

        filters = json.dumps(
            {
                "subject": {"type": "text", "value": "python"},
                "platform": {"type": "select", "selected": ["linkedin"]},
            }
        )
        response = test_regular_user.client.get(self.endpoint, params={"filters": filters})

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total_filtered"] == 1
        assert data["items"][0]["subject"] == "Python on LinkedIn"

    # ------------------------------------------- EMPTY / INVALID FILTERS ----------------------------------------------

    def test_empty_filters_returns_all(self, test_regular_user: FixtureUser) -> None:
        """Empty filters JSON should return all emails (no filtering)."""

        test_regular_user.create_job_email(subject="Email1")
        test_regular_user.create_job_email(subject="Email2")

        response = test_regular_user.client.get(self.endpoint, params={"filters": json.dumps({})})

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["total_filtered"] >= 2

    def test_no_filters_param_returns_all(self, test_regular_user: FixtureUser) -> None:
        """Omitting the filters param entirely should return all emails."""

        test_regular_user.create_job_email(subject="Email1")

        response = test_regular_user.client.get(self.endpoint)

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["total_filtered"] >= 1

    def test_filter_on_unknown_column_is_ignored(self, test_regular_user: FixtureUser) -> None:
        """Filters referencing non-existent columns should be silently ignored."""

        test_regular_user.create_job_email(subject="Email1")

        filters = json.dumps({"nonexistent_column": {"type": "text", "value": "test"}})
        response = test_regular_user.client.get(self.endpoint, params={"filters": filters})

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["total_filtered"] >= 1


class TestJobEmailUndefinedMethods:
    ENDPOINT = "/job-alert-emails"
    DEFINED_ACTIONS = []
    UNDEFINED_ACTIONS = ["GET_ALL", "PUT", "POST", "GET_ONE", "DELETE"]

    @pytest.mark.parametrize(
        "http_method,path_suffix,expected_status",
        make_undefined_method_params(DEFINED_ACTIONS, UNDEFINED_ACTIONS),
    )
    def test_undefined_methods(
        self,
        http_method,
        path_suffix,
        expected_status,
        test_admin_user: FixtureUser,
        test_regular_user: FixtureUser,
    ):
        response = test_admin_user.client.request(http_method, f"{self.ENDPOINT}{path_suffix}")
        assert response.status_code == expected_status
        response = test_regular_user.client.request(http_method, f"{self.ENDPOINT}{path_suffix}")
        assert response.status_code == expected_status
