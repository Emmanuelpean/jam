"""
This module contains a set of test functions to validate the functionality of user creation, user login,
and authentication workflows in the application. These tests ensure that the API endpoints for user-related
operations behave as expected under various scenarios, including successful requests and erroneous cases.
"""

from datetime import datetime, timezone, timedelta
from unittest.mock import patch

import pytest

import app.job_rating.models as job_rating_models
from app import models, utils
from app.base_schemas import COLUMN_LIMITS
from app.core import schemas, oauth2
from app.core.utils import generate_token, send_email_change_email
from app.core.models import TokenType
from tests.conftest import CRUDTestBase


class TestUsersCRUD(CRUDTestBase):
    endpoint = "/users"
    admin_only = True
    create_schema = schemas.UserCreate
    out_schema = schemas.UserOut
    test_data_ref = "test_users"
    create_data = [{"email": "test1@test.com", "password": "testpassword1", "premium": {"job_scraping_active": False}}]
    update_data = {"id": 1, "email": "newemail@test.com", "premium": {"job_scraping_active": False}}

    def test_update_admin_incorrect_email_format(self, admin_client, test_regular_user) -> None:
        """Test updating with invalid email."""

        update_data = {"email": "ff"}
        response = admin_client.put(f"/users/{test_regular_user.id}", json=update_data)
        assert response.status_code == 422

    def test_update_admin_existing_email(self, admin_client, test_admin_user, test_regular_user) -> None:
        """Test updating with an email that already exists."""

        update_data = {"email": test_admin_user.email}
        response = admin_client.put(f"/users/{test_regular_user.id}", json=update_data)
        assert response.status_code == 400

    def test_update_account(self, session, admin_client, test_regular_user) -> None:
        """Test updating account does not affect the password."""

        password = test_regular_user.password
        update_data = {"first_name": "New first name"}
        response = admin_client.put(f"/users/{test_regular_user.id}", json=update_data)
        assert response.status_code == 200
        session.refresh(test_regular_user)
        assert test_regular_user.password == password


