"""Tests for Job Scraping routers."""

from sqlalchemy.orm import Session
from starlette import status
from starlette.testclient import TestClient

from app import models
from app.job_email_scraping import schemas
from tests.conftest import CRUDTestBase
from tests.fixtures.users import FixtureUser
from tests.utils.test_data.job_scraping import SCRAPING_FILTER_DATA


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

    # ----------------------------------------------------- DELETE -----------------------------------------------------

    def test_delete_filter_without_filtered_jobs(self, session: Session, test_regular_user: FixtureUser) -> None:
        """Should delete filter completely when it has no filtered jobs"""

        filter_obj = test_regular_user.create_scraping_exclusion_filter()
        response = self.delete(test_regular_user.client, filter_obj.id)
        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify filter was completely deleted from database
        deleted_filter = session.query(models.ScrapingExclusionFilter).filter_by(id=filter_obj.id).first()
        assert deleted_filter is None

    def test_delete_filter_with_filtered_jobs(self, test_regular_user: FixtureUser) -> None:
        """Should deactivate filter when it has filtered jobs instead of deleting"""

        filter_obj = test_regular_user.create_scraping_exclusion_filter()
        test_regular_user.create_scraped_job(title="Engineer", exclusion_filter_id=filter_obj.id)

        response = self.delete(test_regular_user.client, filter_obj.id)
        assert response.status_code == status.HTTP_409_CONFLICT

    def test_delete_filter_not_found(self, test_regular_user: FixtureUser) -> None:
        """Should return 403 when filter doesn't exist"""

        response = self.delete(test_regular_user.client, 99999)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_delete_filter_wrong_owner(self, test_regular_user: FixtureUser, test_admin_user: FixtureUser) -> None:
        """Should return 403 when trying to delete another user's filter"""

        filter_id = test_admin_user.create_scraping_exclusion_filter().id
        response = self.delete(test_regular_user.client, filter_id)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_delete_filter_unauthenticated(self, client: TestClient, test_regular_user: FixtureUser) -> None:
        """Should return 401 when not authenticated"""

        filter_obj = test_regular_user.create_scraping_exclusion_filter()
        response = self.delete(client, filter_obj.id)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    # ----------------------------------------------------- UPDATE -----------------------------------------------------

    def test_update_filter_with_filtered_jobs(self, test_regular_user: FixtureUser) -> None:
        """Should update existing filter when it has filtered jobs"""

        filter_obj = test_regular_user.create_scraping_exclusion_filter()
        test_regular_user.create_scraped_job(title="Engineer", exclusion_filter_id=filter_obj.id)

        response = self.put(test_regular_user.client, filter_obj.id, {"value": "Updated Title"})

        assert response.status_code == status.HTTP_409_CONFLICT

    def test_update_filter_without_filtered_jobs_creates_new(self, test_regular_user: FixtureUser) -> None:
        """Should create new filter when original has no filtered jobs"""

        filter_obj = test_regular_user.create_scraping_exclusion_filter()
        filter_id = filter_obj.id
        filter_operator = filter_obj.operator

        update_data = {"value": "Updated Title"}
        response = self.put(test_regular_user.client, filter_id, update_data)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == filter_id
        assert data["value"] == update_data["value"]
        assert data["operator"] == filter_operator
        assert data["owner_id"] == test_regular_user.id

    def test_update_filter_not_found(self, test_regular_user: FixtureUser) -> None:
        """Should return 403 when filter doesn't exist"""

        update_data = {"title": "Updated"}
        response = self.put(test_regular_user.client, 99999, update_data)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_update_filter_wrong_owner(self, test_regular_user: FixtureUser, test_admin_user: FixtureUser) -> None:
        """Should return 403 when trying to update another user's filter"""

        filter_id = test_admin_user.create_scraping_exclusion_filter().id
        response = self.put(test_regular_user.client, filter_id, {"value": "Updated"})
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_update_filter_unauthenticated(self, client: TestClient, test_regular_user: FixtureUser) -> None:
        """Should return 401 when not authenticated"""

        filter_obj = test_regular_user.create_scraping_exclusion_filter()
        response = self.put(client, filter_obj.id, {"value": "Updated"})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestScrapingFilterPreview:
    endpoint = "/scraping-exclusion-filters/preview/paged"

    # -------------------------------------------------- BASIC ---------------------------------------------------------

    def test_preview_returns_200(self, test_regular_user: FixtureUser) -> None:
        """Should return 200 with the expected pagination shape."""

        response = test_regular_user.client.get(
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

    def test_preview_returns_matching_jobs(self, test_regular_user: FixtureUser) -> None:
        """Should return only jobs that match the filter rule."""
        test_regular_user.create_scraped_job(title="Senior Python Developer")
        test_regular_user.create_scraped_job(title="Junior Developer")

        response = test_regular_user.client.get(
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

    def test_preview_empty_result(self, test_regular_user: FixtureUser) -> None:
        """Should return zero items when no jobs match."""
        response = test_regular_user.client.get(
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

    def test_preview_pagination_first_page(self, test_regular_user: FixtureUser) -> None:
        """First page should return page_size items and correct totals."""
        for i in range(5):
            test_regular_user.create_scraped_job(company="PaginateCorp", title=f"Job {i}")

        response = test_regular_user.client.get(
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

    def test_preview_pagination_second_page(self, test_regular_user: FixtureUser) -> None:
        """Second page should return the remainder."""
        for i in range(3):
            test_regular_user.create_scraped_job(company="Page2Corp", title=f"Job {i}")

        response = test_regular_user.client.get(
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

    def test_preview_search_narrows_results(self, test_regular_user: FixtureUser) -> None:
        """Search term should further filter results by title, company, or location."""
        test_regular_user.create_scraped_job(company="SearchCorp", title="Python Developer")
        test_regular_user.create_scraped_job(company="SearchCorp", title="Java Developer")

        response = test_regular_user.client.get(
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

    def test_preview_case_sensitive_no_match(self, test_regular_user: FixtureUser) -> None:
        """Case-sensitive filter should not match when casing differs."""
        test_regular_user.create_scraped_job(title="CaseSensitiveTitle")

        response = test_regular_user.client.get(
            self.endpoint,
            params={
                "filter_type": "title",
                "filter_operator": "contains",
                "filter_value": "casesensitivetitle",
                "case_sensitive": True,
            },
        )
        assert response.json()["total"] == 0

    def test_preview_case_insensitive_matches(self, test_regular_user: FixtureUser) -> None:
        """Case-insensitive filter should match regardless of casing."""
        test_regular_user.create_scraped_job(title="CaseSensitiveTitle")

        response = test_regular_user.client.get(
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

    def test_preview_respects_ownership(self, test_regular_user: FixtureUser, test_admin_user: FixtureUser) -> None:
        """Preview should only return the requesting user's jobs."""
        test_regular_user.create_scraped_job(company="OwnerCorp", title="Job A")
        test_admin_user.create_scraped_job(company="OwnerCorp", title="Job B")

        response = test_regular_user.client.get(
            self.endpoint, params={"filter_type": "company", "filter_operator": "equals", "filter_value": "OwnerCorp"}
        )
        assert response.json()["total"] == 1

    def test_preview_excludes_imported_jobs(self, test_regular_user: FixtureUser) -> None:
        """Imported jobs should not appear in preview results."""
        test_regular_user.create_scraped_job(title="ImportedJob", is_imported=True)
        test_regular_user.create_scraped_job(title="ImportedJob", is_imported=False)

        response = test_regular_user.client.get(
            self.endpoint,
            params={
                "filter_type": "title",
                "filter_operator": "equals",
                "filter_value": "ImportedJob",
            },
        )
        assert response.json()["total"] == 1

    def test_preview_excludes_inactive_jobs(self, test_regular_user: FixtureUser) -> None:
        """Inactive jobs should not appear in preview results."""
        test_regular_user.create_scraped_job(title="InactiveJob", is_active=False)
        test_regular_user.create_scraped_job(title="InactiveJob", is_active=True)

        response = test_regular_user.client.get(
            self.endpoint,
            params={
                "filter_type": "title",
                "filter_operator": "equals",
                "filter_value": "InactiveJob",
            },
        )
        assert response.json()["total"] == 1

    # ------------------------------------------------ AUTHENTICATION --------------------------------------------------

    def test_preview_unauthenticated(self, client: TestClient) -> None:
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
