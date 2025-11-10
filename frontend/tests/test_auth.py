"""
Authentication End-to-End Tests
This module contains comprehensive Selenium-based tests for the authentication system,
including login, registration, form validation, and mode switching functionality.
"""

import time
import datetime as dt

from conftest import models, BaseTest


class TestAuthenticationPage(BaseTest):
    """Test class for Authentication functionality including:
    - Login with valid credentials
    - Login with invalid credentials
    - Signup with valid data
    - Signup with invalid data
    - Form validation"""

    # ----------------------------------------------------- INPUTS -----------------------------------------------------

    def go_to_login(self) -> None:
        """Go to the login page"""

        self.driver.get(f"{self.frontend_base_url}/login")

    def go_to_register(self) -> None:
        """Go to the register page"""

        self.driver.get(f"{self.frontend_base_url}/register")

    def go_to_forgot_password(self) -> None:
        """Go to the forgot password page"""

        self.driver.get(f"{self.frontend_base_url}/forgot-password")

    def set_email(self, email: str) -> None:
        """Set the email field to the given value"""

        self.get_element("email").send_keys(email)

    def set_password(self, password: str) -> None:
        """Set the password field to the given value"""

        self.get_element("password").send_keys(password)

    def set_confirm_password(self, password: str) -> None:
        """Set the confirm password field to the given value"""

        self.get_element("confirmPassword").send_keys(password)

    def confirm(self) -> None:
        """Confirm the form submission"""

        self.get_element("confirm-button").click()

    def set_terms(self) -> None:
        """Set the accept terms checkbox to True"""

        self.get_element("terms").click()

    def register_user(self, email: str, password: str) -> None:
        """Register a new user"""

        self.go_to_register()
        self.set_email(email)
        self.set_password(password)
        self.set_confirm_password(password)
        self.set_terms()
        self.confirm()

    def login_user(self, email: str, password: str) -> None:
        """Login with given credentials"""

        self.go_to_login()
        self.set_email(email)
        self.set_password(password)
        self.confirm()

    # ----------------------------------------------------- ERRORS -----------------------------------------------------

    def _assert_message(self, key: str, message: str) -> None:
        """Assert that the given message is displayed on the page
        :param key: Key to use for finding the error message element
        :param message: Message to check for"""

        assert message in self.get_element(key + "error-message").text, f"Message not found: {message}"

    def assert_email_error_message(self, error_message: str) -> None:
        """Assert that the given error message is displayed on the page"""

        self._assert_message("email-", error_message)

    def assert_password_error_message(self, error_message: str) -> None:
        """Assert that the given error message is displayed on the page"""

        self._assert_message("password-", error_message)

    def assert_confirm_password_error_message(self, error_message: str) -> None:
        """Assert that the given error message is displayed on the page"""

        self._assert_message("confirmPassword-", error_message)

    def assert_accept_terms_error_message(self, error_message: str) -> None:
        """Assert that the given error message is displayed on the page"""

        self._assert_message("terms-", error_message)

    # ------------------------------------------------------ PAGES -----------------------------------------------------

    def wait_for_dashboard(self) -> None:
        """Wait for the dashboard to load"""

        self.wait_for_page("dashboard")

    def wait_for_login(self) -> None:
        """Wait for the login page to load"""

        self.wait_for_page("login")

    def wait_for_register(self) -> None:
        """Wait for the register page to load"""

        self.wait_for_page("register")

    def switch_mode(self) -> None:
        """Switch between login and register modes"""

        self.get_element("switch-mode-button").click()

    def go_to_verification_url(self, token: str) -> None:
        """Navigate to login page with verification token"""

        self.driver.get(f"{self.frontend_base_url}/verify-email/?token={token}")

    def switch_to_forgot_password(self) -> None:
        """Navigate to forgot password page"""

        self.get_element("forgot-password-link").click()


