"""
Authentication End-to-End Tests
This module contains comprehensive Selenium-based tests for the authentication system,
including login, registration, form validation, and mode switching functionality.
"""

import datetime as dt
import time

from selenium.webdriver.common.by import By

from conftest import models, BaseTest
from test_maintenance import MaintenanceTestBase


class TestLogIn(BaseTest):

    def setup_function(self, request) -> None:
        """Setup for each test method."""

        self.auth_utils.go_to_login()

    def test_valid_login(self, test_regular_user) -> None:
        """Test login with valid credentials"""

        test_email, test_password = test_regular_user.email, test_regular_user.plain_password

        # Fill in login form
        self.auth_utils.set_email(test_email)
        self.auth_utils.set_password(test_password)
        self.auth_utils.confirm()

        # Confirm load by checking the dashboard
        self.auth_utils.wait_for_dashboard()

    def test_invalid_login(self) -> None:
        """Test login with invalid credentials"""

        test_email, test_password = "wrong@email.com", "wrong_password"

        # Fill in login form with invalid credentials
        self.auth_utils.set_email(test_email)
        self.auth_utils.set_password(test_password)
        self.auth_utils.confirm()

        # Verify error message
        self.auth_utils.assert_toast_message("Invalid credentials")

    def test_inactive_login(self, test_inactive_user) -> None:
        """Test login with invalid credentials"""

        test_email, test_password = test_inactive_user.email, test_inactive_user.plain_password

        # Fill in login form with invalid credentials
        self.auth_utils.set_email(test_email)
        self.auth_utils.set_password(test_password)
        self.auth_utils.confirm()

        # Verify error message
        self.auth_utils.assert_toast_message("User account is not active.")

    def test_login_invalid_email(self) -> None:
        """Test login with invalid credentials"""

        test_email, test_password = "wrong", "wrong_password"

        # Fill in login form with invalid credentials
        self.auth_utils.set_email(test_email)
        self.auth_utils.set_password(test_password)
        self.auth_utils.confirm()

        # Verify error message
        self.auth_utils.assert_email_error_message("Please provide a valid email address")

    def test_login_no_email(self) -> None:
        """Test login with invalid credentials"""

        test_email, test_password = "", "wrong_password"

        # Fill in login form with invalid credentials
        self.auth_utils.set_email(test_email)
        self.auth_utils.set_password(test_password)
        self.auth_utils.confirm()

        # Verify error message
        self.auth_utils.assert_email_error_message("Please provide a valid email address")

    def test_login_no_password(self) -> None:
        """Test login with invalid credentials"""

        test_email, test_password = "wrong@email.com", ""

        # Fill in login form with invalid credentials
        self.auth_utils.set_email(test_email)
        self.auth_utils.set_password(test_password)
        self.auth_utils.confirm()

        # Verify error message
        self.auth_utils.assert_password_error_message("Password is required")

    def test_unexpected_error(self) -> None:
        """Test login with unexpected error"""

        self.auth_utils.set_email("crash@crash.com")
        self.auth_utils.set_password("Test123!")
        self.auth_utils.confirm()
        self.auth_utils.assert_toast_message("An unknown error occurred during login.\nRight-click to send email")

    def test_heartbeat_updates_last_login(self):
        """Test that heartbeat updates last login timestamp for authenticated users"""

        assert self.user.last_login is None
        assert self.user.previous_login is None

        # Login
        self.auth_utils.set_email(self.user.email)
        self.auth_utils.set_password(self.user.plain_password)
        self.auth_utils.confirm()
        self.auth_utils.wait_for_dashboard()

        self.db.expire_all()
        login_dt = self.user.last_login
        assert login_dt is not None
        assert self.user.previous_login is None

        # Travel to page and ensure no change in last_login and previous_login
        self.go_to_page("jobs")
        self.db.expire_all()
        assert self.user.last_login == login_dt
        assert self.user.previous_login is None

        # Refresh the page
        self.driver.get("https://google.com")
        self.driver.get(self.frontend_base_url + "/jobs")
        time.sleep(0.5)
        self.db.expire_all()
        assert self.user.last_login > login_dt
        assert self.user.previous_login == login_dt


