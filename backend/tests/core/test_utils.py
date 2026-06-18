"""Tests for utility functions in the core module."""

import datetime as dt
from unittest.mock import Mock, patch

import pytest

from app import models
from app.core.models import TokenType
from app.core.utils import (
    check_token_rate_limit,
    generate_token,
    send_rate_limited_tokenized_email,
    send_rate_limited_tokenized_email_verification_email,
    send_rate_limited_tokenized_password_reset_email,
    send_rate_limited_tokenized_email_change_email,
    send_tokenized_password_changed_email_with_rate_limit,
)


class TestGenerateToken:

    def test_generate_token(self, test_regular_user, session) -> None:
        """Test generation of verification token."""

        token, token_entry = generate_token(test_regular_user.id, TokenType.EMAIL_VERIFICATION, session)
        assert len(token) == 43
        assert len(token_entry.token) == 64


class TestCheckTokenRateLimit:

    @staticmethod
    def _add_token(session, user_id: int, token_type: TokenType, minutes_ago: int) -> models.UserToken:
        """Helper to add a token with a creation time offset in the past."""

        token = models.UserToken(
            owner_id=user_id,
            token=f"{token_type}_token_hash",
            token_type=token_type,
        )
        session.add(token)
        session.commit()

        # Manually set created_at to simulate different times
        token.created_at = dt.datetime.now(dt.timezone.utc) - dt.timedelta(minutes=minutes_ago)
        session.commit()
        session.refresh(token)
        return token

    def test_no_existing_token(self, test_regular_user, session) -> None:
        """Test that 0 is returned when the user has no token of the given type."""

        assert check_token_rate_limit(TokenType.EMAIL_VERIFICATION, test_regular_user, session) == 0

    @pytest.mark.parametrize(
        "minutes_ago, expected_remaining",
        [
            (0, 120),  # right now = 120 seconds remaining
            (1, 60),  # 1 minute ago = 60 seconds remaining
            (2, 0),  # 2 minutes ago = 0 seconds remaining
            (3, -60),  # 3 minutes ago = expired
        ],
    )
    def test_existing_token(self, test_regular_user, session, minutes_ago, expected_remaining) -> None:
        """Test that the remaining seconds of the latest matching token are returned."""

        self._add_token(session, test_regular_user.id, TokenType.EMAIL_VERIFICATION, minutes_ago)

        assert check_token_rate_limit(TokenType.EMAIL_VERIFICATION, test_regular_user, session) == expected_remaining

    def test_ignores_other_token_types(self, test_regular_user, session) -> None:
        """Test that tokens of a different type do not count towards the rate limit."""

        self._add_token(session, test_regular_user.id, TokenType.PASSWORD_RESET, 0)

        assert check_token_rate_limit(TokenType.EMAIL_VERIFICATION, test_regular_user, session) == 0

    def test_ignores_other_users_tokens(self, test_regular_user, test_users, session) -> None:
        """Test that tokens belonging to other users do not count towards the rate limit."""

        other_user = test_users[1]
        self._add_token(session, other_user.id, TokenType.EMAIL_VERIFICATION, 0)

        assert check_token_rate_limit(TokenType.EMAIL_VERIFICATION, test_regular_user, session) == 0


class TestSendVerificationWithRateLimit:

    def test_send_rate_limited_tokenized_email(self, test_regular_user, session) -> None:
        """Test sending of verification email."""

        result = send_rate_limited_tokenized_email(
            TokenType.EMAIL_VERIFICATION,
            test_regular_user,
            session,
            lambda x, y, z: None,
            "verify-email",
            name="Verification",
        )
        assert result.model_dump() == {
            "success": True,
            "message": "Verification email sent successfully.",
            "error_code": None,
        }

        # Check that a verification token was created
        verification_token = session.query(models.UserToken).filter(models.UserToken.id == test_regular_user.id).first()
        assert verification_token is not None
        assert verification_token.token is not None
        assert verification_token.created_at is not None
        assert verification_token.is_valid is True

    def test_send_rate_limited_tokenized_email_rate_limited(self, test_regular_user, session) -> None:
        """Test rate limiting when sending verification email."""

        mock_send_function = Mock()
        generate_token(test_regular_user.id, TokenType.EMAIL_VERIFICATION, session)

        result = send_rate_limited_tokenized_email(
            TokenType.EMAIL_VERIFICATION,
            test_regular_user,
            session,
            mock_send_function,
            "verify-email",
            name="Verification",
        )

        assert result.model_dump() == {
            "error_code": 429,
            "message": "Please wait 120 seconds before requesting another Verification email.",
            "success": False,
        }
        assert mock_send_function.call_count == 0