class TestCurrentUser:

    @staticmethod
    def get_user(user_id, session) -> models.User:
        """Helper method to get a user by ID."""
        return session.query(models.User).filter(models.User.id == user_id).first()

    def test_get_current_user_profile_success(
        self, admin_client, test_admin_user, regular_user_client, test_regular_user
    ) -> None:
        """Test successfully getting current user profile."""

        # Admin
        response = admin_client.get("/current-user")
        assert test_admin_user.email == response.json()["email"]

        # Non-admin
        response = regular_user_client.get("/current-user")
        assert test_regular_user.email == response.json()["email"]

    @patch("app.core.routers.auth.email_service.send_email_change_verification")
    def test_update_email(self, mock_email_verif, regular_user_client, test_regular_user, session) -> None:
        """Test updating own profile as non-admin (with email change)."""

        # Get initial token version
        initial_token_version = test_regular_user.token_version

        update_data = {"email": "newemail@example.com", "current_password": test_regular_user.plain_password}
        response = regular_user_client.put("/current-user", json=update_data)
        assert mock_email_verif.call_count == 1
        assert mock_email_verif.call_args[0][0] == "newemail@example.com"
        assert response.status_code == 200

        # Verify email hasn't changed yet (pending verification)
        updated_user = self.get_user(test_regular_user.id, session)
        assert updated_user.email != update_data["email"]

        # Check pending_email is in UserToken table
        token_entry = (
            session.query(models.UserToken)
            .filter(models.UserToken.owner_id == test_regular_user.id, models.UserToken.token_type == "email_change")
            .first()
        )
        assert token_entry is not None
        assert token_entry.pending_email == update_data["email"]

        # Verify token version has not changed
        assert updated_user.token_version == initial_token_version

    @patch("app.core.routers.auth.email_service.send_email_change_verification")
    def test_update_email_demo_fail(self, mock_email_verif, demo_user_client, test_demo_user) -> None:
        """Test updating own profile as demo user (should fail)."""

        update_data = {"email": "newemail@example.com", "current_password": test_demo_user.plain_password}
        response = demo_user_client.put("/current-user", json=update_data)
        assert mock_email_verif.call_count == 0
        assert response.status_code == 403

    def test_update_password(self, regular_user_client, test_regular_user, session) -> None:
        """Test updating own password as non-admin."""

        # Get initial token version
        initial_token_version = test_regular_user.token_version

        update_data = {"current_password": test_regular_user.plain_password, "password": "newpassword1"}
        response = regular_user_client.put("/current-user", json=update_data)

        assert response.status_code == 200

        # Verify password changed
        updated_user = self.get_user(test_regular_user.id, session)
        assert utils.verify_password(update_data["password"], updated_user.password)

        # Verify token version incremented
        assert updated_user.token_version == initial_token_version + 1

        # Verify response indicates logout
        assert response.json()["logged_out"] is True
        assert "log in again" in response.json()["message"].lower()

    def test_update_password_demo_fail(self, demo_user_client, test_demo_user, session) -> None:
        """Test updating own password as demo user (should fail)."""

        update_data = {"current_password": test_demo_user.plain_password, "password": "newpassword1"}
        response = demo_user_client.put("/current-user", json=update_data)
        assert response.status_code == 403

    def test_update_password_revokes_token(self, regular_user_client, test_regular_user, session) -> None:
        """Test that updating password invalidates current token."""

        # Change password
        update_data = {"current_password": test_regular_user.plain_password, "password": "newpassword1"}
        response = regular_user_client.put("/current-user", json=update_data)
        assert response.status_code == 200

        # Try to use the old token (test_client still has it)
        response = regular_user_client.get("/current-user")
        assert response.status_code == 401
        assert "revoked" in response.json()["detail"].lower()

    def test_update_password_incorrect_password(self, regular_user_client, test_regular_user, session) -> None:
        """Test updating password with incorrect current password."""

        update_data = {"current_password": "", "password": "newpassword1"}
        response = regular_user_client.put("/current-user", json=update_data)
        assert response.status_code == 401

    def test_update_incorrect_email_format(self, session, regular_user_client, test_regular_user) -> None:
        """Test updating with invalid email."""

        update_data = {"email": "ff", "current_password": test_regular_user.plain_password}
        response = regular_user_client.put("/current-user", json=update_data)
        assert response.status_code == 422

    def test_update_existing_email(self, session, regular_user_client, test_regular_user, test_admin_user) -> None:
        """Test updating with an email that already exists."""

        update_data = {"email": test_admin_user.email, "current_password": test_regular_user.plain_password}
        response = regular_user_client.put("/current-user", json=update_data)
        assert response.status_code == 400

    def test_update_account(self, session, regular_user_client, test_regular_user) -> None:
        """Test updating account does not affect the password."""

        password = test_regular_user.password
        update_data = {"first_name": "New first name"}
        response = regular_user_client.put("/current-user", json=update_data)
        assert response.status_code == 200
        session.refresh(test_regular_user)
        assert test_regular_user.password == password

    def test_update_preferences(self, session, regular_user_client, test_regular_user) -> None:
        """Test updating user preferences that don't require password."""

        # Get initial token version
        initial_token_version = test_regular_user.token_version

        update_data = {"preferences": {"chase_threshold": 100}}
        response = regular_user_client.put("/current-user", json=update_data)
        assert response.status_code == 200

        updated_user = self.get_user(test_regular_user.id, session)
        assert updated_user.preferences.chase_threshold == 100

        # Verify token version NOT incremented (no password/email change)
        assert updated_user.token_version == initial_token_version

        # Verify response does NOT indicate logout
        assert response.json().get("logged_out") is None

    def test_update_premium(self, session, regular_user_client, test_regular_user) -> None:
        """Test updating user premium details that don't require password."""

        # Get initial token version
        initial_token_version = test_regular_user.token_version

        assert test_regular_user.premium.job_scraping_active is True
        update_data = {"premium": {"job_scraping_active": False}}
        response = regular_user_client.put("/current-user", json=update_data)
        assert response.status_code == 200

        updated_user = self.get_user(test_regular_user.id, session)
        assert not updated_user.premium.job_scraping_active

        # Verify token version NOT incremented (no password/email change)
        assert updated_user.token_version == initial_token_version

        # Verify response does NOT indicate logout
        assert response.json().get("logged_out") is None

    def test_update_premium_is_active(self, session, regular_user_client, test_regular_user) -> None:
        """Test updating user premium is_active does not work"""

        # Get initial token version
        initial_token_version = test_regular_user.token_version

        assert test_regular_user.premium.is_active is True
        update_data = {"premium": {"is_active": False}}
        response = regular_user_client.put("/current-user", json=update_data)
        assert response.status_code == 200

        updated_user = self.get_user(test_regular_user.id, session)
        assert updated_user.premium.is_active

        # Verify token version NOT incremented (no password/email change)
        assert updated_user.token_version == initial_token_version

        # Verify response does NOT indicate logout
        assert response.json().get("logged_out") is None

    def test_unauthorised_update(self, session, client, test_regular_user) -> None:
        """Test updating without authentication."""

        update_data = {"chase_threshold": 100}
        response = client.put("/current-user", json=update_data)
        assert response.status_code == 401

    def test_heartbeat_updates_last_login(self, regular_user_client, test_regular_user, session) -> None:
        """Test that heartbeat updates last_login and previous_login."""

        # Set an initial last_login
        initial_last_login = datetime(2024, 1, 1, tzinfo=timezone.utc)
        test_regular_user.last_login = initial_last_login
        session.commit()

        response = regular_user_client.post("/current-user/heartbeat")
        assert response.status_code == 200
        assert response.json()["success"] is True

        updated_user = self.get_user(test_regular_user.id, session)
        assert updated_user.previous_login == initial_last_login
        assert updated_user.last_login > initial_last_login

    def test_heartbeat_unauthenticated(self, client) -> None:
        """Test that heartbeat requires authentication."""

        response = client.post("/current-user/heartbeat")
        assert response.status_code == 401

    @pytest.mark.parametrize(
        "field, value",
        [
            ("first_name", "x" * (COLUMN_LIMITS.first_name + 1)),
            ("last_name", "x" * (COLUMN_LIMITS.last_name + 1)),
            ("password", "x" * (COLUMN_LIMITS.password + 1)),
            ("current_password", "x" * (COLUMN_LIMITS.password + 1)),
            ("app_version", "x" * (COLUMN_LIMITS.app_version + 1)),
        ],
    )
    def test_update_field_too_long(self, field, value, regular_user_client) -> None:
        """Test that updating current user with a field exceeding its max length returns 422."""
        response = regular_user_client.put("/current-user", json={field: value})
        assert response.status_code == 422