class TestLogIn(TestAuthenticationPage):

    def test_valid_login(self, test_users) -> None:
        """Test login with valid credentials"""

        self.go_to_login()
        test_email, test_password = test_users[0].email, test_users[0].plain_password

        # Fill in login form
        self.set_email(test_email)
        self.set_password(test_password)
        self.confirm()

        # Confirm load by checking the dashboard
        self.wait_for_dashboard()

    def test_invalid_login(self) -> None:
        """Test login with invalid credentials"""

        self.go_to_login()
        test_email, test_password = "wrong@email.com", "wrong_password"

        # Fill in login form with invalid credentials
        self.set_email(test_email)
        self.set_password(test_password)
        self.confirm()

        # Verify error message
        self.assert_toast_message("Invalid credentials")

    def test_inactive_login(self, test_users) -> None:
        """Test login with invalid credentials"""

        self.go_to_login()
        test_email, test_password = test_users[2].email, test_users[2].plain_password

        # Fill in login form with invalid credentials
        self.set_email(test_email)
        self.set_password(test_password)
        self.confirm()

        # Verify error message
        self.assert_toast_message("User account is not active.")

    def test_login_invalid_email(self) -> None:
        """Test login with invalid credentials"""

        self.go_to_login()
        test_email, test_password = "wrong", "wrong_password"

        # Fill in login form with invalid credentials
        self.set_email(test_email)
        self.set_password(test_password)
        self.confirm()

        # Verify error message
        self.assert_email_error_message("Please provide a valid email address")

    def test_login_no_email(self) -> None:
        """Test login with invalid credentials"""

        self.go_to_login()
        test_email, test_password = "", "wrong_password"

        # Fill in login form with invalid credentials
        self.set_email(test_email)
        self.set_password(test_password)
        self.confirm()

        # Verify error message
        self.assert_email_error_message("Please provide a valid email address")

    def test_login_no_password(self) -> None:
        """Test login with invalid credentials"""

        self.go_to_login()
        test_email, test_password = "wrong@email.com", ""

        # Fill in login form with invalid credentials
        self.set_email(test_email)
        self.set_password(test_password)
        self.confirm()

        # Verify error message
        self.assert_password_error_message("Password is required")


