"""Tests for the login/register page of the application."""

from datetime import datetime, timezone, timedelta
from unittest.mock import patch

import jwt
import pytest

from app import models
from app.base_schemas import COLUMN_LIMITS
from app.config import settings
from app.core import schemas
from app.core.models import Setting
from app.core.utils import send_password_reset_email
from app.utils import hash_token


def _create_maintenance_setting(session, minutes_offset: int) -> Setting:
    """Insert a maintenance_scheduled_at setting with a timestamp offset from now.

    A negative offset puts the time in the past (maintenance active).
    A positive offset puts the time in the future (scheduled but not yet active).
    """
    scheduled_at = datetime.now(timezone.utc) + timedelta(minutes=minutes_offset)
    setting = Setting(name="maintenance_scheduled_at", value=scheduled_at.isoformat())
    session.add(setting)
    session.commit()
    session.refresh(setting)
    return setting


# -------------------------------------------------------- LOGIN -------------------------------------------------------


class TestLogin:

    def test_login_user(self, test_regular_user, client) -> None:
        """Test successful login for an existing user."""

        user_data = {
            "username": test_regular_user.email,
            "password": test_regular_user.plain_password,
        }
        response = client.post("/login", data=user_data)
        login_response = schemas.Token(**response.json())
        payload = jwt.decode(
            login_response.access_token,
            settings.secret_key,
            algorithms=[settings.algorithm],
        )
        user_id = payload.get("user_id")
        assert user_id == test_regular_user.id
        assert login_response.token_type == "bearer"
        assert response.status_code == 200

    def test_login_user_different_case(self, test_regular_user, client) -> None:
        """Test successful login for an existing user."""

        user_data = {
            "username": test_regular_user.email.upper(),
            "password": test_regular_user.plain_password,
        }
        response = client.post("/login", data=user_data)
        assert response.status_code == 200
        login_response = schemas.Token(**response.json())
        payload = jwt.decode(
            login_response.access_token,
            settings.secret_key,
            algorithms=[settings.algorithm],
        )
        user_id = payload.get("user_id")
        assert user_id == test_regular_user.id
        assert login_response.token_type == "bearer"

    def test_login_inactive_user(self, test_inactive_user, client) -> None:
        """Test login attempt for an inactive user."""

        user_data = {
            "username": test_inactive_user.email,
            "password": test_inactive_user.plain_password,
        }
        response = client.post("/login", data=user_data)
        assert response.status_code == 401

    @patch("app.core.routers.auth.email_service.send_verification_email")
    def test_login_unverified_user(self, mock_email, test_unverified_user, client) -> None:
        """Test that login for unverified user sends verification email."""

        user_data = {
            "username": test_unverified_user.email,
            "password": test_unverified_user.plain_password,
        }
        response = client.post("/login", data=user_data)

        assert response.status_code == 401
        assert "not verified" in response.json()["detail"].lower()
        assert mock_email.call_count == 1

    @patch("app.core.routers.auth.email_service.send_verification_email")
    def test_login_unverified_user_rate_limit(self, _mock, test_unverified_token_user, client, session) -> None:
        """Test rate limiting for unverified user login attempts."""

        user_data = {
            "username": test_unverified_token_user.email,
            "password": test_unverified_token_user.plain_password,
        }
        response = client.post("/login", data=user_data)

        assert response.status_code == 429
        assert "wait" in response.json()["detail"].lower()

    @pytest.mark.parametrize(
        "email, password, status_code",
        [
            ("wrongemail@gmail.com", "pass123", 403),
            ("user1@email.com", "wrongpassword", 403),
            ("wrongemail@gmail.com", "wrongpassword", 403),
            (None, "pass123", 403),
            ("user1@email.com", None, 403),
        ],
    )
    def test_incorrect_login(self, email, password, status_code, client) -> None:
        """Test login failure scenarios with incorrect or incomplete credentials."""

        response = client.post("/login/", data={"username": email, "password": password})
        assert response.status_code == status_code

    def test_regular_user_login_blocked_during_maintenance(self, session, test_regular_user, client) -> None:
        """Non-admin users receive 401 when trying to log in during maintenance."""

        _create_maintenance_setting(session, minutes_offset=-5)
        data = {"username": test_regular_user.email, "password": test_regular_user.plain_password}
        response = client.post("/login", data=data)
        assert response.status_code == 401
        assert "maintenance" in response.json()["detail"].lower()

    def test_admin_user_login_allowed_during_maintenance(self, session, test_admin_user, client) -> None:
        """Admin users can log in when maintenance is active."""

        _create_maintenance_setting(session, minutes_offset=-5)
        data = {"username": test_admin_user.email, "password": test_admin_user.plain_password}
        response = client.post("/login", data=data)
        assert response.status_code == 200

    def test_regular_user_login_allowed_outside_maintenance(self, test_regular_user, client) -> None:
        """Regular users can log in when no maintenance setting is present."""

        data = {"username": test_regular_user.email, "password": test_regular_user.plain_password}
        response = client.post("/login", data=data)
        assert response.status_code == 200

    def test_regular_user_login_allowed_when_maintenance_scheduled_in_future(
        self, session, test_regular_user, client
    ) -> None:
        """Regular users can log in when maintenance is scheduled but not yet active."""

        _create_maintenance_setting(session, minutes_offset=30)
        data = {"username": test_regular_user.email, "password": test_regular_user.plain_password}
        response = client.post("/login", data=data)
        assert response.status_code == 200

    def test_demo_user_login_not_allowed_when_maintenance(self, session, test_demo_user, client) -> None:
        """Demo users cannot log in when maintenance is active."""

        _create_maintenance_setting(session, minutes_offset=-30)
        data = {"username": test_demo_user.email, "password": ""}
        response = client.post("/login", data=data)
        assert response.status_code == 401