class TestSignUp(BaseTest):

    def test_mode_switching_buttons(self) -> None:
        """Test switching between login and register modes using the toggle buttons"""

        self.auth_utils.go_to_login()
        self.auth_utils.wait_for_login()
        self.auth_utils.switch_mode()
        self.auth_utils.wait_for_register()
        self.auth_utils.switch_mode()
        self.auth_utils.wait_for_login()

    def test_signup_valid(self) -> None:
        """Test signup with valid data"""

        self.auth_utils.go_to_register()
        test_email, test_password = f"test@test.com", "Test123!"

        # Fill in signup form
        self.auth_utils.set_email(test_email)
        self.auth_utils.set_password(test_password)
        self.auth_utils.set_confirm_password(test_password)
        self.auth_utils.set_terms()
        self.auth_utils.confirm()
        self.auth_utils.set_first_name("Test")
        self.auth_utils.set_last_name("Test")
        self.auth_utils.confirm()

        # Verify redirect to login page
        self.auth_utils.wait_for_login()
        assert self.verify_user_in_database(test_email)
        self.auth_utils.assert_toast_message(
            "Account created! Please check your email to verify your account before logging in."
        )

    def test_signup_existing_email(self, test_users) -> None:
        """Test signup with an already registered email"""

        self.auth_utils.go_to_register()
        test_email, test_password = test_users[0].email, "Test123!"

        # Fill in signup form with existing email
        self.auth_utils.set_email(test_users[0].email)
        self.auth_utils.set_password(test_password)
        self.auth_utils.set_confirm_password(test_password)
        self.auth_utils.set_terms()
        self.auth_utils.confirm()
        self.auth_utils.set_first_name("Test")
        self.auth_utils.set_last_name("Test")
        self.auth_utils.confirm()

        # Verify error message and database
        self.auth_utils.assert_toast_message("Email already registered")
        assert len(self.verify_user_in_database(test_email)) == 1, "Multiple users with the same email found"

    def test_signup_invalid_email(self) -> None:
        """Test signup with invalid email format"""

        self.auth_utils.go_to_register()
        test_email, test_password = "invalid-email", "Test123!"

        # Fill in signup form with invalid email
        self.auth_utils.set_email(test_email)
        self.auth_utils.set_password(test_password)
        self.auth_utils.set_confirm_password(test_password)
        self.auth_utils.set_terms()
        self.auth_utils.confirm()

        # Verify error message and database
        self.auth_utils.assert_email_error_message("Please provide a valid email address")
        assert not self.verify_user_in_database(test_email)

    def test_signup_no_email(self) -> None:
        """Test signup with invalid email format"""

        self.auth_utils.go_to_register()
        test_email, test_password = "", "Test123!"

        # Fill in signup form with invalid email
        self.auth_utils.set_email(test_email)
        self.auth_utils.set_password(test_password)
        self.auth_utils.set_confirm_password(test_password)
        self.auth_utils.set_terms()
        self.auth_utils.confirm()

        # Verify error message and database
        self.auth_utils.assert_email_error_message("Please provide a valid email address")
        assert not self.verify_user_in_database(test_email)

    def test_signup_no_password(self) -> None:
        """Test signup with no password"""

        self.auth_utils.go_to_register()
        test_email, test_password = "test@test.com", ""

        # Fill in signup form with invalid password
        self.auth_utils.set_email(test_email)
        self.auth_utils.set_password(test_password)
        self.auth_utils.set_confirm_password(test_password)
        self.auth_utils.set_terms()
        self.auth_utils.confirm()

        # Verify error message and database
        self.auth_utils.assert_password_error_message("Password is required")
        self.auth_utils.assert_confirm_password_error_message("Please confirm your password")
        assert not self.verify_user_in_database(test_email)

    def test_signup_password_mismatch(self) -> None:
        """Test signup with mismatched passwords"""

        self.auth_utils.go_to_register()
        test_email = f"test@test.com"

        # Fill in signup form with non-matching passwords
        self.auth_utils.set_email(test_email)
        self.auth_utils.set_password("Password123")
        self.auth_utils.set_confirm_password("Password124")
        self.auth_utils.set_terms()
        self.auth_utils.confirm()

        # Verify error message and database
        self.auth_utils.assert_confirm_password_error_message("Passwords do not match")
        assert not self.verify_user_in_database(test_email)

    def test_signup_password_requirement(self) -> None:
        """Test signup with mismatched passwords"""

        self.auth_utils.go_to_register()
        test_email = f"test@test.com"

        # Fill in signup form with non-matching passwords
        self.auth_utils.set_email(test_email)
        self.auth_utils.set_password("Passw")
        self.auth_utils.set_confirm_password("Passw")
        self.auth_utils.set_terms()
        self.auth_utils.confirm()

        # Verify error message and database
        self.auth_utils.assert_password_error_message("Password must be at least 8 characters long.")
        assert not self.verify_user_in_database(test_email)

    def test_signup_no_tc(self) -> None:
        """Test signup without checking the terms and conditions"""

        self.auth_utils.go_to_register()
        test_email, test_password = f"test@test.com", "Test123!"

        # Fill in signup form with non-matching passwords
        self.auth_utils.set_email(test_email)
        self.auth_utils.set_password(test_password)
        self.auth_utils.set_confirm_password(test_password)
        self.auth_utils.confirm()

        # Verify error message and database
        self.auth_utils.assert_accept_terms_error_message(
            "You must accept the Terms and Conditions and Privacy Policy to register."
        )
        assert not self.verify_user_in_database(test_email)

    def test_signup_limited(self, test_settings) -> None:
        """Test signup when registrations are limited"""

        self.auth_utils.go_to_register()
        test_email, test_password = f"test@test.com", "Test123!"
        self.auth_utils.set_email(test_email)
        self.auth_utils.set_password(test_password)
        self.auth_utils.set_confirm_password(test_password)
        self.auth_utils.set_terms()
        self.auth_utils.confirm()
        self.auth_utils.set_first_name("Test")
        self.auth_utils.set_last_name("Test")
        self.auth_utils.confirm()

        self.auth_utils.assert_toast_message("You are not allowed to sign up for now.")
        assert not self.verify_user_in_database(test_email)


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
        self.auth_utils.assert_toast_message("Please wait")
        self._verify_account_via_email_link(test_email)
        self.auth_utils.wait_for_login()
        self.auth_utils.login_user(test_email, test_password)
        self.auth_utils.wait_for_dashboard()

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
        token = session.query(models.UserToken).filter(models.UserToken.owner_id == user.id).first()
        token.created_at = dt.datetime.now(dt.timezone.utc) - dt.timedelta(minutes=67)
        session.commit()
        invalid_verification_url = self.auth_utils.get_verification_link_from_email(test_email)
        self.driver.get(invalid_verification_url)
        self.auth_utils.assert_toast_message("Verification token has expired. Please request a new one by logging in.")


