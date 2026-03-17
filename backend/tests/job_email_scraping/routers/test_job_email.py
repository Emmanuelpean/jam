"""Tests for Job Scraping routers."""

import pytest
from starlette import status

from tests.conftest import make_undefined_method_params


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
