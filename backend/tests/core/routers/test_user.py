"""
This module contains a set of test functions to validate the functionality of user creation, user login,
and authentication workflows in the application. These tests ensure that the API endpoints for user-related
operations behave as expected under various scenarios, including successful requests and erroneous cases.
"""

import uuid
from datetime import datetime, timezone, timedelta
from unittest.mock import Mock

import pytest
from sqlalchemy.orm import Session
from starlette.testclient import TestClient

from app import models
from app.base_schemas import COLUMN_LIMITS
from app.core import schemas
from app.core.models import TokenType
from app.core.schemas import UserQualificationOut, UserOut
from app.utilities import security
from tests.base_test import BaseTest
from tests.conftest import CRUDTestBase
from tests.fixtures.users import FixtureUser


class TestUsersCRUD(CRUDTestBase[models.User]):
    endpoint = "/users"
    admin_only = True
    create_schema = schemas.UserCreate
    out_schema = schemas.UserOut
    update_data = {"email": "newemail@test.com", "premium": {"job_scraping_active": False}}

    def create_entry(self, session: Session, owner: FixtureUser, **overrides) -> models.User:
        overrides.setdefault("email", f"user_{uuid.uuid4().hex}@test.com")
        overrides.setdefault("password", "testpassword1")
        return self.create_user(session, **overrides)

    def create_payload(self, session: Session, owner: FixtureUser) -> dict:
        return {
            "email": f"user_{uuid.uuid4().hex}@test.com",
            "password": "testpassword1",
            "premium": {"job_scraping_active": False},
        }

    def test_update_admin_incorrect_email_format(
        self, test_regular_user: models.User, test_admin_user: models.User
    ) -> None:
        """Test updating with invalid email."""

        update_data = {"email": "incorrect_email"}
        response = test_admin_user.client.put(f"/users/{test_regular_user.id}", json=update_data)
        assert response.status_code == 422

    def test_update_admin_existing_email(self, test_admin_user: models.User, test_regular_user: models.User) -> None:
        """Test updating with an email that already exists."""

        update_data = {"email": test_admin_user.email}
        response = test_admin_user.client.put(f"/users/{test_regular_user.id}", json=update_data)
        assert response.status_code == 400

    def test_update_account(self, test_regular_user: models.User, test_admin_user: models.User) -> None:
        """Test updating account does not affect the password."""

        password = test_regular_user.password
        update_data = {"first_name": "New first name"}
        response = test_admin_user.client.put(f"/users/{test_regular_user.id}", json=update_data)
        assert response.status_code == 200
        test_regular_user.refresh()
        assert test_regular_user.password == password


class TestGetCurrentUser(BaseTest):

    endpoint = "/current-user"

    def test_get_current_user_admin_profile_success(self, test_admin_user: models.User) -> None:
        """Test successfully getting current admin user profile."""

        response = test_admin_user.client.get(self.endpoint)
        self.check_output(test_admin_user, response.json(), UserOut)

    def test_get_current_user_profile_success(self, test_regular_user: models.User) -> None:
        """Test successfully getting current user profile."""

        response = test_regular_user.client.get(self.endpoint)
        self.check_output(test_regular_user, response.json(), UserOut)


