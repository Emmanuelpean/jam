"""Tests for utility functions in the core module."""

from unittest.mock import Mock

from app import models
from app.core.utils import generate_token, send_verification_with_rate_limit


class TestGenerateToken:

    def test_generate_token(self, test_regular_user, session) -> None:
        """Test generation of verification token."""

        token, token_entry = generate_token(test_regular_user.id, "verification", session)
        assert len(token) == 43
        assert len(token_entry.token) == 64


class TestSendVerificationWithRateLimit:

    def test_send_verification_email(self, test_regular_user, session) -> None:
        """Test sending of verification email."""

        result = send_verification_with_rate_limit(
            "verification",
            test_regular_user,
            session,
            lambda x, y: None,
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

    def test_send_verification_email_rate_limited(self, test_unverified_token_user, session) -> None:
        """Test rate limiting when sending verification email."""

        mock_send_function = Mock()

        result = send_verification_with_rate_limit(
            "verification",
            test_unverified_token_user,
            session,
            mock_send_function,
            "verify-email",
            name="Verification",
        )

        assert result.model_dump() == {
            "error_code": 429,
            "message": "Please wait 120 seconds before requesting another verification email.",
            "success": False,
        }
        assert mock_send_function.call_count == 0
