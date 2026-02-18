"""Tests for GET /email-templates/preview/{template_name} endpoint."""

import pytest
from starlette import status
from starlette.testclient import TestClient

ENDPOINT = "/email-templates/preview"

ALL_TEMPLATES = [
    "email_confirmation",
    "password_reset",
    "email_change",
    "password_changed",
    "email_changed",
    "trial_end_reminder",
    "new_version",
]


class TestPreviewEmailTemplate:
    """Tests for the email template preview endpoint."""

    def test_admin_gets_valid_template(self, admin_client: TestClient) -> None:
        """Admin receives 200 and HTML content for a known template."""
        response = admin_client.get(f"{ENDPOINT}/email_confirmation")

        assert response.status_code == status.HTTP_200_OK
        assert "text/html" in response.headers["content-type"]
        assert len(response.text) > 0

    def test_unauthenticated_returns_401(self, client: TestClient) -> None:
        """Unauthenticated request is rejected with 401."""
        response = client.get(f"{ENDPOINT}/email_confirmation")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_non_admin_returns_403(self, regular_user_client: TestClient) -> None:
        """Non-admin authenticated user is rejected with 403."""
        response = regular_user_client.get(f"{ENDPOINT}/email_confirmation")

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_unknown_template_returns_404(self, admin_client: TestClient) -> None:
        """Unknown template name returns 404."""
        response = admin_client.get(f"{ENDPOINT}/does_not_exist")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "does_not_exist" in response.json()["detail"]

    @pytest.mark.parametrize("template_name", ALL_TEMPLATES)
    def test_all_templates_render(self, admin_client: TestClient, template_name: str) -> None:
        """Every known template renders successfully and returns non-empty HTML."""
        response = admin_client.get(f"{ENDPOINT}/{template_name}")

        assert response.status_code == status.HTTP_200_OK
        assert "text/html" in response.headers["content-type"]
        assert len(response.text) > 0

    def test_rendered_new_version_contains_features(self, admin_client: TestClient) -> None:
        """New version template renders with its sample feature list."""
        response = admin_client.get(f"{ENDPOINT}/new_version")

        assert response.status_code == status.HTTP_200_OK
        assert "Email Template Previewer" in response.text
