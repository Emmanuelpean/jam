"""Tests for Job Scraping routers."""

import datetime as dt
import json

import pytest
from starlette import status

from app import models
from app.job_email_scraping import schemas
from tests.conftest import CRUDTestBase
from tests.utils.create_data.utils import create_db_entries
from tests.utils.test_data.job_scraping import JOB_EMAIL_DATA, SCRAPING_FILTER_DATA


# --------------------------------------------------- JOB ALERT EMAILS --------------------------------------------------


class TestJobAlertEmailCRUD(CRUDTestBase):
    endpoint = "/job-alert-emails"
    out_schema = schemas.JobEmailOut
    test_data_ref = "test_job_alert_emails"
    create_data = JOB_EMAIL_DATA
    update_data = {
        "id": 1,
        "subject": "Updated Python",
    }
    required_fixture = ["test_job_scraping_service_logs"]
    actions_to_test = ["get_all"]
    admin_only = True


# ---------------------------------------------------- SCRAPED JOBS ----------------------------------------------------


class TestScrapedJobCRUDRegularUser(CRUDTestBase):
    endpoint = "/scraped-jobs"
    out_schema = schemas.ScrapedJobOut
    test_data_ref = "test_scraped_jobs"
    update_data = {
        "id": 1,
        "is_imported": True,
    }
    actions_to_test = ["put"]

    def test_get_all(
        self,
        test_users,
        authorised_clients,
        test_scraped_jobs,
        session,
    ) -> None:
        """Test retrieving all scraped jobs for the authorised user that are scraped, not imported, active"""

        self.get_user_data(test_users, test_scraped_jobs)
        client = self._get_authorised_client(authorised_clients)
        # user = self._get_admin_authorised_user(test_users)
        response = client.get(self.endpoint + "/paged/?page=1&page_size=5&show_past_deadline=true")
        assert response.status_code == status.HTTP_200_OK
        scraped_jobs = response.json()
        assert scraped_jobs["total"] == 48
        assert len(scraped_jobs["items"]) == 5

    def test_get_all_ids_only(
        self,
        test_users,
        authorised_clients,
        test_scraped_jobs,
    ) -> None:
        """Test ids_only=true returns just a list of integer IDs instead of full objects"""

        self.get_user_data(test_users, test_scraped_jobs)
        client = self._get_authorised_client(authorised_clients)
        response = client.get(self.endpoint + "/paged/?page=0&page_size=10&show_past_deadline=true&ids_only=true")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 48
        assert len(data["items"]) == 10
        assert all(isinstance(item, int) for item in data["items"])

    def test_get_all_no_past_deadlines(
        self,
        test_users,
        authorised_clients,
        test_scraped_jobs,
    ) -> None:
        """Test retrieving all scraped jobs for the authorised user that are scraped, not imported, active"""

        self.get_user_data(test_users, test_scraped_jobs)
        client = self._get_authorised_client(authorised_clients)
        response = client.get(self.endpoint + "/paged/?page=1&page_size=5")
        assert response.status_code == status.HTTP_200_OK
        scraped_jobs = response.json()
        assert scraped_jobs["total"] == 46
        assert len(scraped_jobs["items"]) == 5

    def test_get_count(self, test_users, authorised_clients, test_scraped_jobs) -> None:
        """Test retrieving count of scraped jobs for the authorised user that are scraped, not imported, active"""

        client = self._get_authorised_client(authorised_clients)
        response = client.get(self.endpoint + "/count")
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["count"] == 48

    @staticmethod
    def _create_job(
        session, owner_id: int, service_log_id: int, created_at: dt.datetime, **kwargs
    ) -> models.ScrapedJob:
        return create_db_entries(
            session,
            models.ScrapedJob,
            {
                "external_job_id": f"since_login_job_{created_at.timestamp()}",
                "platform": "linkedin",
                "owner_id": owner_id,
                "is_processed": True,
                "title": "Test Job",
                "url": "https://example.com",
                "service_log_id": service_log_id,
                "created_at": created_at,
                **kwargs,
            },
        )[0]

    def test_since_last_login_filters_jobs_before_previous_login(
        self, session, test_regular_user, regular_user_client, test_job_scraping_service_logs
    ) -> None:
        """Jobs created before previous_login are excluded when since_last_login=True."""

        previous_login = dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=3)
        test_regular_user.previous_login = previous_login
        session.commit()

        service_log_id = test_job_scraping_service_logs[0].id
        self._create_job(session, test_regular_user.id, service_log_id, previous_login - dt.timedelta(days=1))
        self._create_job(session, test_regular_user.id, service_log_id, previous_login + dt.timedelta(hours=1))
        self._create_job(session, test_regular_user.id, service_log_id, previous_login + dt.timedelta(days=1))

        response = regular_user_client.get(self.endpoint + "/paged", params={"since_last_login": "true"})

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["total"] == 2

    def test_since_last_login_no_previous_login_returns_all_jobs(
        self, session, test_regular_user, regular_user_client, test_job_scraping_service_logs
    ) -> None:
        """All jobs are returned when since_last_login=True but the user has no previous_login."""

        test_regular_user.previous_login = None
        session.commit()

        service_log_id = test_job_scraping_service_logs[0].id
        now = dt.datetime.now(dt.timezone.utc)
        self._create_job(session, test_regular_user.id, service_log_id, now - dt.timedelta(days=10))
        self._create_job(session, test_regular_user.id, service_log_id, now - dt.timedelta(days=5))
        self._create_job(session, test_regular_user.id, service_log_id, now)

        response = regular_user_client.get(self.endpoint + "/paged", params={"since_last_login": "true"})

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["total"] == 3


