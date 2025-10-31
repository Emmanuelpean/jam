"""
This module contains a set of test functions to validate the functionality of user creation, user login,
and authentication workflows in the application. These tests ensure that the API endpoints for user-related
operations behave as expected under various scenarios, including successful requests and erroneous cases.
"""

from datetime import datetime, timezone, timedelta
from unittest.mock import patch

from app import schemas, models, utils, oauth2
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


class TestCurrentUser:

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
        """Test updating own profile as non-admin (with email change)."""

        # Get initial token version
        initial_token_version = test_user.token_version

        update_data = {"email": "newemail@example.com", "current_password": test_user.plain_password}
        response = test_client.put("/current_user", json=update_data)
        assert mock_email_verif.call_count == 1
        assert mock_email_verif.call_args[0][0] == "newemail@example.com"
        assert response.status_code == 200

        # Verify email hasn't changed yet (pending verification)
        updated_user = self.get_user(test_user.id, session)
        assert updated_user.email != update_data["email"]
        assert updated_user.pending_email == update_data["email"]

        # Verify token version has not changed
        assert updated_user.token_version == initial_token_version

    def test_update_password(self, test_client, test_user, session) -> None:
        """Test updating own password as non-admin."""

        # Get initial token version
        initial_token_version = test_user.token_version

        update_data = {"current_password": test_user.plain_password, "password": "newpassword1"}
        response = test_client.put("/current_user", json=update_data)

        assert response.status_code == 200

        # Verify password changed
        updated_user = self.get_user(test_user.id, session)
        assert utils.verify_password(update_data["password"], updated_user.password)

        # Verify token version incremented
        assert updated_user.token_version == initial_token_version + 1

        # Verify response indicates logout
        assert response.json()["logged_out"] is True
        assert "log in again" in response.json()["message"].lower()

    def test_update_password_revokes_token(self, test_client, test_user, session) -> None:
        """Test that updating password invalidates current token."""

        # Change password
        update_data = {"current_password": test_user.plain_password, "password": "newpassword1"}
        response = test_client.put("/current_user", json=update_data)
        assert response.status_code == 200

        # Try to use the old token (test_client still has it)
        response = test_client.get("/current_user")
        assert response.status_code == 401
        assert "revoked" in response.json()["detail"].lower()

    def test_update_password_incorrect_password(self, test_client, test_user, session) -> None:
        """Test updating password with incorrect current password."""

        update_data = {"current_password": "", "password": "newpassword1"}
        response = test_client.put("/current_user", json=update_data)
        assert response.status_code == 401

    def test_update_incorrect_email_format(self, session, test_client, test_user) -> None:
        """Test updating with invalid email."""

        update_data = {"email": "ff", "current_password": test_user.plain_password}
        response = test_client.put(f"/current_user", json=update_data)
        assert response.status_code == 422

    def test_update_existing_email(self, session, test_client, test_user, admin_user) -> None:
        """Test updating with an email that already exists."""

        update_data = {"email": admin_user.email, "current_password": test_user.plain_password}
        response = test_client.put(f"/current_user", json=update_data)
        assert response.status_code == 400

    def test_update_settings(self, session, test_client, test_user) -> None:
        """Test updating user settings that don't require password."""

        # Get initial token version
        initial_token_version = test_user.token_version

        update_data = {"chase_threshold": 100}
        response = test_client.put(f"/current_user", json=update_data)
        assert response.status_code == 200

        updated_user = self.get_user(test_user.id, session)
        assert updated_user.chase_threshold == 100

        # Verify token version NOT incremented (no password/email change)
        assert updated_user.token_version == initial_token_version

        # Verify response does NOT indicate logout
        assert response.json().get("logged_out") is None

    def test_unauthorised_update(self, session, client, test_user) -> None:
        """Test updating without authentication."""

        update_data = {"chase_threshold": 100}
        response = client.put(f"/current_user", json=update_data)
        assert response.status_code == 401


class TestSendEmailChangeWithRateLimit:

    @patch("app.routers.auth.email_service.send_email_change_verification")
    def test_send_verification_email(self, mock_email, test_users, session) -> None:
        """Test sending of email change verification email."""

        result = send_email_change_with_rate_limit(test_users[0], session, "newemail@test.com")
        assert result == {"error_code": None, "message": "Verification email sent successfully", "success": True}
        assert mock_email.call_count == 1
        assert test_users[0].email_change_token is not None
        assert test_users[0].email_change_token_created_at is not None

    @patch("app.routers.auth.email_service.send_email_change_verification")
    def test_send_verification_email_rate_limited(self, mock_email, test_users, session) -> None:
        """Test rate limiting when sending email change verification email."""

        send_email_change_with_rate_limit(test_users[0], session, "newemail@test.com")
        result = send_email_change_with_rate_limit(test_users[0], session, "newemail@test.com")
        assert result["success"] is False
        assert result["error_code"] == 429
        assert mock_email.call_count == 1


