"""Tests for the login/register page of the application."""

from datetime import datetime, timezone, timedelta
from unittest.mock import Mock

import jwt
import pytest
from sqlalchemy.orm import Session
from starlette.testclient import TestClient

from app import models
from app.base_schemas import COLUMN_LIMITS
from app.config import settings
from app.core import schemas
from app.core.models import TokenType
from tests.base_test import BaseTest
from tests.fixtures.users import FixtureUser

# -------------------------------------------------------- LOGIN -------------------------------------------------------


class TestLogin(BaseTest):

    endpoint = "/login"

    def test_login_user(self, test_regular_user: models.User, client: TestClient) -> None:
        """Test successful login for an existing user."""

        data = {"username": test_regular_user.email, "password": test_regular_user.plain_password}
        response = client.post(self.endpoint, data=data)
        assert response.status_code == 200

        login_response = schemas.Token(**response.json())
        payload = jwt.decode(login_response.access_token, settings.secret_key, algorithms=[settings.algorithm])
        assert payload.get("user_id") == test_regular_user.id
        assert login_response.token_type == "bearer"

    def test_login_user_different_case(self, test_regular_user: models.User, client: TestClient) -> None:
        """Test that login is case-insensitive for the email address."""

        data = {"username": test_regular_user.email.upper(), "password": test_regular_user.plain_password}
        response = client.post(self.endpoint, data=data)
        assert response.status_code == 200

        login_response = schemas.Token(**response.json())
        payload = jwt.decode(login_response.access_token, settings.secret_key, algorithms=[settings.algorithm])
        assert payload.get("user_id") == test_regular_user.id
        assert login_response.token_type == "bearer"

    def test_login_inactive_user(self, test_inactive_user: models.User, client: TestClient) -> None:
        """Test login attempt for an inactive user."""

        data = {"username": test_inactive_user.email, "password": test_inactive_user.plain_password}
        response = client.post(self.endpoint, data=data)
        assert response.status_code == 401

    def test_login_unverified_user(
        self, mock_verification_email: Mock, test_unverified_user: models.User, client: TestClient
    ) -> None:
        """Test that login for an unverified user sends a verification email."""

        data = {"username": test_unverified_user.email, "password": test_unverified_user.plain_password}
        response = client.post(self.endpoint, data=data)

        assert response.status_code == 401
        assert "not verified" in response.json()["detail"].lower()
        assert mock_verification_email.call_count == 1

    def test_login_unverified_user_rate_limit(
        self, mock_verification_email: Mock, test_unverified_user: models.User, client: TestClient
    ) -> None:
        """Test rate limiting for unverified user login attempts."""

        data = {"username": test_unverified_user.email, "password": test_unverified_user.plain_password}

        # First attempt sends a verification email and seeds a recent token
        response = client.post(self.endpoint, data=data)
        assert response.status_code == 401
        assert mock_verification_email.call_count == 1

        # Second attempt is rate limited by the recent token
        response = client.post(self.endpoint, data=data)
        assert response.status_code == 429
        assert "wait" in response.json()["detail"].lower()
        assert mock_verification_email.call_count == 1

    @pytest.mark.parametrize(
        "email, password, status_code",
        [
            ("wrongemail@gmail.com", "pass123", 403),
            ("user1@email.com", "wrongpassword", 403),
            ("wrongemail@gmail.com", "wrongpassword", 403),
            (None, "pass123", 422),
            ("user1@email.com", None, 422),
        ],
    )
    def test_incorrect_login(
        self, email: str | None, password: str | None, status_code: int, client: TestClient
    ) -> None:
        """Test login failure scenarios with incorrect or incomplete credentials."""

        data = {key: value for key, value in {"username": email, "password": password}.items() if value is not None}
        response = client.post(f"{self.endpoint}/", data=data)
        assert response.status_code == status_code

    def test_regular_user_login_blocked_during_maintenance(
        self, session: Session, test_regular_user: models.User, client: TestClient
    ) -> None:
        """Non-admin users receive 401 when trying to log in during maintenance."""

        self._create_maintenance_setting(session, minutes_offset=-5)
        data = {"username": test_regular_user.email, "password": test_regular_user.plain_password}
        response = client.post(self.endpoint, data=data)
        assert response.status_code == 401
        assert "maintenance" in response.json()["detail"].lower()

    def test_admin_user_login_allowed_during_maintenance(
        self, session: Session, test_admin_user: models.User, client: TestClient
    ) -> None:
        """Admin users can log in when maintenance is active."""

        self._create_maintenance_setting(session, minutes_offset=-5)
        data = {"username": test_admin_user.email, "password": test_admin_user.plain_password}
        response = client.post(self.endpoint, data=data)
        assert response.status_code == 200

    def test_regular_user_login_allowed_outside_maintenance(
        self, test_regular_user: models.User, client: TestClient
    ) -> None:
        """Regular users can log in when no maintenance setting is present."""

        data = {"username": test_regular_user.email, "password": test_regular_user.plain_password}
        response = client.post(self.endpoint, data=data)
        assert response.status_code == 200

    def test_regular_user_login_allowed_when_maintenance_scheduled_in_future(
        self, session: Session, test_regular_user: models.User, client: TestClient
    ) -> None:
        """Regular users can log in when maintenance is scheduled but not yet active."""

        self._create_maintenance_setting(session, minutes_offset=30)
        data = {"username": test_regular_user.email, "password": test_regular_user.plain_password}
        response = client.post(self.endpoint, data=data)
        assert response.status_code == 200

    def test_demo_user_login_not_allowed_when_maintenance(
        self, session: Session, test_demo_user: models.User, client: TestClient
    ) -> None:
        """Demo users cannot log in when maintenance is active."""

        self._create_maintenance_setting(session, minutes_offset=-30)
        data = {"username": test_demo_user.email, "password": "demo"}
        response = client.post(self.endpoint, data=data)
        assert response.status_code == 401