class TestSendEmailChangeWithRateLimit:

    @patch("app.core.routers.auth.email_service.send_email_change_verification")
    def test_send_verification_email(self, mock_email, test_users, session) -> None:
        """Test sending of email change verification email."""

        result = send_email_change_email(test_users[0], "newemail@test.com", session)
        assert result.success is True
        assert result.message == "Email change verification email sent successfully."
        assert mock_email.call_count == 1

        # Check token was created
        token_entry = (
            session.query(models.UserToken)
            .filter(models.UserToken.owner_id == test_users[0].id, models.UserToken.token_type == "email_change")
            .first()
        )
        assert token_entry is not None
        assert token_entry.pending_email == "newemail@test.com"

    @patch("app.core.routers.auth.email_service.send_email_change_verification")
    def test_send_verification_email_rate_limited(self, mock_email, test_users, session) -> None:
        """Test rate limiting when sending email change verification email."""

        send_email_change_email(test_users[0], "newemail@test.com", session)
        result = send_email_change_email(test_users[0], "newemail2@test.com", session)
        assert result.success is False
        assert result.error_code == 429
        assert mock_email.call_count == 1


class TestEmailVerification:

    @patch("app.core.routers.auth.email_service.send_email_change_notification")
    def test_verify_email_success(self, mock_email, client, test_user_change_email_token_user, session) -> None:
        """Test successful email change with valid token."""

        # Get initial token version
        initial_token_version = test_user_change_email_token_user.token_version

        # Get pending email from token
        token_entry = (
            session.query(models.UserToken)
            .filter(
                models.UserToken.owner_id == test_user_change_email_token_user.id,
                models.UserToken.token_type == "email_change",
            )
            .first()
        )
        assert token_entry
        pending_email = token_entry.pending_email

        response = client.get(
            f"/current-user/verify-email/{test_user_change_email_token_user.plain_verification_token}"
        )

        assert response.status_code == 200
        assert "email address changed successfully" in response.json()["message"].lower()

        user = session.query(models.User).filter(models.User.id == test_user_change_email_token_user.id).first()

        # Verify email updated
        assert user
        assert user.email == pending_email

        # Verify token was deleted
        token_entry = (
            session.query(models.UserToken)
            .filter(
                models.UserToken.owner_id == test_user_change_email_token_user.id,
                models.UserToken.token_type == "email_change",
            )
            .first()
        )
        assert token_entry is None

        # Verify token version incremented
        assert user.token_version == initial_token_version + 1

        # Verify notification sent
        assert mock_email.call_count == 1
        assert mock_email.call_args[0][0] == pending_email

    @patch("app.core.routers.auth.email_service.send_email_change_notification")
    def test_verify_email_demo_fail(self, mock_email, client, test_demo_user, session) -> None:
        """Test email change fails for demo user."""

        # Create email change token for demo user
        plain_token, token_obj = generate_token(
            test_demo_user.id, TokenType.EMAIL_CHANGE, session, pending_email="newemail@test.com"
        )

        response = client.get(f"/current-user/verify-email/{plain_token}")

        assert response.status_code == 403
        assert mock_email.call_count == 0

    def test_verify_email_invalid_token(self, client) -> None:
        """Test email verification with invalid token."""

        response = client.get("/current-user/verify-email/invalid_token_xyz")

        assert response.status_code == 403
        assert "invalid" in response.json()["detail"].lower()

    def test_verify_email_expired_token(self, client, session) -> None:
        """Test email verification with expired token."""

        # Create user with all required relationships
        user = models.User(
            email="unverified@test.com",
            password="password",
            is_verified=False,
            is_active=True,
            token_version=0,
        )
        session.add(user)
        session.commit()

        # Create expired token
        token = "expired_token_123"
        hashed_token = utils.hash_token(token)
        expired_time = datetime.now(timezone.utc) - timedelta(hours=25)

        token_entry = models.UserToken(
            owner_id=user.id,
            token=hashed_token,
            token_type="email_change",
            pending_email="newemail@test.com",
        )
        session.add(token_entry)
        session.commit()

        # Set expired time
        token_entry.created_at = expired_time
        session.commit()

        response = client.get(f"/current-user/verify-email/{token}")

        assert response.status_code == 403
        assert "expired" in response.json()["detail"].lower()

    def test_verify_email_existing(self, client, session, test_users) -> None:
        """Test email verification when pending email already exists."""

        # Create user
        user = models.User(
            email="unverified@test.com",
            password="password",
            is_verified=False,
            is_active=True,
            token_version=0,
        )
        session.add(user)
        session.commit()

        # Create token with existing email as pending
        plain_token, token_obj = generate_token(
            user.id, TokenType.EMAIL_CHANGE, session, pending_email=test_users[1].email
        )

        response = client.get(f"/current-user/verify-email/{plain_token}")

        assert response.status_code == 400
        assert response.json()["detail"].lower() == "email already registered"


