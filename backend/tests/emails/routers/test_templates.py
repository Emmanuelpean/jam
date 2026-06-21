"""Tests for the GET /email-templates/ endpoint."""

from starlette import status
from starlette.testclient import TestClient

ENDPOINT = "/email-templates/"


class TestPreviewAllEmailTemplates:
    """Tests for the GET /email-templates/ endpoint (all templates at once)."""

    def test_admin_gets_all_templates(self, admin_client: TestClient) -> None:
        """Admin receives 200 and a list of templates, each with an id, label, and HTML."""
        response = admin_client.get(ENDPOINT)

        assert response.status_code == status.HTTP_200_OK
        body = response.json()
        assert len(body) > 0
        assert all(item["id"] and item["label"] and len(item["html"]) > 0 for item in body)

    def test_rendered_new_version_contains_features(self, admin_client: TestClient) -> None:
        """The bundled new_version preview renders with its sample feature list."""
        response = admin_client.get(ENDPOINT)

        assert response.status_code == status.HTTP_200_OK
        new_version = next(item for item in response.json() if item["id"] == "new_version")
        assert new_version["label"] == "New Version Announcement"
        assert "Email Template Previewer" in new_version["html"]

    def test_unauthenticated_returns_401(self, client: TestClient) -> None:
        """Unauthenticated request is rejected with 401."""
        response = client.get(ENDPOINT)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_non_admin_returns_403(self, regular_user_client: TestClient) -> None:
        """Non-admin authenticated user is rejected with 403."""
        response = regular_user_client.get(ENDPOINT)

        assert response.status_code == status.HTTP_403_FORBIDDEN
