"""Tests for the login/register page of the application."""

import datetime as dt

import pytest
from sqlalchemy.orm import Session

from app import models
from app.core.models import TokenType
from fixtures.users import FixtureUser

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
    def test_remaining_seconds(
        self,
        session: Session,
        minutes_ago: int,
        expected_remaining: int,
        test_regular_user: FixtureUser,
    ) -> None:
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
            (TokenType.EMAIL_VERIFICATION, 35, True),  # verification: 10 min ago = valid
            (TokenType.EMAIL_VERIFICATION, 70, False),  # verification: 25 min ago = expired
            (TokenType.PASSWORD_RESET, 10, True),  # password_reset: 10 min ago = valid
            (TokenType.PASSWORD_RESET, 35, False),  # password_reset: 25 min ago = expired
            (TokenType.EMAIL_CHANGE, 10, True),  # email_change: 10 min ago = valid
            (TokenType.EMAIL_CHANGE, 65, False),  # email_change: 25 min ago = expired
        ],
    )
    def test_is_valid_different_token_types(
        self,
        session: Session,
        token_type: TokenType,
        minutes_ago: int,
        expected_valid: bool,
        test_regular_user: FixtureUser,
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
    def _add_token(
        session: Session,
        user_id: int,
        token_type: TokenType,
        token: str,
    ) -> None:
        """Helper function to add a token to the database."""

        token = models.UserToken(owner_id=user_id, token=token, token_type=token_type)
        session.add(token)
        session.commit()

    def test_new_token_deletes_existing_same_type(
        self,
        session: Session,
        test_regular_user: FixtureUser,
    ) -> None:
        """Test that creating a new token deletes existing token of the same type."""

        self._add_token(session, test_regular_user.id, TokenType.EMAIL_VERIFICATION, "first_token")
        assert session.query(models.UserToken).filter_by(token="first_token").first() is not None

        self._add_token(session, test_regular_user.id, TokenType.EMAIL_VERIFICATION, "second_token")
        assert session.query(models.UserToken).filter_by(token="first_token").first() is None
        assert session.query(models.UserToken).filter_by(token="second_token").first() is not None

        # Verify only one token exists for this user and type
        count = (
            session.query(models.UserToken)
            .filter_by(owner_id=test_regular_user.id, token_type=TokenType.EMAIL_VERIFICATION)
            .count()
        )
        assert count == 1

    def test_new_token_does_not_delete_different_type(
        self,
        session: Session,
        test_regular_user: FixtureUser,
    ) -> None:
        """Test that creating a new token does not delete tokens of a different type."""

        self._add_token(session, test_regular_user.id, TokenType.EMAIL_VERIFICATION, "verification_token")
        self._add_token(session, test_regular_user.id, TokenType.PASSWORD_RESET, "password_reset_token")

        # Verify both tokens still exist
        assert session.query(models.UserToken).filter_by(token="verification_token").first() is not None
        assert session.query(models.UserToken).filter_by(token="password_reset_token").first() is not None

    def test_new_token_does_not_delete_other_users_tokens(
        self,
        session: Session,
        test_regular_user: FixtureUser,
        test_admin_user: FixtureUser,
    ) -> None:
        """Test that creating a new token does not delete tokens of the same type for other users."""

        self._add_token(session, test_regular_user.id, TokenType.EMAIL_VERIFICATION, "user1_token")
        self._add_token(session, test_admin_user.id, TokenType.EMAIL_VERIFICATION, "user2_token")

        # Verify both tokens still exist
        assert session.query(models.UserToken).filter_by(token="user1_token").first() is not None
        assert session.query(models.UserToken).filter_by(token="user2_token").first() is not None
