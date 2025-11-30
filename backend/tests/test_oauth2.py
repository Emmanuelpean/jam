"""
Test module for OAuth2 authentication and JWT token functionality.
Tests token creation, verification, and user authentication with token versioning.
"""

from datetime import datetime, timedelta, timezone

import pytest
from fastapi import HTTPException, status
from jose import jwt

from app import oauth2, schemas
from app.config import settings


class TestCreateAccessToken:
    """Test suite for create_access_token function."""

    def test_create_access_token_success(self):
        """Test successful creation of JWT access token."""

        user_data = {"user_id": 1}
        token_version = 5

        token = oauth2.create_access_token(user_data, token_version)

        # Verify token is a string
        assert isinstance(token, str)
        assert len(token) > 0

        # Decode and verify payload
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        assert payload["user_id"] == 1
        assert payload["token_version"] == 5
        assert "exp" in payload

    def test_create_access_token_default_token_version(self):
        """Test token creation with default token version (0)."""

        user_data = {"user_id": 456}

        token = oauth2.create_access_token(user_data)
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])

        assert payload["token_version"] == 0

    def test_create_access_token_expiration(self):
        """Test that token has correct expiration time."""

        user_data = {"user_id": 1}
        before_creation = datetime.now(timezone.utc)

        token = oauth2.create_access_token(user_data)

        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])

        # Convert exp timestamp to datetime
        exp_time = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
        expected_exp = before_creation + timedelta(minutes=settings.access_token_expire_minutes)

        # Allow 5 second tolerance for test execution time
        assert abs((exp_time - expected_exp).total_seconds()) < 5

    def test_create_access_token_preserves_original_data(self):
        """Test that original data dictionary is not modified."""

        original_data = {"user_id": 1, "email": "test@test.com"}
        data_copy = original_data.copy()

        oauth2.create_access_token(original_data)

        # Verify original data unchanged
        assert original_data == data_copy
        assert "exp" not in original_data
        assert "token_version" not in original_data


class TestVerifyAccessToken:
    """Test suite for verify_access_token function."""

    def test_verify_access_token_success(self):
        """Test successful token verification."""

        user_data = {"user_id": 1}
        token = oauth2.create_access_token(user_data, token_version=2)
        credentials_exception = HTTPException(status_code=401, detail="Invalid")

        token_data = oauth2.verify_access_token(token, credentials_exception)

        assert isinstance(token_data, schemas.TokenData)
        assert token_data.id == "1"
        assert token_data.token_version == 2

    def test_verify_access_token_invalid_token(self):
        """Test verification fails with invalid token."""

        invalid_token = "invalid.token.here"
        credentials_exception = HTTPException(status_code=401, detail="Invalid token")

        with pytest.raises(HTTPException) as exc_info:
            oauth2.verify_access_token(invalid_token, credentials_exception)

        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == "Invalid token"

    def test_verify_access_token_missing_user_id(self):
        """Test verification fails when user_id is missing from payload."""

        # Create token without user_id
        token_data = {"some_field": "value"}
        token = jwt.encode(token_data, settings.secret_key, algorithm=settings.algorithm)
        credentials_exception = HTTPException(status_code=401, detail="No user ID")

        with pytest.raises(HTTPException) as exc_info:
            oauth2.verify_access_token(token, credentials_exception)

        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == "No user ID"

    def test_verify_access_token_expired(self):
        """Test verification fails with expired token."""

        # Create expired token
        user_data = {"user_id": 1}
        expired_time = datetime.now(timezone.utc) - timedelta(hours=1)
        payload = {**user_data, "exp": expired_time, "token_version": 0}
        expired_token = jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)

        credentials_exception = HTTPException(status_code=401, detail="Token expired")

        with pytest.raises(HTTPException) as exc_info:
            oauth2.verify_access_token(expired_token, credentials_exception)

        assert exc_info.value.status_code == 401

    def test_verify_access_token_wrong_secret(self):
        """Test verification fails with token signed with different secret."""

        user_data = {"user_id": 1}
        wrong_secret_token = jwt.encode(user_data, "wrong_secret_key", algorithm=settings.algorithm)
        credentials_exception = HTTPException(status_code=401, detail="Invalid signature")

        with pytest.raises(HTTPException) as exc_info:
            oauth2.verify_access_token(wrong_secret_token, credentials_exception)

        assert exc_info.value.status_code == 401

    def test_verify_access_token_default_token_version(self):
        """Test token verification handles missing token_version (defaults to 0)."""

        # Create token without token_version
        user_data = {"user_id": 1}
        payload = {**user_data, "exp": datetime.now(timezone.utc) + timedelta(minutes=30)}
        token = jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)

        credentials_exception = HTTPException(status_code=401, detail="Invalid")
        token_data = oauth2.verify_access_token(token, credentials_exception)

        assert token_data.token_version == 0

    def test_verify_access_token_malformed(self):
        """Test verification fails with malformed token."""

        malformed_tokens = [
            "not.a.token",
            "only_one_part",
            "two.parts",
            "",
            "header.payload.signature.extra",
        ]

        credentials_exception = HTTPException(status_code=401, detail="Malformed token")

        for malformed_token in malformed_tokens:
            with pytest.raises(HTTPException):
                oauth2.verify_access_token(malformed_token, credentials_exception)


