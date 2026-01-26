"""Tests for EIS routers."""

import datetime as dt

import pytest
from starlette import status

from app import models
from app.job_email_scraping import schemas
from tests.conftest import CRUDTestBase
from tests.utils.create_data import add_to_db
from tests.utils.test_data.job_scraping_service import JOB_EMAIL_DATA, SCRAPING_FILTER_DATA


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
    required_fixture = ["test_eis_service_logs"]
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
    ) -> None:
        """Test retrieving all scraped jobs for the authorised user that are scraped, not imported, active"""

        self.get_user_data(test_users, test_scraped_jobs)
        client = self._get_authorised_client(authorised_clients)
        response = client.get(self.endpoint + "/paged/?page=1&page_size=5&show_past_deadline=true")
        assert response.status_code == status.HTTP_200_OK
        scraped_jobs = response.json()
        assert scraped_jobs["total"] == 51
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
        assert len(scraped_jobs["items"]) == 5

    def test_get_count(self, test_users, authorised_clients, test_scraped_jobs) -> None:
        """Test retrieving count of scraped jobs for the authorised user that are scraped, not imported, active"""

        client = self._get_authorised_client(authorised_clients)
        response = client.get(self.endpoint + "/count")
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["count"] == 51


class TestScrapedJobCRUDAdminUser(CRUDTestBase):
    endpoint = "/scraped-jobs"
    out_schema = schemas.ScrapedJobOut
    test_data_ref = "test_scraped_jobs"
    actions_to_test = ["get_all"]
    admin_only = True


# -------------------------------------------------- EIS SERVICE LOGS --------------------------------------------------


class TestEisServiceLog:
    """Test suite for Email Ingestion Service log endpoints"""

    def test_get_service_logs_no_filters(self, admin_client, test_eis_service_logs, test_platform_stats) -> None:
        """Test retrieving all service logs without filters"""

        response = admin_client.get("/job-scraping-service-logs/")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == len(test_eis_service_logs)
        assert data[0]["run_datetime"] >= data[-1]["run_datetime"]

    def test_get_service_logs_with_start_date(self, admin_client, test_eis_service_logs, test_platform_stats) -> None:
        """Test filtering logs by start date"""

        start_date = (dt.datetime.now() - dt.timedelta(days=5)).isoformat()
        response = admin_client.get("/job-scraping-service-logs/", params={"start_date": start_date})

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        for log in data:
            assert log["run_datetime"] >= start_date

    def test_get_service_logs_with_end_date(self, admin_client, test_eis_service_logs, test_platform_stats) -> None:
        """Test filtering logs by end date"""

        end_date = (dt.datetime.now() - dt.timedelta(days=2)).isoformat()
        response = admin_client.get("/job-scraping-service-logs/", params={"end_date": end_date})

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        # Verify all logs are before end_date
        for log in data:
            assert log["run_datetime"] <= end_date

    def test_get_service_logs_with_date_range(self, admin_client, test_eis_service_logs, test_platform_stats) -> None:
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
        self, admin_client, test_eis_service_logs, test_platform_stats
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
        self, admin_client, test_eis_service_logs, test_platform_stats, limit: int
    ) -> None:
        """Test limiting number of returned logs"""

        response = admin_client.get("/job-scraping-service-logs/", params={"limit": limit})

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) <= limit

    def test_get_service_logs_combined_params(self, admin_client, test_eis_service_logs, test_platform_stats) -> None:
        """Test combining multiple query parameters"""

        response = admin_client.get("/job-scraping-service-logs/", params={"delta_days": 30, "limit": 5})

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) <= 5

    def test_get_service_logs_non_admin_forbidden(
        self, regular_user_client, test_eis_service_logs, test_platform_stats
    ) -> None:
        """Test that non-admin users cannot access service logs"""

        response = regular_user_client.get("/job-scraping-service-logs/")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_get_service_logs_unauthenticated(self, client, test_eis_service_logs, test_platform_stats) -> None:
        """Test that unauthenticated requests are rejected"""

        response = client.get("/job-scraping-service-logs/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_latest_log_success(self, admin_client, test_eis_service_logs, test_platform_stats) -> None:
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

    def test_get_latest_log_non_admin_forbidden(self, regular_user_client, test_eis_service_logs) -> None:
        """Test that non-admin users cannot access latest log"""
        response = regular_user_client.get("/job-scraping-service-logs/latest")

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_get_latest_log_unauthenticated(self, client, test_eis_service_logs) -> None:
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

        # noinspection PyArgumentList
        filters = models.ScrapingExclusionFilter(
            type="title", operator="contains", value="Some", owner_id=owner_id, **kwargs
        )
        return add_to_db(session, [filters])[0]

    def test_delete_filter_without_filtered_jobs(self, session, authorised_clients, test_users) -> None:
        """Should delete filter completely when it has no filtered jobs"""

        filter_obj = self._create_filter(session)
        response = self.delete(authorised_clients[0], filter_obj.id)
        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify filter was completely deleted from database
        deleted_filter = session.query(models.ScrapingExclusionFilter).filter_by(id=filter_obj.id).first()
        assert deleted_filter is None

    def test_delete_filter_with_filtered_jobs(
        self, session, authorised_clients, test_users, test_eis_service_logs
    ) -> None:
        """Should deactivate filter when it has filtered jobs instead of deleting"""

        filter_obj = self._create_filter(session)
        filter_id = filter_obj.id

        # Add a filtered job
        # noinspection PyArgumentList
        scraped_job = models.ScrapedJob(
            external_job_id="A",
            platform="saf",
            title="Engineer",
            exclusion_filter_id=filter_obj.id,
            owner_id=filter_obj.owner_id,
            service_log_id=test_eis_service_logs[0].id,
        )
        add_to_db(session, [scraped_job])

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
        self, session, authorised_clients, test_users, test_eis_service_logs
    ) -> None:
        """Should update existing filter when it has filtered jobs"""

        filter_obj = self._create_filter(session)
        filter_id = filter_obj.id

        # Add a filtered job
        # noinspection PyArgumentList
        scraped_job = models.ScrapedJob(
            external_job_id="A",
            platform="saf",
            title="Engineer",
            exclusion_filter_id=filter_id,
            owner_id=filter_obj.owner_id,
            service_log_id=test_eis_service_logs[0].id,
        )
        add_to_db(session, [scraped_job])

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
