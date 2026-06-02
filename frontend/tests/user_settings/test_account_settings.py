"""Tests for the User Settings Page"""

import datetime as dt
import time

from app.utils import verify_password
from base_test import models, BaseTest


class TestAccountSettingsPage(BaseTest):
    """Test class for the User Settings Page"""

    page_url = "settings/account"

    def setup_function(self, request) -> None:
        """Setup function"""

        self.login()

    # ------------------------------------------------- UPDATING EMAIL -------------------------------------------------

    def test_update_email_no_password(self) -> None:
        """Test updating email without current password"""

        self.set_text(self.user_settings_utils.current_password, "")
        self.set_text(self.user_settings_utils.email, "test@test.com")
        time.sleep(1)
        self.user_settings_utils.confirm()
        self.user_settings_utils.assert_password_error_message(
            "Current password is required to update email or password"
        )

    def test_update_email_incorrect_password(self) -> None:
        """Test updating email without current password"""

        self.set_text(self.user_settings_utils.current_password, "wrong")
        self.set_text(self.user_settings_utils.email, "test@test.com")
        self.user_settings_utils.confirm()
        self.assert_toast_message("The current password is incorrect.")

    def test_change_email_success(self) -> None:
        """Test changing the email address"""

        new_email = "newemail@email.com"
        self.clear_test_emails()
        self.set_text(self.user_settings_utils.current_password, self.user.plain_password)
        self.set_text(self.user_settings_utils.email, new_email)
        self.user_settings_utils.confirm()
        self.assert_toast_message("Email change verification email sent successfully.")
        assert new_email in self.get_element("pending-email-info").text
        verification_url = self.get_verification_link_from_email(new_email)
        self.driver.get(verification_url)
        self.assert_toast_message("Email address changed successfully. You can now log in with your new email.")
        self.db_user.email = new_email

    def test_verification_with_invalid_token_shows_error(self, session) -> None:
        """Test visiting email verification URL with an invalid or expired token shows an error message."""

        new_email = "newuser@test.com"
        self.clear_test_emails()
        self.set_text(self.user_settings_utils.current_password, self.user.plain_password)
        self.set_text(self.user_settings_utils.email, new_email)
        self.user_settings_utils.confirm()
        self.assert_toast_message("Email change verification email sent successfully.")
        invalid_verification_url = self.get_verification_link_from_email(new_email)[:-4]
        self.driver.get(invalid_verification_url)
        self.assert_toast_message(
            "Invalid or expired token. Please request a new one by logging in and changing your email address."
        )

    def test_expired_verification_token(self, session) -> None:
        """Test email verification with an expired token."""

        new_email = "newuser@test.com"
        self.clear_test_emails()
        self.set_text(self.user_settings_utils.current_password, self.user.plain_password)
        self.set_text(self.user_settings_utils.email, new_email)
        self.user_settings_utils.confirm()
        self.assert_toast_message("Email change verification email sent successfully.")
        self.db_user.verification_token_created_at = dt.datetime.now(dt.timezone.utc) - dt.timedelta(minutes=20)
        invalid_verification_url = self.get_verification_link_from_email(new_email)[:-4]
        self.driver.get(invalid_verification_url)
        self.assert_toast_message(
            "Invalid or expired token. Please request a new one by logging in and changing your email address."
        )

    def test_change_email_already_exist(self, test_users) -> None:
        """Test changing the email address"""

        self.set_text(self.user_settings_utils.current_password, self.user.plain_password)
        self.set_text(self.user_settings_utils.email, test_users[2].email)
        self.user_settings_utils.confirm()
        self.assert_toast_message("Email already registered")
        assert self.db_user.email == self.user.email

    def test_change_email_incorrect_format(self, test_users) -> None:
        """Test changing the email address"""

        self.set_text(self.user_settings_utils.current_password, self.user.plain_password)
        self.set_text(self.user_settings_utils.email, "f")
        self.user_settings_utils.confirm()
        self.user_settings_utils.assert_email_error_message("Email format is invalid")

        # Adding 1 more character fixes the error and re-enables the button
        self.user_settings_utils.email.send_keys("a")
        self.user_settings_utils.assert_no_email_error_message()
        self.user_settings_utils.assert_confirm_button_enabled()

        assert self.db_user.email == self.user.email

    # ------------------------------------------------ UPDATING PASSWORD -----------------------------------------------

    def test_change_password_success(self) -> None:
        """Test changing the password"""

        new_password = "newpassword"
        self.user_settings_utils.current_password.send_keys(self.user.plain_password)
        self.set_text(self.user_settings_utils.new_password, new_password)
        self.set_text(self.user_settings_utils.confirm_password, new_password)
        self.user_settings_utils.confirm()
        self.wait_for_page("login")
        self.assert_toast_message("Password updated successfully. Please log in again.")
        assert verify_password(new_password, self.db_user.password)

    def test_change_password_invalid(self) -> None:
        """Test changing the password"""

        self.user_settings_utils.current_password.send_keys(self.user.plain_password)
        self.set_text(self.user_settings_utils.new_password, "n")
        self.set_text(self.user_settings_utils.confirm_password, "n")
        self.user_settings_utils.confirm()
        self.user_settings_utils.assert_new_password_error_message("New password must be at least 8 characters long")

        # Adding 1 more character fixes the error and re-enables the button
        self.user_settings_utils.new_password.send_keys("a")
        self.user_settings_utils.assert_no_new_password_error_message()
        self.user_settings_utils.assert_confirm_button_enabled()

        assert verify_password(self.user.plain_password, self.db_user.password)

    def test_change_password_nonmatching(self) -> None:
        """Test changing the password"""

        self.user_settings_utils.current_password.send_keys(self.user.plain_password)
        self.set_text(self.user_settings_utils.new_password, "testpassword")
        self.set_text(self.user_settings_utils.confirm_password, "n")
        self.user_settings_utils.confirm()
        self.user_settings_utils.assert_confirm_password_error_message("Passwords do not match")

        # Adding 1 more character fixes the error and re-enables the button
        self.user_settings_utils.confirm_password.send_keys("a")
        self.user_settings_utils.assert_no_confirm_password_error_message()
        self.user_settings_utils.assert_confirm_button_enabled()

        assert verify_password(self.user.plain_password, self.db_user.password)

    # -------------------------------------------------- DATA EXPORT ---------------------------------------------------

    def test_download_data_export(self) -> None:
        """Test downloading user data export"""

        # Find and click the download data button
        self.user_settings_utils.download_data_button.click()

        # Wait for the download to complete (toast notification)
        self.assert_toast_message("Data downloaded")

    # ------------------------------------------------ ACCOUNT DELETION ------------------------------------------------

    def test_delete_account_cancel_first_modal(self) -> None:
        """Test cancelling account deletion from the first modal"""

        self.user_settings_utils.delete_account_button.click()
        self.user_settings_utils.cancel_delete_button.click()
        assert self.db_user is not None
        assert self.db_user.email == self.user.email

    def test_delete_account_cancel_confirmation_modal(self) -> None:
        """Test cancelling account deletion from the confirmation modal"""

        self.user_settings_utils.delete_account_button.click()
        self.set_text(self.user_settings_utils.delete_password, self.user.plain_password)
        self.user_settings_utils.continue_delete_button.click()
        self.user_settings_utils.cancel_confirm_delete_button.click()
        assert self.db_user is not None
        assert self.db_user.email == self.user.email

    def test_delete_account_success(self, session) -> None:
        """Test successful account deletion"""

        user_id = self.user.id
        self.user_settings_utils.delete_account_button.click()
        self.set_text(self.user_settings_utils.delete_password, self.user.plain_password)
        self.user_settings_utils.continue_delete_button.click()
        self.user_settings_utils.final_delete_button.click()
        self.wait_for_page("login")
        self.assert_toast_message("Your account has been permanently deleted.")
        deleted_user = session.query(models.User).filter(models.User.id == user_id).first()
        assert deleted_user is None

    def test_delete_account_wrong_password(self) -> None:
        """Test account deletion with wrong password"""

        self.user_settings_utils.delete_account_button.click()
        self.set_text(self.user_settings_utils.delete_password, self.user.plain_password + "something")
        self.user_settings_utils.continue_delete_button.click()
        self.user_settings_utils.final_delete_button.click()
        self.assert_toast_message("Failed to delete account. Password is incorrect.")
        assert self.db_user is not None
        assert self.db_user.email == self.user.email

    def test_download_data_before_deletion(self, session) -> None:
        """Test downloading data from the confirmation modal before deletion"""

        self.user_settings_utils.delete_account_button.click()
        self.set_text(self.user_settings_utils.delete_password, self.user.plain_password)
        self.user_settings_utils.continue_delete_button.click()
        self.user_settings_utils.download_data_modal_button.click()
        self.assert_toast_message("Data downloaded")