# ------------------------------------------------------ REGISTER ------------------------------------------------------


class TestRegister:

    @patch("app.core.routers.auth.email_service.send_verification_email")
    def test_register_user(self, mock_email, client, session) -> None:
        """Test successful registration of a new user."""

        user_data = {
            "email": "Test_user@test.com",
            "password": "testpassword",
            "first_name": "Test",
            "last_name": "User",
        }
        response = client.post("/register", json=user_data)

        assert response.status_code == 201
        assert mock_email.call_count == 1
        call_args = mock_email.call_args[0]
        assert call_args[0] == user_data["email"].lower()
        user = session.query(models.User).first()
        assert user.email == user_data["email"].lower()

    def test_register_user_exist(self, client, test_regular_user) -> None:
        """Test registration attempt with already verified email."""

        # Incorrect password
        user_data = {
            "email": test_regular_user.email,
            "password": test_regular_user.plain_password + "123",
            "first_name": "Test",
            "last_name": "User",
        }
        response = client.post("/register", json=user_data)
        assert response.status_code == 400

        # Correct password
        user_data = {
            "email": test_regular_user.email,
            "password": test_regular_user.plain_password,
            "first_name": "Test",
            "last_name": "User",
        }
        response = client.post("/register", json=user_data)
        assert response.status_code == 400

    def test_register_user_exist_different_case(self, client, test_regular_user) -> None:
        """Test registration attempt with already verified email."""

        # Incorrect password
        user_data = {
            "email": test_regular_user.email,
            "password": test_regular_user.plain_password + "123",
            "first_name": "Test",
            "last_name": "User",
        }
        response = client.post("/register", json=user_data)
        assert response.status_code == 400

        # Correct password
        user_data = {
            "email": test_regular_user.email,
            "password": test_regular_user.plain_password,
            "first_name": "Test",
            "last_name": "User",
        }
        response = client.post("/register", json=user_data)
        assert response.status_code == 400

    @patch("app.core.routers.auth.email_service.send_verification_email")
    def test_register_user_unverified_exists_resends_email(
        self, mock_email, test_unverified_user, client, session, test_regular_user
    ) -> None:
        """Test that registering with unverified email resends verification."""

        user_data = {
            "email": test_unverified_user.email,
            "password": test_unverified_user.plain_password,
            "first_name": "Test",
            "last_name": "User",
        }
        response = client.post("/register", json=user_data)

        assert response.status_code == 401
        assert "not verified" in response.json()["detail"].lower()
        assert mock_email.call_count == 1

    @patch("app.core.routers.auth.email_service.send_verification_email")
    def test_register_user_unverified_exists_rate_limit(
        self, mock_email, test_unverified_token_user, client, session, test_regular_user
    ) -> None:
        """Test rate limiting when re-registering with unverified email."""

        user_data = {
            "email": test_unverified_token_user.email,
            "password": test_unverified_token_user.plain_password,
            "first_name": "Test",
            "last_name": "User",
        }
        response = client.post("/register", json=user_data)

        assert response.status_code == 429
        assert "wait" in response.json()["detail"].lower()
        assert mock_email.call_count == 0

    def test_register_not_setting_allowed(self, client, test_settings) -> None:
        """Test registration blocked when email not on allowlist."""

        user_data = {
            "email": "test_user1@test.com",
            "password": "testpassword",
            "first_name": "Test",
            "last_name": "User",
        }
        response = client.post("/register", json=user_data)
        assert response.status_code == 401

    @patch("app.core.routers.auth.email_service.send_verification_email", side_effect=Exception("SMTP error"))
    def test_register_email_sending_failure(self, mock_email, client) -> None:
        """Test handling of email sending failure during registration."""

        user_data = {
            "email": "test_fail@test.com",
            "password": "testpassword",
            "first_name": "Test",
            "last_name": "User",
        }
        response = client.post("/register", json=user_data)

        assert response.status_code == 500
        assert "error" in response.json()["detail"].lower()
        assert mock_email.call_count == 1

    def test_register_blocked_during_maintenance(self, session, client) -> None:
        _create_maintenance_setting(session, minutes_offset=-5)
        data = {
            "email": "newuser@test.com",
            "password": "testpassword",
            "first_name": "New",
            "last_name": "User",
        }
        response = client.post("/register", json=data)
        assert response.status_code == 401
        assert "maintenance" in response.json()["detail"].lower()

    @pytest.mark.parametrize(
        "field, value",
        [
            ("password", "x" * (COLUMN_LIMITS.password + 1)),
            ("first_name", "x" * (COLUMN_LIMITS.first_name + 1)),
            ("last_name", "x" * (COLUMN_LIMITS.last_name + 1)),
        ],
    )
    def test_register_field_too_long(self, field, value, client) -> None:
        """Test that registering with a field exceeding its max length returns 422."""
        data = {
            "email": "new_user@test.com",
            "password": "testpassword",
            "first_name": "Test",
            "last_name": "User",
            field: value,
        }
        response = client.post("/register", json=data)
        assert response.status_code == 422