class TestGetCurrentUser:
    """Test suite for get_current_user function."""

    def test_get_current_user_success(self, test_regular_user, session):
        """Test successful retrieval of current user."""

        # Create valid token for test user
        token = oauth2.create_access_token({"user_id": test_regular_user.id}, token_version=test_regular_user.token_version)

        # Retrieve current user from the token
        user = oauth2.get_current_user(token=token, db=session)

        # Verify returned user matches test user
        assert user is not None
        assert user.id == test_regular_user.id
        assert user.email == test_regular_user.email

    def test_get_current_user_invalid_token(self, session):
        """Test get_current_user raises exception with invalid token."""

        invalid_token = "invalid.token.here"

        with pytest.raises(HTTPException) as exc_info:
            oauth2.get_current_user(token=invalid_token, db=session)

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "could not validate credentials" in exc_info.value.detail.lower()

    def test_get_current_user_nonexistent_user(self, session):
        """Test get_current_user raises exception when user doesn't exist."""

        # Create token for non-existent user
        token = oauth2.create_access_token({"user_id": 99999}, token_version=0)

        with pytest.raises(HTTPException) as exc_info:
            oauth2.get_current_user(token=token, db=session)

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "could not validate credentials" in exc_info.value.detail.lower()

    def test_get_current_user_token_version_mismatch(self, test_regular_user, session):
        """Test get_current_user rejects token with outdated version."""

        token_version = 1
        assert test_regular_user.token_version != token_version

        # Create token with new token version
        token = oauth2.create_access_token({"user_id": test_regular_user.id}, token_version=token_version)

        # Try to use old token
        with pytest.raises(HTTPException) as exc_info:
            oauth2.get_current_user(token=token, db=session)

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "revoked" in exc_info.value.detail.lower()
        assert "log in again" in exc_info.value.detail.lower()

    def test_get_current_user_token_version_matches(self, test_regular_user, session):
        """Test get_current_user succeeds when token version matches."""

        test_regular_user.token_version = 5
        session.commit()

        # Create token with matching version
        token = oauth2.create_access_token({"user_id": test_regular_user.id}, token_version=test_regular_user.token_version)

        user = oauth2.get_current_user(token=token, db=session)

        assert user is not None
        assert user.id == test_regular_user.id
        assert user.token_version == test_regular_user.token_version

    def test_get_current_user_expired_token(self, test_regular_user, session):
        """Test get_current_user rejects expired token."""

        # Create expired token
        expired_time = datetime.now(timezone.utc) - timedelta(hours=1)
        payload = {"user_id": test_regular_user.id, "exp": expired_time, "token_version": test_regular_user.token_version}
        expired_token = jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)

        with pytest.raises(HTTPException) as exc_info:
            oauth2.get_current_user(token=expired_token, db=session)

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_current_user_www_authenticate_header(self, session):
        """Test get_current_user includes WWW-Authenticate header in error."""

        invalid_token = "invalid.token"

        with pytest.raises(HTTPException) as exc_info:
            oauth2.get_current_user(token=invalid_token, db=session)

        assert "WWW-Authenticate" in exc_info.value.headers
        assert exc_info.value.headers["WWW-Authenticate"] == "Bearer"

    def test_get_current_user_multiple_users_correct_one_returned(self, test_users, session):
        """Test get_current_user returns correct user when multiple exist."""

        # Create tokens for different users
        user1_token = oauth2.create_access_token({"user_id": test_users[0].id}, token_version=test_users[0].token_version)
        user2_token = oauth2.create_access_token({"user_id": test_users[1].id}, token_version=test_users[1].token_version)

        # Verify correct users are returned
        user1 = oauth2.get_current_user(token=user1_token, db=session)
        user2 = oauth2.get_current_user(token=user2_token, db=session)

        assert user1.id == test_users[0].id
        assert user2.id == test_users[1].id
        assert user1.email == test_users[0].email
        assert user2.email == test_users[1].email

    def test_get_current_user_admin_user(self, test_admin_user, session):
        """Test get_current_user works with admin users."""

        token = oauth2.create_access_token({"user_id": test_admin_user.id}, token_version=test_admin_user.token_version)

        user = oauth2.get_current_user(token=token, db=session)

        assert user is not None
        assert user.id == test_admin_user.id
        assert user.is_admin is True