class TestTokenVersioning:
    """Test suite for token versioning and invalidation."""

    def test_token_version_starts_at_zero(self, test_regular_user) -> None:
        """Test that new users start with token_version 0."""
        assert test_regular_user.token_version == 0

    def test_old_token_rejected_after_password_change(
        self, regular_user_client, test_regular_user, session, client
    ) -> None:
        """Test that tokens with old version are rejected after password change."""

        # First verify current token works
        response = regular_user_client.get("/current-user")
        assert response.status_code == 200

        # Change password (this increments token_version)
        update_data = {"current_password": test_regular_user.plain_password, "password": "newpassword1"}
        response = regular_user_client.put("/current-user", json=update_data)
        assert response.status_code == 200

        # Try to use old token - should fail
        response = regular_user_client.get("/current-user")
        assert response.status_code == 401
        assert "revoked" in response.json()["detail"].lower()

        # Verify new login works
        user = session.query(models.User).filter(models.User.id == test_regular_user.id).first()
        assert user
        new_token = oauth2.create_access_token(data={"user_id": test_regular_user.id}, token_version=user.token_version)
        response = client.get("/current-user", headers={"Authorization": f"Bearer {new_token}"})
        assert response.status_code == 200

    @patch("app.core.routers.auth.email_service.send_email_change_verification")
    def test_token_version_no_increments_on_email_change_request(
        self, _mock_email, regular_user_client, test_regular_user, session
    ) -> None:
        """Test that token version does NOT increment when email change is requested."""

        initial_version = test_regular_user.token_version

        update_data = {"email": "newemail@example.com", "current_password": test_regular_user.plain_password}
        response = regular_user_client.put("/current-user", json=update_data)
        assert response.status_code == 200

        user = session.query(models.User).filter(models.User.id == test_regular_user.id).first()
        assert user
        assert user.token_version == initial_version

    @patch("app.core.routers.auth.email_service.send_email_change_notification")
    def test_token_version_increments_on_email_verification(
        self, mock_email, client, test_user_change_email_token_user, session
    ) -> None:
        """Test that token version increments when email change is verified."""

        initial_version = test_user_change_email_token_user.token_version

        response = client.get(
            f"/current-user/verify-email/{test_user_change_email_token_user.plain_verification_token}"
        )
        assert response.status_code == 200

        user = session.query(models.User).filter(models.User.id == test_user_change_email_token_user.id).first()
        assert user
        assert user.token_version == initial_version + 1
        assert mock_email.call_count == 1

    def test_token_version_unchanged_for_non_sensitive_updates(
        self, regular_user_client, test_regular_user, session
    ) -> None:
        """Test that token version does NOT increment for non-password/email updates."""

        initial_version = test_regular_user.token_version

        update_data = {"chase_threshold": 200}
        response = regular_user_client.put("/current-user", json=update_data)
        assert response.status_code == 200

        user = session.query(models.User).filter(models.User.id == test_regular_user.id).first()
        assert user
        assert user.token_version == initial_version

        # Verify token still works
        response = regular_user_client.get("/current-user")
        assert response.status_code == 200


