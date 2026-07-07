"""Tests for the login page."""

import time

from fixtures.users import FixtureUser
from frontend_base_test import BaseTest


class TestLogIn(BaseTest):

    def setup_function(self, request) -> None:
        """Setup for each test method."""

        self.auth_utils.go_to_login()

    def test_valid_login(self, test_regular_user: FixtureUser) -> None:
        """Test login with valid credentials"""

        test_email, test_password = test_regular_user.email, test_regular_user.plain_password

        # Fill in login form
        self.auth_utils.set_email(test_email)
        self.auth_utils.set_password(test_password)
        self.auth_utils.confirm()

        # Confirm load by checking the dashboard
        self.auth_utils.wait_for_dashboard()

    def test_incorrect_credentials_login(self) -> None:
        """Test login with incorrect credentials"""

        test_email, test_password = "wrong@email.com", "wrong_password"

        # Fill in login form with incorrect credentials
        self.auth_utils.set_email(test_email)
        self.auth_utils.set_password(test_password)
        self.auth_utils.confirm()

        # Verify error message
        self.auth_utils.assert_toast_message("Invalid credentials")

    def test_inactive_login(self, test_inactive_user: FixtureUser) -> None:
        """Test login with an inactive user's credentials"""

        test_email, test_password = test_inactive_user.email, test_inactive_user.plain_password
        assert not test_inactive_user.is_active

        # Fill in login form with invalid credentials
        self.auth_utils.set_email(test_email)
        self.auth_utils.set_password(test_password)
        self.auth_utils.confirm()

        # Verify error message
        self.auth_utils.assert_toast_message("User account is not active.")

    def test_login_malformed_email(self) -> None:
        """Test login with invalid email"""

        # Fill in login form with malformed email
        self.auth_utils.set_email("wrong")
        self.auth_utils.set_password("Test123!")
        self.auth_utils.confirm()

        # Verify error message
        self.auth_utils.assert_email_error_message("Please provide a valid email address")
        self.auth_utils.assert_confirm_button_disabled()

        # Adding 1 more character fixes the error and re-enables the button
        self.auth_utils.get_element("email").send_keys("a")
        self.auth_utils.assert_no_email_error_message()
        self.auth_utils.assert_confirm_button_enabled()

    def test_login_no_email(self) -> None:
        """Test login with no email"""

        # Fill in login form with invalid credentials
        self.auth_utils.set_email("")
        self.auth_utils.set_password("Test123!")
        self.auth_utils.confirm()

        # Verify error message
        self.auth_utils.assert_email_error_message("Please provide a valid email address")
        self.auth_utils.assert_confirm_button_disabled()

        # Adding 1 more character fixes the error and re-enables the button
        self.auth_utils.get_element("email").send_keys("a")
        self.auth_utils.assert_no_email_error_message()
        self.auth_utils.assert_confirm_button_enabled()

    def test_login_no_password(self) -> None:
        """Test login with no password"""

        # Fill in login form with invalid credentials
        self.auth_utils.set_email("email@email.com")
        self.auth_utils.set_password("")
        self.auth_utils.confirm()

        # Verify error message
        self.auth_utils.assert_password_error_message("Password is required")
        self.auth_utils.assert_confirm_button_disabled()

        # Adding 1 more character fixes the error and re-enables the button
        self.auth_utils.get_element("password").send_keys("a")
        self.auth_utils.assert_no_password_error_message()
        self.auth_utils.assert_confirm_button_enabled()

    def test_unexpected_error(self) -> None:
        """Test login with unexpected error"""

        self.auth_utils.set_email("crash@crash.com")  # causes the backend to crash in test mode
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
        deadline = time.time() + 5
        while time.time() < deadline:
            self.db.expire_all()
            if self.user.last_login and self.user.last_login > login_dt:
                break
            time.sleep(0.2)
        assert self.user.last_login > login_dt
        assert self.user.previous_login == login_dt

    def test_logout(self):
        """Test logout"""

        self.login()
        self.get_element("logout-btn").click()
        self.logout_modal.confirm_button.click()
        self.auth_utils.wait_for_login()

    def test_remember_me_unchecked_stores_in_session_storage(self, test_regular_user: FixtureUser) -> None:
        """Test that login without remember me stores the token in sessionStorage, not localStorage"""

        self.auth_utils.set_email(test_regular_user.email)
        self.auth_utils.set_password(test_regular_user.plain_password)
        self.auth_utils.confirm()
        self.auth_utils.wait_for_dashboard()

        token_in_local = self.driver.execute_script("return window.localStorage.getItem('token')")
        token_in_session = self.driver.execute_script("return window.sessionStorage.getItem('token')")

        assert token_in_local is None, "Token should not be in localStorage when remember me is unchecked"
        assert token_in_session is not None, "Token should be in sessionStorage when remember me is unchecked"

    def test_remember_me_checked_stores_in_local_storage(self, test_regular_user: FixtureUser) -> None:
        """Test that login with remember me checked stores the token in localStorage, not sessionStorage"""

        self.auth_utils.set_email(test_regular_user.email)
        self.auth_utils.set_password(test_regular_user.plain_password)
        self.auth_utils.set_remember_me()
        self.auth_utils.confirm()
        self.auth_utils.wait_for_dashboard()

        token_in_local = self.driver.execute_script("return window.localStorage.getItem('token')")
        token_in_session = self.driver.execute_script("return window.sessionStorage.getItem('token')")

        assert token_in_local is not None, "Token should be in localStorage when remember me is checked"
        assert token_in_session is None, "Token should not be in sessionStorage when remember me is checked"

    def test_login_field_limits(self) -> None:
        """Entering email or password over the limit disables Sign In; reducing re-enables it."""

        # Email over limit (254 char limit)
        self.auth_utils.set_email("a" * 246 + "@test.com")
        self.auth_utils.assert_confirm_button_disabled()

        # Back within limit
        self.auth_utils.set_email("test@test.com")
        self.auth_utils.assert_confirm_button_enabled()

        # Password over limit (128 char limit)
        self.auth_utils.set_password("P" * 129)
        self.auth_utils.assert_confirm_button_disabled()

        # Back within limit
        self.auth_utils.set_password("Password123!")
        self.auth_utils.assert_confirm_button_enabled()