class TestEmailVerification:

    @patch("app.routers.auth.email_service.send_email_change_notification")
    def test_verify_email_success(self, mock_email, client, test_user_change_email_token_user, session) -> None:
        """Test successful email change with valid token."""

        # Get initial token version
        initial_token_version = test_user_change_email_token_user.token_version
        pending_email = test_user_change_email_token_user.pending_email

        response = client.get(
            f"/current_user/verify-email/{test_user_change_email_token_user.plain_verification_token}"
        )

        assert response.status_code == 200
        assert "email address changed successfully" in response.json()["message"].lower()

        user = session.query(models.User).filter(models.User.id == test_user_change_email_token_user.id).first()

        # Verify email updated and pending fields cleared
        assert user.pending_email is None
        assert user.email_change_token is None
        assert user.email_change_token_created_at is None
        assert user.email == pending_email

        # Verify token version incremented
        assert user.token_version == initial_token_version + 1

        # Verify notification sent
        assert mock_email.call_count == 1
        assert mock_email.call_args[0][0] == pending_email

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
            token_version=0,
        )
        session.add(user)
        session.commit()

        response = client.get(f"/current_user/verify-email/{token}")

        assert response.status_code == 403
        assert "expired" in response.json()["detail"].lower()

    def test_verify_email_existing(self, client, session, test_users) -> None:
        """Test email verification when pending email already exists."""

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
            token_version=0,
        )
        session.add(user)
        session.commit()

        response = client.get(f"/current_user/verify-email/{token}")

        assert response.status_code == 400
        assert response.json()["detail"].lower() == "email already registered"


class TestTokenVersioning:
    """Test suite for token versioning and invalidation."""

    def test_token_version_starts_at_zero(self, test_user) -> None:
        """Test that new users start with token_version 0."""

        assert test_user.token_version == 0

    def test_old_token_rejected_after_password_change(self, test_client, test_user, session, client) -> None:
        """Test that tokens with old version are rejected after password change."""

        # First verify current token works
        response = test_client.get("/current_user")
        assert response.status_code == 200

        # Change password (this increments token_version)
        update_data = {"current_password": test_user.plain_password, "password": "newpassword1"}
        response = test_client.put("/current_user", json=update_data)
        assert response.status_code == 200

        # Try to use old token - should fail
        response = test_client.get("/current_user")
        assert response.status_code == 401
        assert "revoked" in response.json()["detail"].lower()

        # Verify new login works
        user = session.query(models.User).filter(models.User.id == test_user.id).first()
        new_token = oauth2.create_access_token(data={"user_id": test_user.id}, token_version=user.token_version)
        response = client.get("/current_user", headers={"Authorization": f"Bearer {new_token}"})
        assert response.status_code == 200

    @patch("app.routers.auth.email_service.send_email_change_verification")
    def test_token_version_no_increments_on_email_change_request(
        self, _mock_email, test_client, test_user, session
    ) -> None:
        """Test that token version increments when email change is requested."""

        initial_version = test_user.token_version

        update_data = {"email": "newemail@example.com", "current_password": test_user.plain_password}
        response = test_client.put("/current_user", json=update_data)
        assert response.status_code == 200

        user = session.query(models.User).filter(models.User.id == test_user.id).first()
        assert user.token_version == initial_version

    @patch("app.routers.auth.email_service.send_email_change_notification")
    def test_token_version_increments_on_email_verification(
        self, mock_email, client, test_user_change_email_token_user, session
    ) -> None:
        """Test that token version increments when email change is verified."""

        initial_version = test_user_change_email_token_user.token_version

        response = client.get(
            f"/current_user/verify-email/{test_user_change_email_token_user.plain_verification_token}"
        )
        assert response.status_code == 200

        user = session.query(models.User).filter(models.User.id == test_user_change_email_token_user.id).first()
        assert user.token_version == initial_version + 1
        assert mock_email.call_count == 1

    def test_token_version_unchanged_for_non_sensitive_updates(self, test_client, test_user, session) -> None:
        """Test that token version does NOT increment for non-password/email updates."""

        initial_version = test_user.token_version

        update_data = {"chase_threshold": 200}
        response = test_client.put("/current_user", json=update_data)
        assert response.status_code == 200

        user = session.query(models.User).filter(models.User.id == test_user.id).first()
        assert user.token_version == initial_version

        # Verify token still works
        response = test_client.get("/current_user")
        assert response.status_code == 200