class TestUpdateCurrentUserEmail(BaseTest):

    endpoint = "/current-user/email"

    def test_update_email(self, mock_email_verif: Mock, test_regular_user: models.User) -> None:
        """Test updating own profile as non-admin (with email change)."""

        # Get initial token version
        initial_token_version = test_regular_user.token_version

        update_data = {"email": "newemail@example.com", "current_password": test_regular_user.plain_password}
        response = test_regular_user.client.put(self.endpoint, json=update_data)
        assert mock_email_verif.call_count == 1
        assert mock_email_verif.call_args[0][0] == "newemail@example.com"
        assert response.status_code == 200

        # Verify email hasn't changed yet (pending verification)
        test_regular_user.refresh()
        assert test_regular_user.email != update_data["email"]

        # Check pending_email is in UserToken table
        token_entry = test_regular_user.get_token(TokenType.EMAIL_CHANGE)
        assert token_entry is not None
        assert token_entry.pending_email == update_data["email"]

        # Verify token version has not changed
        assert test_regular_user.token_version == initial_token_version

    def test_update_email_rate_limited(self, mock_email_verif: Mock, test_regular_user: models.User) -> None:
        """Test that a rate-limited email change returns 429."""

        test_regular_user.client.put(
            self.endpoint, json={"email": "newemail@example.com", "current_password": test_regular_user.plain_password}
        )
        # Second request — should be rate limited
        response = test_regular_user.client.put(
            self.endpoint, json={"email": "another@example.com", "current_password": test_regular_user.plain_password}
        )
        assert response.status_code == 429
        assert mock_email_verif.call_count == 1
        assert "wait" in response.json()["detail"].lower()

    def test_update_email_same_as_current(self, mock_email_verif: Mock, test_regular_user: models.User) -> None:
        """Test that requesting an email change to the current email returns 400."""

        response = test_regular_user.client.put(
            self.endpoint,
            json={"email": test_regular_user.email, "current_password": test_regular_user.plain_password},
        )
        assert response.status_code == 400
        assert mock_email_verif.call_count == 0

    def test_update_email_incorrect_password(self, mock_email_verif: Mock, test_regular_user: models.User) -> None:
        """Test that an email change with an incorrect current password returns 401."""

        update_data = {"email": "newemail@example.com", "current_password": "wrongpassword"}
        response = test_regular_user.client.put(self.endpoint, json=update_data)
        assert response.status_code == 401
        assert mock_email_verif.call_count == 0

    def test_update_email_demo_fail(self, mock_email_verif: Mock, test_demo_user: models.User) -> None:
        """Test updating own email as demo user (should fail)."""

        update_data = {"email": "newemail@example.com", "current_password": test_demo_user.plain_password}
        response = test_demo_user.client.put(self.endpoint, json=update_data)
        assert response.status_code == 403
        assert mock_email_verif.call_count == 0

    def test_update_incorrect_email_format(self, mock_email_verif: Mock, test_regular_user: models.User) -> None:
        """Test updating with invalid email."""

        update_data = {"email": "ff", "current_password": test_regular_user.plain_password}
        response = test_regular_user.client.put(self.endpoint, json=update_data)
        assert response.status_code == 422
        assert mock_email_verif.call_count == 0

    def test_update_existing_email(
        self, mock_email_verif: Mock, test_regular_user: models.User, test_admin_user: models.User
    ) -> None:
        """Test updating with an email that already exists."""

        update_data = {"email": test_admin_user.email, "current_password": test_regular_user.plain_password}
        response = test_regular_user.client.put(self.endpoint, json=update_data)
        assert response.status_code == 400
        assert mock_email_verif.call_count == 0


