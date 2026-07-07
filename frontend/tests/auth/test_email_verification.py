"""Tests for the email verification flow."""

import datetime as dt

from app.core.models import TokenType
from tests.fixtures.users import FixtureUser
from frontend_base_test import BaseTest


class TestEmailVerification(BaseTest):

    def _register_and_verify_redirect(self, email: str, password: str) -> None:
        """Helper to clear emails, register user, wait for login page, and assert account creation message."""

        self.auth_utils.clear_test_emails()
        self.auth_utils.register_user(email, password)
        self.auth_utils.wait_for_login()
        toast_message = "Account created! Please check your email inbox to verify your account before logging in."
        self.assert_toast_message(toast_message)

    def _verify_account_via_email_link(self, email: str) -> None:
        """Helper to retrieve the verification link from email and visit it, asserting success."""

        verification_url = self.auth_utils.get_verification_link_from_email(email)
        self.driver.get(verification_url)
        self.auth_utils.assert_toast_message("Account verified successfully")
        self.auth_utils.wait_for_login()

    def test_full_email_verification_flow(self) -> None:
        """Test the full email verification flow starting from registration to successful login after email verification."""

        test_email = "newuser@test.com"
        test_password = "Test123!"

        self._register_and_verify_redirect(test_email, test_password)
        self._verify_account_via_email_link(test_email)
        self.auth_utils.login_user(test_email, test_password)
        self.auth_utils.wait_for_dashboard()

    def test_valid_token_verifies_account(self, test_unverified_user: FixtureUser) -> None:
        """Test that visiting the verification URL with a valid token verifies the account and shows a success message."""

        plain_token = test_unverified_user.create_token(TokenType.EMAIL_VERIFICATION)[0]
        self.auth_utils.go_to_verification_url(plain_token)
        self.auth_utils.assert_toast_message("Account verified successfully")

    def test_login_before_verification_shows_wait_then_allows_login(self) -> None:
        """Test that attempting to log in before verifying shows the 'not verified / please wait' message,
        then after verifying via the email link the login succeeds."""

        test_email = "newuser@test.com"
        test_password = "Test123!"

        self._register_and_verify_redirect(test_email, test_password)
        self.auth_utils.login_user(test_email, test_password)
        message = "Your account is not verified. Please check your emails for the verification link or please wait"
        self.auth_utils.assert_toast_message(message)
        self._verify_account_via_email_link(test_email)
        self.auth_utils.wait_for_login()
        self.auth_utils.login_user(test_email, test_password)
        self.auth_utils.wait_for_dashboard()

    def test_login_after_rate_limit_sends_new_verification_email(self, test_unverified_user: FixtureUser) -> None:
        """Test that logging in with an unverified account after the rate limit window sends a new verification email."""

        # Simulate the last verification email having been sent outside the rate-limit window
        last_sent = dt.datetime.now(dt.timezone.utc) - dt.timedelta(minutes=3)
        test_unverified_user.create_token(TokenType.EMAIL_VERIFICATION, created_at=last_sent)

        self.auth_utils.login_user(test_unverified_user.email, test_unverified_user.plain_password)
        self.auth_utils.assert_toast_message(f"A new verification email has been sent to {test_unverified_user.email}.")

    def test_registering_same_email_before_verification_shows_wait_then_allows_login(self) -> None:
        """Test that re-registering the same email before verification shows the 'Please wait' message,
        then after verifying via the email link the login succeeds."""

        test_email = "newuser@test.com"
        test_password = "Test123!"

        self._register_and_verify_redirect(test_email, test_password)
        self.auth_utils.register_user(test_email, test_password)
        self.auth_utils.assert_toast_message("Please wait")
        self._verify_account_via_email_link(test_email)
        self.auth_utils.login_user(test_email, test_password)
        self.auth_utils.wait_for_dashboard()

    def test_verification_with_invalid_token_shows_error(self, test_unverified_user: FixtureUser) -> None:
        """Test that visiting the email verification URL with an invalid (malformed) token shows an error message."""

        plain_token = test_unverified_user.create_token(TokenType.EMAIL_VERIFICATION)[0]
        self.auth_utils.go_to_verification_url(plain_token[:-4])
        self.auth_utils.assert_toast_message("Invalid or expired token. Please request a new one by logging in.")

    def test_expired_verification_token_shows_error(self, test_unverified_user: FixtureUser) -> None:
        """Test that visiting the email verification URL with an expired token shows an error message."""

        expired = dt.datetime.now(dt.timezone.utc) - dt.timedelta(minutes=67)
        plain_token = test_unverified_user.create_token(TokenType.EMAIL_VERIFICATION, created_at=expired)[0]
        self.auth_utils.go_to_verification_url(plain_token)
        self.auth_utils.assert_toast_message("Verification token has expired. Please request a new one by logging in.")