# ------------------------------------------------------ REGISTER ------------------------------------------------------


class TestRegister(BaseTest):

    endpoint = "/register"

    def test_register_user(self, mock_verification_email: Mock, client: TestClient, session: Session) -> None:
        """Test successful registration of a new user."""

        user_data = {
            "email": "Test_user@test.com",
            "password": "test_password",
            "first_name": "Test",
            "last_name": "User",
        }
        response = client.post(self.endpoint, json=user_data)

        assert response.status_code == 201
        assert mock_verification_email.call_count == 1
        assert mock_verification_email.call_args[0][0] == user_data["email"].lower()
        user = session.query(models.User).first()
        assert user
        assert user.email == user_data["email"].lower()

    def test_register_user_exist(
        self, mock_verification_email: Mock, client: TestClient, test_regular_user: models.User
    ) -> None:
        """Test registration attempt with an already verified email."""

        # Incorrect password
        user_data = {
            "email": test_regular_user.email,
            "password": test_regular_user.plain_password + "123",
            "first_name": "Test",
            "last_name": "User",
        }
        response = client.post(self.endpoint, json=user_data)
        assert response.status_code == 400

        # Correct password
        user_data = {
            "email": test_regular_user.email,
            "password": test_regular_user.plain_password,
            "first_name": "Test",
            "last_name": "User",
        }
        response = client.post(self.endpoint, json=user_data)
        assert response.status_code == 400
        assert mock_verification_email.call_count == 0

        # Different email case
        user_data = {
            "email": test_regular_user.email.upper(),
            "password": test_regular_user.plain_password,
            "first_name": "Test",
            "last_name": "User",
        }
        response = client.post(self.endpoint, json=user_data)
        assert response.status_code == 400
        assert mock_verification_email.call_count == 0

    def test_register_user_unverified_exists_resends_email(
        self, mock_verification_email: Mock, test_unverified_user: models.User, client: TestClient
    ) -> None:
        """Test that registering with an unverified email resends the verification email."""

        user_data = {
            "email": test_unverified_user.email,
            "password": test_unverified_user.plain_password,
            "first_name": "Test",
            "last_name": "User",
        }
        response = client.post(self.endpoint, json=user_data)

        assert response.status_code == 401
        assert "not verified" in response.json()["detail"].lower()
        assert mock_verification_email.call_count == 1

    def test_register_user_unverified_exists_rate_limit(
        self, mock_verification_email: Mock, test_unverified_user: models.User, client: TestClient
    ) -> None:
        """Test rate limiting when re-registering with an unverified email."""

        user_data = {
            "email": test_unverified_user.email,
            "password": test_unverified_user.plain_password,
            "first_name": "Test",
            "last_name": "User",
        }

        # First attempt resends a verification email and seeds a recent token
        response = client.post(self.endpoint, json=user_data)
        assert response.status_code == 401
        assert mock_verification_email.call_count == 1

        # Second attempt is rate limited by the recent token
        response = client.post(self.endpoint, json=user_data)
        assert response.status_code == 429
        assert "wait" in response.json()["detail"].lower()
        assert mock_verification_email.call_count == 1

    def test_register_not_setting_allowed(
        self, mock_verification_email: Mock, session: Session, client: TestClient
    ) -> None:
        """Test registration blocked when email not on allowlist."""

        self.create_setting(session, "allowlist", "")
        user_data = {
            "email": "test_user1@test.com",
            "password": "testpassword",
            "first_name": "Test",
            "last_name": "User",
        }
        response = client.post(self.endpoint, json=user_data)
        assert response.status_code == 401
        assert mock_verification_email.call_count == 0

    def test_register_email_sending_failure(self, mock_verification_email: Mock, client: TestClient) -> None:
        """Test handling of email sending failure during registration."""

        mock_verification_email.side_effect = Exception("SMTP error")
        user_data = {
            "email": "test_fail@test.com",
            "password": "testpassword",
            "first_name": "Test",
            "last_name": "User",
        }
        response = client.post(self.endpoint, json=user_data)

        assert response.status_code == 500
        assert "error" in response.json()["detail"].lower()
        assert mock_verification_email.call_count == 1

    def test_register_blocked_during_maintenance(
        self, mock_verification_email: Mock, session: Session, client: TestClient
    ) -> None:
        """Test registration is blocked while maintenance is active."""

        self._create_maintenance_setting(session, minutes_offset=-5)
        user_data = {
            "email": "newuser@test.com",
            "password": "testpassword",
            "first_name": "New",
            "last_name": "User",
        }
        response = client.post(self.endpoint, json=user_data)
        assert response.status_code == 401
        assert "maintenance" in response.json()["detail"].lower()
        assert mock_verification_email.call_count == 0

    @pytest.mark.parametrize(
        "field, value",
        [
            ("password", "x" * (COLUMN_LIMITS.password + 1)),
            ("first_name", "x" * (COLUMN_LIMITS.first_name + 1)),
            ("last_name", "x" * (COLUMN_LIMITS.last_name + 1)),
        ],
        ids=[
            "password_too_long",
            "first_name_too_long",
            "last_name_too_long",
        ],
    )
    def test_register_field_too_long(self, field: str, value: str, client: TestClient) -> None:
        """Test that registering with a field exceeding its max length returns 422."""

        data = {
            "email": "new_user@test.com",
            "password": "testpassword",
            "first_name": "Test",
            "last_name": "User",
            field: value,
        }
        response = client.post(self.endpoint, json=data)
        assert response.status_code == 422


