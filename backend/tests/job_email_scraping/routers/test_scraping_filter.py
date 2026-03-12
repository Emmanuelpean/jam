"""Tests for Job Scraping routers."""

import datetime as dt

import pytest
from starlette import status

from app import models
from app.job_email_scraping import schemas
from tests.conftest import CRUDTestBase
from tests.utils.create_data.utils import create_db_entries
from tests.utils.test_data.job_scraping import JOB_EMAIL_DATA, SCRAPING_FILTER_DATA


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