class TestPasswordReset(BaseTest):

    def test_password_reset_flow(self, test_users) -> None:
        """Test complete password reset flow using test email endpoints"""

        test_email = test_users[0].email
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


class TestDemoLogin(BaseTest):

    def setup_function(self, request) -> None:
        """Setup for each test method."""

        self.auth_utils.go_to_login()

    def test_demo_login_shows_banner(self, test_demo_user) -> None:
        """Clicking 'Try Demo' must log in and display the demo banner."""

        self.auth_utils.try_button.click()
        self.auth_utils.wait_for_dashboard()

        banner = self.get_element("demo-banner")
        assert "demo account" in banner.text.lower()

    def test_demo_logout_cancel_stays_logged_in(self, test_demo_user) -> None:
        """Cancelling the demo logout confirmation must keep the user on the dashboard."""

        self.auth_utils.try_button.click()
        self.auth_utils.wait_for_dashboard()
        self.wait_for_disappear("loading-spinner")

        # Click logout
        self.get_element("btn-close", By.CLASS_NAME).click()
        self.get_element("logout-btn").click()
        self.delete_modal.cancel_button.click()

        # Still on dashboard, banner still visible
        assert self.check_element_exists("demo-banner")

        # Fully log out
        self.get_element("logout-btn").click()
        self.delete_modal.confirm_button.click()

        self.auth_utils.wait_for_login()

    def test_regular_user_has_no_demo_banner(self, test_regular_user) -> None:
        """A regular user must not see the demo banner after login."""

        self.auth_utils.set_email(test_regular_user.email)
        self.auth_utils.set_password(test_regular_user.plain_password)
        self.auth_utils.confirm()
        self.auth_utils.wait_for_dashboard()

        assert not self.check_element_exists("demo-banner", timeout=2)


