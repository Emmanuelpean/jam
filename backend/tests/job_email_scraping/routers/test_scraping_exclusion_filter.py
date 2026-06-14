"""Tests for Job Scraping routers."""

import random

from starlette import status

from app import models
from app.job_email_scraping import schemas
from tests.conftest import CRUDTestBase
from tests.utils.create_data.utils import create_db_entries
from tests.utils.test_data.job_scraping import SCRAPING_FILTER_DATA


def _make_scraped_job(session, owner_id: int, service_log_id: int, **kwargs) -> models.ScrapedJob:
    """Create a minimal active scraped job for preview testing."""
    data = {
        "external_job_id": f"preview_{random.random()}",
        "platform": "test",
        "is_active": True,
        "is_imported": False,
        "owner_id": owner_id,
        "service_log_id": service_log_id,
        **kwargs,
    }
    return create_db_entries(session, models.ScrapedJob, data)[0]


class TestScrapingFilters(CRUDTestBase):
    endpoint = "/scraping-exclusion-filters"
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

    # ----------------------------------------------------- DELETE -----------------------------------------------------

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


# ----------------------------------------------- EXCLUSION FILTER PREVIEW --------------------------------------------


class TestScrapingFilterPreview:
    endpoint = "/scraping-exclusion-filters/preview/paged"

    # -------------------------------------------------- BASIC ---------------------------------------------------------

    def test_preview_returns_200(self, regular_user_client, test_job_scraping_service_logs) -> None:
        """Should return 200 with the expected pagination shape."""

        response = regular_user_client.get(
            self.endpoint,
            params={
                "filter_type": "title",
                "filter_operator": "contains",
                "filter_value": "test",
            },
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        for field in ("items", "total", "total_filtered", "page", "page_size", "total_pages"):
            assert field in data

    def test_preview_returns_matching_jobs(
        self, session, regular_user_client, test_users, test_job_scraping_service_logs
    ) -> None:
        """Should return only jobs that match the filter rule."""
        log_id = test_job_scraping_service_logs[0].id
        owner_id = test_users[0].id
        _make_scraped_job(session, owner_id, log_id, title="Senior Python Developer")
        _make_scraped_job(session, owner_id, log_id, title="Junior Developer")

        response = regular_user_client.get(
            self.endpoint,
            params={
                "filter_type": "title",
                "filter_operator": "contains",
                "filter_value": "Senior",
            },
        )
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["title"] == "Senior Python Developer"

    def test_preview_empty_result(self, regular_user_client, test_job_scraping_service_logs) -> None:
        """Should return zero items when no jobs match."""
        response = regular_user_client.get(
            self.endpoint,
            params={
                "filter_type": "title",
                "filter_operator": "contains",
                "filter_value": "zzz_no_match",
            },
        )
        data = response.json()
        assert data["total"] == 0
        assert data["items"] == []

    # ------------------------------------------------- PAGINATION -----------------------------------------------------

    def test_preview_pagination_first_page(
        self, session, regular_user_client, test_users, test_job_scraping_service_logs
    ) -> None:
        """First page should return page_size items and correct totals."""
        log_id = test_job_scraping_service_logs[0].id
        owner_id = test_users[0].id
        for i in range(5):
            _make_scraped_job(session, owner_id, log_id, company="PaginateCorp", title=f"Job {i}")

        response = regular_user_client.get(
            self.endpoint,
            params={
                "filter_type": "company",
                "filter_operator": "equals",
                "filter_value": "PaginateCorp",
                "page": 0,
                "page_size": 2,
            },
        )
        data = response.json()
        assert data["total"] == 5
        assert len(data["items"]) == 2
        assert data["page"] == 0
        assert data["page_size"] == 2
        assert data["total_pages"] == 3

    def test_preview_pagination_second_page(
        self, session, regular_user_client, test_users, test_job_scraping_service_logs
    ) -> None:
        """Second page should return the remainder."""
        log_id = test_job_scraping_service_logs[0].id
        owner_id = test_users[0].id
        for i in range(3):
            _make_scraped_job(session, owner_id, log_id, company="Page2Corp", title=f"Job {i}")

        response = regular_user_client.get(
            self.endpoint,
            params={
                "filter_type": "company",
                "filter_operator": "equals",
                "filter_value": "Page2Corp",
                "page": 1,
                "page_size": 2,
            },
        )
        data = response.json()
        assert data["page"] == 1
        assert len(data["items"]) == 1

    # --------------------------------------------------- SEARCH -------------------------------------------------------

    def test_preview_search_narrows_results(
        self, session, regular_user_client, test_users, test_job_scraping_service_logs
    ) -> None:
        """Search term should further filter results by title, company, or location."""
        log_id = test_job_scraping_service_logs[0].id
        owner_id = test_users[0].id
        _make_scraped_job(session, owner_id, log_id, company="SearchCorp", title="Python Developer")
        _make_scraped_job(session, owner_id, log_id, company="SearchCorp", title="Java Developer")

        response = regular_user_client.get(
            self.endpoint,
            params={
                "filter_type": "company",
                "filter_operator": "equals",
                "filter_value": "SearchCorp",
                "search": "Python",
            },
        )
        data = response.json()
        assert data["total_filtered"] == 1
        assert data["items"][0]["title"] == "Python Developer"

    # ----------------------------------------------- CASE SENSITIVITY ------------------------------------------------

    def test_preview_case_sensitive_no_match(
        self, session, regular_user_client, test_users, test_job_scraping_service_logs
    ) -> None:
        """Case-sensitive filter should not match when casing differs."""
        log_id = test_job_scraping_service_logs[0].id
        owner_id = test_users[0].id
        _make_scraped_job(session, owner_id, log_id, title="CaseSensitiveTitle")

        response = regular_user_client.get(
            self.endpoint,
            params={
                "filter_type": "title",
                "filter_operator": "contains",
                "filter_value": "casesensitivetitle",
                "case_sensitive": True,
            },
        )
        assert response.json()["total"] == 0

    def test_preview_case_insensitive_matches(
        self, session, regular_user_client, test_users, test_job_scraping_service_logs
    ) -> None:
        """Case-insensitive filter should match regardless of casing."""
        log_id = test_job_scraping_service_logs[0].id
        owner_id = test_users[0].id
        _make_scraped_job(session, owner_id, log_id, title="CaseSensitiveTitle")

        response = regular_user_client.get(
            self.endpoint,
            params={
                "filter_type": "title",
                "filter_operator": "contains",
                "filter_value": "casesensitivetitle",
                "case_sensitive": False,
            },
        )
        assert response.json()["total"] == 1

    # --------------------------------------------- OWNERSHIP / FILTERING ---------------------------------------------

    def test_preview_respects_ownership(
        self, session, regular_user_client, test_users, test_job_scraping_service_logs
    ) -> None:
        """Preview should only return the requesting user's jobs."""
        log_id = test_job_scraping_service_logs[0].id
        _make_scraped_job(session, test_users[0].id, log_id, company="OwnerCorp", title="Job A")
        _make_scraped_job(session, test_users[1].id, log_id, company="OwnerCorp", title="Job B")

        response = regular_user_client.get(
            self.endpoint, params={"filter_type": "company", "filter_operator": "equals", "filter_value": "OwnerCorp"}
        )
        assert response.json()["total"] == 1

    def test_preview_excludes_imported_jobs(
        self, session, regular_user_client, test_users, test_job_scraping_service_logs
    ) -> None:
        """Imported jobs should not appear in preview results."""
        log_id = test_job_scraping_service_logs[0].id
        owner_id = test_users[0].id
        _make_scraped_job(session, owner_id, log_id, title="ImportedJob", is_imported=True)
        _make_scraped_job(session, owner_id, log_id, title="ImportedJob", is_imported=False)

        response = regular_user_client.get(
            self.endpoint,
            params={
                "filter_type": "title",
                "filter_operator": "equals",
                "filter_value": "ImportedJob",
            },
        )
        assert response.json()["total"] == 1

    def test_preview_excludes_inactive_jobs(
        self, session, regular_user_client, test_users, test_job_scraping_service_logs
    ) -> None:
        """Inactive jobs should not appear in preview results."""
        log_id = test_job_scraping_service_logs[0].id
        owner_id = test_users[0].id
        _make_scraped_job(session, owner_id, log_id, title="InactiveJob", is_active=False)
        _make_scraped_job(session, owner_id, log_id, title="InactiveJob", is_active=True)

        response = regular_user_client.get(
            self.endpoint,
            params={
                "filter_type": "title",
                "filter_operator": "equals",
                "filter_value": "InactiveJob",
            },
        )
        assert response.json()["total"] == 1

    # ------------------------------------------------ AUTHENTICATION --------------------------------------------------

    def test_preview_unauthenticated(self, client) -> None:
        """Should return 401 when not authenticated."""
        response = client.get(
            self.endpoint,
            params={
                "filter_type": "title",
                "filter_operator": "contains",
                "filter_value": "test",
            },
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
