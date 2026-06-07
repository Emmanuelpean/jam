"""Tests for Job Scraping routers."""

import datetime as dt
import json
import uuid

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
            """Context object for tests in this class."""

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

        filters = json.dumps(
            {"job_rating.overall_score": {"type": "number", "min": None, "max": None, "nullFilter": "not_null"}}
        )
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

        filters = json.dumps(
            {"job_rating.overall_score": {"type": "number", "min": None, "max": None, "nullFilter": "null"}}
        )
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

        filters = json.dumps(
            {"job_rating.overall_score": {"type": "number", "min": None, "max": None, "nullFilter": "all"}}
        )
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

        filters = json.dumps(
            {"job_rating.overall_score": {"type": "number", "min": 5, "max": None, "nullFilter": "not_null"}}
        )
        response = regular_user_client.get(self.endpoint, params={"filters": filters, "show_past_deadline": "true"})

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total_filtered"] == 1
        assert data["items"][0]["title"] == "Score7"

    # --------------------------------------------------- DATE FILTER --------------------------------------------------

    def test_date_filter_from(self, session, regular_user_client, setup):
        """Date filter with 'from' should exclude jobs with deadline before the date."""

        self._create_job(
            session,
            setup.user.id,
            setup.service_log_id,
            title="Past",
            deadline=dt.datetime(2020, 1, 1, tzinfo=dt.timezone.utc),
        )
        self._create_job(
            session,
            setup.user.id,
            setup.service_log_id,
            title="Future",
            deadline=dt.datetime(2099, 6, 15, tzinfo=dt.timezone.utc),
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
            session,
            setup.user.id,
            setup.service_log_id,
            title="Early",
            deadline=dt.datetime(2025, 3, 1, tzinfo=dt.timezone.utc),
        )
        self._create_job(
            session,
            setup.user.id,
            setup.service_log_id,
            title="Mid",
            deadline=dt.datetime(2025, 3, 15, tzinfo=dt.timezone.utc),
        )
        self._create_job(
            session,
            setup.user.id,
            setup.service_log_id,
            title="Late",
            deadline=dt.datetime(2025, 4, 10, tzinfo=dt.timezone.utc),
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
            session,
            setup.user.id,
            setup.service_log_id,
            title="Python at Acme",
            company="Acme",
            platform="linkedin",
        )
        self._create_job(
            session,
            setup.user.id,
            setup.service_log_id,
            title="Python at Beta",
            company="Beta",
            platform="indeed",
        )
        self._create_job(
            session,
            setup.user.id,
            setup.service_log_id,
            title="Java at Acme",
            company="Acme",
            platform="linkedin",
        )

        filters = json.dumps(
            {
                "title": {"type": "text", "value": "python"},
                "platform": {"type": "select", "selected": ["linkedin"]},
            }
        )
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


