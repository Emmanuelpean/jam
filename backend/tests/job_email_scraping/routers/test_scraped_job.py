"""Tests for Job Scraping routers."""

import datetime as dt
import json

import pytest
from starlette import status

from app import models
from app.job_email_scraping import schemas
from tests.conftest import CRUDTestBase, make_undefined_method_params
from tests.utils.create_data.utils import create_db_entries


class TestScrapedJobsByEmail:
    """Test suite for GET /scraped-jobs/by-email/{email_id}"""

    endpoint = "/scraped-jobs/by-email"

    def test_get_scraped_jobs_for_email(self, regular_user_client, test_scraped_jobs, test_job_alert_emails) -> None:
        """Should return scraped jobs linked to an email owned by the user"""

        email = test_job_alert_emails[0]
        response = regular_user_client.get(f"{self.endpoint}/{email.id}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == len(email.jobs)
        returned_ids = {item["id"] for item in data}
        expected_ids = {job.id for job in email.jobs}
        assert returned_ids == expected_ids

    def test_get_scraped_jobs_for_email_with_few_jobs(
        self, admin_client, test_scraped_jobs, test_job_alert_emails
    ) -> None:
        """Should return correct number of scraped jobs for an email with fewer links"""

        # Email at index 3 belongs to admin user and has 2 scraped jobs
        email = test_job_alert_emails[3]
        response = admin_client.get(f"{self.endpoint}/{email.id}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == len(email.jobs)

    def test_not_found_nonexistent_email(self, regular_user_client, test_scraped_jobs) -> None:
        """Should return 404 when email doesn't exist"""

        response = regular_user_client.get(f"{self.endpoint}/99999")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_not_found_other_users_email(self, regular_user_client, test_scraped_jobs, test_job_alert_emails) -> None:
        """Should return 404 when email belongs to another user"""

        # Index 3 belongs to admin user (owner_id=2 in test data)
        admin_email = test_job_alert_emails[3]
        response = regular_user_client.get(f"{self.endpoint}/{admin_email.id}")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_unauthenticated(self, client, test_job_alert_emails) -> None:
        """Should return 401 when not authenticated"""

        response = client.get(f"{self.endpoint}/{test_job_alert_emails[0].id}")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


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
        response = client.get(self.endpoint + "/paged/?page=1&page_size=5&show_past_deadline=true")
        assert response.status_code == status.HTTP_200_OK
        scraped_jobs = response.json()
        assert scraped_jobs["total"] == 50
        assert len(scraped_jobs["items"]) == 5

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
        assert scraped_jobs["total"] == 50
        assert scraped_jobs["total_filtered"] == 47
        assert len(scraped_jobs["items"]) == 5

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
        assert response.json()["total"] == 3
        assert response.json()["total_filtered"] == 2

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
        assert data["total"] == 50
        assert len(data["items"]) == 10
        assert all(isinstance(item, int) for item in data["items"])


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
        assert data["total_filtered"] == 1
        assert data["items"][0]["title"] == "Senior Python Developer"

    def test_text_filter_on_company(self, session, regular_user_client, setup):
        """Text filter should match company name."""

        self._create_job(session, setup.user.id, setup.service_log_id, title="A", company="Acme Corp")
        self._create_job(session, setup.user.id, setup.service_log_id, title="B", company="Beta Inc")

        filters = json.dumps({"company": {"type": "text", "value": "acme"}})
        response = regular_user_client.get(self.endpoint, params={"filters": filters, "show_past_deadline": "true"})

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["total_filtered"] == 1
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
        assert data["total_filtered"] == 2
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
        assert data["total_filtered"] == 2
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
        assert response.json()["total_filtered"] == 1
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
        assert data["total_filtered"] == 1
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
        assert data["total_filtered"] == 1
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
        assert data["total_filtered"] == 1
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
        assert response.json()["total_filtered"] == 2

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
        assert data["total_filtered"] == 1
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
        assert data["total_filtered"] == 1
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
        assert data["total_filtered"] == 1
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
        assert data["total_filtered"] == 1
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
        assert response.json()["total_filtered"] >= 2

    def test_no_filters_param_returns_all(self, session, regular_user_client, setup):
        """Omitting the filters param entirely should return all jobs."""

        self._create_job(session, setup.user.id, setup.service_log_id, title="Job1")

        response = regular_user_client.get(self.endpoint, params={"show_past_deadline": "true"})

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["total_filtered"] >= 1

    def test_filter_on_unknown_column_is_ignored(self, session, regular_user_client, setup):
        """Filters referencing non-existent columns should be silently ignored."""

        self._create_job(session, setup.user.id, setup.service_log_id, title="Job1")

        filters = json.dumps({"nonexistent_column": {"type": "text", "value": "test"}})
        response = regular_user_client.get(self.endpoint, params={"filters": filters, "show_past_deadline": "true"})

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["total_filtered"] >= 1


class TestScrapedJobCRUDAdminUser(CRUDTestBase):
    endpoint = "/scraped-jobs"
    out_schema = schemas.ScrapedJobOut
    test_data_ref = "test_scraped_jobs"
    actions_to_test = ["get_all"]
    admin_only = True


class TestScrapedJobRegularUserUndefinedMethods:
    ENDPOINT = "/scraped-jobs"
    DEFINED_ACTIONS = ["PUT", "GET_ALL"]
    UNDEFINED_ACTIONS = ["POST", "GET_ONE", "DELETE"]

    @pytest.mark.parametrize(
        "http_method,path_suffix,expected_status",
        make_undefined_method_params(DEFINED_ACTIONS, UNDEFINED_ACTIONS),
    )
    def test_undefined_methods(self, admin_client, regular_user_client, http_method, path_suffix, expected_status):
        response = admin_client.request(http_method, f"{self.ENDPOINT}{path_suffix}")
        assert response.status_code == expected_status
        response = regular_user_client.request(http_method, f"{self.ENDPOINT}{path_suffix}")
        assert response.status_code == expected_status