class TestSignUp(TestAuthenticationPage):

    def test_mode_switching_buttons(self) -> None:
        """Test switching between login and register modes using the toggle buttons"""

        self.go_to_login()
        self.wait_for_login()
        self.switch_mode()
        self.wait_for_register()
        time.sleep(0.4)  # Wait for animation
        self.switch_mode()
        self.wait_for_login()

    def test_signup_valid(self) -> None:
        """Test signup with valid data"""

        self.go_to_register()
        test_email, test_password = f"test@test.com", "Test123!"

        # Fill in signup form
        self.set_email(test_email)
        self.set_password(test_password)
        self.set_confirm_password(test_password)
        self.set_terms()
        self.confirm()

        # Verify redirect to login page
        self.wait_for_login()
        assert self.verify_user_in_database(test_email)
        self.assert_toast_message("Account created! Please check your email to verify your account before logging in.")

    def test_signup_existing_email(self, test_users) -> None:
        """Test signup with an already registered email"""

        self.go_to_register()
        test_email, test_password = test_users[0].email, "Test123!"

        # Fill in signup form with existing email
        self.set_email(test_users[0].email)
        self.set_password(test_password)
        self.set_confirm_password(test_password)
        self.set_terms()
        self.confirm()

        # Verify error message and database
        self.assert_toast_message("Email already registered")
        assert len(self.verify_user_in_database(test_email)) == 1, "Multiple users with the same email found"

    def test_signup_invalid_email(self) -> None:
        """Test signup with invalid email format"""

        self.go_to_register()
        test_email, test_password = "invalid-email", "Test123!"

        # Fill in signup form with invalid email
        self.set_email(test_email)
        self.set_password(test_password)
        self.set_confirm_password(test_password)
        self.set_terms()
        self.confirm()

        # Verify error message and database
        self.assert_email_error_message("Please provide a valid email address")
        assert not self.verify_user_in_database(test_email)

    def test_signup_no_email(self) -> None:
        """Test signup with invalid email format"""

        self.go_to_register()
        test_email, test_password = "", "Test123!"

        # Fill in signup form with invalid email
        self.set_email(test_email)
        self.set_password(test_password)
        self.set_confirm_password(test_password)
        self.set_terms()
        self.confirm()

        # Verify error message and database
        self.assert_email_error_message("Please provide a valid email address")
        assert not self.verify_user_in_database(test_email)

    def test_signup_no_password(self) -> None:
        """Test signup with no password"""

        self.go_to_register()
        test_email, test_password = "test@test.com", ""

        # Fill in signup form with invalid password
        self.set_email(test_email)
        self.set_password(test_password)
        self.set_confirm_password(test_password)
        self.set_terms()
        self.confirm()

        # Verify error message and database
        self.assert_password_error_message("Password is required")
        self.assert_confirm_password_error_message("Please confirm your password")
        assert not self.verify_user_in_database(test_email)

    def test_signup_password_mismatch(self) -> None:
        """Test signup with mismatched passwords"""

        self.go_to_register()
        test_email = f"test@test.com"

        # Fill in signup form with non-matching passwords
        self.set_email(test_email)
        self.set_password("Password123")
        self.set_confirm_password("Password124")
        self.set_terms()
        self.confirm()

        # Verify error message and database
        self.assert_confirm_password_error_message("Passwords do not match")
        assert not self.verify_user_in_database(test_email)

    def test_signup_password_requirement(self) -> None:
        """Test signup with mismatched passwords"""

        self.go_to_register()
        test_email = f"test@test.com"

        # Fill in signup form with non-matching passwords
        self.set_email(test_email)
        self.set_password("Passw")
        self.set_confirm_password("Passw")
        self.set_terms()
        self.confirm()

        # Verify error message and database
        self.assert_password_error_message("Password must be at least 8 characters long.")
        assert not self.verify_user_in_database(test_email)

    def test_signup_no_tc(self) -> None:
        """Test signup without checking the terms and conditions"""

        self.go_to_register()
        test_email, test_password = f"test@test.com", "Test123!"

        # Fill in signup form with non-matching passwords
        self.set_email(test_email)
        self.set_password(test_password)
        self.set_confirm_password(test_password)
        self.confirm()

        # Verify error message and database
        self.assert_accept_terms_error_message("You must accept the Terms and Conditions to register")
        assert not self.verify_user_in_database(test_email)

    def test_signup_limited(self, test_settings) -> None:
        """Test signup when registrations are limited"""

        self.go_to_register()
        test_email, test_password = f"test@test.com", "Test123!"
        self.set_email(test_email)
        self.set_password(test_password)
        self.set_confirm_password(test_password)
        self.set_terms()
        self.confirm()

        self.assert_toast_message("You are not allowed to sign up for now.")
        assert not self.verify_user_in_database(test_email)


