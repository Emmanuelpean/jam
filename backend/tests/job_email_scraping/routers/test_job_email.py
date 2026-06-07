"""Tests for Job Scraping routers."""

import datetime as dt
import json
import uuid

import pytest
from starlette import status

from app import models
from tests.conftest import make_undefined_method_params
from tests.utils.create_data.utils import create_db_entries


class TestJobEmailsByScrapedJob:
    """Test suite for GET /job-alert-emails/by-scraped-job/{job_id}"""

    endpoint = "/job-alert-emails/by-scraped-job"

    def test_get_emails_for_scraped_job(self, regular_user_client, test_scraped_jobs) -> None:
        """Should return emails linked to a scraped job owned by the user"""

        job = test_scraped_jobs[0]
        response = regular_user_client.get(f"{self.endpoint}/{job.id}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == len(job.emails)
        returned_ids = {item["id"] for item in data}
        expected_ids = {email.id for email in job.emails}
        assert returned_ids == expected_ids

    def test_get_emails_for_job_with_multiple_emails(self, regular_user_client, test_scraped_jobs) -> None:
        """Should return multiple emails when a scraped job is linked to several emails"""

        # Scraped job at index 1 is linked to emails at indices 0 and 2
        job = test_scraped_jobs[1]
        response = regular_user_client.get(f"{self.endpoint}/{job.id}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == len(job.emails)
        assert len(data) > 1

    def test_not_found_nonexistent_job(self, regular_user_client, test_scraped_jobs) -> None:
        """Should return 404 when scraped job doesn't exist"""

        response = regular_user_client.get(f"{self.endpoint}/99999")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_not_found_other_users_job(self, regular_user_client, test_scraped_jobs) -> None:
        """Should return 404 when scraped job belongs to another user"""

        # Index 5 belongs to admin user (owner_id=2 in test data)
        admin_job = test_scraped_jobs[5]
        response = regular_user_client.get(f"{self.endpoint}/{admin_job.id}")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_unauthenticated(self, client, test_scraped_jobs) -> None:
        """Should return 401 when not authenticated"""

        response = client.get(f"{self.endpoint}/{test_scraped_jobs[0].id}")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestJobAlertEmailsPaged:
    """Test suite for GET /job-alert-emails/paged"""

    endpoint = "/job-alert-emails/paged"

    def test_get_paged_default_params(self, regular_user_client, test_job_alert_emails) -> None:
        """Should return paginated emails for the current user with default params"""

        response = regular_user_client.get(self.endpoint)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 4  # Regular user owns 4 emails
        assert data["page"] == 0
        assert data["page_size"] == 10
        assert len(data["items"]) == 4

    def test_pagination(self, regular_user_client, test_job_alert_emails) -> None:
        """Should respect page and page_size parameters"""

        response = regular_user_client.get(self.endpoint, params={"page": 0, "page_size": 2})

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 4
        assert data["page_size"] == 2
        assert len(data["items"]) == 2
        assert data["total_pages"] == 2

    def test_pagination_second_page(self, regular_user_client, test_job_alert_emails) -> None:
        """Should return the correct items for the second page"""

        response = regular_user_client.get(self.endpoint, params={"page": 1, "page_size": 2})

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 4
        assert len(data["items"]) == 2
        assert data["page"] == 1

    def test_sort_by_date_received_desc(self, regular_user_client, test_job_alert_emails) -> None:
        """Should sort by date_received descending by default"""

        response = regular_user_client.get(self.endpoint)

        assert response.status_code == status.HTTP_200_OK
        items = response.json()["items"]
        dates = [item["date_received"] for item in items]
        assert dates == sorted(dates, reverse=True)

    def test_sort_by_date_received_asc(self, regular_user_client, test_job_alert_emails) -> None:
        """Should sort by date_received ascending when specified"""

        response = regular_user_client.get(self.endpoint, params={"sort_direction": "asc"})

        assert response.status_code == status.HTTP_200_OK
        items = response.json()["items"]
        dates = [item["date_received"] for item in items]
        assert dates == sorted(dates)

    def test_sort_by_subject(self, regular_user_client, test_job_alert_emails) -> None:
        """Should sort by subject when specified"""

        response = regular_user_client.get(self.endpoint, params={"sort_by": "subject", "sort_direction": "asc"})

        assert response.status_code == status.HTTP_200_OK
        items = response.json()["items"]
        subjects = [item["subject"] for item in items]
        assert subjects == sorted(subjects)

    def test_search_by_subject(self, regular_user_client, test_job_alert_emails) -> None:
        """Should filter emails by search term matching subject"""

        response = regular_user_client.get(self.endpoint, params={"search": "Python"})

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] >= 1
        for item in data["items"]:
            assert any(
                "python" in (item.get(field) or "").lower() for field in ["subject", "sender", "platform", "alert_name"]
            )

    def test_search_by_platform(self, regular_user_client, test_job_alert_emails) -> None:
        """Should filter emails by search term matching platform"""

        response = regular_user_client.get(self.endpoint, params={"search": "indeed"})

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] >= 1
        for item in data["items"]:
            assert any(
                "indeed" in (item.get(field) or "").lower() for field in ["subject", "sender", "platform", "alert_name"]
            )

    def test_search_no_results(self, regular_user_client, test_job_alert_emails) -> None:
        """Should return empty results when search term matches nothing"""

        response = regular_user_client.get(self.endpoint, params={"search": "nonexistent_xyz_123"})

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 4
        assert data["total_filtered"] == 0
        assert len(data["items"]) == 0

    def test_only_returns_own_emails(self, regular_user_client, test_job_alert_emails) -> None:
        """Should only return emails belonging to the authenticated user"""

        response = regular_user_client.get(self.endpoint, params={"page_size": 100})

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        # Regular user owns 4 emails, not 12 total
        assert data["total"] == 4

    def test_unauthenticated(self, client, test_job_alert_emails) -> None:
        """Should return 401 when not authenticated"""

        response = client.get(self.endpoint)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestJobAlertEmailsPagedFilters:
    """Tests for the JSON `filters` query parameter on /job-alert-emails/paged."""

    endpoint = "/job-alert-emails/paged"

    @staticmethod
    def _create_email(session, owner_id: int, service_log_id: int, **kwargs) -> models.JobEmail:
        """Helper to create a job alert email with sensible defaults."""

        data = {
            "external_email_id": f"filter_test_{uuid.uuid4()}",
            "subject": kwargs.pop("subject", "Job Alert"),
            "sender": kwargs.pop("sender", "alerts@example.com"),
            "date_received": kwargs.pop("date_received", dt.datetime.now(dt.timezone.utc)),
            "platform": kwargs.pop("platform", "linkedin"),
            "body": kwargs.pop("body", "You have new job matches."),
            "job_found_n": kwargs.pop("job_found_n", 5),
            "owner_id": owner_id,
            "service_log_id": service_log_id,
            **kwargs,
        }
        return create_db_entries(session, models.JobEmail, data)[0]

    @pytest.fixture()
    def setup(self, session, test_regular_user, test_job_scraping_service_logs):
        """Provide common objects needed by every test in this class."""

        class Ctx:
            """Context object for the test."""

            user = test_regular_user
            service_log_id = test_job_scraping_service_logs[0].id

        return Ctx()

    # --------------------------------------------------- TEXT FILTER --------------------------------------------------

    def test_text_filter_on_subject(self, session, regular_user_client, setup):
        """Text filter should match subject via case-insensitive substring."""

        self._create_email(session, setup.user.id, setup.service_log_id, subject="Python Developer Roles")
        self._create_email(session, setup.user.id, setup.service_log_id, subject="Java Engineer Openings")
        self._create_email(session, setup.user.id, setup.service_log_id, subject="Data Scientist Positions")

        filters = json.dumps({"subject": {"type": "text", "value": "python"}})
        response = regular_user_client.get(self.endpoint, params={"filters": filters})

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total_filtered"] == 1
        assert data["items"][0]["subject"] == "Python Developer Roles"

    def test_text_filter_on_sender(self, session, regular_user_client, setup):
        """Text filter should match sender address."""

        self._create_email(session, setup.user.id, setup.service_log_id, sender="jobalerts@linkedin.com")
        self._create_email(session, setup.user.id, setup.service_log_id, sender="noreply@indeed.com")

        filters = json.dumps({"sender": {"type": "text", "value": "linkedin"}})
        response = regular_user_client.get(self.endpoint, params={"filters": filters})

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["total_filtered"] == 1
        assert response.json()["items"][0]["sender"] == "jobalerts@linkedin.com"

    # -------------------------------------------------- SELECT FILTER -------------------------------------------------

    def test_select_filter_on_platform(self, session, regular_user_client, setup):
        """Select filter should match exact platform values."""

        self._create_email(session, setup.user.id, setup.service_log_id, platform="linkedin")
        self._create_email(session, setup.user.id, setup.service_log_id, platform="indeed")
        self._create_email(session, setup.user.id, setup.service_log_id, platform="nhs")

        filters = json.dumps({"platform": {"type": "select", "selected": ["indeed", "nhs"]}})
        response = regular_user_client.get(self.endpoint, params={"filters": filters})

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total_filtered"] == 2
        platforms = {item["platform"] for item in data["items"]}
        assert platforms == {"indeed", "nhs"}

    # -------------------------------------------------- NUMBER FILTER -------------------------------------------------

    def test_number_filter_min_on_job_found_n(self, session, regular_user_client, setup):
        """Number filter with min should return emails with job_found_n >= value."""

        self._create_email(session, setup.user.id, setup.service_log_id, subject="Few", job_found_n=2)
        self._create_email(session, setup.user.id, setup.service_log_id, subject="Some", job_found_n=10)
        self._create_email(session, setup.user.id, setup.service_log_id, subject="Many", job_found_n=50)

        filters = json.dumps({"job_found_n": {"type": "number", "min": 9, "max": None}})
        response = regular_user_client.get(self.endpoint, params={"filters": filters})

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total_filtered"] == 2
        subjects = {item["subject"] for item in data["items"]}
        assert subjects == {"Some", "Many"}

    def test_number_filter_range_on_job_found_n(self, session, regular_user_client, setup):
        """Number filter with both min and max should return emails in range."""

        self._create_email(session, setup.user.id, setup.service_log_id, subject="Low", job_found_n=1)
        self._create_email(session, setup.user.id, setup.service_log_id, subject="Mid", job_found_n=20)
        self._create_email(session, setup.user.id, setup.service_log_id, subject="High", job_found_n=100)

        filters = json.dumps({"job_found_n": {"type": "number", "min": 10, "max": 50}})
        response = regular_user_client.get(self.endpoint, params={"filters": filters})

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["total_filtered"] == 1
        assert response.json()["items"][0]["subject"] == "Mid"

    # ------------------------------------------ NULL FILTER (nullFilter) ----------------------------------------------

    def test_null_filter_null_shows_only_emails_without_alert_name(self, session, regular_user_client, setup):
        """nullFilter='null' should show only emails with no alert_name."""

        self._create_email(session, setup.user.id, setup.service_log_id, subject="Named", alert_name="Python jobs")
        self._create_email(session, setup.user.id, setup.service_log_id, subject="Unnamed", alert_name=None)

        filters = json.dumps({"alert_name": {"type": "number", "min": None, "max": None, "nullFilter": "null"}})
        response = regular_user_client.get(self.endpoint, params={"filters": filters})

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total_filtered"] == 1
        assert data["items"][0]["subject"] == "Unnamed"

    def test_null_filter_not_null_excludes_emails_without_alert_name(self, session, regular_user_client, setup):
        """nullFilter='not_null' should exclude emails with no alert_name."""

        self._create_email(session, setup.user.id, setup.service_log_id, subject="Named", alert_name="Python jobs")
        self._create_email(session, setup.user.id, setup.service_log_id, subject="Unnamed", alert_name=None)

        filters = json.dumps({"alert_name": {"type": "number", "min": None, "max": None, "nullFilter": "not_null"}})
        response = regular_user_client.get(self.endpoint, params={"filters": filters})

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total_filtered"] == 1
        assert data["items"][0]["subject"] == "Named"

    def test_null_filter_all_returns_everything(self, session, regular_user_client, setup):
        """nullFilter='all' should not filter on nullability."""

        self._create_email(session, setup.user.id, setup.service_log_id, subject="Named", alert_name="Python jobs")
        self._create_email(session, setup.user.id, setup.service_log_id, subject="Unnamed", alert_name=None)

        filters = json.dumps({"alert_name": {"type": "number", "min": None, "max": None, "nullFilter": "all"}})
        response = regular_user_client.get(self.endpoint, params={"filters": filters})

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["total_filtered"] == 2

    # --------------------------------------------------- DATE FILTER --------------------------------------------------

    def test_date_filter_from(self, session, regular_user_client, setup):
        """Date filter with 'from' should exclude emails received before the date."""

        self._create_email(
            session,
            setup.user.id,
            setup.service_log_id,
            subject="Old",
            date_received=dt.datetime(2020, 1, 1, tzinfo=dt.timezone.utc),
        )
        self._create_email(
            session,
            setup.user.id,
            setup.service_log_id,
            subject="Recent",
            date_received=dt.datetime(2099, 6, 15, tzinfo=dt.timezone.utc),
        )

        filters = json.dumps({"date_received": {"type": "date", "from": "2025-01-01", "to": None}})
        response = regular_user_client.get(self.endpoint, params={"filters": filters})

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total_filtered"] == 1
        assert data["items"][0]["subject"] == "Recent"

    def test_date_filter_range(self, session, regular_user_client, setup):
        """Date filter with from and to should return emails within the range."""

        self._create_email(
            session,
            setup.user.id,
            setup.service_log_id,
            subject="Early",
            date_received=dt.datetime(2025, 3, 1, tzinfo=dt.timezone.utc),
        )
        self._create_email(
            session,
            setup.user.id,
            setup.service_log_id,
            subject="Mid",
            date_received=dt.datetime(2025, 3, 15, tzinfo=dt.timezone.utc),
        )
        self._create_email(
            session,
            setup.user.id,
            setup.service_log_id,
            subject="Late",
            date_received=dt.datetime(2025, 4, 10, tzinfo=dt.timezone.utc),
        )

        filters = json.dumps({"date_received": {"type": "date", "from": "2025-03-10", "to": "2025-03-31"}})
        response = regular_user_client.get(self.endpoint, params={"filters": filters})

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total_filtered"] == 1
        assert data["items"][0]["subject"] == "Mid"

    # -------------------------------------------- MULTIPLE FILTERS COMBINED -------------------------------------------

    def test_multiple_filters_combined(self, session, regular_user_client, setup):
        """Multiple filters should be combined with AND logic."""

        self._create_email(
            session, setup.user.id, setup.service_log_id, subject="Python on LinkedIn", platform="linkedin"
        )
        self._create_email(session, setup.user.id, setup.service_log_id, subject="Python on Indeed", platform="indeed")
        self._create_email(
            session, setup.user.id, setup.service_log_id, subject="Java on LinkedIn", platform="linkedin"
        )

        filters = json.dumps(
            {
                "subject": {"type": "text", "value": "python"},
                "platform": {"type": "select", "selected": ["linkedin"]},
            }
        )
        response = regular_user_client.get(self.endpoint, params={"filters": filters})

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total_filtered"] == 1
        assert data["items"][0]["subject"] == "Python on LinkedIn"

    # ------------------------------------------- EMPTY / INVALID FILTERS ----------------------------------------------

    def test_empty_filters_returns_all(self, session, regular_user_client, setup):
        """Empty filters JSON should return all emails (no filtering)."""

        self._create_email(session, setup.user.id, setup.service_log_id, subject="Email1")
        self._create_email(session, setup.user.id, setup.service_log_id, subject="Email2")

        response = regular_user_client.get(self.endpoint, params={"filters": json.dumps({})})

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["total_filtered"] >= 2

    def test_no_filters_param_returns_all(self, session, regular_user_client, setup):
        """Omitting the filters param entirely should return all emails."""

        self._create_email(session, setup.user.id, setup.service_log_id, subject="Email1")

        response = regular_user_client.get(self.endpoint)

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["total_filtered"] >= 1

    def test_filter_on_unknown_column_is_ignored(self, session, regular_user_client, setup):
        """Filters referencing non-existent columns should be silently ignored."""

        self._create_email(session, setup.user.id, setup.service_log_id, subject="Email1")

        filters = json.dumps({"nonexistent_column": {"type": "text", "value": "test"}})
        response = regular_user_client.get(self.endpoint, params={"filters": filters})

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
    def test_undefined_methods(self, admin_client, regular_user_client, http_method, path_suffix, expected_status):
        response = admin_client.request(http_method, f"{self.ENDPOINT}{path_suffix}")
        assert response.status_code == expected_status
        response = regular_user_client.request(http_method, f"{self.ENDPOINT}{path_suffix}")
        assert response.status_code == expected_status