class TestUpdateCurrentUserPassword(BaseTest):

    endpoint = "/current-user/password"

    def test_update_password(self, mock_password_notify: Mock, test_regular_user: models.User) -> None:
        """Test updating own password as non-admin."""

        # Get initial token version
        initial_token_version = test_regular_user.token_version

        update_data = {"current_password": test_regular_user.plain_password, "new_password": "newpassword1"}
        response = test_regular_user.client.put(self.endpoint, json=update_data)
        assert response.status_code == 200
        assert "password changed email sent successfully" in response.json()["message"].lower()

        # Verify password changed and token version incremented
        test_regular_user.refresh()
        assert security.verify_password(update_data["new_password"], test_regular_user.password)
        assert test_regular_user.token_version == initial_token_version + 1

        # Verify email sent
        assert mock_password_notify.call_count == 1
        assert mock_password_notify.call_args[0][0] == test_regular_user.email

    def test_update_password_rate_limited(self, mock_password_notify: Mock, test_regular_user: models.User) -> None:
        """Test that a rate-limited password change returns 429."""

        # A first password change succeeds and seeds a recent PASSWORD_CHANGE token
        response = test_regular_user.client.put(
            self.endpoint,
            json={"current_password": test_regular_user.plain_password, "new_password": "newpassword1"},
        )
        assert response.status_code == 200

        # The change revoked the current token, so re-authenticate before the next request
        test_regular_user.reauthenticate()

        response = test_regular_user.client.put(
            self.endpoint,
            json={"current_password": "newpassword1", "new_password": "newpassword2"},
        )
        assert response.status_code == 429
        assert "wait" in response.json()["detail"].lower()
        assert mock_password_notify.call_count == 1

    def test_update_password_demo_fail(self, mock_password_notify: Mock, test_demo_user: models.User) -> None:
        """Test updating own password as demo user (should fail)."""

        update_data = {"current_password": test_demo_user.plain_password, "new_password": "newpassword1"}
        response = test_demo_user.client.put(self.endpoint, json=update_data)
        assert response.status_code == 403
        assert mock_password_notify.call_count == 0

    def test_update_password_revokes_token(self, mock_password_notify: Mock, test_regular_user: models.User) -> None:
        """Test that updating password invalidates current token."""

        # Change password
        update_data = {"current_password": test_regular_user.plain_password, "new_password": "newpassword1"}
        response = test_regular_user.client.put(self.endpoint, json=update_data)
        assert response.status_code == 200
        assert mock_password_notify.call_count == 1

        # Try to use the old token (test_client still has it)
        response = test_regular_user.client.get("/current-user")
        assert response.status_code == 401
        assert "revoked" in response.json()["detail"].lower()

    def test_update_password_incorrect_password(
        self, mock_password_notify: Mock, test_regular_user: models.User
    ) -> None:
        """Test updating password with incorrect current password."""

        update_data = {"current_password": "", "new_password": "newpassword1"}
        response = test_regular_user.client.put(self.endpoint, json=update_data)
        assert response.status_code == 401
        assert mock_password_notify.call_count == 0

    @pytest.mark.parametrize(
        "field, value",
        [
            ("current_password", "x" * (COLUMN_LIMITS.password + 1)),
            ("new_password", "x" * (COLUMN_LIMITS.password + 1)),
        ],
        ids=[
            "current_password_too_long",
            "new_password_too_long",
        ],
    )
    def test_update_password_field_too_long(self, field: str, value: str, test_regular_user: models.User) -> None:
        """Test that updating password with a field exceeding its max length returns 422."""
        response = test_regular_user.client.put(self.endpoint, json={field: value})
        assert response.status_code == 422

    def test_token_version_starts_at_zero(self, test_regular_user: models.User) -> None:
        """Test that new users start with token_version 0."""

        assert test_regular_user.token_version == 0

    def test_old_token_rejected_after_password_change(
        self, mock_password_notify: Mock, test_regular_user: models.User
    ) -> None:
        """Test that tokens with an old version are rejected after a password change, and a fresh one works."""

        # Current token works
        assert test_regular_user.client.get("/current-user").status_code == 200

        # Change password (this increments token_version, revoking existing tokens)
        update_data = {"current_password": test_regular_user.plain_password, "new_password": "newpassword1"}
        assert test_regular_user.client.put(self.endpoint, json=update_data).status_code == 200

        # The old token is now rejected
        response = test_regular_user.client.get("/current-user")
        assert response.status_code == 401
        assert "revoked" in response.json()["detail"].lower()

        # A token minted for the new version is accepted
        test_regular_user.reauthenticate()
        assert test_regular_user.client.get("/current-user").status_code == 200