class TestWhatsNewModal(BaseTest):

    def test_welcome_modal_shows_for_new_user(self, session) -> None:
        """Test that the Welcome modal appears after login when user has no app_version (new user)."""

        self.db_user.app_version = None
        session.commit()

        self.login()
        modal = self.get_element("welcome-modal")
        assert "Welcome to Jam" in modal.text

        # Navigate through all steps and close
        for _ in range(6):
            self.get_element("welcome-modal-next-button").click()
        self.wait_for_disappear("welcome-modal")

        # Verify app_version is updated in the database
        assert self.db_user.app_version is not None

    def test_whats_new_modal_shows_for_returning_user(self, session) -> None:
        """Test that the What's New carousel appears after login when user has an older app_version."""

        self.db_user.app_version = "1.0.0"
        session.commit()

        self.login()
        modal = self.get_element("whats-new-modal")
        assert "What's New" in modal.text
        assert "Job Scraping" in modal.text

        # Navigate through all slides and close
        for _ in range(10):
            self.get_element("whats-new-modal-next-button").click()
        self.wait_for_disappear("whats-new-modal")

        # Verify app_version is updated in the database
        assert self.db_user.app_version != "1.1.0"
        assert self.db_user.app_version != "1.0.0"

    def test_no_modal_shown_when_up_to_date(self, session) -> None:
        """Test that no modal appears when user's app_version matches the current version."""

        # Set user's app_version to a future version (already seen everything)
        self.db_user.app_version = "10.0.0"
        session.commit()
        self.login()
        assert not self.check_element_exists("whats-new-modal", timeout=3)
        assert not self.check_element_exists("welcome-modal", timeout=1)


class TestMaintenanceModeAuthEndpoints(MaintenanceTestBase):
    """Auth endpoints (login, register, verify-email, password reset) are blocked during maintenance."""

    MAINTENANCE_MSG = "Service is currently under maintenance."

    def test_login_blocked_during_maintenance(self, test_regular_user) -> None:
        """Non-admin users cannot log in when maintenance is active."""

        past_time = self._get_past_timestamp(minutes=5)
        self._set_maintenance_scheduled_at(past_time)
        self.auth_utils.login_user(test_regular_user.email, test_regular_user.plain_password)
        self.auth_utils.assert_toast_message(self.MAINTENANCE_MSG)
        self._clear_maintenance_scheduled_at()

    def test_register_blocked_during_maintenance(self) -> None:
        """Registration is blocked when maintenance is active."""

        past_time = self._get_past_timestamp(minutes=5)
        self._set_maintenance_scheduled_at(past_time)
        self.auth_utils.register_user("newuser@test.com", "Test123!")
        self.auth_utils.assert_toast_message(self.MAINTENANCE_MSG)
        self._clear_maintenance_scheduled_at()

    def test_email_verification_blocked_during_maintenance(self, test_unverified_token_user) -> None:
        """Email verification is blocked when maintenance is active."""

        past_time = self._get_past_timestamp(minutes=5)
        self._set_maintenance_scheduled_at(past_time)
        self.auth_utils.go_to_verification_url(test_unverified_token_user.plain_verification_token)
        self.auth_utils.assert_toast_message(self.MAINTENANCE_MSG)
        self._clear_maintenance_scheduled_at()

    def test_password_reset_request_blocked_during_maintenance(self, test_regular_user) -> None:
        """Password reset requests are blocked when maintenance is active."""

        past_time = self._get_past_timestamp(minutes=5)
        self._set_maintenance_scheduled_at(past_time)
        self.auth_utils.go_to_login()
        self.auth_utils.switch_to_forgot_password()
        self.auth_utils.set_email(test_regular_user.email)
        self.auth_utils.confirm()
        self.auth_utils.assert_toast_message(self.MAINTENANCE_MSG)
        self._clear_maintenance_scheduled_at()

    def test_password_reset_confirm_blocked_during_maintenance(self, test_regular_user) -> None:
        """Submitting a new password via a reset token is blocked when maintenance is active."""

        self.auth_utils.clear_test_emails()
        self.auth_utils.go_to_login()
        self.auth_utils.switch_to_forgot_password()
        self.auth_utils.set_email(test_regular_user.email)
        self.auth_utils.confirm()
        self.auth_utils.assert_toast_message("Password reset email sent successfully")
        reset_url = self.auth_utils.get_reset_link_from_email(test_regular_user.email)

        past_time = self._get_past_timestamp(minutes=5)
        self._set_maintenance_scheduled_at(past_time)
        self.driver.get(reset_url)
        self.auth_utils.set_password("NewPassword123!")
        self.auth_utils.set_confirm_password("NewPassword123!")
        self.auth_utils.confirm()
        self.auth_utils.assert_toast_message(self.MAINTENANCE_MSG)
        self._clear_maintenance_scheduled_at()