class TestEmailVerification(BaseTest):

    endpoint = "/register/verify-email"

    def test_verify_email_success(
        self, test_unverified_user: FixtureUser, client: TestClient, session: Session
    ) -> None:
        """Test successful email verification with valid token."""

        user_id = test_unverified_user.id
        plain_token = test_unverified_user.create_token(TokenType.EMAIL_VERIFICATION)[0]
        response = client.get(f"{self.endpoint}/{plain_token}")

        assert response.status_code == 200
        assert "verified successfully" in response.json()["message"].lower()

        verified_user = self.get_user(session, user_id)
        assert verified_user
        assert verified_user.is_verified is True

        # The verification token was consumed
        assert verified_user.get_token(TokenType.EMAIL_VERIFICATION) is None

    def test_verify_email_invalid_token(self, client: TestClient) -> None:
        """Test email verification with invalid token."""

        response = client.get(f"{self.endpoint}/invalid_token_xyz")

        assert response.status_code == 403
        assert "invalid" in response.json()["detail"].lower()

    def test_verify_email_expired_token(
        self, test_unverified_user: FixtureUser, client: TestClient, session: Session
    ) -> None:
        """Test email verification with expired token."""

        plain_token = test_unverified_user.create_token(
            TokenType.EMAIL_VERIFICATION, created_at=datetime.now(timezone.utc) - timedelta(hours=25)
        )[0]
        response = client.get(f"{self.endpoint}/{plain_token}")

        assert response.status_code == 403
        assert response.json()["detail"] == "Verification token has expired. Please request a new one by logging in."

        user = self.get_user(session, test_unverified_user.id)
        assert user
        assert user.is_verified is False

    def test_verify_email_blocked_during_maintenance(
        self, session: Session, test_unverified_user: FixtureUser, client: TestClient
    ) -> None:
        """Test email verification is blocked while maintenance is active."""

        plain_token = test_unverified_user.create_token(TokenType.EMAIL_VERIFICATION)[0]
        self._create_maintenance_setting(session, minutes_offset=-5)
        response = client.get(f"{self.endpoint}/{plain_token}")
        assert response.status_code == 401
        assert "maintenance" in response.json()["detail"].lower()


# --------------------------------------------------- PASSWORD RESET ---------------------------------------------------


