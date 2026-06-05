"""Tests for the email verification flow."""

import datetime as dt

from base_test import models, BaseTest


class TestEmailVerification(BaseTest):

    def _register_and_verify_redirect(self, email: str, password: str) -> None:
        """Helper to clear emails, register user, wait for login page, and assert account creation message."""

        self.auth_utils.clear_test_emails()
        self.auth_utils.register_user(email, password)
        self.auth_utils.wait_for_login()
        self.assert_toast_message("Account created! Please check your email to verify your account before logging in.")

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

    def test_login_with_non_verified_user_verifies_account(self, test_unverified_token_user, session) -> None:
        """Test that logging in with a non-verified user redirects to verification and successfully verifies the account."""

        self.auth_utils.go_to_verification_url(test_unverified_token_user.plain_verification_token)
        self.auth_utils.assert_toast_message("Account verified successfully")

    def test_login_before_verification_shows_wait_then_allows_login(self, session) -> None:
        """Test attempting login before email verification shows 'Please wait' message,
        then after verification login succeeds."""

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

    def test_login_after_rate_limit_sends_new_verification_email(self, session) -> None:
        """Test that logging in with an unverified account after the rate limit window sends a new verification email."""

        test_email = "newuser@test.com"
        test_password = "Test123!"

        self._register_and_verify_redirect(test_email, test_password)
        user = session.query(models.User).filter(models.User.email == test_email).first()
        assert user
        token = session.query(models.UserToken).filter(models.UserToken.owner_id == user.id).first()
        token.created_at = dt.datetime.now(dt.timezone.utc) - dt.timedelta(minutes=3)
        session.commit()

        self.auth_utils.login_user(test_email, test_password)
        self.auth_utils.assert_toast_message(f"A new verification email has been sent to {test_email}.")

    def test_registering_same_email_before_verification_shows_wait_then_allows_login(self, session) -> None:
        """Test that trying to register the same email before verification shows 'Please wait' message,
        then after verification login succeeds."""

        test_email = "newuser@test.com"
        test_password = "Test123!"

        self._register_and_verify_redirect(test_email, test_password)
        self.auth_utils.register_user(test_email, test_password)
        self.auth_utils.assert_toast_message("Please wait")
        self._verify_account_via_email_link(test_email)
        self.auth_utils.login_user(test_email, test_password)
        self.auth_utils.wait_for_dashboard()

    def test_verification_with_invalid_token_shows_error(self, session) -> None:
        """Test visiting email verification URL with an invalid or expired token shows an error message."""

        test_email = "newuser@test.com"
        test_password = "Test123!"
        self._register_and_verify_redirect(test_email, test_password)
        invalid_verification_url = self.auth_utils.get_verification_link_from_email(test_email)[:-4]
        self.driver.get(invalid_verification_url)
        self.auth_utils.assert_toast_message("Invalid or expired token. Please request a new one by logging in.")

    def test_expired_verification_token(self, session) -> None:
        """Test email verification with an expired token."""

        test_email = "newuser@test.com"
        test_password = "Test123!"
        self._register_and_verify_redirect(test_email, test_password)
        user = session.query(models.User).filter(models.User.email == test_email).first()
        assert user
        token = session.query(models.UserToken).filter(models.UserToken.owner_id == user.id).first()
        token.created_at = dt.datetime.now(dt.timezone.utc) - dt.timedelta(minutes=67)
        session.commit()
        invalid_verification_url = self.auth_utils.get_verification_link_from_email(test_email)
        self.driver.get(invalid_verification_url)
        self.auth_utils.assert_toast_message("Verification token has expired. Please request a new one by logging in.")
