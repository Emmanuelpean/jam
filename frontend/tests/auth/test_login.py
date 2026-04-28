"""Tests for login functionality"""

import time

from base_test import BaseTest


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

    def test_logout(self):
        """Test logout"""

        self.login()
        self.get_element("logout-btn").click()
        self.logout_modal.confirm_button.click()
        self.auth_utils.wait_for_login()

    def test_remember_me_unchecked_stores_in_session_storage(self, test_regular_user) -> None:
        """Test that login without remember me stores the token in sessionStorage, not localStorage"""

        self.auth_utils.set_email(test_regular_user.email)
        self.auth_utils.set_password(test_regular_user.plain_password)
        self.auth_utils.confirm()
        self.auth_utils.wait_for_dashboard()

        token_in_local = self.driver.execute_script("return window.localStorage.getItem('token')")
        token_in_session = self.driver.execute_script("return window.sessionStorage.getItem('token')")

        assert token_in_local is None, "Token should not be in localStorage when remember me is unchecked"
        assert token_in_session is not None, "Token should be in sessionStorage when remember me is unchecked"

    def test_remember_me_checked_stores_in_local_storage(self, test_regular_user) -> None:
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