class TestEmailVerification:

    def test_verify_email_success(self, client, test_unverified_token_user, session) -> None:
        """Test successful email verification with valid token."""

        user_id = test_unverified_token_user.id
        response = client.get(f"/register/verify-email/{test_unverified_token_user.plain_verification_token}")

        assert response.status_code == 200
        assert "verified successfully" in response.json()["message"].lower()

        verified_user = session.query(models.User).filter(models.User.id == user_id).first()
        assert verified_user.is_verified is True

        # Check that the token was marked as used
        verification_token = (
            session.query(models.UserToken)
            .filter(
                models.UserToken.owner_id == user_id,
                models.UserToken.token_type == "verification",
            )
            .first()
        )
        assert verification_token is None

    def test_verify_email_invalid_token(self, client) -> None:
        """Test email verification with invalid token."""

        response = client.get("/register/verify-email/invalid_token_xyz")

        assert response.status_code == 403
        assert "invalid" in response.json()["detail"].lower()

    def test_verify_email_expired_token(self, client, session) -> None:
        """Test email verification with expired token."""

        token = "expired_token_123"
        verification_code = hash_token(token)
        expired_time = datetime.now(timezone.utc) - timedelta(hours=25)

        # Create user with preferences and stripe details
        # noinspection PyArgumentList
        user = models.User(
            email="unverified@test.com",
            password="password",
            is_verified=False,
            is_active=True,
        )
        session.add(user)
        session.commit()

        # Store user_id for later queries
        user_id = user.id

        # Create expired verification token
        # noinspection PyArgumentList
        expired_token = models.UserToken(
            owner_id=user_id,
            token=verification_code,
            token_type="verification",
            created_at=expired_time,
        )
        session.add(expired_token)
        session.commit()

        response = client.get(f"/register/verify-email/{token}")

        assert response.status_code == 403
        assert response.json()["detail"] == "Verification token has expired. Please request a new one by logging in."

        # Re-query user to check verification status
        user = session.query(models.User).filter(models.User.id == user_id).first()
        assert user.is_verified is False

    def test_verify_email_blocked_during_maintenance(self, session, test_unverified_token_user, client) -> None:
        _create_maintenance_setting(session, minutes_offset=-5)
        response = client.get(f"/register/verify-email/{test_unverified_token_user.plain_verification_token}")
        assert response.status_code == 401
        assert "maintenance" in response.json()["detail"].lower()


