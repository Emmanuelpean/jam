"""Tests for the User Settings Page"""

import datetime as dt
import time

from selenium.webdriver.remote.webelement import WebElement

from app.utils import verify_password
from conftest import models, BaseTest


class TestUserSettingsPage(BaseTest):
    """Test class for the User Settings Page"""

    page_url = "settings"

    def setup_function(self, request) -> None:
        """Setup for each test function"""

        self.login()

    def verify_user_in_database(self, email: str) -> bool:
        """Helper method to verify user exists in database"""

        return self.db.query(models.User).filter(models.User.email == email).all()

    @property
    def current_password(self) -> WebElement:
        """Get the current password field"""
        return self.get_element("current_password")

    @property
    def email(self) -> WebElement:
        """Get the email field"""

        return self.get_element("email")

    @property
    def new_password(self) -> WebElement:
        """Get the new password field"""

        return self.get_element("new_password")

    @property
    def confirm_password(self) -> WebElement:
        """Get the confirmation password field"""

        return self.get_element("confirm_password")

    @property
    def theme_hint(self) -> WebElement:
        """Get the theme hint text"""

        return self.get_element("theme-hint")

    @property
    def chase_threshold(self) -> WebElement:
        """Get the chase threshold input"""

        return self.get_element("chase_threshold")

    @property
    def deadline_threshold(self) -> WebElement:
        """Get the deadline threshold input"""

        return self.get_element("deadline_threshold")

    @property
    def update_limit(self) -> WebElement:
        """Get the update limit input"""

        return self.get_element("update_limit")

    def confirm(self) -> None:
        """Confirm the form submission"""

        self.get_element("confirm-button").click()

    def assert_toast(self, message) -> None:
        """Assert that the given toast message is displayed on the page"""
        assert message in self.get_element("toast").text, f"Message not found: {message}"

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

        self._assert_message("current_password-", error_message)

    def assert_new_password_error_message(self, error_message: str) -> None:
        """Assert that the given error message is displayed on the page"""

        self._assert_message("new_password-", error_message)

    def assert_confirm_password_error_message(self, error_message: str) -> None:
        """Assert that the given error message is displayed on the page"""

        self._assert_message("confirm_password-", error_message)

    # ------------------------------------------------- UPDATING EMAIL -------------------------------------------------

    def test_no_password(self) -> None:
        """Test updating email without current password"""

        self.set_text(self.current_password, "")
        self.set_text(self.email, "test@test.com")
        time.sleep(1)
        self.confirm()
        self.assert_password_error_message("Current password is required to update email or password")

    def test_incorrect_password(self) -> None:
        """Test updating email without current password"""

        self.set_text(self.current_password, "wrong")
        self.set_text(self.email, "test@test.com")
        self.confirm()
        self.assert_toast("Current password is incorrect. Please try again.")

    def test_change_email_success(self) -> None:
        """Test changing the email address"""

        new_email = "newemail@email.com"
        self.clear_test_emails()
        self.set_text(self.current_password, self.user.plain_password)
        self.set_text(self.email, new_email)
        self.confirm()
        self.assert_toast("Verification email sent successfully.")
        verification_url = self.get_verification_link_from_email(new_email)
        self.driver.get(verification_url)
        self.assert_toast_message("Email address changed successfully. You can now log in with your new email.")
        self.db_user.email = new_email

    def test_verification_with_invalid_token_shows_error(self, session) -> None:
        """Test visiting email verification URL with an invalid or expired token shows an error message."""

        new_email = "newuser@test.com"
        self.clear_test_emails()
        self.set_text(self.current_password, self.user.plain_password)
        self.set_text(self.email, new_email)
        self.confirm()
        self.assert_toast("Verification email sent successfully.")
        invalid_verification_url = self.get_verification_link_from_email(new_email)[:-4]
        self.driver.get(invalid_verification_url)
        self.assert_toast_message(
            "Invalid or expired token. Please request a new one by logging in and changing your email address."
        )

    def test_expired_verification_token(self, session) -> None:
        """Test email verification with an expired token."""

        new_email = "newuser@test.com"
        self.clear_test_emails()
        self.set_text(self.current_password, self.user.plain_password)
        self.set_text(self.email, new_email)
        self.confirm()
        self.assert_toast("Verification email sent successfully.")
        user = session.query(models.User).filter(models.User.email == self.user.email).first()
        user.verification_token_created_at = dt.datetime.now(dt.timezone.utc) - dt.timedelta(minutes=20)
        invalid_verification_url = self.get_verification_link_from_email(new_email)[:-4]
        self.driver.get(invalid_verification_url)
        self.assert_toast_message(
            "Invalid or expired token. Please request a new one by logging in and changing your email address."
        )

    def test_change_email_already_exist(self, test_users) -> None:
        """Test changing the email address"""

        self.set_text(self.current_password, self.user.plain_password)
        self.set_text(self.email, test_users[2].email)
        self.confirm()
        self.assert_toast("Email is already in use. Please try a different email.")
        assert self.db_user.email == self.user.email

    def test_change_email_incorrect_format(self, test_users) -> None:
        """Test changing the email address"""

        self.set_text(self.current_password, self.user.plain_password)
        self.set_text(self.email, "f")
        self.confirm()
        self.assert_email_error_message("Email format is invalid")
        assert self.db_user.email == self.user.email

    # ------------------------------------------------ UPDATING PASSWORD -----------------------------------------------

    def test_change_password_success(self) -> None:
        """Test changing the password"""

        new_password = "newpassword"
        self.current_password.send_keys(self.user.plain_password)
        self.set_text(self.new_password, new_password)
        self.set_text(self.confirm_password, new_password)
        self.confirm()
        self.wait_for_page("login")
        self.assert_toast("Password updated successfully. Please log in again.")
        assert verify_password(new_password, self.db_user.password)

    def test_change_password_invalid(self) -> None:
        """Test changing the password"""

        self.current_password.send_keys(self.user.plain_password)
        self.set_text(self.new_password, "n")
        self.set_text(self.confirm_password, "n")
        self.confirm()
        self.assert_new_password_error_message("New password must be at least 8 characters long")
        assert verify_password(self.user.plain_password, self.db_user.password)

    def test_change_password_nonmatching(self) -> None:
        """Test changing the password"""

        self.current_password.send_keys(self.user.plain_password)
        self.set_text(self.new_password, "testpassword")
        self.set_text(self.confirm_password, "n")
        self.confirm()
        self.assert_confirm_password_error_message("Passwords do not match")
        assert verify_password(self.user.plain_password, self.db_user.password)

    # ------------------------------------------------------ THEME -----------------------------------------------------

    def test_theme_hint(self) -> None:
        """Test theme hint"""

        assert self.theme_hint.text == (
            "Mixed Berry is not your favourite flavour of JAM?! You can easily pick "
            "another flavour by clicking on the JAM logo in the sidebar."
        )

    # ----------------------------------------------- DASHBOARD SETTINGS -----------------------------------------------

    def test_dashboard_settings(self) -> None:
        """Test changing the dashboard settings"""

        assert self.db_user.chase_threshold == 14
        assert self.db_user.deadline_threshold == 7
        assert self.db_user.update_limit == 10

        self.set_text(self.chase_threshold, "100")
        self.set_text(self.deadline_threshold, "101")
        self.set_text(self.update_limit, "102")
        self.confirm()
        time.sleep(0.1)

        assert self.db_user.chase_threshold == 100
        assert self.db_user.deadline_threshold == 101
        assert self.db_user.update_limit == 102
