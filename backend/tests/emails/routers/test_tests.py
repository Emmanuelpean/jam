"""Tests for email testing endpoints."""

from unittest.mock import Mock, patch

import pytest
from fastapi import status
from starlette.testclient import TestClient

from app.main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def _enable_test_mode(enable_test_mode):
    """Every /test/emails endpoint is gated by require_test_mode, so enable it for this module.
    The explicit "returns 403 when disabled" tests patch test_mode=False themselves; that patch is
    applied when the test is called (after fixture setup), so it still wins for those cases."""

    yield


class TestGetTestEmails:
    """Tests for GET /test/emails/emails/{email_address} endpoint."""

    @patch("app.emails.routers.tests.email_service")
    def test_returns_emails_when_test_mode_enabled(self, mock_email_service: Mock) -> None:
        """Returns list of emails when test mode is enabled."""

        mock_emails = [
            {"subject": "Test 1", "body": "Body 1"},
            {"subject": "Test 2", "body": "Body 2"},
        ]
        mock_email_service.get_test_emails.return_value = mock_emails

        response = client.get("/test/emails/emails/user@example.com")

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"emails": mock_emails}
        mock_email_service.get_test_emails.assert_called_once_with("user@example.com")

    @patch("app.routers.utility.settings.test_mode", False)
    def test_returns_403_when_test_mode_disabled(self) -> None:
        """Returns 403 Forbidden when test mode is not enabled."""

        response = client.get("/test/emails/emails/user@example.com")

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "Test mode not enabled" in response.json()["detail"]

    @patch("app.emails.routers.tests.email_service")
    def test_returns_empty_list_when_no_emails(self, mock_email_service: Mock) -> None:
        """Returns empty list when no test emails exist."""

        mock_email_service.get_test_emails.return_value = []

        response = client.get("/test/emails/emails/nobody@example.com")

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"emails": []}


class TestGetVerificationLink:
    """Tests for GET /test/emails/verification-link/{email_address} endpoint."""

    @patch("app.emails.routers.tests.settings")
    @patch("app.emails.routers.tests.email_service")
    def test_returns_verification_link_when_found(self, mock_email_service: Mock, mock_settings: Mock) -> None:
        """Extracts and returns verification link from email body."""

        mock_settings.frontend_url = "https://example.com"
        mock_email_service.get_test_emails.return_value = [
            {
                "subject": "Verify your email",
                "body": "Click here: https://example.com/verify/?token=abc123_XYZ-test",
            }
        ]

        response = client.get("/test/emails/verification-link/user@example.com")

        assert response.status_code == status.HTTP_200_OK
        assert "verification_url" in response.json()
        assert "token=abc123_XYZ-test" in response.json()["verification_url"]

    @patch("app.routers.utility.settings.test_mode", False)
    def test_returns_403_when_test_mode_disabled(self) -> None:
        """Returns 403 Forbidden when test mode is not enabled."""

        response = client.get("/test/emails/verification-link/user@example.com")

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "Test mode not enabled" in response.json()["detail"]

    @patch("app.emails.routers.tests.email_service")
    def test_returns_404_when_no_emails(self, mock_email_service: Mock) -> None:
        """Returns 404 when no emails found for the address."""

        mock_email_service.get_test_emails.return_value = []

        response = client.get("/test/emails/verification-link/user@example.com")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "No emails found" in response.json()["detail"]

    @patch("app.emails.routers.tests.settings")
    @patch("app.emails.routers.tests.email_service")
    def test_returns_404_when_no_link_in_email(self, mock_email_service: Mock, mock_settings: Mock) -> None:
        """Returns 404 when email exists but contains no verification link."""

        mock_settings.frontend_url = "https://example.com"
        mock_email_service.get_test_emails.return_value = [{"subject": "Welcome", "body": "No link here"}]

        response = client.get("/test/emails/verification-link/user@example.com")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "No verification link found" in response.json()["detail"]

    @patch("app.emails.routers.tests.settings")
    @patch("app.emails.routers.tests.email_service")
    def test_uses_most_recent_email(self, mock_email_service: Mock, mock_settings: Mock) -> None:
        """Extracts verification link from the most recent (last) email."""

        mock_settings.frontend_url = "https://example.com"
        mock_email_service.get_test_emails.return_value = [
            {
                "subject": "Old verification",
                "body": "https://example.com/verify/?token=old_token",
            },
            {
                "subject": "New verification",
                "body": "https://example.com/verify/?token=new_token",
            },
        ]

        response = client.get("/test/emails/verification-link/user@example.com")

        assert response.status_code == status.HTTP_200_OK
        assert "new_token" in response.json()["verification_url"]