class TestSendEmailVerificationEmailWithRateLimit:

    @patch("app.core.routers.auth.email_service.send_email_verification_email")
    def test_send_rate_limited_tokenized_email_verification_email(self, mock_email, test_regular_user, session) -> None:
        """Test sending of verification email."""

        result = send_rate_limited_tokenized_email_verification_email(test_regular_user, session)
        assert result.model_dump() == {
            "success": True,
            "message": "Verification email sent successfully.",
            "error_code": None,
        }
        assert mock_email.call_count == 1

        # Check that a verification token was created
        verification_token = (
            session.query(models.UserToken)
            .filter(
                models.UserToken.owner_id == test_regular_user.id,
                models.UserToken.token_type == "email_verification",
            )
            .order_by(models.UserToken.created_at.desc())
            .first()
        )
        assert verification_token is not None
        assert verification_token.token is not None
        assert verification_token.created_at is not None
        assert verification_token.is_valid is True

    @patch("app.core.routers.auth.email_service.send_email_verification_email")
    def test_send_rate_limited_tokenized_email_verification_email_rate_limited(
        self, mock_email, test_regular_user, session
    ) -> None:
        """Test rate limiting when sending verification email."""

        send_rate_limited_tokenized_email_verification_email(test_regular_user, session)
        result = send_rate_limited_tokenized_email_verification_email(test_regular_user, session)
        assert result.model_dump() == {
            "error_code": 429,
            "message": "Please wait 120 seconds before requesting another Verification email.",
            "success": False,
        }
        assert mock_email.call_count == 1


class TestSendPasswordResetWithRateLimit:

    @patch("app.core.routers.auth.email_service.send_password_reset_email")
    def test_send_rate_limited_tokenized_password_reset_email(self, mock_email, test_regular_user, session) -> None:
        """Test sending of password reset email."""

        result = send_rate_limited_tokenized_password_reset_email(test_regular_user, session)
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
    def test_send_rate_limited_tokenized_password_reset_email_rate_limited(
        self, mock_email, test_regular_user, session
    ) -> None:
        """Test rate limiting when sending password reset email."""

        send_rate_limited_tokenized_password_reset_email(test_regular_user, session)
        result = send_rate_limited_tokenized_password_reset_email(test_regular_user, session)
        assert result.model_dump() == {
            "error_code": 429,
            "message": "Please wait 120 seconds before requesting another Password reset email.",
            "success": False,
        }
        assert mock_email.call_count == 1


class TestSendEmailChangeWithRateLimit:

    @patch("app.core.routers.auth.email_service.send_email_change_verification")
    def test_send_rate_limited_tokenized_email_change_email(self, mock_email, test_users, session) -> None:
        """Test sending of email change verification email."""

        result = send_rate_limited_tokenized_email_change_email(test_users[0], "newemail@test.com", session)
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
    def test_send_rate_limited_tokenized_email_change_email_rate_limited(self, mock_email, test_users, session) -> None:
        """Test rate limiting when sending email change verification email."""

        send_rate_limited_tokenized_email_change_email(test_users[0], "newemail@test.com", session)
        result = send_rate_limited_tokenized_email_change_email(test_users[0], "newemail2@test.com", session)
        assert result.success is False
        assert result.error_code == 429
        assert mock_email.call_count == 1


class TestSendPasswordChangedWithRateLimit:

    @patch("app.core.routers.auth.email_service.send_password_changed_notification")
    def test_send_tokenized_password_changed_email_with_rate_limit(
        self, mock_email, test_regular_user, session
    ) -> None:
        """Test sending of password changed notification email."""

        result = send_tokenized_password_changed_email_with_rate_limit(test_regular_user, session)
        assert result.model_dump() == {
            "success": True,
            "message": "Password changed email sent successfully.",
            "error_code": None,
        }
        assert mock_email.call_count == 1

        # Check that a password change token was created
        password_change_token = (
            session.query(models.UserToken)
            .filter(
                models.UserToken.owner_id == test_regular_user.id,
                models.UserToken.token_type == "password_change",
            )
            .order_by(models.UserToken.created_at.desc())
            .first()
        )
        assert password_change_token is not None
        assert password_change_token.token is not None
        assert password_change_token.created_at is not None

    @patch("app.core.routers.auth.email_service.send_password_changed_notification")
    def test_send_tokenized_password_changed_email_with_rate_limit_rate_limited(
        self, mock_email, test_regular_user, session
    ) -> None:
        """Test rate limiting when sending password changed notification email."""

        send_tokenized_password_changed_email_with_rate_limit(test_regular_user, session)
        result = send_tokenized_password_changed_email_with_rate_limit(test_regular_user, session)
        assert result.model_dump() == {
            "error_code": 429,
            "message": "Please wait 120 seconds before requesting another Password changed email.",
            "success": False,
        }
        assert mock_email.call_count == 1