class TestRequestPasswordReset(BaseTest):

    endpoint = "/password/forgot"

    def test_request_password_reset(
        self, mock_password_reset_email: Mock, client: TestClient, test_regular_user: FixtureUser
    ) -> None:
        """Test successful password reset request."""

        response = client.post(self.endpoint, json={"email": test_regular_user.email})

        assert response.status_code == 200
        assert response.json()["message"] == "Password reset email sent successfully."
        assert mock_password_reset_email.call_count == 1

    def test_request_password_reset_fail_demo(
        self, mock_password_reset_email: Mock, client: TestClient, test_demo_user: FixtureUser
    ) -> None:
        """Test that a demo user cannot request a password reset."""

        response = client.post(self.endpoint, json={"email": test_demo_user.email})

        assert response.status_code == 403
        assert mock_password_reset_email.call_count == 0

    def test_request_password_reset_case_insensitive(
        self, mock_password_reset_email: Mock, client: TestClient, test_regular_user: FixtureUser
    ) -> None:
        """Test that the password reset request is case-insensitive for the email address."""

        response = client.post(self.endpoint, json={"email": test_regular_user.email.upper()})

        assert response.status_code == 200
        assert response.json()["message"] == "Password reset email sent successfully."
        assert mock_password_reset_email.call_count == 1

    def test_request_password_reset_rate_limit(
        self, mock_password_reset_email: Mock, client: TestClient, test_regular_user: FixtureUser
    ) -> None:
        """Test rate limiting on password reset requests."""

        user_data = {"email": test_regular_user.email}

        client.post(self.endpoint, json=user_data)
        response = client.post(self.endpoint, json=user_data)

        assert response.status_code == 429
        assert "wait" in response.json()["detail"].lower()
        assert mock_password_reset_email.call_count == 1

    def test_request_password_reset_nonexistent_email(self, client: TestClient) -> None:
        """Test password reset request with non-existent email."""

        response = client.post(self.endpoint, json={"email": "test@test.com"})
        assert response.status_code == 404
        assert response.json()["detail"] == "User with this email does not exist."

    def test_request_password_reset_inactive_user(self, client: TestClient, test_inactive_user: FixtureUser) -> None:
        """Test password reset request for inactive user."""

        response = client.post(self.endpoint, json={"email": test_inactive_user.email})

        assert response.status_code == 401
        assert response.json()["detail"] == "User account is not active."

    def test_request_password_reset_no_email(self, client: TestClient) -> None:
        """Test password reset request with an empty email."""

        response = client.post(self.endpoint, json={"email": ""})

        assert response.status_code == 422

    def test_password_reset_request_blocked_during_maintenance(
        self, session: Session, test_regular_user: FixtureUser, client: TestClient
    ) -> None:
        """Test password reset request is blocked while maintenance is active."""

        self._create_maintenance_setting(session, minutes_offset=-5)
        response = client.post(self.endpoint, json={"email": test_regular_user.email})
        assert response.status_code == 401
        assert "maintenance" in response.json()["detail"].lower()


class TestResetPassword(BaseTest):

    endpoint = "/password/reset"

    def test_reset_password_success(
        self,
        mock_password_changed_email: Mock,
        client: TestClient,
        test_regular_user: FixtureUser,
    ) -> None:
        """Test successful password reset with valid token."""

        old_password_hash = test_regular_user.password
        plain_token = test_regular_user.create_token(TokenType.PASSWORD_RESET)[0]
        response = client.post(self.endpoint, json={"token": plain_token, "new_password": "new_secure_password"})
        assert response.status_code == 200
        assert "password has been reset" in response.json()["message"].lower()

        test_regular_user.refresh()
        assert test_regular_user and test_regular_user.password != old_password_hash
        assert test_regular_user.get_token(TokenType.PASSWORD_RESET) is None
        assert mock_password_changed_email.call_count == 1

    def test_reset_password_demo_fail(self, client: TestClient, test_demo_user: FixtureUser) -> None:
        """Test that a demo user cannot reset their password."""

        plain_token = test_demo_user.create_token(TokenType.PASSWORD_RESET)[0]
        response = client.post(self.endpoint, json={"token": plain_token, "new_password": "new_secure_password"})
        assert response.status_code == 403

    def test_reset_password_invalid_token(self, client: TestClient) -> None:
        """Test password reset with invalid token."""

        response = client.post(self.endpoint, json={"token": "invalid_token", "new_password": "new_secure_password"})
        assert response.status_code == 403
        assert "invalid" in response.json()["detail"].lower()

    def test_password_reset_confirm_blocked_during_maintenance(
        self,
        mock_password_changed_email: Mock,
        session: Session,
        test_regular_user: FixtureUser,
        client: TestClient,
    ) -> None:
        """Test password reset confirmation is blocked while maintenance is active."""

        plain_token = test_regular_user.create_token(TokenType.PASSWORD_RESET)[0]
        self._create_maintenance_setting(session, minutes_offset=-5)
        response = client.post(self.endpoint, json={"token": plain_token, "new_password": "newpassword123"})

        assert response.status_code == 401
        assert "maintenance" in response.json()["detail"].lower()