class TestUpdateCurrentUser(BaseTest):

    endpoint = "/current-user"

    def test_update_account(self, test_regular_user: models.User) -> None:
        """Test updating account does not affect the password."""

        password = test_regular_user.password
        update_data = {"first_name": "New first name"}
        response = test_regular_user.client.put(self.endpoint, json=update_data)
        assert response.status_code == 200
        test_regular_user.refresh()
        assert test_regular_user.password == password

    def test_update_preferences(self, test_regular_user: models.User) -> None:
        """Test updating user preferences that don't require password."""

        # Get initial token version
        initial_token_version = test_regular_user.token_version

        update_data = {"preferences": {"default_currency": "USD"}}
        response = test_regular_user.client.put(self.endpoint, json=update_data)
        assert response.status_code == 200

        test_regular_user.refresh()
        assert test_regular_user.preferences.default_currency == "USD"

        # Verify token version NOT incremented (no password/email change)
        assert test_regular_user.token_version == initial_token_version

    def test_update_table_page_size(self, test_regular_user: models.User) -> None:
        """Test storing, clearing and validating the per-table page size preference."""

        assert test_regular_user.preferences.table_page_size is None

        # "speculativeApplication" is the longest entity type the frontend sends
        page_sizes = {"job": 50, "speculativeApplication": 30}
        response = test_regular_user.client.put(self.endpoint, json={"preferences": {"table_page_size": page_sizes}})
        assert response.status_code == 200
        test_regular_user.refresh()
        assert test_regular_user.preferences.table_page_size == page_sizes

        response = test_regular_user.client.put(self.endpoint, json={"preferences": {"table_page_size": None}})
        assert response.status_code == 200
        test_regular_user.refresh()
        assert test_regular_user.preferences.table_page_size is None

        for invalid in ({"job": 0}, {"job": 201}, {"job": "many"}):
            response = test_regular_user.client.put(self.endpoint, json={"preferences": {"table_page_size": invalid}})
            assert response.status_code == 422

    def test_update_premium(self, test_regular_user: models.User) -> None:
        """Test updating user premium details that don't require password."""

        # Get initial token version
        initial_token_version = test_regular_user.token_version

        assert test_regular_user.premium.job_scraping_active is True
        update_data = {"premium": {"job_scraping_active": False}}
        response = test_regular_user.client.put(self.endpoint, json=update_data)
        assert response.status_code == 200

        test_regular_user.refresh()
        assert not test_regular_user.premium.job_scraping_active

        # Verify token version NOT incremented (no password/email change)
        assert test_regular_user.token_version == initial_token_version

    def test_update_premium_is_active(self, test_regular_user: models.User) -> None:
        """Test updating user premium is_active does not work"""

        # Get initial token version
        initial_token_version = test_regular_user.token_version

        assert test_regular_user.premium.is_active is True
        update_data = {"premium": {"is_active": False}}
        response = test_regular_user.client.put(self.endpoint, json=update_data)
        assert response.status_code == 200

        test_regular_user.refresh()
        assert test_regular_user.premium.is_active

        # Verify token version NOT incremented (no password/email change)
        assert test_regular_user.token_version == initial_token_version

    def test_unauthorised_update(self, client: TestClient) -> None:
        """Test updating without authentication."""

        update_data = {"preferences": {"default_currency": "USD"}}
        response = client.put(self.endpoint, json=update_data)
        assert response.status_code == 401

    def test_heartbeat_updates_last_login(self, test_regular_user: models.User, session: Session) -> None:
        """Test that heartbeat updates last_login and previous_login."""

        # Set an initial last_login
        initial_last_login = datetime(2024, 1, 1, tzinfo=timezone.utc)
        test_regular_user.last_login = initial_last_login
        session.commit()

        response = test_regular_user.client.post(f"{self.endpoint}/heartbeat")
        assert response.status_code == 200
        assert response.json()["success"] is True

        test_regular_user.refresh()
        assert test_regular_user.previous_login == initial_last_login
        assert test_regular_user.last_login > initial_last_login

    def test_heartbeat_unauthenticated(self, client: TestClient) -> None:
        """Test that heartbeat requires authentication."""

        response = client.post(f"{self.endpoint}/heartbeat")
        assert response.status_code == 401

    @pytest.mark.parametrize(
        "field, value",
        [
            ("first_name", "x" * (COLUMN_LIMITS.first_name + 1)),
            ("last_name", "x" * (COLUMN_LIMITS.last_name + 1)),
            ("app_version", "x" * (COLUMN_LIMITS.app_version + 1)),
        ],
        ids=[
            "first_name_too_long",
            "last_name_too_long",
            "app_version_too_long",
        ],
    )
    def test_update_field_too_long(self, field: str, value: str, test_regular_user: models.User) -> None:
        """Test that updating current user with a field exceeding its max length returns 422."""

        response = test_regular_user.client.put(self.endpoint, json={field: value})
        assert response.status_code == 422


