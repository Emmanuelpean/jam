"""Tests for Job Scraping routers."""

import datetime as dt

import pytest
from starlette import status

from tests.conftest import make_undefined_method_params


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


class TestUndefinedMethods:
    ENDPOINT = "//job-scraping-service-logs"
    DEFINED_ACTIONS = ["GET_ALL"]
    UNDEFINED_ACTIONS = ["PUT", "POST", "GET_ONE", "DELETE"]

    @pytest.mark.parametrize(
        "http_method,path_suffix,expected_status",
        make_undefined_method_params(DEFINED_ACTIONS, UNDEFINED_ACTIONS),
    )
    def test_undefined_methods(self, admin_client, regular_user_client, http_method, path_suffix, expected_status):
        response = admin_client.request(http_method, f"{self.ENDPOINT}{path_suffix}")
        assert response.status_code == expected_status
