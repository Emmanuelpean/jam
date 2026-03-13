"""Tests for Job Scraping routers."""

import pytest
from starlette import status

from app import models
from tests.conftest import make_undefined_method_params
from tests.utils.create_data.utils import create_db_entries


class TestForwardingConfirmationLinks:
    """Test suite for forwarding confirmation link endpoints"""

    endpoint = "/forwarding-confirmation-links"

    @staticmethod
    def _create_link(session, owner_id: int = 1, is_used: bool = False, **kwargs) -> models.ForwardingConfirmationLink:
        """Helper to create a forwarding confirmation link"""

        data = {
            "email_external_id": "ext_123",
            "url": "https://example.com/confirm",
            "platform": "gmail",
            "is_used": is_used,
            "owner_id": owner_id,
            **kwargs,
        }
        return create_db_entries(session, models.ForwardingConfirmationLink, data)[0]

    # ------------------------------------------------- GET /pending ---------------------------------------------------

    def test_get_pending_returns_unused_link(self, session, regular_user_client) -> None:
        """Should return the latest unused confirmation link"""

        link = self._create_link(session)
        response = regular_user_client.get(f"{self.endpoint}/pending")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == link.id
        assert data["url"] == "https://example.com/confirm"
        assert data["platform"] == "gmail"

    def test_get_pending_returns_none_when_latest_is_used(self, session, regular_user_client) -> None:
        """Should return null when the latest link has been used"""

        self._create_link(session, is_used=True)
        response = regular_user_client.get(f"{self.endpoint}/pending")

        assert response.status_code == status.HTTP_200_OK
        assert response.json() is None

    def test_get_pending_returns_none_when_no_links(self, regular_user_client) -> None:
        """Should return null when no links exist for the user"""

        response = regular_user_client.get(f"{self.endpoint}/pending")

        assert response.status_code == status.HTTP_200_OK
        assert response.json() is None

    def test_get_pending_returns_latest_link(self, session, regular_user_client) -> None:
        """Should return the most recently created link"""

        self._create_link(session, url="https://example.com/old")
        latest = self._create_link(session, url="https://example.com/new")

        response = regular_user_client.get(f"{self.endpoint}/pending")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == latest.id
        assert data["url"] == "https://example.com/new"

    def test_get_pending_only_returns_own_links(self, session, regular_user_client) -> None:
        """Should not return links belonging to other users"""

        self._create_link(session, owner_id=2)
        response = regular_user_client.get(f"{self.endpoint}/pending")

        assert response.status_code == status.HTTP_200_OK
        assert response.json() is None

    def test_get_pending_unauthenticated(self, client) -> None:
        """Should return 401 when not authenticated"""

        response = client.get(f"{self.endpoint}/pending")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    # ------------------------------------------------ PUT /{link_id} --------------------------------------------------

    def test_update_link_success(self, session, regular_user_client) -> None:
        """Should successfully mark a link as used"""

        link = self._create_link(session)
        response = regular_user_client.put(f"{self.endpoint}/{link.id}", json={"is_used": True})

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == link.id
        assert data["url"] == link.url
        assert data["platform"] == link.platform

    def test_update_link_not_found(self, regular_user_client) -> None:
        """Should return 404 when link doesn't exist"""

        response = regular_user_client.put(f"{self.endpoint}/99999", json={"is_used": True})
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_link_wrong_owner(self, session, regular_user_client) -> None:
        """Should return 404 when link belongs to another user"""

        link = self._create_link(session, owner_id=2)
        response = regular_user_client.put(f"{self.endpoint}/{link.id}", json={"is_used": True})
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_link_unauthenticated(self, session, client, test_users) -> None:
        """Should return 401 when not authenticated"""

        link = self._create_link(session)
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
    def test_undefined_methods(self, admin_client, regular_user_client, http_method, path_suffix, expected_status):
        response = regular_user_client.request(http_method, f"{self.ENDPOINT}{path_suffix}")
        assert response.status_code == expected_status
        response = admin_client.request(http_method, f"{self.ENDPOINT}{path_suffix}")
        assert response.status_code == expected_status