class TestEmailVerification(BaseTest):
    """Test the email verification flow"""

    endpoint = "/current-user/verify-email"

    def test_verify_email_success(
        self, mock_email_notify: Mock, client: TestClient, test_regular_user: models.User
    ) -> None:
        """Test successful email change with valid token."""

        # Create a pending email change token
        pending_email = "newemail@test.com"
        plain_token, _ = test_regular_user.create_token(TokenType.EMAIL_CHANGE, pending_email=pending_email)
        initial_token_version = test_regular_user.token_version

        response = client.get(f"{self.endpoint}/{plain_token}")
        assert response.status_code == 200
        assert "email address has been successfully updated" in response.json()["message"].lower()

        # Verify email updated
        test_regular_user.refresh()
        assert test_regular_user.email == pending_email

        # Verify token was deleted
        assert test_regular_user.get_token(TokenType.EMAIL_CHANGE) is None

        # Verify token version incremented
        assert test_regular_user.token_version == initial_token_version + 1

        # Verify notification sent
        assert mock_email_notify.call_count == 1
        assert mock_email_notify.call_args[0][0] == pending_email

    def test_verify_email_demo_fail(
        self, mock_email_notify: Mock, client: TestClient, test_demo_user: models.User
    ) -> None:
        """Test email change fails for demo user."""

        plain_token = test_demo_user.create_token(TokenType.EMAIL_CHANGE, pending_email="newemail@test.com")[0]
        response = client.get(f"{self.endpoint}/{plain_token}")
        assert response.status_code == 403
        assert mock_email_notify.call_count == 0

    def test_verify_email_invalid_token(self, mock_email_notify: Mock, client: TestClient) -> None:
        """Test email verification with invalid token."""

        response = client.get(f"{self.endpoint}/invalid_token_xyz")
        assert response.status_code == 403
        assert "invalid" in response.json()["detail"].lower()
        assert mock_email_notify.call_count == 0

    def test_verify_email_expired_token(
        self, mock_email_notify: Mock, client: TestClient, test_regular_user: models.User
    ) -> None:
        """Test email verification with expired token."""

        # Create an already-expired email change token
        expired_time = datetime.now(timezone.utc) - timedelta(hours=25)
        plain_token, _ = test_regular_user.create_token(
            TokenType.EMAIL_CHANGE, pending_email="newemail@test.com", created_at=expired_time
        )

        response = client.get(f"{self.endpoint}/{plain_token}")

        assert response.status_code == 403
        assert "expired" in response.json()["detail"].lower()
        assert mock_email_notify.call_count == 0

    def test_verify_email_existing(
        self,
        mock_email_notify: Mock,
        client: TestClient,
        test_unverified_user: models.User,
        test_admin_user: models.User,
    ) -> None:
        """Test email verification when pending email already exists."""

        # Create token with an existing email as pending
        plain_token = test_unverified_user.create_token(TokenType.EMAIL_CHANGE, pending_email=test_admin_user.email)[0]

        response = client.get(f"{self.endpoint}/{plain_token}")

        assert response.status_code == 400
        assert response.json()["detail"].lower() == "email already registered"
        assert mock_email_notify.call_count == 0


class TestVerifyPassword(BaseTest):
    """Test suite for the POST /current-user/verify-password endpoint."""

    endpoint = "/current-user/verify-password"

    def test_verify_password_success(self, test_regular_user: models.User) -> None:
        """Test that the correct password returns 200."""

        response = test_regular_user.client.post(self.endpoint, json={"password": test_regular_user.plain_password})
        assert response.status_code == 200
        assert response.json()["success"] is True

    def test_verify_password_incorrect_password(self, test_regular_user: models.User) -> None:
        """Test that a wrong password returns 401."""

        response = test_regular_user.client.post(
            self.endpoint, json={"password": test_regular_user.plain_password + "wrong"}
        )
        assert response.status_code == 401
        assert "incorrect" in response.json()["detail"].lower()

    def test_verify_password_empty_password(self, test_regular_user: models.User) -> None:
        """Test that an empty password returns 401."""

        response = test_regular_user.client.post(self.endpoint, json={"password": ""})
        assert response.status_code == 401
        assert "incorrect" in response.json()["detail"].lower()

    def test_verify_password_unauthenticated(self, client: TestClient) -> None:
        """Test that unauthenticated requests return 401."""

        response = client.post(self.endpoint, json={"password": "anypassword"})
        assert response.status_code == 401


