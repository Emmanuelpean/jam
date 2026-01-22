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
        # noinspection PyArgumentList
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
        # noinspection PyArgumentList
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