class TestDeleteAccount:
    """Test suite for account deletion endpoint."""

    def test_delete_account_success(self, regular_user_client, test_regular_user, session) -> None:
        """Test successful account deletion with correct password."""

        # Get user ID before deletion
        user_id = test_regular_user.id

        # Verify user exists
        user = session.query(models.User).filter(models.User.id == user_id).first()
        assert user is not None

        # Delete account
        delete_data = {"password": test_regular_user.plain_password}
        response = regular_user_client.request("DELETE", "/current-user", json=delete_data)

        assert response.status_code == 200
        assert response.json()["success"] is True
        assert "deleted successfully" in response.json()["message"].lower()

        # Verify user was deleted
        user = session.query(models.User).filter(models.User.id == user_id).first()
        assert user is None

    def test_delete_account_incorrect_password(self, regular_user_client, test_regular_user, session) -> None:
        """Test account deletion fails with incorrect password."""

        user_id = test_regular_user.id

        # Try to delete with wrong password
        delete_data = {"password": "wrongpassword"}
        response = regular_user_client.request("DELETE", "/current-user", json=delete_data)

        assert response.status_code == 401
        assert "incorrect" in response.json()["detail"].lower()

        # Verify user still exists
        user = session.query(models.User).filter(models.User.id == user_id).first()
        assert user is not None

    def test_delete_account_demo_user_fails(self, demo_user_client, test_demo_user, session) -> None:
        """Test that demo users cannot delete their account."""

        user_id = test_demo_user.id

        # Try to delete demo account
        delete_data = {"password": test_demo_user.plain_password}
        response = demo_user_client.request("DELETE", "/current-user", json=delete_data)

        assert response.status_code == 403
        assert "test users cannot delete" in response.json()["detail"].lower()

        # Verify demo user still exists
        user = session.query(models.User).filter(models.User.id == user_id).first()
        assert user is not None

    def test_delete_account_unauthenticated(self, client) -> None:
        """Test that unauthenticated users cannot delete accounts."""

        delete_data = {"password": "somepassword"}
        response = client.request("DELETE", "/current-user", json=delete_data)

        assert response.status_code == 401

    def test_delete_account_empty_password(self, regular_user_client, test_regular_user, session) -> None:
        """Test account deletion fails with empty password."""

        user_id = test_regular_user.id

        # Try to delete with empty password
        delete_data = {"password": ""}
        response = regular_user_client.request("DELETE", "/current-user", json=delete_data)

        assert response.status_code == 401
        assert "incorrect" in response.json()["detail"].lower()

        # Verify user still exists
        user = session.query(models.User).filter(models.User.id == user_id).first()
        assert user is not None

    def test_delete_account_cascades_to_related_data(self, regular_user_client, test_regular_user, session) -> None:
        """Test that deleting account cascades to all related data."""

        user_id = test_regular_user.id

        # Verify user has related data
        assert test_regular_user.preferences is not None
        assert test_regular_user.premium is not None
        preferences_id = test_regular_user.preferences.id
        premium_id = test_regular_user.premium.id

        # Create a Job for the user

        job = models.Job(title="Test Job", owner_id=user_id)
        session.add(job)
        session.commit()
        job_id = job.id

        # Create a Person and link it to the Job

        person = models.Person(first_name="John", last_name="Doe", owner_id=user_id)
        session.add(person)
        session.commit()
        person_id = person.id
        person.jobs.append(job)
        session.commit()

        # Create a service log for JobEmail

        email_service_log = models.JobEmailScrapingServiceLog(run_datetime=datetime.now(timezone.utc))
        session.add(email_service_log)
        session.commit()

        # Create a JobEmail

        job_email = models.JobEmail(
            external_email_id=f"test_email_{user_id}",
            subject="Test Job Alert",
            sender="jobs@linkedin.com",
            date_received=datetime.now(timezone.utc),
            platform="LinkedIn",
            body="Test email body",
            service_log_id=email_service_log.id,
            owner_id=user_id,
        )
        session.add(job_email)
        session.commit()
        job_email_id = job_email.id

        # Create a ScrapedJob and link it to the JobEmail

        scraped_job = models.ScrapedJob(
            external_job_id=f"test_scraped_job_{user_id}",
            platform="LinkedIn",
            title="Test Scraped Job",
            service_log_id=email_service_log.id,
            owner_id=user_id,
        )
        session.add(scraped_job)
        session.commit()
        scraped_job_id = scraped_job.id
        scraped_job.emails.append(job_email)
        session.commit()

        # Create a UserQualification for JobRating

        user_qualification = models.UserQualification(experience="Test experience", owner_id=user_id)
        session.add(user_qualification)
        session.commit()
        user_qualification_id = user_qualification.id

        # Create a JobRating for the ScrapedJob

        job_rating = job_rating_models.JobRating(
            overall_score=8,
            scraped_job_id=scraped_job_id,
            user_qualification_id=user_qualification_id,
            owner_id=user_id,
            llm_model="chatgpt",
        )
        session.add(job_rating)
        session.commit()
        job_rating_id = job_rating.id

        # Delete account
        delete_data = {"password": test_regular_user.plain_password}
        response = regular_user_client.request("DELETE", "/current-user", json=delete_data)

        assert response.status_code == 200

        # Verify user was deleted
        user = session.query(models.User).filter(models.User.id == user_id).first()
        assert user is None

        # Verify preferences were cascade deleted
        preferences = session.query(models.UserPreferences).filter(models.UserPreferences.id == preferences_id).first()
        assert preferences is None

        # Verify premium settings were cascade deleted
        premium = session.query(models.PremiumSettings).filter(models.PremiumSettings.id == premium_id).first()
        assert premium is None

        # Verify Job was cascade deleted
        job = session.query(models.Job).filter(models.Job.id == job_id).first()
        assert job is None

        # Verify Person was cascade deleted
        person = session.query(models.Person).filter(models.Person.id == person_id).first()
        assert person is None

        # Verify JobEmail was cascade deleted
        job_email = session.query(models.JobEmail).filter(models.JobEmail.id == job_email_id).first()
        assert job_email is None

        # Verify ScrapedJob was cascade deleted
        scraped_job = session.query(models.ScrapedJob).filter(models.ScrapedJob.id == scraped_job_id).first()
        assert scraped_job is None

        # Verify JobRating was cascade deleted
        job_rating = (
            session.query(job_rating_models.JobRating).filter(job_rating_models.JobRating.id == job_rating_id).first()
        )
        assert job_rating is None

        # Verify UserQualification was cascade deleted
        user_qualification = (
            session.query(models.UserQualification).filter(models.UserQualification.id == user_qualification_id).first()
        )
        assert user_qualification is None

    def test_delete_account_invalidates_token(self, regular_user_client, test_regular_user, session) -> None:
        """Test that deleting account prevents further API calls with the same token."""

        # Verify token works before deletion
        response = regular_user_client.get("/current-user")
        assert response.status_code == 200

        # Delete account
        delete_data = {"password": test_regular_user.plain_password}
        response = regular_user_client.request("DELETE", "/current-user", json=delete_data)
        assert response.status_code == 200

        # Try to use the same token after deletion - should fail
        response = regular_user_client.get("/current-user")
        assert response.status_code == 401

    def test_delete_account_with_user_tokens(self, regular_user_client, test_regular_user, session) -> None:
        """Test that deleting account also deletes associated user tokens."""

        from app.core.utils import generate_token

        user_id = test_regular_user.id

        # Create an email change token for the user
        generate_token(test_regular_user.id, TokenType.EMAIL_CHANGE, session, pending_email="newemail@test.com")

        # Verify token exists
        user_token = (
            session.query(models.UserToken)
            .filter(models.UserToken.owner_id == user_id, models.UserToken.token_type == "email_change")
            .first()
        )
        assert user_token is not None

        # Delete account
        delete_data = {"password": test_regular_user.plain_password}
        response = regular_user_client.request("DELETE", "/current-user", json=delete_data)
        assert response.status_code == 200

        # Verify user token was cascade deleted
        user_token = (
            session.query(models.UserToken)
            .filter(models.UserToken.owner_id == user_id, models.UserToken.token_type == "email_change")
            .first()
        )
        assert user_token is None