class TestDeleteAccount(BaseTest):
    """Test suite for account deletion endpoint."""

    endpoint = "/current-user"

    def test_delete_account_success(self, test_regular_user: models.User, session: Session) -> None:
        """Test successful account deletion with correct password."""

        delete_data = {"password": test_regular_user.plain_password}
        response = test_regular_user.client.request("DELETE", self.endpoint, json=delete_data)

        assert response.status_code == 200
        assert response.json()["success"] is True
        assert "deleted successfully" in response.json()["message"].lower()
        assert self.get_user(session, test_regular_user.id) is None

    def test_delete_account_incorrect_password(self, test_regular_user: models.User, session: Session) -> None:
        """Test account deletion fails with incorrect password."""

        delete_data = {"password": "wrongpassword"}
        response = test_regular_user.client.request("DELETE", self.endpoint, json=delete_data)

        assert response.status_code == 401
        assert "incorrect" in response.json()["detail"].lower()
        assert self.get_user(session, test_regular_user.id) == test_regular_user

    def test_delete_account_demo_user_fails(self, test_demo_user: models.User, session: Session) -> None:
        """Test that demo users cannot delete their account."""

        delete_data = {"password": test_demo_user.plain_password}
        response = test_demo_user.client.request("DELETE", self.endpoint, json=delete_data)

        assert response.status_code == 403
        assert "test users cannot delete" in response.json()["detail"].lower()
        assert self.get_user(session, test_demo_user.id) is not None

    def test_delete_account_unauthenticated(self, client: TestClient) -> None:
        """Test that unauthenticated users cannot delete accounts."""

        delete_data = {"password": "somepassword"}
        response = client.request("DELETE", self.endpoint, json=delete_data)

        assert response.status_code == 401

    def test_delete_account_empty_password(self, test_regular_user: models.User, session: Session) -> None:
        """Test account deletion fails with empty password."""

        delete_data = {"password": ""}
        response = test_regular_user.client.request("DELETE", self.endpoint, json=delete_data)

        assert response.status_code == 401
        assert "incorrect" in response.json()["detail"].lower()
        assert self.get_user(session, test_regular_user.id) == test_regular_user

    def test_delete_account_cascades_to_related_data(self, test_regular_user: models.User, session: Session) -> None:
        """Test that deleting account cascades to all related data."""

        user_id = test_regular_user.id

        # Verify user has related data
        assert test_regular_user.preferences is not None
        assert test_regular_user.premium is not None
        preferences_id = test_regular_user.preferences.id
        premium_id = test_regular_user.premium.id

        # Create a Job and a Person linked to it
        job = test_regular_user.create_job(title="Test Job")
        job_id = job.id
        person = test_regular_user.create_person(first_name="John", last_name="Doe")
        person_id = person.id
        person.jobs.append(job)
        session.commit()

        # Create a JobEmail and a ScrapedJob linked to it
        job_email = test_regular_user.create_job_email()
        job_email_id = job_email.id
        scraped_job = test_regular_user.create_scraped_job(title="Test Scraped Job")
        scraped_job_id = scraped_job.id
        scraped_job.emails.append(job_email)
        session.commit()

        # Create a UserQualification and a JobRating for the ScrapedJob
        user_qualification = test_regular_user.create_user_qualification(experience="Test experience")
        user_qualification_id = user_qualification.id
        job_rating = test_regular_user.create_job_rating(
            scraped_job=scraped_job, user_qualification=user_qualification, overall_score=8
        )
        job_rating_id = job_rating.id

        # Delete account
        delete_data = {"password": test_regular_user.plain_password}
        response = test_regular_user.client.request("DELETE", self.endpoint, json=delete_data)

        assert response.status_code == 200

        # Verify the user and all related data were cascade deleted
        assert self.get_user(session, user_id) is None
        assert self.get_by_id(session, models.UserPreferences, preferences_id) is None
        assert self.get_by_id(session, models.PremiumSettings, premium_id) is None
        assert self.get_by_id(session, models.Job, job_id) is None
        assert self.get_by_id(session, models.Person, person_id) is None
        assert self.get_by_id(session, models.JobEmail, job_email_id) is None
        assert self.get_by_id(session, models.ScrapedJob, scraped_job_id) is None
        assert self.get_by_id(session, models.JobRating, job_rating_id) is None
        assert self.get_by_id(session, models.UserQualification, user_qualification_id) is None

    def test_delete_account_invalidates_token(self, test_regular_user: models.User) -> None:
        """Test that deleting account prevents further API calls with the same token."""

        # Delete account
        delete_data = {"password": test_regular_user.plain_password}
        response = test_regular_user.client.request("DELETE", self.endpoint, json=delete_data)
        assert response.status_code == 200

        # Try to use the same token after deletion - should fail
        response = test_regular_user.client.get(self.endpoint)
        assert response.status_code == 401

    def test_delete_account_with_user_tokens(self, test_regular_user: models.User) -> None:
        """Test that deleting account also deletes associated user tokens."""

        # Create an email change token for the user and verify it exists
        test_regular_user.create_token(TokenType.EMAIL_CHANGE, pending_email="newemail@test.com")
        assert test_regular_user.get_token(TokenType.EMAIL_CHANGE) is not None

        # Delete account
        delete_data = {"password": test_regular_user.plain_password}
        response = test_regular_user.client.request("DELETE", self.endpoint, json=delete_data)
        assert response.status_code == 200

        # Verify user token was cascade deleted
        assert test_regular_user.get_token(TokenType.EMAIL_CHANGE) is None