class TestGetResetLink:
    """Tests for GET /test/emails/reset-link/{email_address} endpoint."""

    @patch("app.emails.routers.tests.settings")
    @patch("app.emails.routers.tests.email_service")
    def test_returns_reset_link_when_found(self, mock_email_service: Mock, mock_settings: Mock) -> None:
        """Extracts and returns password reset link from email body."""

        mock_settings.frontend_url = "https://example.com"
        mock_email_service.get_test_emails.return_value = [
            {
                "subject": "Reset your password",
                "body": "Click here: https://example.com/reset-password/?token=reset123_ABC",
            }
        ]

        response = client.get("/test/emails/reset-link/user@example.com")

        assert response.status_code == status.HTTP_200_OK
        assert "reset_url" in response.json()
        assert "token=reset123_ABC" in response.json()["reset_url"]

    @patch("app.routers.utility.settings.test_mode", False)
    def test_returns_403_when_test_mode_disabled(self) -> None:
        """Returns 403 Forbidden when test mode is not enabled."""

        response = client.get("/test/emails/reset-link/user@example.com")

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "Test mode not enabled" in response.json()["detail"]

    @patch("app.emails.routers.tests.email_service")
    def test_returns_404_when_no_emails(self, mock_email_service: Mock) -> None:
        """Returns 404 when no emails found for the address."""

        mock_email_service.get_test_emails.return_value = []

        response = client.get("/test/emails/reset-link/user@example.com")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "No emails found" in response.json()["detail"]

    @patch("app.emails.routers.tests.settings")
    @patch("app.emails.routers.tests.email_service")
    def test_returns_404_when_no_link_in_email(self, mock_email_service: Mock, mock_settings: Mock) -> None:
        """Returns 404 when email exists but contains no reset link."""

        mock_settings.frontend_url = "https://example.com"
        mock_email_service.get_test_emails.return_value = [{"subject": "Hello", "body": "No reset link here"}]

        response = client.get("/test/emails/reset-link/user@example.com")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "No reset link found" in response.json()["detail"]

    @patch("app.emails.routers.tests.settings")
    @patch("app.emails.routers.tests.email_service")
    def test_uses_most_recent_email(self, mock_email_service: Mock, mock_settings: Mock) -> None:
        """Extracts reset link from the most recent (last) email."""

        mock_settings.frontend_url = "https://example.com"
        mock_email_service.get_test_emails.return_value = [
            {
                "subject": "Old reset",
                "body": "https://example.com/reset-password/?token=old_reset",
            },
            {
                "subject": "New reset",
                "body": "https://example.com/reset-password/?token=new_reset",
            },
        ]

        response = client.get("/test/emails/reset-link/user@example.com")

        assert response.status_code == status.HTTP_200_OK
        assert "new_reset" in response.json()["reset_url"]


class TestClearTestEmails:
    """Tests for DELETE /test/emails/emails endpoint."""

    @patch("app.emails.routers.tests.email_service")
    def test_clears_emails_when_test_mode_enabled(self, mock_email_service: Mock) -> None:
        """Clears test emails and returns success status."""

        response = client.delete("/test/emails/emails")

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"status": "cleared"}
        mock_email_service.clear_test_emails.assert_called_once()

    @patch("app.routers.utility.settings.test_mode", False)
    def test_returns_403_when_test_mode_disabled(self) -> None:
        """Returns 403 Forbidden when test mode is not enabled."""

        response = client.delete("/test/emails/emails")

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "Test mode not enabled" in response.json()["detail"]