class TestScrapedJobCRUDAdminUser(CRUDTestBase):
    endpoint = "/scraped-jobs"
    out_schema = schemas.ScrapedJobOut
    test_data_ref = "test_scraped_jobs"
    actions_to_test = ["get_all"]
    admin_only = True


class TestPagedFilters:
    """Tests for the JSON `filters` query parameter on /scraped-jobs/paged."""

    endpoint = "/scraped-jobs/paged"

    @staticmethod
    def _create_job(session, owner_id: int, service_log_id: int, **kwargs) -> models.ScrapedJob:
        """Helper to create a scraped job with sensible defaults."""

        data = {
            "external_job_id": f"filter_test_{id(kwargs)}_{kwargs.get('title', '')}",
            "platform": kwargs.pop("platform", "linkedin"),
            "owner_id": owner_id,
            "is_processed": True,
            "is_scraped": True,
            "is_active": True,
            "is_imported": False,
            "service_log_id": service_log_id,
            **kwargs,
        }
        return create_db_entries(session, models.ScrapedJob, data)[0]

    @staticmethod
    def _create_rating(session, scraped_job, owner_id: int, qualification_id: int, **kwargs) -> models.JobRating:
        """Helper to create a job rating for a scraped job."""

        data = {
            "scraped_job_id": scraped_job.id,
            "owner_id": owner_id,
            "user_qualification_id": qualification_id,
            "llm_model": "test-model",
            "is_success": True,
            **kwargs,
        }
        return create_db_entries(session, models.JobRating, data)[0]

    @pytest.fixture()
    def setup(self, session, test_regular_user, test_user_qualifications, test_job_scraping_service_logs):
        """Provide common objects needed by every test in this class."""

        class Ctx:
            user = test_regular_user
            service_log_id = test_job_scraping_service_logs[0].id
            qualification_id = test_user_qualifications[0].id

        return Ctx()

    # --------------------------------------------------- TEXT FILTER --------------------------------------------------

    def test_text_filter_on_title(self, session, regular_user_client, setup):
        """Text filter should match title via case-insensitive substring."""

        self._create_job(session, setup.user.id, setup.service_log_id, title="Senior Python Developer")
        self._create_job(session, setup.user.id, setup.service_log_id, title="Junior Java Developer")
        self._create_job(session, setup.user.id, setup.service_log_id, title="Data Scientist")

        filters = json.dumps({"title": {"type": "text", "value": "python"}})
        response = regular_user_client.get(self.endpoint, params={"filters": filters, "show_past_deadline": "true"})

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["title"] == "Senior Python Developer"

    def test_text_filter_on_company(self, session, regular_user_client, setup):
        """Text filter should match company name."""

        self._create_job(session, setup.user.id, setup.service_log_id, title="A", company="Acme Corp")
        self._create_job(session, setup.user.id, setup.service_log_id, title="B", company="Beta Inc")

        filters = json.dumps({"company": {"type": "text", "value": "acme"}})
        response = regular_user_client.get(self.endpoint, params={"filters": filters, "show_past_deadline": "true"})

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["total"] == 1
        assert response.json()["items"][0]["company"] == "Acme Corp"

    # -------------------------------------------------- SELECT FILTER -------------------------------------------------

    def test_select_filter_on_platform(self, session, regular_user_client, setup):
        """Select filter should match exact platform values."""

        self._create_job(session, setup.user.id, setup.service_log_id, title="A", platform="linkedin")
        self._create_job(session, setup.user.id, setup.service_log_id, title="B", platform="indeed")
        self._create_job(session, setup.user.id, setup.service_log_id, title="C", platform="nhs")

        filters = json.dumps({"platform": {"type": "select", "selected": ["indeed", "nhs"]}})
        response = regular_user_client.get(self.endpoint, params={"filters": filters, "show_past_deadline": "true"})

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 2
        platforms = {item["platform"] for item in data["items"]}
        assert platforms == {"indeed", "nhs"}

    # -------------------------------------------------- NUMBER FILTER -------------------------------------------------

    def test_number_filter_min_on_salary(self, session, regular_user_client, setup):
        """Number filter with min should return jobs with salary_min >= value."""

        self._create_job(session, setup.user.id, setup.service_log_id, title="Low", salary_min=20000)
        self._create_job(session, setup.user.id, setup.service_log_id, title="Mid", salary_min=50000)
        self._create_job(session, setup.user.id, setup.service_log_id, title="High", salary_min=80000)

        filters = json.dumps({"salary_min": {"type": "number", "min": 45000, "max": None}})
        response = regular_user_client.get(self.endpoint, params={"filters": filters, "show_past_deadline": "true"})

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 2
        titles = {item["title"] for item in data["items"]}
        assert titles == {"Mid", "High"}

    def test_number_filter_range(self, session, regular_user_client, setup):
        """Number filter with both min and max should return jobs in range."""

        self._create_job(session, setup.user.id, setup.service_log_id, title="Low", salary_min=20000)
        self._create_job(session, setup.user.id, setup.service_log_id, title="Mid", salary_min=50000)
        self._create_job(session, setup.user.id, setup.service_log_id, title="High", salary_min=80000)

        filters = json.dumps({"salary_min": {"type": "number", "min": 30000, "max": 60000}})
        response = regular_user_client.get(self.endpoint, params={"filters": filters, "show_past_deadline": "true"})

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["total"] == 1
        assert response.json()["items"][0]["title"] == "Mid"

    # --------------------------------------------- NUMBER FILTER + SCORES ---------------------------------------------

    def test_number_filter_on_overall_score(self, session, regular_user_client, setup):
        """Number filter on job_rating.overall_score should filter via the related JobRating."""

        job_a = self._create_job(session, setup.user.id, setup.service_log_id, title="Scored3")
        self._create_rating(session, job_a, setup.user.id, setup.qualification_id, overall_score=3)

        job_b = self._create_job(session, setup.user.id, setup.service_log_id, title="Scored7")
        self._create_rating(session, job_b, setup.user.id, setup.qualification_id, overall_score=7)

        job_c = self._create_job(session, setup.user.id, setup.service_log_id, title="Scored9")
        self._create_rating(session, job_c, setup.user.id, setup.qualification_id, overall_score=9)

        filters = json.dumps({"job_rating.overall_score": {"type": "number", "min": 5, "max": 8}})
        response = regular_user_client.get(self.endpoint, params={"filters": filters, "show_past_deadline": "true"})

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["title"] == "Scored7"

    # ---------------------------------------------- NULL FILTER (nullFilter) -------------------------------------------

    def test_null_filter_not_null_excludes_unscored(self, session, regular_user_client, setup):
        """nullFilter='not_null' should exclude jobs without a score."""

        job_a = self._create_job(session, setup.user.id, setup.service_log_id, title="HasScore")
        self._create_rating(session, job_a, setup.user.id, setup.qualification_id, overall_score=5)
        self._create_job(session, setup.user.id, setup.service_log_id, title="NoScore")

        filters = json.dumps({
            "job_rating.overall_score": {"type": "number", "min": None, "max": None, "nullFilter": "not_null"}
        })
        response = regular_user_client.get(self.endpoint, params={"filters": filters, "show_past_deadline": "true"})

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["title"] == "HasScore"

    def test_null_filter_null_shows_only_unscored(self, session, regular_user_client, setup):
        """nullFilter='null' should show only jobs without a score."""

        job_a = self._create_job(session, setup.user.id, setup.service_log_id, title="HasScore")
        self._create_rating(session, job_a, setup.user.id, setup.qualification_id, overall_score=5)
        self._create_job(session, setup.user.id, setup.service_log_id, title="NoScore")

        filters = json.dumps({
            "job_rating.overall_score": {"type": "number", "min": None, "max": None, "nullFilter": "null"}
        })
        response = regular_user_client.get(self.endpoint, params={"filters": filters, "show_past_deadline": "true"})

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["title"] == "NoScore"

    def test_null_filter_all_returns_everything(self, session, regular_user_client, setup):
        """nullFilter='all' (or absent) should not filter on nullability."""

        job_a = self._create_job(session, setup.user.id, setup.service_log_id, title="HasScore")
        self._create_rating(session, job_a, setup.user.id, setup.qualification_id, overall_score=5)
        self._create_job(session, setup.user.id, setup.service_log_id, title="NoScore")

        filters = json.dumps({
            "job_rating.overall_score": {"type": "number", "min": None, "max": None, "nullFilter": "all"}
        })
        response = regular_user_client.get(self.endpoint, params={"filters": filters, "show_past_deadline": "true"})

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["total"] == 2

    def test_null_filter_not_null_combined_with_range(self, session, regular_user_client, setup):
        """nullFilter='not_null' combined with a range should apply both constraints."""

        job_a = self._create_job(session, setup.user.id, setup.service_log_id, title="Score3")
        self._create_rating(session, job_a, setup.user.id, setup.qualification_id, overall_score=3)

        job_b = self._create_job(session, setup.user.id, setup.service_log_id, title="Score7")
        self._create_rating(session, job_b, setup.user.id, setup.qualification_id, overall_score=7)

        self._create_job(session, setup.user.id, setup.service_log_id, title="NoScore")

        filters = json.dumps({
            "job_rating.overall_score": {"type": "number", "min": 5, "max": None, "nullFilter": "not_null"}
        })
        response = regular_user_client.get(self.endpoint, params={"filters": filters, "show_past_deadline": "true"})

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["title"] == "Score7"

    # --------------------------------------------------- DATE FILTER --------------------------------------------------

    def test_date_filter_from(self, session, regular_user_client, setup):
        """Date filter with 'from' should exclude jobs with deadline before the date."""

        self._create_job(
            session, setup.user.id, setup.service_log_id,
            title="Past", deadline=dt.datetime(2020, 1, 1, tzinfo=dt.timezone.utc),
        )
        self._create_job(
            session, setup.user.id, setup.service_log_id,
            title="Future", deadline=dt.datetime(2099, 6, 15, tzinfo=dt.timezone.utc),
        )

        filters = json.dumps({"deadline": {"type": "date", "from": "2025-01-01", "to": None}})
        response = regular_user_client.get(self.endpoint, params={"filters": filters, "show_past_deadline": "true"})

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["title"] == "Future"

    def test_date_filter_range(self, session, regular_user_client, setup):
        """Date filter with from and to should return jobs within the range."""

        self._create_job(
            session, setup.user.id, setup.service_log_id,
            title="Early", deadline=dt.datetime(2025, 3, 1, tzinfo=dt.timezone.utc),
        )
        self._create_job(
            session, setup.user.id, setup.service_log_id,
            title="Mid", deadline=dt.datetime(2025, 3, 15, tzinfo=dt.timezone.utc),
        )
        self._create_job(
            session, setup.user.id, setup.service_log_id,
            title="Late", deadline=dt.datetime(2025, 4, 10, tzinfo=dt.timezone.utc),
        )

        filters = json.dumps({"deadline": {"type": "date", "from": "2025-03-10", "to": "2025-03-31"}})
        response = regular_user_client.get(self.endpoint, params={"filters": filters, "show_past_deadline": "true"})

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["title"] == "Mid"

    # -------------------------------------------- MULTIPLE FILTERS COMBINED -------------------------------------------

    def test_multiple_filters_combined(self, session, regular_user_client, setup):
        """Multiple filters should be combined with AND logic."""

        self._create_job(
            session, setup.user.id, setup.service_log_id,
            title="Python at Acme", company="Acme", platform="linkedin",
        )
        self._create_job(
            session, setup.user.id, setup.service_log_id,
            title="Python at Beta", company="Beta", platform="indeed",
        )
        self._create_job(
            session, setup.user.id, setup.service_log_id,
            title="Java at Acme", company="Acme", platform="linkedin",
        )

        filters = json.dumps({
            "title": {"type": "text", "value": "python"},
            "platform": {"type": "select", "selected": ["linkedin"]},
        })
        response = regular_user_client.get(self.endpoint, params={"filters": filters, "show_past_deadline": "true"})

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["title"] == "Python at Acme"

    # ------------------------------------------- EMPTY / INVALID FILTERS ----------------------------------------------

    def test_empty_filters_returns_all(self, session, regular_user_client, setup):
        """Empty filters JSON should return all jobs (no filtering)."""

        self._create_job(session, setup.user.id, setup.service_log_id, title="Job1")
        self._create_job(session, setup.user.id, setup.service_log_id, title="Job2")

        response = regular_user_client.get(
            self.endpoint, params={"filters": json.dumps({}), "show_past_deadline": "true"}
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["total"] >= 2

    def test_no_filters_param_returns_all(self, session, regular_user_client, setup):
        """Omitting the filters param entirely should return all jobs."""

        self._create_job(session, setup.user.id, setup.service_log_id, title="Job1")

        response = regular_user_client.get(self.endpoint, params={"show_past_deadline": "true"})

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["total"] >= 1

    def test_filter_on_unknown_column_is_ignored(self, session, regular_user_client, setup):
        """Filters referencing non-existent columns should be silently ignored."""

        self._create_job(session, setup.user.id, setup.service_log_id, title="Job1")

        filters = json.dumps({"nonexistent_column": {"type": "text", "value": "test"}})
        response = regular_user_client.get(self.endpoint, params={"filters": filters, "show_past_deadline": "true"})

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["total"] >= 1


# ------------------------------------=--------- JOB SCRAPING SERVICE LOGS ---------------------------------------------


class TestJobScrapingServiceLog:
    """Test suite for Email Ingestion Service log endpoints"""

    def test_get_service_logs_no_filters(
        self, admin_client, test_job_scraping_service_logs, test_platform_stats
    ) -> None:
        """Test retrieving all service logs without filters"""

        response = admin_client.get("/job-scraping-service-logs/")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == len(test_job_scraping_service_logs)
        assert data[0]["run_datetime"] >= data[-1]["run_datetime"]

    def test_get_service_logs_with_start_date(
        self, admin_client, test_job_scraping_service_logs, test_platform_stats
    ) -> None:
        """Test filtering logs by start date"""

        start_date = (dt.datetime.now() - dt.timedelta(days=5)).isoformat()
        response = admin_client.get("/job-scraping-service-logs/", params={"start_date": start_date})

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        for log in data:
            assert log["run_datetime"] >= start_date

    def test_get_service_logs_with_end_date(
        self, admin_client, test_job_scraping_service_logs, test_platform_stats
    ) -> None:
        """Test filtering logs by end date"""

        end_date = (dt.datetime.now() - dt.timedelta(days=2)).isoformat()
        response = admin_client.get("/job-scraping-service-logs/", params={"end_date": end_date})

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        # Verify all logs are before end_date
        for log in data:
            assert log["run_datetime"] <= end_date

    def test_get_service_logs_with_date_range(
        self, admin_client, test_job_scraping_service_logs, test_platform_stats
    ) -> None:
        """Test filtering logs by date range"""

        start_date = (dt.datetime.now() - dt.timedelta(days=7)).isoformat()
        end_date = (dt.datetime.now() - dt.timedelta(days=1)).isoformat()
        response = admin_client.get(
            "/job-scraping-service-logs/", params={"start_date": start_date, "end_date": end_date}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        # Verify all logs are within range
        for log in data:
            assert start_date <= log["run_datetime"] <= end_date

    def test_get_service_logs_with_date_range_in_url(
        self, admin_client, test_job_scraping_service_logs, test_platform_stats
    ) -> None:
        """Test filtering logs by date range"""

        start_date = (dt.datetime.now() - dt.timedelta(days=7)).isoformat()
        end_date = (dt.datetime.now() - dt.timedelta(days=1)).isoformat()
        response = admin_client.get(f"/job-scraping-service-logs/?start_date={start_date}&end_date={end_date}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        # Verify all logs are within range
        for log in data:
            assert start_date <= log["run_datetime"] <= end_date

    @pytest.mark.parametrize("limit", [1, 5, 10])
    def test_get_service_logs_with_limit(
        self, admin_client, test_job_scraping_service_logs, test_platform_stats, limit: int
    ) -> None:
        """Test limiting number of returned logs"""

        response = admin_client.get("/job-scraping-service-logs/", params={"limit": limit})

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) <= limit

    def test_get_service_logs_combined_params(
        self, admin_client, test_job_scraping_service_logs, test_platform_stats
    ) -> None:
        """Test combining multiple query parameters"""

        response = admin_client.get("/job-scraping-service-logs/", params={"delta_days": 30, "limit": 5})

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) <= 5

    def test_get_service_logs_non_admin_forbidden(
        self, regular_user_client, test_job_scraping_service_logs, test_platform_stats
    ) -> None:
        """Test that non-admin users cannot access service logs"""

        response = regular_user_client.get("/job-scraping-service-logs/")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_get_service_logs_unauthenticated(
        self, client, test_job_scraping_service_logs, test_platform_stats
    ) -> None:
        """Test that unauthenticated requests are rejected"""

        response = client.get("/job-scraping-service-logs/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_latest_log_success(self, admin_client, test_job_scraping_service_logs, test_platform_stats) -> None:
        """Test retrieving the latest service log"""

        response = admin_client.get("/job-scraping-service-logs/latest")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "run_datetime" in data

        # Verify it's the most recent log
        all_logs_response = admin_client.get("/job-scraping-service-logs/")
        all_logs = all_logs_response.json()
        assert data["run_datetime"] == all_logs[0]["run_datetime"]

    def test_get_latest_log_no_logs(self, admin_client) -> None:
        """Test retrieving latest log when no logs exist"""

        response = admin_client.get("/job-scraping-service-logs/latest")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "No service logs found" in response.json()["detail"]

    def test_get_latest_log_non_admin_forbidden(self, regular_user_client, test_job_scraping_service_logs) -> None:
        """Test that non-admin users cannot access latest log"""
        response = regular_user_client.get("/job-scraping-service-logs/latest")

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_get_latest_log_unauthenticated(self, client, test_job_scraping_service_logs) -> None:
        """Test that unauthenticated requests to latest are rejected"""

        response = client.get("/job-scraping-service-logs/latest")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


# ------------------------------------------------- SCRAPED JOB FILTERS ------------------------------------------------


class TestScrapingFilters(CRUDTestBase):
    endpoint = "/scraping-filters"
    out_schema = schemas.ScrapingFilterOut
    test_data_ref = "test_scraping_filters"
    create_data = SCRAPING_FILTER_DATA
    update_data = {
        "id": 1,
        "type": "title",
    }
    required_fixture = ["test_scraped_jobs"]
    actions_to_test = ["get_all", "get_one", "post"]

    @staticmethod
    def _create_filter(session, owner_id: int = 1, **kwargs) -> models.ScrapingExclusionFilter:
        """Helper to create a scraped job filter"""

        data = {"type": "title", "operator": "contains", "value": "Some", "owner_id": owner_id, **kwargs}
        return create_db_entries(session, models.ScrapingExclusionFilter, data)[0]

    def test_delete_filter_without_filtered_jobs(self, session, authorised_clients, test_users) -> None:
        """Should delete filter completely when it has no filtered jobs"""

        filter_obj = self._create_filter(session)
        response = self.delete(authorised_clients[0], filter_obj.id)
        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify filter was completely deleted from database
        deleted_filter = session.query(models.ScrapingExclusionFilter).filter_by(id=filter_obj.id).first()
        assert deleted_filter is None

    def test_delete_filter_with_filtered_jobs(
        self, session, authorised_clients, test_users, test_job_scraping_service_logs
    ) -> None:
        """Should deactivate filter when it has filtered jobs instead of deleting"""

        filter_obj = self._create_filter(session)
        filter_id = filter_obj.id

        # Add a filtered job
        scraped_job_data = {
            "external_job_id": "A",
            "platform": "saf",
            "title": "Engineer",
            "exclusion_filter_id": filter_obj.id,
            "owner_id": filter_obj.owner_id,
            "service_log_id": test_job_scraping_service_logs[0].id,
        }
        create_db_entries(session, models.ScrapedJob, scraped_job_data)

        response = self.delete(authorised_clients[0], filter_id)
        assert response.status_code == status.HTTP_409_CONFLICT

    def test_delete_filter_not_found(self, authorised_clients) -> None:
        """Should return 403 when filter doesn't exist"""

        response = self.delete(authorised_clients[0], 99999)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_delete_filter_wrong_owner(self, session, authorised_clients, test_users) -> None:
        """Should return 403 when trying to delete another user's filter"""

        filter_id = self._create_filter(session, 2).id
        response = self.delete(authorised_clients[0], filter_id)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_delete_filter_unauthenticated(self, session, client, test_users) -> None:
        """Should return 401 when not authenticated"""

        filter_obj = self._create_filter(session)
        response = self.delete(client, filter_obj.id)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    # ----------------------------------------------------- UPDATE -----------------------------------------------------

    def test_update_filter_with_filtered_jobs(
        self, session, authorised_clients, test_users, test_job_scraping_service_logs
    ) -> None:
        """Should update existing filter when it has filtered jobs"""

        filter_obj = self._create_filter(session)
        filter_id = filter_obj.id

        # Add a filtered job
        scraped_job_data = {
            "external_job_id": "A",
            "platform": "saf",
            "title": "Engineer",
            "exclusion_filter_id": filter_id,
            "owner_id": filter_obj.owner_id,
            "service_log_id": test_job_scraping_service_logs[0].id,
        }
        create_db_entries(session, models.ScrapedJob, scraped_job_data)

        update_data = {"value": "Updated Title"}
        response = self.put(authorised_clients[0], filter_id, update_data)

        assert response.status_code == status.HTTP_409_CONFLICT

    def test_update_filter_without_filtered_jobs_creates_new(self, session, authorised_clients, test_users) -> None:
        """Should create new filter when original has no filtered jobs"""

        filter_obj = self._create_filter(session)
        filter_id = filter_obj.id
        filter_operator = filter_obj.operator
        user_id = test_users[0].id

        update_data = {"value": "Updated Title"}
        response = self.put(authorised_clients[0], filter_id, update_data)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == filter_id
        assert data["value"] == update_data["value"]
        assert data["operator"] == filter_operator
        assert data["owner_id"] == user_id

    def test_update_filter_not_found(self, authorised_clients) -> None:
        """Should return 403 when filter doesn't exist"""

        update_data = {"title": "Updated"}
        response = self.put(authorised_clients[0], 99999, update_data)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_update_filter_wrong_owner(self, session, authorised_clients, test_users) -> None:
        """Should return 403 when trying to update another user's filter"""

        filter_id = self._create_filter(session, 2).id
        response = self.put(authorised_clients[0], filter_id, {"value": "Updated"})
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_update_filter_unauthenticated(self, session, client, test_users) -> None:
        """Should return 401 when not authenticated"""

        filter_obj = self._create_filter(session)
        response = self.put(client, filter_obj.id, {"value": "Updated"})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


# ------------------------------------------- FORWARDING CONFIRMATION LINKS --------------------------------------------


class TestForwardingConfirmationLinks:
    """Test suite for forwarding confirmation link endpoints"""

    endpoint = "/forwarding-confirmation-links"

    @staticmethod
    def _create_link(session, owner_id: int = 1, is_used: bool = False, **kwargs) -> models.ForwardingConfirmationLink:
        """Helper to create a forwarding confirmation link"""

        data = {
            "email_external_id": "ext_123",
            "url": "https://example.com/confirm",
            "platform": "gmail",
            "is_used": is_used,
            "owner_id": owner_id,
            **kwargs,
        }
        return create_db_entries(session, models.ForwardingConfirmationLink, data)[0]

    # ------------------------------------------------- GET /pending ---------------------------------------------------

    def test_get_pending_returns_unused_link(self, session, regular_user_client) -> None:
        """Should return the latest unused confirmation link"""

        link = self._create_link(session)
        response = regular_user_client.get(f"{self.endpoint}/pending")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == link.id
        assert data["url"] == "https://example.com/confirm"
        assert data["platform"] == "gmail"

    def test_get_pending_returns_none_when_latest_is_used(self, session, regular_user_client) -> None:
        """Should return null when the latest link has been used"""

        self._create_link(session, is_used=True)
        response = regular_user_client.get(f"{self.endpoint}/pending")

        assert response.status_code == status.HTTP_200_OK
        assert response.json() is None

    def test_get_pending_returns_none_when_no_links(self, regular_user_client) -> None:
        """Should return null when no links exist for the user"""

        response = regular_user_client.get(f"{self.endpoint}/pending")

        assert response.status_code == status.HTTP_200_OK
        assert response.json() is None

    def test_get_pending_returns_latest_link(self, session, regular_user_client) -> None:
        """Should return the most recently created link"""

        self._create_link(session, url="https://example.com/old")
        latest = self._create_link(session, url="https://example.com/new")

        response = regular_user_client.get(f"{self.endpoint}/pending")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == latest.id
        assert data["url"] == "https://example.com/new"

    def test_get_pending_only_returns_own_links(self, session, regular_user_client) -> None:
        """Should not return links belonging to other users"""

        self._create_link(session, owner_id=2)
        response = regular_user_client.get(f"{self.endpoint}/pending")

        assert response.status_code == status.HTTP_200_OK
        assert response.json() is None

    def test_get_pending_unauthenticated(self, client) -> None:
        """Should return 401 when not authenticated"""

        response = client.get(f"{self.endpoint}/pending")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    # ------------------------------------------------ PUT /{link_id} --------------------------------------------------

    def test_update_link_success(self, session, regular_user_client) -> None:
        """Should successfully mark a link as used"""

        link = self._create_link(session)
        response = regular_user_client.put(f"{self.endpoint}/{link.id}", json={"is_used": True})

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == link.id
        assert data["url"] == link.url
        assert data["platform"] == link.platform

    def test_update_link_not_found(self, regular_user_client) -> None:
        """Should return 404 when link doesn't exist"""

        response = regular_user_client.put(f"{self.endpoint}/99999", json={"is_used": True})
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_link_wrong_owner(self, session, regular_user_client) -> None:
        """Should return 404 when link belongs to another user"""

        link = self._create_link(session, owner_id=2)
        response = regular_user_client.put(f"{self.endpoint}/{link.id}", json={"is_used": True})
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_link_unauthenticated(self, session, client, test_users) -> None:
        """Should return 401 when not authenticated"""

        link = self._create_link(session)
        response = client.put(f"{self.endpoint}/{link.id}", json={"is_used": True})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
