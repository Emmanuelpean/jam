"""
This module contains a set of test functions to validate the functionality of user creation, user login,
and authentication workflows in the application. These tests ensure that the API endpoints for user-related
operations behave as expected under various scenarios, including successful requests and erroneous cases.
"""

from datetime import datetime, timezone, timedelta
from unittest.mock import patch

from app import schemas, models, utils
from tests.conftest import CRUDTestBase
from app.routers.user import send_email_change_with_rate_limit


class TestUsersCRUS(CRUDTestBase):
    endpoint = "/users"
    admin_only = True
    create_schema = schemas.UserCreate
    out_schema = schemas.UserOut
    test_data_ref = "test_users"
    create_data = [{"email": "test1@test.com", "password": "testpassword1"}]
    update_data = {"id": 1, "email": "newemail@test.com"}

    def test_update_admin_incorrect_email_format(self, admin_client, test_user) -> None:
        """Test updating with invalid email."""

        update_data = {"email": "ff"}
        response = admin_client.put(f"/users/{test_user.id}", json=update_data)
        assert response.status_code == 422

    def test_update_admin_existing_email(self, admin_client, admin_user, test_user) -> None:
        """Test updating with an email that already exists."""

        update_data = {"email": admin_user.email}
        response = admin_client.put(f"/users/{test_user.id}", json=update_data)
        assert response.status_code == 400


class TestMe:

    @staticmethod
    def get_user(user_id, session) -> models.User:
        """Helper method to get a user by ID."""

        return session.query(models.User).filter(models.User.id == user_id).first()

    def test_get_current_user_profile_success(self, admin_client, admin_user, test_client, test_user) -> None:
        """Test successfully getting current user profile."""

        # Admin
        response = admin_client.get("/current_user")
        assert admin_user.email == response.json()["email"]

        # Non-admin
        response = test_client.get("/current_user")
        assert test_user.email == response.json()["email"]

    @patch("app.routers.auth.email_service.send_email_change_verification")
    def test_update_email(self, mock_email_verif, test_client, test_user, session) -> None:
        """Test updating own profile as non-admin (with password)."""

        update_data = {"email": "newemail@example.com", "current_password": test_user.password}
        response = test_client.put("/current_user", json=update_data)
        assert mock_email_verif.call_count == 1
        assert mock_email_verif.call_args[0][0] == test_user.email.lower()
        assert response.status_code == 200
        assert self.get_user(test_user.id, session).email != update_data["email"]

    def test_update_password(self, test_client, test_user, session) -> None:
        """Test updating own profile as non-admin (with password)."""

        update_data = {"current_password": test_user.password, "password": "newpassword1"}
        response = test_client.put("/current_user", json=update_data)
        assert response.status_code == 200
        utils.verify_password(update_data["password"], self.get_user(test_user.id, session).password)

    def test_update_password_incorrect_password(self, test_client, test_user, session) -> None:
        """Test updating own profile as non-admin (with password)."""

        update_data = {"current_password": "", "password": "newpassword1"}
        response = test_client.put("/current_user", json=update_data)
        assert response.status_code == 401

    def test_update_incorrect_email_format(self, session, test_client, test_user) -> None:
        """Test updating with invalid email."""

        update_data = {"email": "ff", "current_password": test_user.password}
        response = test_client.put(f"/current_user", json=update_data)
        assert response.status_code == 422

    def test_update_existing_email(self, session, test_client, test_user, admin_user) -> None:
        """Test updating with invalid email."""

        update_data = {"email": admin_user.email, "current_password": test_user.password}
        response = test_client.put(f"/current_user", json=update_data)
        assert response.status_code == 400

    def test_update_settings(self, session, test_client, test_user) -> None:
        """Test updating with invalid email."""

        update_data = {"chase_threshold": 100}
        response = test_client.put(f"/current_user", json=update_data)
        assert response.status_code == 200
        assert self.get_user(test_user.id, session).chase_threshold == 100

    def test_unauthorised_update(self, session, client, test_user) -> None:
        """Test updating with invalid email."""

        update_data = {"chase_threshold": 100}
        response = client.put(f"/current_user", json=update_data)
        assert response.status_code == 401


class TestSendEmailChangeWithRateLimit:

    @patch("app.routers.auth.email_service.send_email_change_verification")
    def test_send_verification_email(self, mock_email, test_users, session) -> None:
        """Test sending of password reset email."""

        result = send_email_change_with_rate_limit(test_users[0], session, "newemail@test.com")
        assert result == {"error_code": None, "message": "Verification email sent successfully", "success": True}
        assert mock_email.call_count == 1
        assert test_users[0].email_change_token is not None
        assert test_users[0].email_change_token_created_at is not None

    @patch("app.routers.auth.email_service.send_email_change_verification")
    def test_send_verification_email_rate_limited(self, mock_email, test_users, session) -> None:
        """Test rate limiting when sending password reset email."""

        send_email_change_with_rate_limit(test_users[0], session, "newemail@test.com")
        result = send_email_change_with_rate_limit(test_users[0], session, "newemail@test.com")
        assert result["success"] is False
        assert result["error_code"] == 429
        assert mock_email.call_count == 1


class TestEmailVerification:

    @patch("app.routers.auth.email_service.send_email_change_notification")
    def test_verify_email_success(self, mock_email, client, test_user_change_email_token_user, session) -> None:
        """Test successful email change with valid token."""

        response = client.get(
            f"/current_user/verify-email/{test_user_change_email_token_user.plain_verification_token}"
        )

        assert response.status_code == 200
        assert response.json()["message"].lower() == "email address changed successfully"

        user = session.query(models.User).filter(models.User.id == test_user_change_email_token_user.id).first()

        assert user.pending_email is None
        assert user.email_change_token is None
        assert user.email_change_token_created_at is None
        assert user.email == test_user_change_email_token_user.pending_email
        assert mock_email.call_count == 1
        assert mock_email.call_args[0][0] == test_user_change_email_token_user.pending_email

    def test_verify_email_invalid_token(self, client) -> None:
        """Test email verification with invalid token."""

        response = client.get("/current_user/verify-email/invalid_token_xyz")

        assert response.status_code == 403
        assert "invalid" in response.json()["detail"].lower()

    def test_verify_email_expired_token(self, client, session) -> None:
        """Test email verification with expired token."""

        token = "expired_token_123"
        verification_code = utils.hash_token(token)
        expired_time = datetime.now(timezone.utc) - timedelta(hours=25)

        # noinspection PyArgumentList
        user = models.User(
            email="unverified@test.com",
            password="password",
            is_verified=False,
            is_active=True,
            email_change_token=verification_code,
            email_change_token_created_at=expired_time,
            pending_email="newemail@test.com",
        )
        session.add(user)
        session.commit()

        response = client.get(f"/current_user/verify-email/{token}")

        assert response.status_code == 403
        assert "expired" in response.json()["detail"].lower()

    def test_verify_email_existing(self, client, session, test_users) -> None:
        """Test email verification with existing user."""

        token = "token_123"
        verification_code = utils.hash_token(token)
        # noinspection PyArgumentList
        user = models.User(
            email="unverified@test.com",
            password="password",
            is_verified=False,
            is_active=True,
            email_change_token=verification_code,
            email_change_token_created_at=datetime.now(timezone.utc),
            pending_email=test_users[1].email,
        )
        session.add(user)
        session.commit()

        response = client.get(f"/current_user/verify-email/{token}")

        assert response.status_code == 400
        assert response.json()["detail"].lower() == "email already registered"