class TestTokenVersioning:
    """Test suite for token versioning security feature."""

    def test_token_version_incremented_invalidates_old_tokens(self, test_regular_user, session):
        """Test that incrementing token version invalidates old tokens."""

        # Create token with current version
        initial_version = test_regular_user.token_version
        token = oauth2.create_access_token({"user_id": test_regular_user.id}, token_version=initial_version)

        # Verify old token works
        user = oauth2.get_current_user(token=token, db=session)
        assert user is not None

        # Simulate password change - increment token version
        test_regular_user.token_version += 1
        session.commit()

        # Old token should now be invalid
        with pytest.raises(HTTPException) as exc_info:
            oauth2.get_current_user(token=token, db=session)

        assert exc_info.value.status_code == 401
        assert "revoked" in exc_info.value.detail.lower()

    def test_new_token_works_after_version_increment(self, test_regular_user, session):
        """Test that new token with updated version works after increment."""

        # Increment token version
        test_regular_user.token_version = 10
        session.commit()

        # Create new token with new version
        new_token = oauth2.create_access_token({"user_id": test_regular_user.id}, token_version=test_regular_user.token_version)

        # New token should work
        user = oauth2.get_current_user(token=new_token, db=session)
        assert user is not None
        assert user.token_version == test_regular_user.token_version

    def test_multiple_version_increments(self, test_regular_user, session):
        """Test multiple token version increments invalidate all old tokens."""

        # Create tokens at different versions
        tokens = []
        for version in range(5):
            test_regular_user.token_version = version
            session.commit()
            token = oauth2.create_access_token({"user_id": test_regular_user.id}, token_version=version)
            tokens.append(token)

        # Set final version
        test_regular_user.token_version = 5
        session.commit()
        session.refresh(test_regular_user)

        # All old tokens should be invalid
        for old_token in tokens:
            with pytest.raises(HTTPException) as exc_info:
                oauth2.get_current_user(token=old_token, db=session)
            assert exc_info.value.status_code == 401


class TestIntegrationScenarios:
    """Integration tests for complete authentication workflows."""

    def test_complete_auth_flow(self, test_regular_user, session):
        """Test complete authentication flow from token creation to user retrieval."""

        # 1. Create access token
        token = oauth2.create_access_token({"user_id": test_regular_user.id}, token_version=test_regular_user.token_version)

        # 2. Verify token is valid
        credentials_exception = HTTPException(status_code=401, detail="Invalid")
        token_data = oauth2.verify_access_token(token, credentials_exception)
        assert token_data.id == str(test_regular_user.id)

        # 3. Get current user
        user = oauth2.get_current_user(token=token, db=session)
        assert user.id == test_regular_user.id
        assert user.email == test_regular_user.email

    def test_password_change_flow(self, test_regular_user, session):
        """Test token invalidation after password change."""

        # 1. User logs in (token created)
        old_token = oauth2.create_access_token({"user_id": test_regular_user.id}, token_version=test_regular_user.token_version)

        # 2. Verify token works
        user = oauth2.get_current_user(token=old_token, db=session)
        assert user is not None

        # 3. User changes password (version incremented)
        test_regular_user.token_version += 1
        session.commit()
        session.refresh(test_regular_user)

        # 4. Old token no longer works
        with pytest.raises(HTTPException) as exc_info:
            oauth2.get_current_user(token=old_token, db=session)
        assert "revoked" in exc_info.value.detail.lower()

        # 5. User logs in again with new token
        new_token = oauth2.create_access_token({"user_id": test_regular_user.id}, token_version=test_regular_user.token_version)

        # 6. New token works
        user = oauth2.get_current_user(token=new_token, db=session)
        assert user is not None
