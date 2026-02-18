"""Tests for email testing endpoints."""

from unittest.mock import patch

from fastapi import status
from starlette.testclient import TestClient

from app.main import app

client = TestClient(app)


class TestGetTestEmails:
    """Tests for GET /test/emails/{email_address} endpoint."""

    @patch("app.emails.routers.tests.settings")
    @patch("app.emails.routers.tests.email_service")
    def test_returns_emails_when_test_mode_enabled(self, mock_email_service, mock_settings) -> None:
        """Returns list of emails when test mode is enabled."""

        mock_settings.test_mode = True
        mock_emails = [
            {"subject": "Test 1", "body": "Body 1"},
            {"subject": "Test 2", "body": "Body 2"},
        ]
        mock_email_service.get_test_emails.return_value = mock_emails

        response = client.get("/test/emails/user@example.com")

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"emails": mock_emails}
        mock_email_service.get_test_emails.assert_called_once_with("user@example.com")

    @patch("app.emails.routers.tests.settings")
    def test_returns_403_when_test_mode_disabled(self, mock_settings) -> None:
        """Returns 403 Forbidden when test mode is not enabled."""

        mock_settings.test_mode = False

        response = client.get("/test/emails/user@example.com")

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "Test mode not enabled" in response.json()["detail"]

    @patch("app.emails.routers.tests.settings")
    @patch("app.emails.routers.tests.email_service")
    def test_returns_empty_list_when_no_emails(self, mock_email_service, mock_settings) -> None:
        """Returns empty list when no test emails exist."""

        mock_settings.test_mode = True
        mock_email_service.get_test_emails.return_value = []

        response = client.get("/test/emails/nobody@example.com")

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"emails": []}


class TestGetVerificationLink:
    """Tests for GET /test/verification-link/{email_address} endpoint."""

    @patch("app.emails.routers.tests.settings")
    @patch("app.emails.routers.tests.email_service")
    def test_returns_verification_link_when_found(self, mock_email_service, mock_settings) -> None:
        """Extracts and returns verification link from email body."""

        mock_settings.test_mode = True
        mock_settings.frontend_url = "https://example.com"
        mock_email_service.get_test_emails.return_value = [
            {
                "subject": "Verify your email",
                "body": "Click here: https://example.com/verify/?token=abc123_XYZ-test",
            }
        ]

        response = client.get("/test/verification-link/user@example.com")

        assert response.status_code == status.HTTP_200_OK
        assert "verification_url" in response.json()
        assert "token=abc123_XYZ-test" in response.json()["verification_url"]

    @patch("app.emails.routers.tests.settings")
    def test_returns_403_when_test_mode_disabled(self, mock_settings) -> None:
        """Returns 403 Forbidden when test mode is not enabled."""

        mock_settings.test_mode = False

        response = client.get("/test/verification-link/user@example.com")

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "Test mode not enabled" in response.json()["detail"]

    @patch("app.emails.routers.tests.settings")
    @patch("app.emails.routers.tests.email_service")
    def test_returns_404_when_no_emails(self, mock_email_service, mock_settings) -> None:
        """Returns 404 when no emails found for the address."""

        mock_settings.test_mode = True
        mock_email_service.get_test_emails.return_value = []

        response = client.get("/test/verification-link/user@example.com")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "No emails found" in response.json()["detail"]

    @patch("app.emails.routers.tests.settings")
    @patch("app.emails.routers.tests.email_service")
    def test_returns_404_when_no_link_in_email(self, mock_email_service, mock_settings) -> None:
        """Returns 404 when email exists but contains no verification link."""

        mock_settings.test_mode = True
        mock_settings.frontend_url = "https://example.com"
        mock_email_service.get_test_emails.return_value = [{"subject": "Welcome", "body": "No link here"}]

        response = client.get("/test/verification-link/user@example.com")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "No verification link found" in response.json()["detail"]

    @patch("app.emails.routers.tests.settings")
    @patch("app.emails.routers.tests.email_service")
    def test_uses_most_recent_email(self, mock_email_service, mock_settings) -> None:
        """Extracts verification link from the most recent (last) email."""

        mock_settings.test_mode = True
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

        response = client.get("/test/verification-link/user@example.com")

        assert response.status_code == status.HTTP_200_OK
        assert "new_token" in response.json()["verification_url"]


class TestGetResetLink:
    """Tests for GET /test/reset-link/{email_address} endpoint."""

    @patch("app.emails.routers.tests.settings")
    @patch("app.emails.routers.tests.email_service")
    def test_returns_reset_link_when_found(self, mock_email_service, mock_settings) -> None:
        """Extracts and returns password reset link from email body."""

        mock_settings.test_mode = True
        mock_settings.frontend_url = "https://example.com"
        mock_email_service.get_test_emails.return_value = [
            {
                "subject": "Reset your password",
                "body": "Click here: https://example.com/reset-password/?token=reset123_ABC",
            }
        ]

        response = client.get("/test/reset-link/user@example.com")

        assert response.status_code == status.HTTP_200_OK
        assert "reset_url" in response.json()
        assert "token=reset123_ABC" in response.json()["reset_url"]

    @patch("app.emails.routers.tests.settings")
    def test_returns_403_when_test_mode_disabled(self, mock_settings) -> None:
        """Returns 403 Forbidden when test mode is not enabled."""

        mock_settings.test_mode = False

        response = client.get("/test/reset-link/user@example.com")

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "Test mode not enabled" in response.json()["detail"]

    @patch("app.emails.routers.tests.settings")
    @patch("app.emails.routers.tests.email_service")
    def test_returns_404_when_no_emails(self, mock_email_service, mock_settings) -> None:
        """Returns 404 when no emails found for the address."""

        mock_settings.test_mode = True
        mock_email_service.get_test_emails.return_value = []

        response = client.get("/test/reset-link/user@example.com")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "No emails found" in response.json()["detail"]

    @patch("app.emails.routers.tests.settings")
    @patch("app.emails.routers.tests.email_service")
    def test_returns_404_when_no_link_in_email(self, mock_email_service, mock_settings) -> None:
        """Returns 404 when email exists but contains no reset link."""

        mock_settings.test_mode = True
        mock_settings.frontend_url = "https://example.com"
        mock_email_service.get_test_emails.return_value = [{"subject": "Hello", "body": "No reset link here"}]

        response = client.get("/test/reset-link/user@example.com")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "No reset link found" in response.json()["detail"]

    @patch("app.emails.routers.tests.settings")
    @patch("app.emails.routers.tests.email_service")
    def test_uses_most_recent_email(self, mock_email_service, mock_settings) -> None:
        """Extracts reset link from the most recent (last) email."""

        mock_settings.test_mode = True
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

        response = client.get("/test/reset-link/user@example.com")

        assert response.status_code == status.HTTP_200_OK
        assert "new_reset" in response.json()["reset_url"]


class TestClearTestEmails:
    """Tests for DELETE /test/emails endpoint."""

    @patch("app.emails.routers.tests.settings")
    @patch("app.emails.routers.tests.email_service")
    def test_clears_emails_when_test_mode_enabled(self, mock_email_service, mock_settings) -> None:
        """Clears test emails and returns success status."""

        mock_settings.test_mode = True

        response = client.delete("/test/emails")

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"status": "cleared"}
        mock_email_service.clear_test_emails.assert_called_once()

    @patch("app.emails.routers.tests.settings")
    def test_returns_403_when_test_mode_disabled(self, mock_settings) -> None:
        """Returns 403 Forbidden when test mode is not enabled."""

        mock_settings.test_mode = False

        response = client.delete("/test/emails")

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "Test mode not enabled" in response.json()["detail"]
