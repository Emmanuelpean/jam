"""Tests for the password reset flow."""

import datetime as dt

from sqlalchemy.orm import Session

from tests.fixtures.users import FixtureUser
from frontend_base_test import models, BaseTest


class TestPasswordReset(BaseTest):

    def test_password_reset_within_rate_limit_shows_wait(self, test_regular_user: FixtureUser) -> None:
        """Test that requesting a second password reset within the rate limit window shows a 'Please wait' message."""

        self.auth_utils.clear_test_emails()
        self.auth_utils.go_to_forgot_password()
        self.auth_utils.set_email(test_regular_user.email)
        self.auth_utils.confirm()
        self.auth_utils.assert_toast_message("Password reset email sent successfully")

        self.auth_utils.go_to_forgot_password()
        self.auth_utils.set_email(test_regular_user.email)
        self.auth_utils.confirm()
        self.auth_utils.assert_toast_message("Please wait")

    def test_password_reset_after_rate_limit_sends_new_email(
        self, test_regular_user: FixtureUser, session: Session
    ) -> None:
        """Test that requesting a password reset after the rate limit window sends a new email and shows a success message."""

        self.auth_utils.clear_test_emails()
        self.auth_utils.go_to_forgot_password()
        self.auth_utils.set_email(test_regular_user.email)
        self.auth_utils.confirm()
        self.auth_utils.assert_toast_message("Password reset email sent successfully")

        token = test_regular_user.get_token(models.TokenType.PASSWORD_RESET)
        assert token
        token.created_at = dt.datetime.now(dt.timezone.utc) - dt.timedelta(minutes=3)
        session.commit()

        self.auth_utils.go_to_forgot_password()
        self.auth_utils.set_email(test_regular_user.email)
        self.auth_utils.confirm()
        self.auth_utils.assert_toast_message("Password reset email sent successfully")

    def test_password_reset_flow(self, test_regular_user: FixtureUser) -> None:
        """Test complete password reset flow using test email endpoints"""

        test_email = test_regular_user.email
        new_password = "NewPassword123!"

        # Clear any existing test emails
        self.auth_utils.clear_test_emails()

        # Request password reset
        self.auth_utils.go_to_login()
        self.auth_utils.switch_to_forgot_password()
        self.auth_utils.set_email(test_email)
        self.auth_utils.confirm()

        # Verify success message
        self.auth_utils.assert_toast_message("Password reset email sent successfully")

        # Get reset link from test endpoint
        reset_url = self.auth_utils.get_reset_link_from_email(test_email)

        # Visit reset URL
        self.driver.get(reset_url)

        # Set new password
        self.auth_utils.set_password(new_password)
        self.auth_utils.set_confirm_password(new_password)
        self.auth_utils.confirm()

        # Verify success message
        self.auth_utils.assert_toast_message("Password has been reset successfully")

        # Login with new password
        self.auth_utils.wait_for_login()
        self.auth_utils.set_email(test_email)
        self.auth_utils.set_password(new_password)
        self.auth_utils.confirm()
        self.auth_utils.wait_for_dashboard()

    def test_password_reset_invalid_token(self) -> None:
        """Test password reset with invalid token"""

        invalid_reset_url = f"{self.frontend_base_url}/reset-password?token=invalid_token"
        self.driver.get(invalid_reset_url)
        self.auth_utils.set_password("password")
        self.auth_utils.set_confirm_password("password")
        self.auth_utils.confirm()
        self.auth_utils.assert_toast_message("Invalid or expired password reset token")

    def test_forgot_password_field_limits(self) -> None:
        """Entering email over the limit disables Send Reset Link; reducing re-enables it."""

        self.auth_utils.go_to_forgot_password()

        # Email over limit (254 char limit)
        self.auth_utils.set_email("a" * 246 + "@test.com")
        self.auth_utils.assert_confirm_button_disabled()

        # Back within limit
        self.auth_utils.set_email("test@test.com")
        self.auth_utils.assert_confirm_button_enabled()

    def test_reset_password_lower_limit(self) -> None:
        """Entering a password below the minimum length (8 chars) shows an error and disables Reset Password."""

        self.driver.get(f"{self.frontend_base_url}/reset-password?token=dummytoken123")
        self.get_element("password")  # wait for form to render

        # Password below minimum (5 chars)
        self.auth_utils.set_password("Passw")
        self.auth_utils.set_confirm_password("Passw")
        self.auth_utils.confirm()

        # Verify error message and disabled button
        self.auth_utils.assert_password_error_message("Password must be at least 8 characters long.")
        self.auth_utils.assert_confirm_button_disabled()

        # Adding 1 more character clears the error and re-enables the button
        self.auth_utils.get_element("password").send_keys("a")
        self.auth_utils.assert_no_password_error_message()
        self.auth_utils.assert_confirm_button_enabled()

    def test_reset_password_field_limits(self) -> None:
        """Entering password or confirm password over the limit disables Reset Password; reducing re-enables it."""

        self.driver.get(f"{self.frontend_base_url}/reset-password?token=dummytoken123")
        self.get_element("password")  # wait for form to render

        # Password over limit (128 char limit)
        self.auth_utils.set_password("P" * 129)
        self.auth_utils.assert_confirm_button_disabled()

        # Back within limit
        self.auth_utils.set_password("Password123!")
        self.auth_utils.assert_confirm_button_enabled()

        # Confirm password over limit
        self.auth_utils.set_confirm_password("P" * 129)
        self.auth_utils.assert_confirm_button_disabled()

        # Back within limit
        self.auth_utils.set_confirm_password("Password123!")
        self.auth_utils.assert_confirm_button_enabled()