class TestEmailVerification(TestAuthenticationPage):

    def _register_and_verify_redirect(self, email: str, password: str) -> None:
        """Helper to clear emails, register user, wait for login page, and assert account creation message."""

        self.clear_test_emails()
        self.register_user(email, password)
        self.wait_for_login()
        self.assert_toast_message("Account created! Please check your email to verify your account before logging in.")

    def _verify_account_via_email_link(self, email: str) -> None:
        """Helper to retrieve the verification link from email and visit it, asserting success."""

        verification_url = self.get_verification_link_from_email(email)
        self.driver.get(verification_url)
        self.assert_toast_message("Account verified successfully")

    def test_full_email_verification_flow(self) -> None:
        """Test the full email verification flow starting from registration to successful login after email verification."""

        test_email = "newuser@test.com"
        test_password = "Test123!"

        self._register_and_verify_redirect(test_email, test_password)
        self._verify_account_via_email_link(test_email)
        self.login_user(test_email, test_password)
        self.wait_for_dashboard()

    def test_login_with_non_verified_user_verifies_account(self, test_unverified_token_user, session) -> None:
        """Test that logging in with a non-verified user redirects to verification and successfully verifies the account."""

        self.go_to_verification_url(test_unverified_token_user.plain_verification_token)
        self.assert_toast_message("Account verified successfully")

    def test_login_before_verification_shows_wait_then_allows_login(self, session) -> None:
        """Test attempting login before email verification shows 'Please wait' message,
        then after verification login succeeds."""

        test_email = "newuser@test.com"
        test_password = "Test123!"

        self._register_and_verify_redirect(test_email, test_password)
        self.login_user(test_email, test_password)
        self.assert_toast_message("Please wait")
        self._verify_account_via_email_link(test_email)
        self.login_user(test_email, test_password)
        self.wait_for_dashboard()

    def test_registering_same_email_before_verification_shows_wait_then_allows_login(self, session) -> None:
        """Test that trying to register the same email before verification shows 'Please wait' message,
        then after verification login succeeds."""

        test_email = "newuser@test.com"
        test_password = "Test123!"

        self._register_and_verify_redirect(test_email, test_password)
        self.register_user(test_email, test_password)
        self.assert_toast_message("Please wait")
        self._verify_account_via_email_link(test_email)
        self.login_user(test_email, test_password)
        self.wait_for_dashboard()

    def test_verification_with_invalid_token_shows_error(self, session) -> None:
        """Test visiting email verification URL with an invalid or expired token shows an error message."""

        test_email = "newuser@test.com"
        test_password = "Test123!"
        self._register_and_verify_redirect(test_email, test_password)
        invalid_verification_url = self.get_verification_link_from_email(test_email)[:-4]
        self.driver.get(invalid_verification_url)
        self.assert_toast_message("Invalid or expired token. Please request a new one by logging in.")

    def test_expired_verification_token(self, session) -> None:
        """Test email verification with an expired token."""

        test_email = "newuser@test.com"
        test_password = "Test123!"
        self._register_and_verify_redirect(test_email, test_password)
        user = session.query(models.User).filter(models.User.email == test_email).first()
        user.verification_token_created_at = dt.datetime.now(dt.timezone.utc) - dt.timedelta(minutes=20)
        session.commit()
        invalid_verification_url = self.get_verification_link_from_email(test_email)
        self.driver.get(invalid_verification_url)
        self.assert_toast_message("Verification token has expired. Please request a new one by logging in.")


class TestPasswordReset(TestAuthenticationPage):

    def test_password_reset_flow(self, test_users) -> None:
        """Test complete password reset flow using test email endpoints"""

        test_email = test_users[0].email
        new_password = "NewPassword123!"

        # Clear any existing test emails
        self.clear_test_emails()

        # Request password reset
        self.go_to_login()
        self.switch_to_forgot_password()
        self.set_email(test_email)
        self.confirm()

        # Verify success message
        self.assert_toast_message("Password reset email sent successfully")

        # Get reset link from test endpoint
        reset_url = self.get_reset_link_from_email(test_email)

        # Visit reset URL
        self.driver.get(reset_url)

        # Set new password
        self.set_password(new_password)
        self.set_confirm_password(new_password)
        self.confirm()

        # Verify success message
        self.assert_toast_message("Password has been reset successfully")

        # Login with new password
        self.wait_for_login()
        self.set_email(test_email)
        self.set_password(new_password)
        self.confirm()
        self.wait_for_dashboard()

    def test_password_reset_invalid_token(self) -> None:
        """Test password reset with invalid token"""

        invalid_reset_url = f"{self.frontend_base_url}/reset-password?token=invalid_token"
        self.driver.get(invalid_reset_url)
        self.set_password("password")
        self.set_confirm_password("password")
        self.confirm()
        self.assert_toast_message("Invalid or expired password reset token")
