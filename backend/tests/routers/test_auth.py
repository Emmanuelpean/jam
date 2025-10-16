"""Tests for the login/register page of the application."""

import hashlib
import os
from datetime import datetime, timezone, timedelta
from unittest.mock import patch

import pytest
from jose import jwt

from app import schemas, models
from app.config import settings


@pytest.fixture
def unverified_user(session) -> models.User:
    """Fixture to create an unverified user."""

    # noinspection PyArgumentList
    user = models.User(
        email="unverified@test.com",
        password="password",
        is_verified=False,
        is_active=True,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    user.password = "password"
    return user


class TestLogin:

    def test_login_user(self, test_users, client) -> None:
        """Test successful login for an existing user."""

        user_data = {
            "username": test_users[0].email,
            "password": test_users[0].password,
        }
        response = client.post("/login", data=user_data)
        login_response = schemas.Token(**response.json())
        payload = jwt.decode(
            login_response.access_token,
            settings.secret_key,
            algorithms=[settings.algorithm],
        )
        user_id = payload.get("user_id")
        assert user_id == test_users[0].id
        assert login_response.token_type == "bearer"
        assert response.status_code == 200

    def test_login_inactive_user(self, test_users, client) -> None:
        """Test login attempt for an inactive user."""

        user_data = {
            "username": test_users[2].email,
            "password": test_users[2].password,
        }
        response = client.post("/login", data=user_data)
        assert response.status_code == 401

    @patch("app.routers.auth.email_service.send_verification_email")
    def test_login_unverified_user_sends_email(self, mock_email, unverified_user, client) -> None:
        """Test that login for unverified user sends verification email."""

        user_data = {
            "username": unverified_user.email,
            "password": unverified_user.password,
        }
        response = client.post("/login", data=user_data)

        assert response.status_code == 401
        assert "not verified" in response.json()["detail"].lower()
        assert mock_email.call_count == 1

    @patch("app.routers.auth.email_service.send_verification_email")
    def test_login_unverified_user_rate_limit(self, _mock, unverified_user, client, session) -> None:
        """Test rate limiting for unverified user login attempts."""

        # Update unverified user with recent verification email timestamp
        unverified_user.verification_code = "dummy_code"
        unverified_user.verification_code_created_at = datetime.now(timezone.utc)
        session.commit()

        user_data = {
            "username": unverified_user.email,
            "password": unverified_user.password,
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


class TestRegister:

    @patch("app.routers.auth.email_service.send_verification_email")
    def test_register_user(self, mock_email, client) -> None:
        """Test successful registration of a new user."""

        user_data = {
            "email": "test_user@test.com",
            "password": "testpassword",
        }
        response = client.post("/register", json=user_data)

        assert response.status_code == 201
        assert mock_email.call_count == 1
        call_args = mock_email.call_args[0]
        assert call_args[0] == user_data["email"]
        assert "verify-email" in call_args[1]

    def test_register_user_exist(self, client, test_users) -> None:
        """Test registration attempt with already verified email."""

        # Incorrect password
        user_data = {
            "email": test_users[0].email,
            "password": test_users[0].password + "123",
        }
        response = client.post("/register", json=user_data)
        assert response.status_code == 400

        # Correct password
        user_data = {
            "email": test_users[0].email,
            "password": test_users[0].password,
        }
        response = client.post("/register", json=user_data)
        assert response.status_code == 400

    @patch("app.routers.auth.email_service.send_verification_email")
    def test_register_user_unverified_exists_resends_email(
        self, mock_email, unverified_user, client, session, test_users
    ) -> None:
        """Test that registering with unverified email resends verification."""

        user_data = {
            "email": unverified_user.email,
            "password": unverified_user.password,
        }
        response = client.post("/register", json=user_data)

        assert response.status_code == 400
        assert "not verified" in response.json()["detail"].lower()
        assert mock_email.call_count == 1

    @patch("app.routers.auth.email_service.send_verification_email")
    def test_register_user_unverified_exists_rate_limit(
        self, _mock_email, unverified_user, client, session, test_users
    ) -> None:
        """Test rate limiting when re-registering with unverified email."""

        # Update unverified user with recent verification email timestamp
        unverified_user.verification_code = "dummy_code"
        unverified_user.verification_code_created_at = datetime.now(timezone.utc)
        session.commit()

        user_data = {
            "email": unverified_user.email,
            "password": unverified_user.password,
        }
        response = client.post("/register", json=user_data)

        assert response.status_code == 429
        assert "wait" in response.json()["detail"].lower()

    def test_register_not_setting_allowed(self, client, test_settings) -> None:
        """Test registration blocked when email not on allowlist."""

        user_data = {
            "email": "test_user1@test.com",
            "password": "testpassword",
        }
        response = client.post("/register", json=user_data)
        assert response.status_code == 401

    @patch("app.routers.auth.email_service.send_verification_email", side_effect=Exception("SMTP error"))
    def test_register_email_sending_failure(self, _mock_email, client) -> None:
        """Test handling of email sending failure during registration."""

        user_data = {
            "email": "test_fail@test.com",
            "password": "testpassword",
        }
        response = client.post("/register", json=user_data)

        assert response.status_code == 500
        assert "error" in response.json()["detail"].lower()


class TestEmailVerification:

    def test_verify_email_success(self, client, unverified_user, session, test_users) -> None:
        """Test successful email verification with valid token."""

        token = "test_token_123"
        verification_code = hashlib.sha256(token.encode()).hexdigest()

        unverified_user.verification_code = verification_code
        unverified_user.verification_code_created_at = datetime.now(timezone.utc)
        session.commit()
        user_id = unverified_user.id

        response = client.get(f"/register/verify-email/{token}")

        assert response.status_code == 200
        assert "verified successfully" in response.json()["message"].lower()

        # Query fresh from database instead of refreshing
        verified_user = session.query(models.User).filter(models.User.id == user_id).first()
        assert verified_user.is_verified is True
        assert verified_user.verification_code is None
        assert verified_user.verification_code_created_at is None

    def test_verify_email_invalid_token(self, client) -> None:
        """Test email verification with invalid token."""

        response = client.get("/register/verify-email/invalid_token_xyz")

        assert response.status_code == 403
        assert "invalid" in response.json()["detail"].lower()

    @patch.dict(os.environ, {"VERIFICATION_TOKEN_EXPIRATION_HOURS": "24"})
    def test_verify_email_expired_token(self, client, unverified_user, session, test_users) -> None:
        """Test email verification with expired token."""

        token = "expired_token_123"
        verification_code = hashlib.sha256(token.encode()).hexdigest()
        expired_time = datetime.now(timezone.utc) - timedelta(hours=25)  # created more than 24 hours ago

        unverified_user.verification_code = verification_code
        unverified_user.verification_code_created_at = expired_time
        session.commit()

        response = client.get(f"/register/verify-email/{token}")

        assert response.status_code == 403
        assert "expired" in response.json()["detail"].lower()
        assert unverified_user.is_verified is False
