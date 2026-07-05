"""Tests for Job Scraping routers."""

import pytest
from starlette import status
from starlette.testclient import TestClient

from tests.conftest import make_undefined_method_params
from tests.fixtures.users import FixtureUser


class TestForwardingConfirmationLinks:
    """Test suite for forwarding confirmation link endpoints"""

    endpoint = "/forwarding-confirmation-links"

    # ------------------------------------------------- GET /pending ---------------------------------------------------

    def test_get_pending_returns_unused_link(self, test_regular_user: FixtureUser) -> None:
        """Should return the latest unused confirmation link"""

        link = test_regular_user.create_forwarding_confirmation_link()
        response = test_regular_user.client.get(f"{self.endpoint}/pending")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == link.id
        assert data["url"] == "https://example.com/confirm"
        assert data["platform"] == "gmail"

    def test_get_pending_returns_none_when_latest_is_used(self, test_regular_user: FixtureUser) -> None:
        """Should return null when the latest link has been used"""

        test_regular_user.create_forwarding_confirmation_link(is_used=True)
        response = test_regular_user.client.get(f"{self.endpoint}/pending")

        assert response.status_code == status.HTTP_200_OK
        assert response.json() is None

    def test_get_pending_returns_none_when_no_links(self, test_regular_user: FixtureUser) -> None:
        """Should return null when no links exist for the user"""

        response = test_regular_user.client.get(f"{self.endpoint}/pending")

        assert response.status_code == status.HTTP_200_OK
        assert response.json() is None

    def test_get_pending_returns_latest_link(self, test_regular_user: FixtureUser) -> None:
        """Should return the most recently created link"""

        test_regular_user.create_forwarding_confirmation_link(url="https://example.com/old")
        latest = test_regular_user.create_forwarding_confirmation_link(url="https://example.com/new")

        response = test_regular_user.client.get(f"{self.endpoint}/pending")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == latest.id
        assert data["url"] == "https://example.com/new"

    def test_get_pending_only_returns_own_links(
        self, test_regular_user: FixtureUser, test_admin_user: FixtureUser
    ) -> None:
        """Should not return links belonging to other users"""

        test_admin_user.create_forwarding_confirmation_link()
        response = test_regular_user.client.get(f"{self.endpoint}/pending")

        assert response.status_code == status.HTTP_200_OK
        assert response.json() is None

    def test_get_pending_unauthenticated(self, client: TestClient) -> None:
        """Should return 401 when not authenticated"""

        response = client.get(f"{self.endpoint}/pending")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    # ------------------------------------------------ PUT /{link_id} --------------------------------------------------

    def test_update_link_success(self, test_regular_user: FixtureUser) -> None:
        """Should successfully mark a link as used"""

        link = test_regular_user.create_forwarding_confirmation_link()
        response = test_regular_user.client.put(f"{self.endpoint}/{link.id}", json={"is_used": True})

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == link.id
        assert data["url"] == link.url
        assert data["platform"] == link.platform

    def test_update_link_not_found(self, test_regular_user: FixtureUser) -> None:
        """Should return 404 when link doesn't exist"""

        response = test_regular_user.client.put(f"{self.endpoint}/99999", json={"is_used": True})
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_link_wrong_owner(self, test_regular_user: FixtureUser, test_admin_user: FixtureUser) -> None:
        """Should return 404 when link belongs to another user"""

        link = test_admin_user.create_forwarding_confirmation_link()
        response = test_regular_user.client.put(f"{self.endpoint}/{link.id}", json={"is_used": True})
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_link_unauthenticated(self, client: TestClient, test_regular_user: FixtureUser) -> None:
        """Should return 401 when not authenticated"""

        link = test_regular_user.create_forwarding_confirmation_link()
        response = client.put(f"{self.endpoint}/{link.id}", json={"is_used": True})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestForwardingConfirmationLinkUndefinedMethods:
    ENDPOINT = "/forwarding-confirmation-links"
    DEFINED_ACTIONS = ["PUT"]
    UNDEFINED_ACTIONS = ["GET_ALL", "POST", "GET_ONE", "DELETE"]

    @pytest.mark.parametrize(
        "http_method,path_suffix,expected_status",
        make_undefined_method_params(DEFINED_ACTIONS, UNDEFINED_ACTIONS),
    )
    def test_undefined_methods(
        self,
        http_method: str,
        path_suffix: str,
        expected_status: int,
        test_admin_user: FixtureUser,
        test_regular_user: FixtureUser,
    ) -> None:
        response = test_regular_user.client.request(http_method, f"{self.ENDPOINT}{path_suffix}")
        assert response.status_code == expected_status
        response = test_admin_user.client.request(http_method, f"{self.ENDPOINT}{path_suffix}")
        assert response.status_code == expected_status