class TestSendReleaseEmail(BaseTest):
    """Test suite for the /send-release-email/{version} endpoint."""

    endpoint = "/users/send-release-email"

    @pytest.fixture
    def test_users(
        self,
        test_regular_user: models.User,
        test_admin_user: models.User,
        test_inactive_user: models.User,
        test_unverified_user: models.User,
        test_demo_user: models.User,
    ) -> list[models.User]:
        """Two eligible recipients (regular, admin) plus one each excluded by inactive/unverified/demo."""

        return [test_regular_user, test_admin_user, test_inactive_user, test_unverified_user, test_demo_user]

    def test_send_release_email_success(
        self,
        mock_release_email: Mock,
        test_users: list[models.User],
        test_admin_user: models.User,
    ) -> None:
        """Test successfully sending release emails as admin."""

        response = test_admin_user.client.post(f"{self.endpoint}/1.2.0")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "1.2.0" in data["message"]

        # Should only send to active, verified, non-demo users
        expected_recipients = [u for u in test_users if u.is_active and u.is_verified and not u.is_demo]
        assert mock_release_email.call_count == len(expected_recipients)

    def test_send_release_email_invalid_version(self, mock_release_email: Mock, test_admin_user: models.User) -> None:
        """Test sending release email for a non-existent version returns 404."""

        response = test_admin_user.client.post(f"{self.endpoint}/99.99.99")

        assert response.status_code == 404
        assert "no release data" in response.json()["detail"].lower()
        assert mock_release_email.call_count == 0

    def test_send_release_email_non_admin(self, mock_release_email: Mock, test_regular_user: models.User) -> None:
        """Test that non-admin users cannot send release emails."""

        response = test_regular_user.client.post(f"{self.endpoint}/1.2.0")
        assert response.status_code == 403
        assert mock_release_email.call_count == 0

    def test_send_release_email_unauthenticated(self, mock_release_email: Mock, client: TestClient) -> None:
        """Test that unauthenticated users cannot send release emails."""

        response = client.post(f"{self.endpoint}/1.2.0")
        assert response.status_code == 401
        assert mock_release_email.call_count == 0

    def test_send_release_email_partial_failure(
        self,
        mock_release_email: Mock,
        test_users: list[models.User],
        test_admin_user: models.User,
    ) -> None:
        """Test that partial email failures are handled gracefully."""

        # Fail on the first call, succeed on the rest
        mock_release_email.side_effect = [Exception("SMTP error")] + [None] * (len(test_users) - 1)
        response = test_admin_user.client.post(f"{self.endpoint}/1.2.0")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

        expected_recipients = [u for u in test_users if u.is_active and u.is_verified and not u.is_demo]
        # One failed, so sent_count should be total - 1
        assert f"{len(expected_recipients) - 1}/{len(expected_recipients)}" in data["message"]


