"""Tests for Job Scraping routers."""

import datetime as dt

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