class TestFavouritesOnly:
    """Tests for the favourites_only query parameter on /scraped-jobs/paged."""

    endpoint = "/scraped-jobs/paged"

    @staticmethod
    def _create_job(session, owner_id: int, service_log_id: int, **kwargs) -> models.ScrapedJob:
        return create_db_entries(
            session,
            models.ScrapedJob,
            {
                "external_job_id": f"fav_test_{id(kwargs)}_{kwargs.get('title', '')}",
                "platform": kwargs.pop("platform", "linkedin"),
                "owner_id": owner_id,
                "is_processed": True,
                "is_scraped": True,
                "is_active": True,
                "is_imported": False,
                "service_log_id": service_log_id,
                **kwargs,
            },
        )[0]

    @staticmethod
    def _create_fav_filter(session, owner_id: int, **kwargs) -> models.ScrapingFavouriteFilter:
        return create_db_entries(
            session,
            models.ScrapingFavouriteFilter,
            {
                "owner_id": owner_id,
                "is_active": True,
                **kwargs,
            },
        )[0]

    @pytest.fixture()
    def setup(self, session, test_regular_user, test_job_scraping_service_logs):
        """Create a test setup with a user and a service log."""

        class Ctx:
            """Context manager for test setup."""

            user = test_regular_user
            service_log_id = test_job_scraping_service_logs[0].id

        return Ctx()

    def test_no_active_filters_returns_empty(self, session, regular_user_client, setup):
        """favourites_only=True with no active favourite filters should return an empty result set."""

        self._create_job(session, setup.user.id, setup.service_log_id, title="Any Job")

        response = regular_user_client.get(
            self.endpoint, params={"favourites_only": "true", "show_past_deadline": "true"}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total_filtered"] == 0
        assert data["items"] == []

    def test_matching_filter_returns_only_matched_jobs(self, session, regular_user_client, setup):
        """favourites_only=True should return only jobs matching an active favourite filter."""

        self._create_job(session, setup.user.id, setup.service_log_id, title="Python Engineer")
        self._create_job(session, setup.user.id, setup.service_log_id, title="Java Developer")
        self._create_fav_filter(session, setup.user.id, type="title", operator="contains", value="Python")

        response = regular_user_client.get(
            self.endpoint, params={"favourites_only": "true", "show_past_deadline": "true"}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total_filtered"] == 1
        assert data["items"][0]["title"] == "Python Engineer"

    def test_multiple_filters_use_or_logic(self, session, regular_user_client, setup):
        """Multiple active favourite filters should be combined with OR — a job matching any one is included."""

        self._create_job(session, setup.user.id, setup.service_log_id, title="Python Engineer")
        self._create_job(session, setup.user.id, setup.service_log_id, title="Data Scientist")
        self._create_job(session, setup.user.id, setup.service_log_id, title="Java Developer")
        self._create_fav_filter(session, setup.user.id, type="title", operator="contains", value="Python")
        self._create_fav_filter(session, setup.user.id, type="title", operator="contains", value="Data")

        response = regular_user_client.get(
            self.endpoint, params={"favourites_only": "true", "show_past_deadline": "true"}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total_filtered"] == 2
        titles = {item["title"] for item in data["items"]}
        assert titles == {"Python Engineer", "Data Scientist"}

    def test_inactive_filters_are_ignored(self, session, regular_user_client, setup):
        """Inactive favourite filters should not be applied, resulting in an empty set."""

        self._create_job(session, setup.user.id, setup.service_log_id, title="Python Engineer")
        self._create_fav_filter(
            session, setup.user.id, type="title", operator="contains", value="Python", is_active=False
        )

        response = regular_user_client.get(
            self.endpoint, params={"favourites_only": "true", "show_past_deadline": "true"}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total_filtered"] == 0

    def test_false_does_not_apply_favourite_filtering(self, session, regular_user_client, setup):
        """favourites_only=False should return all eligible jobs, ignoring favourite filters."""

        self._create_job(session, setup.user.id, setup.service_log_id, title="Python Engineer")
        self._create_job(session, setup.user.id, setup.service_log_id, title="Java Developer")
        self._create_fav_filter(session, setup.user.id, type="title", operator="contains", value="Python")

        response = regular_user_client.get(
            self.endpoint, params={"favourites_only": "false", "show_past_deadline": "true"}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total_filtered"] == 2

    def test_does_not_return_other_users_jobs(self, session, regular_user_client, test_admin_user, setup):
        """Jobs belonging to another user are never returned, even if a filter would match."""

        self._create_job(session, test_admin_user.id, setup.service_log_id, title="Python Engineer")
        self._create_fav_filter(session, setup.user.id, type="title", operator="contains", value="Python")

        response = regular_user_client.get(
            self.endpoint, params={"favourites_only": "true", "show_past_deadline": "true"}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total_filtered"] == 0

    def test_other_users_filters_do_not_apply(self, session, regular_user_client, test_admin_user, setup):
        """Favourite filters belonging to another user should not be applied."""

        self._create_job(session, setup.user.id, setup.service_log_id, title="Python Engineer")
        self._create_fav_filter(session, test_admin_user.id, type="title", operator="contains", value="Python")

        response = regular_user_client.get(
            self.endpoint, params={"favourites_only": "true", "show_past_deadline": "true"}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total_filtered"] == 0

    def test_base_filters_still_applied(self, session, regular_user_client, setup):
        """Imported and inactive jobs should be excluded even when they match a favourite filter."""

        self._create_job(session, setup.user.id, setup.service_log_id, title="Python Imported", is_imported=True)
        self._create_job(session, setup.user.id, setup.service_log_id, title="Python Inactive", is_active=False)
        self._create_job(session, setup.user.id, setup.service_log_id, title="Python Active")
        self._create_fav_filter(session, setup.user.id, type="title", operator="contains", value="Python")

        response = regular_user_client.get(
            self.endpoint, params={"favourites_only": "true", "show_past_deadline": "true"}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total_filtered"] == 1
        assert data["items"][0]["title"] == "Python Active"

    def test_company_filter(self, session, regular_user_client, setup):
        """Favourite filter on the company field should match correctly."""

        self._create_job(session, setup.user.id, setup.service_log_id, title="Engineer", company="Acme Corp")
        self._create_job(session, setup.user.id, setup.service_log_id, title="Engineer", company="Beta Ltd")
        self._create_fav_filter(session, setup.user.id, type="company", operator="contains", value="Acme")

        response = regular_user_client.get(
            self.endpoint, params={"favourites_only": "true", "show_past_deadline": "true"}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total_filtered"] == 1
        assert data["items"][0]["company"] == "Acme Corp"

    def test_unauthenticated_returns_401(self, client, setup):
        """Unauthenticated request should return 401."""

        response = client.get(self.endpoint, params={"favourites_only": "true"})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestScrapedJobCRUDAdminUser(CRUDTestBase):
    endpoint = "/scraped-jobs"
    out_schema = schemas.ScrapedJobOut
    test_data_ref = "test_scraped_jobs"
    actions_to_test = ["get_all"]
    admin_only = True


class TestScrapedJobRegularUserUndefinedMethods:
    ENDPOINT = "/scraped-jobs"
    DEFINED_ACTIONS = ["PUT", "GET_ALL", "POST", "DELETE"]
    UNDEFINED_ACTIONS = ["GET_ONE"]

    @pytest.mark.parametrize(
        "http_method,path_suffix,expected_status",
        make_undefined_method_params(DEFINED_ACTIONS, UNDEFINED_ACTIONS),
    )
    def test_undefined_methods(self, admin_client, regular_user_client, http_method, path_suffix, expected_status):
        response = admin_client.request(http_method, f"{self.ENDPOINT}{path_suffix}")
        assert response.status_code == expected_status
        response = regular_user_client.request(http_method, f"{self.ENDPOINT}{path_suffix}")
        assert response.status_code == expected_status


class TestPlatformStats:
    endpoint = "/scraped-jobs/platform-stats"

    @staticmethod
    def _create_email(
        session,
        owner_id: int,
        service_log_id: int,
        platform: str = "linkedin",
        alert_name: str = "default",
    ) -> models.JobEmail:
        """Create a test email."""

        return create_db_entries(
            session,
            models.JobEmail,
            {
                "subject": "Test Subject",
                "sender": "Test Sender",
                "body": "Test Body",
                "date_received": dt.datetime.now(tz=dt.timezone.utc),
                "job_found_n": 20,
                "external_email_id": uuid.uuid1(),
                "owner_id": owner_id,
                "platform": platform,
                "alert_name": alert_name,
                "service_log_id": service_log_id,
            },
        )[0]

    @staticmethod
    def _create_scraped_job(
        session,
        owner_id: int,
        service_log_id: int,
        platform: str = "linkedin",
    ) -> models.ScrapedJob:
        """Create a test scraped job."""

        return create_db_entries(
            session,
            models.ScrapedJob,
            {
                "external_job_id": f"platform_stats_{uuid.uuid4()}",
                "platform": platform,
                "owner_id": owner_id,
                "is_processed": True,
                "is_scraped": True,
                "is_active": True,
                "service_log_id": service_log_id,
            },
        )[0]

    @staticmethod
    def _link_email_job(session, email: models.JobEmail, scraped_job: models.ScrapedJob) -> None:
        """Link an email and a scraped job."""

        email.jobs.append(scraped_job)
        session.commit()

    @staticmethod
    def _create_job(
        session,
        scraped_job: models.ScrapedJob,
        application_status: str | None = None,
        application_date: dt.datetime | None = None,
        applied_via: str | None = None,
        application_url: str | None = None,
    ) -> models.Job:
        """Create a test job."""

        return create_db_entries(
            session,
            models.Job,
            {
                "title": "Test Job",
                "scraped_job_id": scraped_job.id,
                "application_status": application_status,
                "owner_id": scraped_job.owner_id,
                "application_date": application_date,
                "applied_via": applied_via,
                "application_url": application_url,
            },
        )[0]

    def test_basic_counts(
        self,
        session,
        regular_user_client,
        test_regular_user,
        test_job_scraping_service_logs,
    ):
        """Counts scraped, imported, and applied correctly."""

        service_log_id = test_job_scraping_service_logs[0].id

        email = self._create_email(session, service_log_id, test_regular_user.id, "linkedin", "backend")

        # 3 scraped jobs
        sj1 = self._create_scraped_job(session, test_regular_user.id, service_log_id)
        sj2 = self._create_scraped_job(session, test_regular_user.id, service_log_id)
        sj3 = self._create_scraped_job(session, test_regular_user.id, service_log_id)

        for sj in (sj1, sj2, sj3):
            self._link_email_job(session, email, sj)

        # 2 imported
        self._create_job(session, sj1)
        self._create_job(session, sj2)

        # 1 applied
        self._create_job(session, sj1, application_status="applied")

        response = regular_user_client.get(self.endpoint)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert len(data) == 1
        expected = {
            "platform": "linkedin",
            "alert_name": "backend",
            "scraped_count": 3,
            "imported_count": 2,
            "applied_count": 1,
        }
        assert data[0] == expected

    def test_multiple_platforms_and_alerts(
        self,
        session,
        regular_user_client,
        test_regular_user,
        test_job_scraping_service_logs,
    ):
        """Groups correctly by platform and alert."""

        service_log_id = test_job_scraping_service_logs[0].id

        email1 = self._create_email(session, test_regular_user.id, service_log_id, "linkedin", "backend")
        email2 = self._create_email(session, test_regular_user.id, service_log_id, "indeed", "frontend")

        sj1 = self._create_scraped_job(session, test_regular_user.id, service_log_id, "linkedin")
        sj2 = self._create_scraped_job(session, test_regular_user.id, service_log_id, "indeed")

        self._link_email_job(session, email1, sj1)
        self._link_email_job(session, email2, sj2)

        response = regular_user_client.get(self.endpoint)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert len(data) == 2

        expected_1 = {
            "platform": "linkedin",
            "alert_name": "backend",
            "scraped_count": 1,
            "imported_count": 0,
            "applied_count": 0,
        }
        expected_2 = {
            "platform": "indeed",
            "alert_name": "frontend",
            "scraped_count": 1,
            "imported_count": 0,
            "applied_count": 0,
        }
        assert data[0] == expected_2
        assert data[1] == expected_1

    def test_ignores_other_users_data(
        self,
        session,
        regular_user_client,
        test_regular_user,
        test_admin_user,
        test_job_scraping_service_logs,
    ):
        """Should not include other users' data."""

        service_log_id = test_job_scraping_service_logs[0].id

        # Regular user data
        email_user = self._create_email(session, test_regular_user.id, service_log_id)
        sj_user = self._create_scraped_job(session, test_regular_user.id, service_log_id)
        self._link_email_job(session, email_user, sj_user)

        # Admin user data
        email_admin = self._create_email(session, test_admin_user.id, service_log_id)
        sj_admin = self._create_scraped_job(session, test_admin_user.id, service_log_id)
        self._link_email_job(session, email_admin, sj_admin)

        response = regular_user_client.get(self.endpoint)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert len(data) == 1
        assert data[0]["scraped_count"] == 1

    def test_no_jobs_returns_empty(
        self,
        regular_user_client,
    ):
        """No scraped jobs should return empty list."""

        response = regular_user_client.get(self.endpoint)

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []

    def test_unauthenticated(
        self,
        client,
    ):
        """Unauthenticated request should return 401."""

        response = client.get(self.endpoint)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_scraped_job_in_multiple_alerts_counted_in_each(
        self,
        session,
        regular_user_client,
        test_regular_user,
        test_job_scraping_service_logs,
    ):
        """A scraped job linked to two different alerts appears in both groups."""

        service_log_id = test_job_scraping_service_logs[0].id

        email_backend = self._create_email(session, test_regular_user.id, service_log_id, "linkedin", "backend")
        email_python = self._create_email(session, test_regular_user.id, service_log_id, "linkedin", "python")

        sj = self._create_scraped_job(session, test_regular_user.id, service_log_id)
        self._link_email_job(session, email_backend, sj)
        self._link_email_job(session, email_python, sj)

        response = regular_user_client.get(self.endpoint)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert len(data) == 2
        by_alert = {row["alert_name"]: row for row in data}
        assert by_alert["backend"]["scraped_count"] == 1
        assert by_alert["python"]["scraped_count"] == 1

    def test_applied_count_uses_application_date(
        self,
        session,
        regular_user_client,
        test_regular_user,
        test_job_scraping_service_logs,
    ):
        """A job with only application_date set (no status) still counts as applied."""

        service_log_id = test_job_scraping_service_logs[0].id
        email = self._create_email(session, test_regular_user.id, service_log_id)
        sj = self._create_scraped_job(session, test_regular_user.id, service_log_id)
        self._link_email_job(session, email, sj)
        self._create_job(session, sj, application_date=dt.datetime.now(tz=dt.timezone.utc))

        response = regular_user_client.get(self.endpoint)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert len(data) == 1
        assert data[0]["imported_count"] == 1
        assert data[0]["applied_count"] == 1

    def test_applied_count_uses_applied_via_and_application_url(
        self,
        session,
        regular_user_client,
        test_regular_user,
        test_job_scraping_service_logs,
    ):
        """Jobs with only applied_via or application_url set also count as applied."""

        service_log_id = test_job_scraping_service_logs[0].id
        email = self._create_email(session, test_regular_user.id, service_log_id)

        sj1 = self._create_scraped_job(session, test_regular_user.id, service_log_id)
        sj2 = self._create_scraped_job(session, test_regular_user.id, service_log_id)
        self._link_email_job(session, email, sj1)
        self._link_email_job(session, email, sj2)

        self._create_job(session, sj1, applied_via="email")
        self._create_job(session, sj2, application_url="https://example.com/apply")

        response = regular_user_client.get(self.endpoint)

        assert response.status_code == 200
        data = response.json()

        assert len(data) == 1
        assert data[0]["scraped_count"] == 2
        assert data[0]["imported_count"] == 2
        assert data[0]["applied_count"] == 2

    def test_applied_count_any_non_applied_status(
        self,
        session,
        regular_user_client,
        test_regular_user,
        test_job_scraping_service_logs,
    ):
        """interview, offer, rejected, and withdrawn statuses all count as applied."""

        service_log_id = test_job_scraping_service_logs[0].id
        email = self._create_email(session, test_regular_user.id, service_log_id)

        for application_status in ("interview", "offer", "rejected", "withdrawn"):
            sj = self._create_scraped_job(session, test_regular_user.id, service_log_id)
            self._link_email_job(session, email, sj)
            self._create_job(session, sj, application_status=application_status)

        response = regular_user_client.get(self.endpoint)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert len(data) == 1
        assert data[0]["scraped_count"] == 4
        assert data[0]["imported_count"] == 4
        assert data[0]["applied_count"] == 4

    def test_null_alert_name_grouped(
        self,
        session,
        regular_user_client,
        test_regular_user,
        test_job_scraping_service_logs,
    ):
        """Emails with no alert_name group correctly (alert_name=None)."""

        service_log_id = test_job_scraping_service_logs[0].id

        email = create_db_entries(
            session,
            models.JobEmail,
            {
                "subject": "Test Subject",
                "sender": "Test Sender",
                "body": "Test Body",
                "date_received": dt.datetime.now(tz=dt.timezone.utc),
                "job_found_n": 0,
                "external_email_id": uuid.uuid1(),
                "owner_id": test_regular_user.id,
                "platform": "linkedin",
                "alert_name": None,
                "service_log_id": service_log_id,
            },
        )[0]
        sj = self._create_scraped_job(session, test_regular_user.id, service_log_id)
        self._link_email_job(session, email, sj)

        response = regular_user_client.get(self.endpoint)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert len(data) == 1
        assert data[0]["platform"] == "linkedin"
        assert data[0]["alert_name"] is None
        assert data[0]["scraped_count"] == 1

    def test_multiple_jobs_per_scraped_job_no_double_count(
        self,
        session,
        regular_user_client,
        test_regular_user,
        test_job_scraping_service_logs,
    ):
        """A scraped job with multiple linked Jobs is counted once in imported and applied."""

        service_log_id = test_job_scraping_service_logs[0].id
        email = self._create_email(session, test_regular_user.id, service_log_id)
        sj = self._create_scraped_job(session, test_regular_user.id, service_log_id)
        self._link_email_job(session, email, sj)

        # Two jobs linked to the same scraped job: one plain import, one applied
        self._create_job(session, sj)
        self._create_job(session, sj, application_status="applied")

        response = regular_user_client.get(self.endpoint)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert len(data) == 1
        assert data[0]["scraped_count"] == 1
        assert data[0]["imported_count"] == 1
        assert data[0]["applied_count"] == 1

    def test_multiple_emails_same_alert_accumulate(
        self,
        session,
        regular_user_client,
        test_regular_user,
        test_job_scraping_service_logs,
    ):
        """Multiple emails for the same platform/alert accumulate scraped job counts."""

        service_log_id = test_job_scraping_service_logs[0].id

        email1 = self._create_email(session, test_regular_user.id, service_log_id, "indeed", "data")
        email2 = self._create_email(session, test_regular_user.id, service_log_id, "indeed", "data")

        sj1 = self._create_scraped_job(session, test_regular_user.id, service_log_id, "indeed")
        sj2 = self._create_scraped_job(session, test_regular_user.id, service_log_id, "indeed")

        self._link_email_job(session, email1, sj1)
        self._link_email_job(session, email2, sj2)

        response = regular_user_client.get(self.endpoint)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert len(data) == 1
        assert data[0]["platform"] == "indeed"
        assert data[0]["alert_name"] == "data"
        assert data[0]["scraped_count"] == 2

    def test_other_users_imported_job_not_counted(
        self,
        session,
        regular_user_client,
        test_regular_user,
        test_admin_user,
        test_job_scraping_service_logs,
    ):
        """imported_count and applied_count ignore Jobs owned by other users."""

        service_log_id = test_job_scraping_service_logs[0].id

        # Regular user has a scraped job but no linked Job
        email = self._create_email(session, test_regular_user.id, service_log_id)
        sj = self._create_scraped_job(session, test_regular_user.id, service_log_id)
        self._link_email_job(session, email, sj)

        # Admin creates a Job pointing at the regular user's scraped job (different owner)
        create_db_entries(
            session,
            models.Job,
            {
                "title": "Admin Job",
                "scraped_job_id": sj.id,
                "owner_id": test_admin_user.id,
                "application_status": "applied",
            },
        )

        response = regular_user_client.get(self.endpoint)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert len(data) == 1
        assert data[0]["imported_count"] == 0
        assert data[0]["applied_count"] == 0

    def test_same_scraped_job_in_multiple_emails_not_double_counted(
        self,
        session,
        regular_user_client,
        test_regular_user,
        test_job_scraping_service_logs,
    ):
        """A scraped job appearing in two emails of the same alert is counted once, not twice."""

        service_log_id = test_job_scraping_service_logs[0].id

        email1 = self._create_email(session, test_regular_user.id, service_log_id, "linkedin", "backend")
        email2 = self._create_email(session, test_regular_user.id, service_log_id, "linkedin", "backend")

        sj = self._create_scraped_job(session, test_regular_user.id, service_log_id)
        self._link_email_job(session, email1, sj)
        self._link_email_job(session, email2, sj)

        self._create_job(session, sj, application_status="applied")

        response = regular_user_client.get(self.endpoint)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert len(data) == 1
        assert data[0]["scraped_count"] == 1
        assert data[0]["imported_count"] == 1
        assert data[0]["applied_count"] == 1


class TestErrorsOnly:
    """Tests for the errors_only query parameter on /scraped-jobs/paged."""

    endpoint = "/scraped-jobs/paged"

    @staticmethod
    def _create_job(session, owner_id: int, service_log_id: int, **kwargs) -> models.ScrapedJob:
        return create_db_entries(
            session,
            models.ScrapedJob,
            {
                "external_job_id": f"err_test_{id(kwargs)}_{kwargs.get('title', '')}",
                "platform": kwargs.pop("platform", "linkedin"),
                "owner_id": owner_id,
                "is_processed": True,
                "is_scraped": True,
                "is_active": True,
                "is_imported": False,
                "service_log_id": service_log_id,
                **kwargs,
            },
        )[0]

    @staticmethod
    def _create_rating(
        session, scraped_job_id: int, owner_id: int, qualification_id: int = 0, **kwargs
    ) -> models.JobRating:
        return create_db_entries(
            session,
            models.JobRating,
            {
                "scraped_job_id": scraped_job_id,
                "owner_id": owner_id,
                "llm_model": kwargs.pop("llm_model", "test-model"),
                "user_qualification_id": kwargs.pop("user_qualification_id", qualification_id),
                **kwargs,
            },
        )[0]

    def test_errors_only_false_returns_normal_jobs(
        self, session, regular_user_client, test_regular_user, test_job_scraping_service_logs
    ):
        """errors_only=False should return jobs regardless of failure state."""

        self._create_job(session, test_regular_user.id, test_job_scraping_service_logs[0].id, title="Normal Job")

        response = regular_user_client.get(self.endpoint, params={"errors_only": "false"})

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total_filtered"] == 1

    def test_errors_only_excludes_normal_jobs(
        self, session, regular_user_client, test_regular_user, test_job_scraping_service_logs
    ):
        """errors_only=True should return an empty set when no jobs have failed."""

        self._create_job(session, test_regular_user.id, test_job_scraping_service_logs[0].id, title="Normal Job")

        response = regular_user_client.get(self.endpoint, params={"errors_only": "true"})

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total_filtered"] == 0
        assert data["items"] == []

    def test_errors_only_returns_failed_scrape_job(
        self, session, regular_user_client, test_regular_user, test_job_scraping_service_logs
    ):
        """A job with is_failed=True must appear when errors_only=True."""

        uid = test_regular_user.id
        slog = test_job_scraping_service_logs[0].id
        self._create_job(session, uid, slog, title="Failed Scrape", is_failed=True)
        self._create_job(session, uid, slog, title="Normal Job")

        response = regular_user_client.get(self.endpoint, params={"errors_only": "true"})

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total_filtered"] == 1
        assert data["items"][0]["title"] == "Failed Scrape"

    def test_errors_only_returns_failed_rating_job(
        self, session, regular_user_client, test_regular_user, test_job_scraping_service_logs, test_user_qualifications
    ):
        """A job whose JobRating has is_success=False must appear when errors_only=True."""

        uid = test_regular_user.id
        slog = test_job_scraping_service_logs[0].id
        qid = test_user_qualifications[0].id
        job = self._create_job(session, uid, slog, title="Failed Rating")
        self._create_rating(session, job.id, uid, qid, is_success=False)
        self._create_job(session, uid, slog, title="Normal Job")

        response = regular_user_client.get(self.endpoint, params={"errors_only": "true"})

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total_filtered"] == 1
        assert data["items"][0]["title"] == "Failed Rating"

    def test_errors_only_returns_both_failure_types(
        self, session, regular_user_client, test_regular_user, test_job_scraping_service_logs, test_user_qualifications
    ):
        """Both is_failed scrape jobs and failed-rating jobs appear together."""

        uid = test_regular_user.id
        slog = test_job_scraping_service_logs[0].id
        qid = test_user_qualifications[0].id
        self._create_job(session, uid, slog, title="Failed Scrape", is_failed=True)
        rating_job = self._create_job(session, uid, slog, title="Failed Rating")
        self._create_rating(session, rating_job.id, uid, qid, is_success=False)
        self._create_job(session, uid, slog, title="Normal Job")

        response = regular_user_client.get(self.endpoint, params={"errors_only": "true"})

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total_filtered"] == 2
        titles = {item["title"] for item in data["items"]}
        assert titles == {"Failed Scrape", "Failed Rating"}

    def test_errors_only_excludes_successful_rating(
        self, session, regular_user_client, test_regular_user, test_job_scraping_service_logs, test_user_qualifications
    ):
        """A job with a successful rating (is_success=True) is not returned."""

        uid = test_regular_user.id
        slog = test_job_scraping_service_logs[0].id
        qid = test_user_qualifications[0].id
        job = self._create_job(session, uid, slog, title="Rated OK")
        self._create_rating(session, job.id, uid, qid, is_success=True)

        response = regular_user_client.get(self.endpoint, params={"errors_only": "true"})

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total_filtered"] == 0

    def test_errors_only_excludes_imported_jobs(
        self, session, regular_user_client, test_regular_user, test_job_scraping_service_logs
    ):
        """Imported jobs with is_failed=True must still be excluded by the base filter."""

        self._create_job(
            session,
            test_regular_user.id,
            test_job_scraping_service_logs[0].id,
            title="Imported Failed",
            is_failed=True,
            is_imported=True,
        )

        response = regular_user_client.get(self.endpoint, params={"errors_only": "true"})

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total_filtered"] == 0

    def test_errors_only_excludes_inactive_jobs(
        self, session, regular_user_client, test_regular_user, test_job_scraping_service_logs
    ):
        """Inactive jobs with is_failed=True must still be excluded by the base filter."""

        self._create_job(
            session,
            test_regular_user.id,
            test_job_scraping_service_logs[0].id,
            title="Inactive Failed",
            is_failed=True,
            is_active=False,
        )

        response = regular_user_client.get(self.endpoint, params={"errors_only": "true"})

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total_filtered"] == 0

    def test_errors_only_ignores_deadline_filter(
        self, session, regular_user_client, test_regular_user, test_job_scraping_service_logs
    ):
        """errors_only=True should show failed jobs even if their deadline is in the past."""

        past_deadline = dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=5)
        self._create_job(
            session,
            test_regular_user.id,
            test_job_scraping_service_logs[0].id,
            title="Past Deadline Failed",
            is_failed=True,
            deadline=past_deadline,
        )

        response = regular_user_client.get(self.endpoint, params={"errors_only": "true"})

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total_filtered"] == 1

    def test_errors_only_does_not_return_other_users_jobs(
        self, session, regular_user_client, test_admin_user, test_job_scraping_service_logs
    ):
        """Failed jobs belonging to another user are never returned."""

        self._create_job(
            session,
            test_admin_user.id,
            test_job_scraping_service_logs[0].id,
            title="Admin Failed",
            is_failed=True,
        )

        response = regular_user_client.get(self.endpoint, params={"errors_only": "true"})

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total_filtered"] == 0


class TestGetExpired:
    """Test suite for GET /scraped-jobs/expired"""

    endpoint = "/scraped-jobs/expired"

    @staticmethod
    def _create_job(session, owner_id: int, service_log_id: int, **kwargs) -> models.ScrapedJob:
        return create_db_entries(
            session,
            models.ScrapedJob,
            {
                "external_job_id": f"expired_test_{id(kwargs)}_{kwargs.get('title', '')}",
                "platform": "linkedin",
                "owner_id": owner_id,
                "is_processed": True,
                "is_scraped": True,
                "is_active": True,
                "is_imported": False,
                "service_log_id": service_log_id,
                **kwargs,
            },
        )[0]

    def test_returns_closed_jobs(self, session, regular_user_client, test_regular_user, test_job_scraping_service_logs):
        """Should return jobs marked as closed."""

        service_log_id = test_job_scraping_service_logs[0].id
        closed = self._create_job(session, test_regular_user.id, service_log_id, title="Closed Job", is_closed=True)
        self._create_job(session, test_regular_user.id, service_log_id, title="Active Job", is_closed=False)

        response = regular_user_client.get(self.endpoint)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == closed.id

    def test_returns_past_deadline_jobs(
        self, session, regular_user_client, test_regular_user, test_job_scraping_service_logs
    ):
        """Should return jobs with a deadline in the past."""

        service_log_id = test_job_scraping_service_logs[0].id
        past = dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=1)
        future = dt.datetime.now(dt.timezone.utc) + dt.timedelta(days=1)
        expired = self._create_job(
            session, test_regular_user.id, service_log_id, title="Expired Deadline", deadline=past
        )
        self._create_job(session, test_regular_user.id, service_log_id, title="Future Deadline", deadline=future)
        self._create_job(session, test_regular_user.id, service_log_id, title="No Deadline")

        response = regular_user_client.get(self.endpoint)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == expired.id

    def test_excludes_imported_jobs(
        self, session, regular_user_client, test_regular_user, test_job_scraping_service_logs
    ):
        """Should not return jobs that have already been imported."""

        service_log_id = test_job_scraping_service_logs[0].id
        self._create_job(
            session, test_regular_user.id, service_log_id, title="Imported Closed", is_closed=True, is_imported=True
        )

        response = regular_user_client.get(self.endpoint)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 0

    def test_excludes_inactive_jobs(
        self, session, regular_user_client, test_regular_user, test_job_scraping_service_logs
    ):
        """Should not return jobs that are already inactive."""

        service_log_id = test_job_scraping_service_logs[0].id
        self._create_job(
            session, test_regular_user.id, service_log_id, title="Inactive Closed", is_closed=True, is_active=False
        )

        response = regular_user_client.get(self.endpoint)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 0

    def test_excludes_other_users_jobs(
        self, session, regular_user_client, test_admin_user, test_job_scraping_service_logs
    ):
        """Should not return expired jobs belonging to another user."""

        service_log_id = test_job_scraping_service_logs[0].id
        self._create_job(session, test_admin_user.id, service_log_id, title="Admin Closed", is_closed=True)

        response = regular_user_client.get(self.endpoint)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 0

    def test_returns_empty_when_no_expired_jobs(
        self, session, regular_user_client, test_regular_user, test_job_scraping_service_logs
    ):
        """Should return an empty list when there are no expired jobs."""

        service_log_id = test_job_scraping_service_logs[0].id
        self._create_job(session, test_regular_user.id, service_log_id, title="Normal Job")

        response = regular_user_client.get(self.endpoint)

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []

    def test_unauthenticated(self, client):
        """Should return 401 when not authenticated."""

        response = client.get(self.endpoint)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