class TestUserQualificationsCRUD(BaseTest):

    endpoint = "user-qualifications"

    def test_get_latest_user_qualification(self, test_regular_user: models.User) -> None:
        """Test retrieving the latest user qualification for a user."""

        qualifications = [
            test_regular_user.create_user_qualification(education="BSc Computer Science"),
            test_regular_user.create_user_qualification(education="BSc Computer Science + PhD AI"),
        ]
        response = test_regular_user.client.get(f"{self.endpoint}/latest")
        assert response.status_code == 200
        self.check_output(qualifications[1], response.json(), UserQualificationOut)

    def test_upsert_new(self, session: Session, test_regular_user: models.User) -> None:
        """Try to insert a new user qualification."""

        # Without an ID
        response = test_regular_user.client.post(f"{self.endpoint}", json={"experience": "Some stuff"})
        assert response.status_code == 200
        new_id = response.json()["id"]
        assert session.query(models.UserQualification).count() == 1

        # With an ID
        response = test_regular_user.client.post(f"{self.endpoint}", json={"experience": "Some stuff", "id": new_id})
        assert response.status_code == 200
        assert session.query(models.UserQualification).count() == 1

    def test_upsert_with_existing_qualification(self, test_regular_user: models.User) -> None:
        """Updating a user qualification when not linked to a job rating should update the qualification."""

        qualification = test_regular_user.create_user_qualification(education="BSc Computer Science")
        qualification_data = {
            "education": "Some stuff",
            "id": qualification.id,
        }
        response = test_regular_user.client.post(f"{self.endpoint}", json=qualification_data)
        assert response.status_code == 200
        self.check_output(qualification_data, response.json(), UserQualificationOut)

    def test_upsert_with_job_rating(self, test_regular_user: models.User) -> None:
        """Upserting a new user qualification when linked to a job rating creates a new qualification entry"""

        qualification = test_regular_user.create_user_qualification(education="BSc Computer Science")
        test_regular_user.create_job_rating(user_qualification=qualification, overall_score=10)
        new_qualification_data = {
            "education": "Some stuff",
            "id": qualification.id,
        }
        response = test_regular_user.client.post(f"{self.endpoint}", json=new_qualification_data)
        assert response.status_code == 200
        assert response.json()["id"] == qualification.id + 1
        assert response.json()["education"] == new_qualification_data["education"]

    def test_upsert_incorrect_user(self, test_regular_user: models.User, test_admin_user: models.User) -> None:
        """Upserting a user qualification for a different user should create a new qualification entry"""

        qualification = test_regular_user.create_user_qualification(education="BSc Computer Science")
        new_qualification_data = {
            "experience": "Some stuff",
            "id": qualification.id,
        }
        response = test_admin_user.client.post(f"{self.endpoint}", json=new_qualification_data)
        assert response.status_code == 200
        assert response.json()["id"] == qualification.id + 1

    @pytest.mark.parametrize("field", ["experience", "education", "skills", "qualities", "interests"])
    def test_char_limit(self, test_regular_user: models.User, field: str) -> None:
        """Test that a profile field at its character limit is accepted and one character over is rejected."""

        limit = getattr(COLUMN_LIMITS, field)

        response = test_regular_user.client.post(f"{self.endpoint}", json={field: "a" * limit})
        assert response.status_code == 200

        response = test_regular_user.client.post(f"{self.endpoint}", json={field: "a" * (limit + 1)})
        assert response.status_code == 422