# --------------------------------------------------- PASSWORD RESET ---------------------------------------------------


class TestSendPasswordResetWithRateLimit:

    @patch("app.core.routers.auth.email_service.send_password_reset_email")
    def test_send_password_reset_email(self, mock_email, test_regular_user, session) -> None:
        """Test sending of password reset email."""

        result = send_password_reset_email(test_regular_user, session)
        assert result.model_dump() == {
            "success": True,
            "message": "Password reset email sent successfully.",
            "error_code": None,
        }
        assert mock_email.call_count == 1

        # Check that a password reset token was created
        password_reset_token = (
            session.query(models.UserToken)
            .filter(
                models.UserToken.owner_id == test_regular_user.id,
                models.UserToken.token_type == "password_reset",
            )
            .order_by(models.UserToken.created_at.desc())
            .first()
        )
        assert password_reset_token is not None
        assert password_reset_token.token is not None
        assert password_reset_token.created_at is not None

    @patch("app.core.routers.auth.email_service.send_password_reset_email")
    def test_send_verification_email_rate_limited(self, mock_email, test_regular_user, session) -> None:
        """Test rate limiting when sending password reset email."""

        send_password_reset_email(test_regular_user, session)
        result = send_password_reset_email(test_regular_user, session)
        assert result.model_dump() == {
            "error_code": 429,
            "message": "Please wait 120 seconds before requesting another Password reset email.",
            "success": False,
        }
        assert mock_email.call_count == 1


class TestRequestPasswordReset:

    @patch("app.core.routers.auth.email_service.send_password_reset_email")
    def test_request_password_reset(self, mock_email, client, test_regular_user) -> None:
        """Test successful password reset request."""

        user_data = {
            "email": test_regular_user.email,
        }
        response = client.post("/password/forgot", json=user_data)

        assert response.status_code == 200
        assert response.json()["message"] == "Password reset email sent successfully."
        assert mock_email.call_count == 1

    @patch("app.core.routers.auth.email_service.send_password_reset_email")
    def test_request_password_reset_fail_demo(self, mock_email, client, test_demo_user) -> None:
        """Test successful password reset request."""

        user_data = {
            "email": test_demo_user.email,
        }
        response = client.post("/password/forgot", json=user_data)

        assert response.status_code == 403
        assert mock_email.call_count == 0

    @patch("app.core.routers.auth.email_service.send_password_reset_email")
    def test_request_password_reset_different_case(self, mock_email, client, test_regular_user) -> None:
        """Test successful password reset request."""

        user_data = {
            "email": test_regular_user.email.upper(),
        }
        response = client.post("/password/forgot", json=user_data)

        assert response.status_code == 200
        assert response.json()["message"] == "Password reset email sent successfully."
        assert mock_email.call_count == 1

    @patch("app.core.routers.auth.email_service.send_password_reset_email")
    def test_request_password_reset_rate_limit(self, mock_email, client, test_regular_user, session) -> None:
        """Test rate limiting on password reset requests."""

        user_data = {
            "email": test_regular_user.email,
        }
        # First request
        client.post("/password/forgot", json=user_data)
        response = client.post("/password/forgot", json=user_data)

        assert response.status_code == 429
        assert "wait" in response.json()["detail"].lower()
        assert mock_email.call_count == 1

    def test_request_password_reset_nonexistent_email(self, client) -> None:
        """Test password reset request with non-existent email."""

        user_data = {"email": "test@test.com"}
        response = client.post("/password/forgot", json=user_data)
        assert response.status_code == 404
        assert response.json()["detail"] == "User with this email does not exist."

    def test_request_password_reset_inactive_user(self, client, test_inactive_user) -> None:
        """Test password reset request for inactive user."""

        user_data = {
            "email": test_inactive_user.email,
        }
        response = client.post("/password/forgot", json=user_data)

        assert response.status_code == 401
        assert response.json()["detail"] == "User account is not active."

    def test_request_password_reset_no_email(self, client, test_regular_user) -> None:
        """Test password reset request for inactive user."""

        user_data = {
            "email": "",
        }
        response = client.post("/password/forgot", json=user_data)

        assert response.status_code == 422

    def test_password_reset_request_blocked_during_maintenance(self, session, test_regular_user, client) -> None:
        _create_maintenance_setting(session, minutes_offset=-5)
        response = client.post("/password/forgot", json={"email": test_regular_user.email})
        assert response.status_code == 401
        assert "maintenance" in response.json()["detail"].lower()


