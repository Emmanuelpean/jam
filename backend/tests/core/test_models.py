"""Tests for the login/register page of the application."""

import datetime as dt

import pytest

from app import models


# -------------------------------------------------- UTILITY FUNCTIONS -------------------------------------------------


class TestUserTokenRemainingSeconds:

    @pytest.mark.parametrize(
        "minutes_ago, expected_remaining",
        [
            (1, 60),  # 1 minute ago = 60 seconds remaining
            (2, 0),  # 2 minutes ago = 0 seconds remaining (should be capped at 0)
            (3, -60),  # 3 minutes ago = 0 seconds (expired, capped at 0)
            (0, 120),  # right now = 120 seconds remaining
        ],
    )
    def test_remaining_seconds(self, session, minutes_ago, expected_remaining, test_regular_user) -> None:
        """Test calculation of remaining seconds for rate limiting on UserToken model"""

        created_time = dt.datetime.now(dt.timezone.utc) - dt.timedelta(minutes=minutes_ago)

        # Create a token with the specified creation time
        token = models.UserToken(
            owner_id=test_regular_user.id,
            token="test_token_hash",
            token_type="verification",
        )
        session.add(token)
        session.commit()

        # Manually set created_at to simulate different times
        token.created_at = created_time
        session.commit()
        session.refresh(token)

        # Allow for slight timing differences (within 2 seconds)
        assert token.remaining_seconds == expected_remaining


class TestUserTokenIsValid:

    @pytest.mark.parametrize(
        "token_type, minutes_ago, expected_valid",
        [
            ("verification", 35, True),  # verification: 10 min ago = valid
            ("verification", 70, False),  # verification: 25 min ago = expired
            ("password_reset", 10, True),  # password_reset: 10 min ago = valid
            ("password_reset", 35, False),  # password_reset: 25 min ago = expired
            ("email_change", 10, True),  # email_change: 10 min ago = valid
            ("email_change", 65, False),  # email_change: 25 min ago = expired
        ],
    )
    def test_is_valid_different_token_types(
        self, session, token_type, minutes_ago, expected_valid, test_regular_user
    ) -> None:
        """Test token validity for different token types."""

        created_time = dt.datetime.now(dt.timezone.utc) - dt.timedelta(minutes=minutes_ago)

        # Create a token with the specified type and creation time
        token = models.UserToken(
            owner_id=test_regular_user.id,
            token="test_token_hash",
            token_type=token_type,
        )
        session.add(token)
        session.commit()

        # Manually set created_at to simulate different times
        token.created_at = created_time
        session.commit()
        session.refresh(token)

        # Test is_valid property
        assert token.is_valid == expected_valid


class TestUserTokenDeletesExistingOfSameType:
    """Test that creating a new token deletes existing tokens of the same type for the same user."""

    @staticmethod
    def _add_token(session, user_id, token_type, token):
        """Helper function to add a token to the database."""

        token = models.UserToken(owner_id=user_id, token=token, token_type=token_type)
        session.add(token)
        session.commit()

    def test_new_token_deletes_existing_same_type(self, session, test_regular_user) -> None:
        """Test that creating a new token deletes existing token of the same type."""

        self._add_token(session, test_regular_user.id, "verification", "first_token")
        assert session.query(models.UserToken).filter_by(token="first_token").first() is not None

        self._add_token(session, test_regular_user.id, "verification", "second_token")
        assert session.query(models.UserToken).filter_by(token="first_token").first() is None
        assert session.query(models.UserToken).filter_by(token="second_token").first() is not None

        # Verify only one token exists for this user and type
        count = (
            session.query(models.UserToken).filter_by(owner_id=test_regular_user.id, token_type="verification").count()
        )
        assert count == 1

    def test_new_token_does_not_delete_different_type(self, session, test_regular_user) -> None:
        """Test that creating a new token does not delete tokens of a different type."""

        self._add_token(session, test_regular_user.id, "verification", "verification_token")
        self._add_token(session, test_regular_user.id, "password_reset", "password_reset_token")

        # Verify both tokens still exist
        assert session.query(models.UserToken).filter_by(token="verification_token").first() is not None
        assert session.query(models.UserToken).filter_by(token="password_reset_token").first() is not None

    def test_new_token_does_not_delete_other_users_tokens(self, session, test_regular_user, test_users) -> None:
        """Test that creating a new token does not delete tokens of the same type for other users."""

        other_user = test_users[1]

        self._add_token(session, test_regular_user.id, "verification", "user1_token")
        self._add_token(session, other_user.id, "verification", "user2_token")

        # Verify both tokens still exist
        assert session.query(models.UserToken).filter_by(token="user1_token").first() is not None
        assert session.query(models.UserToken).filter_by(token="user2_token").first() is not None