class TestSendReleaseEmail:
    """Test suite for the /send-release-email/{version} endpoint."""

    @patch("app.core.routers.user.email_service.send_new_version_email")
    def test_send_release_email_success(self, mock_send, admin_client, test_users) -> None:
        """Test successfully sending release emails as admin."""

        response = admin_client.post("/users/send-release-email/1.2.0")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "1.2.0" in data["message"]

        # Should only send to active, verified, non-demo users
        expected_recipients = [u for u in test_users if u.is_active and u.is_verified and not u.is_demo]
        assert mock_send.call_count == len(expected_recipients)

    @patch("app.core.routers.user.email_service.send_new_version_email")
    def test_send_release_email_invalid_version(self, mock_send, admin_client) -> None:
        """Test sending release email for a non-existent version returns 404."""

        response = admin_client.post("/users/send-release-email/99.99.99")

        assert response.status_code == 404
        assert "no release data" in response.json()["detail"].lower()
        assert mock_send.call_count == 0

    def test_send_release_email_non_admin(self, regular_user_client) -> None:
        """Test that non-admin users cannot send release emails."""

        response = regular_user_client.post("/users/send-release-email/1.2.0")
        assert response.status_code == 403

    def test_send_release_email_unauthenticated(self, client) -> None:
        """Test that unauthenticated users cannot send release emails."""

        response = client.post("/users/send-release-email/1.2.0")
        assert response.status_code == 401

    @patch("app.core.routers.user.email_service.send_new_version_email")
    def test_send_release_email_partial_failure(self, mock_send, admin_client, test_users) -> None:
        """Test that partial email failures are handled gracefully."""

        # Fail on the first call, succeed on the rest
        mock_send.side_effect = [Exception("SMTP error")] + [None] * (len(test_users) - 1)
        response = admin_client.post("/users/send-release-email/1.2.0")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

        expected_recipients = [u for u in test_users if u.is_active and u.is_verified and not u.is_demo]
        # One failed, so sent_count should be total - 1
        assert f"{len(expected_recipients) - 1}/{len(expected_recipients)}" in data["message"]