class TestResetPassword:

    @patch("app.core.routers.auth.email_service.send_password_changed_notification")
    def test_reset_password_success(self, mock_email, client, test_regular_user, session) -> None:
        """Test successful password reset with valid token."""

        token = "reset_token_123"
        reset_code = hash_token(token)

        # Re-query the user using the test session so modifications persist for the request
        user_id = test_regular_user.id
        user = session.query(models.User).filter(models.User.id == user_id).first()

        # Remember current password for later comparison
        old_password_hash = user.password

        # Create password reset token
        # noinspection PyArgumentList
        reset_token = models.UserToken(
            owner_id=user.id,
            token=reset_code,
            token_type="password_reset",
            created_at=datetime.now(timezone.utc),
        )
        session.add(reset_token)
        session.commit()

        # Store token_id for later query
        token_id = reset_token.id

        new_password_data = {
            "token": token,
            "new_password": "newsecurepassword",
        }
        response = client.post("/password/reset", json=new_password_data)
        assert response.status_code == 200
        assert "password has been reset" in response.json()["message"].lower()

        updated_user = session.query(models.User).filter(models.User.id == user_id).first()
        assert updated_user.password != old_password_hash

        # Re-query the token to check if it was marked as used
        updated_token = session.query(models.UserToken).filter(models.UserToken.id == token_id).first()
        assert updated_token is None
        assert mock_email.call_count == 1

    def test_reset_password_demo_fail(self, client, test_demo_user, session) -> None:
        """Test successful password reset with valid token."""

        token = "reset_token_123"
        reset_code = hash_token(token)

        # Re-query the user using the test session so modifications persist for the request
        user_id = test_demo_user.id
        user = session.query(models.User).filter(models.User.id == user_id).first()

        user.password_reset_token = reset_code
        user.password_reset_token_created_at = datetime.now(timezone.utc)
        session.commit()

        new_password_data = {
            "token": token,
            "new_password": "newsecurepassword",
        }
        response = client.post("/password/reset", json=new_password_data)
        assert response.status_code == 403

    def test_reset_password_invalid_token(self, client) -> None:
        """Test password reset with invalid token."""

        new_password_data = {
            "token": "invalid_token_xyz",
            "new_password": "newsecurepassword",
        }
        response = client.post("/password/reset", json=new_password_data)
        assert response.status_code == 403
        assert "invalid" in response.json()["detail"].lower()

    @patch("app.core.routers.auth.email_service.send_password_changed_notification")
    def test_password_reset_confirm_blocked_during_maintenance(
        self, _mock_email, session, test_unverified_token_user, client
    ) -> None:
        _create_maintenance_setting(session, minutes_offset=-5)
        data = {
            "token": test_unverified_token_user.plain_verification_token,
            "new_password": "newpassword123",
        }
        response = client.post("/password/reset", json=data)
        assert response.status_code == 401
        assert "maintenance" in response.json()["detail"].lower()