class TestUserQualificationsCRUD(CRUDTestBase):

    endpoint = "user-qualifications"
    actions_to_test = []

    def test_get_latest_user_qualification(self, authorised_clients, test_users, test_user_qualifications) -> None:
        """Test retrieving the latest user qualification for a user."""

        response = authorised_clients[0].get(f"{self.endpoint}/latest")
        qualifications = self.get_user_data(test_users, test_user_qualifications)
        latest_qualification = max(qualifications, key=lambda uq: uq.created_at)
        assert response.json()["id"] == latest_qualification.id
        assert response.status_code == 200

    def test_upsert_new(self, authorised_clients, test_users, session) -> None:
        """Try to insert a new user qualification."""

        # Without an ID
        new_qualification_data = {
            "experience": "Some stuff",
        }
        response = authorised_clients[0].post(f"{self.endpoint}", json=new_qualification_data)
        assert response.status_code == 200
        entry = session.query(models.UserQualification).all()
        assert len(entry) == 1

        # With an ID
        new_qualification_data = {
            "experience": "Some stuff",
            "id": 1,
        }
        response = authorised_clients[0].post(f"{self.endpoint}", json=new_qualification_data)
        assert response.status_code == 200
        entry = session.query(models.UserQualification).all()
        assert len(entry) == 1

    def test_upsert_with_existing_qualification(
        self, authorised_clients, test_users, test_user_qualifications, test_scraped_jobs, session
    ) -> None:
        """Try to upsert a new user qualification when not linked to a job rating"""

        qualifications = self.get_user_data(test_users, test_user_qualifications)
        qualification_data = {
            "experience": "Some stuff",
            "id": qualifications[0].id,
        }
        response = authorised_clients[0].post(f"{self.endpoint}", json=qualification_data)
        assert response.status_code == 200
        assert response.json()["id"] == qualifications[0].id

    def test_upsert_with_job_rating(
        self, authorised_clients, test_users, test_user_qualifications, test_scraped_jobs, session
    ) -> None:
        """Try to upsert a new user qualification when linked to a job rating"""

        job_rating = job_rating_models.JobRating(
            owner_id=test_users[0].id,
            scraped_job_id=test_scraped_jobs[0].id,
            overall_score=10,
            user_qualification_id=test_user_qualifications[0].id,
            llm_model="chatgpt",
        )
        session.add(job_rating)
        session.commit()

        new_qualification_data = {
            "experience": "Some stuff",
            "id": test_user_qualifications[0].id,
        }
        response = authorised_clients[0].post(f"{self.endpoint}", json=new_qualification_data)
        assert response.status_code == 200
        assert response.json()["id"] == len(test_user_qualifications) + 1

    def test_upsert_incorrect_user(
        self, authorised_clients, test_users, test_user_qualifications, test_scraped_jobs, session
    ) -> None:
        """Try to upsert a user qualification owned by a different user"""

        new_qualification_data = {
            "experience": "Some stuff",
            "id": test_user_qualifications[0].id,
        }
        response = authorised_clients[1].post(f"{self.endpoint}", json=new_qualification_data)
        assert response.status_code == 200
        assert response.json()["id"] == len(test_user_qualifications) + 1

    def test_experience_within_char_limit(self, authorised_clients, session) -> None:
        """Test that experience within the 10000 character limit is accepted."""

        data = {"experience": "a" * 10000}
        response = authorised_clients[0].post(f"{self.endpoint}", json=data)
        assert response.status_code == 200

    def test_experience_exceeds_char_limit(self, authorised_clients) -> None:
        """Test that experience exceeding 10000 characters is rejected."""

        data = {"experience": "a" * 10001}
        response = authorised_clients[0].post(f"{self.endpoint}", json=data)
        assert response.status_code == 422

    def test_skills_within_char_limit(self, authorised_clients, session) -> None:
        """Test that skills within the 3500 character limit is accepted."""

        data = {"skills": "a" * 3500}
        response = authorised_clients[0].post(f"{self.endpoint}", json=data)
        assert response.status_code == 200

    def test_skills_exceeds_char_limit(self, authorised_clients) -> None:
        """Test that skills exceeding 3500 characters is rejected."""

        data = {"skills": "a" * 3501}
        response = authorised_clients[0].post(f"{self.endpoint}", json=data)
        assert response.status_code == 422

    def test_qualities_exceeds_char_limit(self, authorised_clients) -> None:
        """Test that qualities exceeding 3500 characters is rejected."""

        data = {"qualities": "a" * 3501}
        response = authorised_clients[0].post(f"{self.endpoint}", json=data)
        assert response.status_code == 422

    def test_education_exceeds_char_limit(self, authorised_clients) -> None:
        """Test that education exceeding 3500 characters is rejected."""

        data = {"education": "a" * 3501}
        response = authorised_clients[0].post(f"{self.endpoint}", json=data)
        assert response.status_code == 422

    def test_interests_exceeds_char_limit(self, authorised_clients) -> None:
        """Test that interests exceeding 3500 characters is rejected."""

        data = {"interests": "a" * 3501}
        response = authorised_clients[0].post(f"{self.endpoint}", json=data)
        assert response.status_code == 422
