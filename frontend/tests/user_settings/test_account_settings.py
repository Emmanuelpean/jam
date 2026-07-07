"""Tests for the User Settings Page"""

import datetime as dt

from sqlalchemy.orm import Session

from app.utilities.security import verify_password
from fixtures.users import FixtureUser
from frontend_base_test import models, BaseTest


class TestAccountSettingsPage(BaseTest):
    """Test class for the User Settings Page"""

    page_url = "settings/account"

    def setup_function(self, request) -> None:
        """Setup function"""

        self.login()

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

    def test_delete_account_success(self, session: Session) -> None:
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
        """Test that entering a wrong password in the first modal shows an inline field error"""

        self.user_settings_utils.delete_account_button.click()
        self.set_text(self.user_settings_utils.delete_password, self.user.plain_password + "something")
        self.user_settings_utils.continue_delete_button.click()
        self.user_settings_utils.assert_delete_password_error_message("Password is incorrect.")
        assert self.db_user is not None
        assert self.db_user.email == self.user.email

    def test_delete_account_wrong_then_correct_password(self, session: Session) -> None:
        """Test that correcting the password after a wrong-password error allows deletion"""

        user_id = self.user.id
        self.user_settings_utils.delete_account_button.click()
        self.set_text(self.user_settings_utils.delete_password, self.user.plain_password + "something")
        self.user_settings_utils.continue_delete_button.click()
        self.user_settings_utils.assert_delete_password_error_message("Password is incorrect.")

        # Correct the password and retry
        self.set_text(self.user_settings_utils.delete_password, self.user.plain_password)
        self.user_settings_utils.continue_delete_button.click()
        self.user_settings_utils.final_delete_button.click()
        self.wait_for_page("login")
        self.assert_toast_message("Your account has been permanently deleted.")
        deleted_user = session.query(models.User).filter(models.User.id == user_id).first()
        assert deleted_user is None

    def test_download_data_before_deletion(self) -> None:
        """Test downloading data from the confirmation modal before deletion"""

        self.user_settings_utils.delete_account_button.click()
        self.set_text(self.user_settings_utils.delete_password, self.user.plain_password)
        self.user_settings_utils.continue_delete_button.click()
        self.user_settings_utils.download_data_modal_button.click()
        self.assert_toast_message("Data downloaded")


class TestAccountSettingsPageEmailChange(BaseTest):

    page_url = "settings/account"

    def setup_function(self, request) -> None:
        """Setup function"""

        self.login()

    @staticmethod
    def get_success_message(new_email: str) -> str:
        """Get the success message from the toast notification"""

        return f"A verification email has been sent to {new_email}. Please check your inbox to confirm the change."

    def request_email_change(self, new_email: str, password: str | None = None) -> None:
        """Open the change-email modal, fill in the new email and current password, then submit.
        :param new_email: The new email address to request.
        :param password: The current password to confirm with (defaults to the logged-in user's password)."""

        self.user_settings_utils.change_email_button.click()
        self.set_text(self.user_settings_utils.email, new_email)
        self.set_text(
            self.user_settings_utils.current_password, self.user.plain_password if password is None else password
        )
        self.user_settings_utils.confirm_email_change_button.click()

    def test_change_email_success(self) -> None:
        """Test changing the email address via the change-email modal"""

        new_email = "newemail@email.com"
        self.clear_test_emails()
        self.request_email_change(new_email)
        self.assert_toast_message(self.get_success_message(new_email))
        assert new_email in self.get_element("pending-email-info").text
        verification_url = self.get_verification_link_from_email(new_email)
        self.driver.get(verification_url)
        self.assert_toast_message(
            "Email address has been successfully updated. You can now log in with your new email."
        )
        self.db_user.email = new_email

    def test_verification_with_invalid_token_shows_error(self) -> None:
        """Test visiting email verification URL with an invalid or expired token shows an error message."""

        new_email = "newuser@test.com"
        self.clear_test_emails()
        self.request_email_change(new_email)
        self.assert_toast_message(self.get_success_message(new_email))
        invalid_verification_url = self.get_verification_link_from_email(new_email)[:-4]
        self.driver.get(invalid_verification_url)
        self.assert_toast_message(
            "Invalid or expired token. Please request a new one by logging in and changing your email address."
        )

    def test_expired_verification_token(self) -> None:
        """Test email verification with an expired token."""

        new_email = "newuser@test.com"
        self.clear_test_emails()
        self.request_email_change(new_email)
        self.assert_toast_message(self.get_success_message(new_email))
        self.db_user.verification_token_created_at = dt.datetime.now(dt.timezone.utc) - dt.timedelta(minutes=20)
        invalid_verification_url = self.get_verification_link_from_email(new_email)[:-4]
        self.driver.get(invalid_verification_url)
        self.assert_toast_message(
            "Invalid or expired token. Please request a new one by logging in and changing your email address."
        )

    def test_email_change_within_rate_limit_shows_wait(self) -> None:
        """Test that requesting a second email change within the rate limit window shows an inline 'Please wait' error."""

        new_email = "newemail@email.com"
        self.clear_test_emails()
        self.request_email_change(new_email)
        self.assert_toast_message(self.get_success_message(new_email))

        self.driver.refresh()
        self.request_email_change(new_email)
        self.user_settings_utils.assert_email_error_message("Please wait")

    def test_email_change_after_rate_limit_sends_new_email(self, session: Session) -> None:
        """Test that requesting an email change after the rate limit window sends a new email and shows a success message."""

        new_email = "newemail@email.com"
        self.clear_test_emails()
        self.request_email_change(new_email)
        self.assert_toast_message(self.get_success_message(new_email))

        token = self.user.get_token(models.TokenType.EMAIL_CHANGE)
        assert token
        token.created_at = dt.datetime.now(dt.timezone.utc) - dt.timedelta(minutes=3)
        session.commit()

        self.driver.refresh()
        self.request_email_change(new_email)
        self.assert_toast_message(self.get_success_message(new_email))

    def test_change_email_already_exist(self, test_admin_user: FixtureUser) -> None:
        """Test changing the email to one already registered shows an inline error"""

        self.request_email_change(test_admin_user.email)
        self.user_settings_utils.assert_email_error_message("Email already registered")
        assert self.db_user.email == self.user.email

    def test_change_email_incorrect_password(self) -> None:
        """Test changing the email with an incorrect current password shows an inline error"""

        self.request_email_change("newemail@email.com", password="wrongpassword")
        self.user_settings_utils.assert_password_error_message("The current password is incorrect.")
        assert self.db_user.email == self.user.email

    def test_change_email_incorrect_format(self) -> None:
        """Test changing the email to an invalid format shows an inline error"""

        self.user_settings_utils.change_email_button.click()
        self.set_text(self.user_settings_utils.email, "f")
        self.user_settings_utils.confirm_email_change_button.click()
        self.user_settings_utils.assert_email_error_message("Email format is invalid")

        # Adding 1 more character fixes the error
        self.user_settings_utils.email.send_keys("a")
        self.user_settings_utils.assert_no_email_error_message()

        assert self.db_user.email == self.user.email

    def test_full_email_change_flow_revokes_old_token(self) -> None:
        """Full email-change flow: request a change, confirm the new email via the verification
        link, then re-inject the original token (as if a different tab still holds it) and reload
        the account page. The stale token must be rejected and the user redirected to /login."""

        # Capture the token that the original tab would still be holding after the user opens
        # the verification link elsewhere.
        old_token = self.driver.execute_script(
            "return window.localStorage.getItem('token') || window.sessionStorage.getItem('token');"
        )
        assert old_token, "Expected an auth token in browser storage before the email change"

        new_email = "newemail@email.com"
        self.clear_test_emails()
        self.request_email_change(new_email)
        self.assert_toast_message(self.get_success_message(new_email))

        # Visit the verification link. In a real-world scenario this would happen in a separate
        # browser/tab; here it runs in the same driver, which logs us out and bumps token_version
        # server-side. The original tab is unaffected — that's what we simulate next.
        verification_url = self.get_verification_link_from_email(new_email)
        self.driver.get(verification_url)
        self.assert_toast_message(
            "Email address has been successfully updated. You can now log in with your new email."
        )
        self.db_user.email = new_email

        # Re-inject the now-stale token to simulate returning to the original tab, then reload
        # the account page. The server should reject the token and the app should redirect to
        # /login (and not get stuck on the global loading overlay).
        self.driver.execute_script(f'window.localStorage.setItem("token", "{old_token}");')
        self.driver.get(f"{self.frontend_base_url}/settings/account")
        self.wait_for_page("login")
        self.wait_for_disappear("loading-spinner")


class TestAccountSettingsPagePasswordChange(BaseTest):

    page_url = "settings/account"

    def setup_function(self, request) -> None:
        """Setup function"""

        self.login()

    def test_change_password_success(self) -> None:
        """Test changing the password via the change-password modal.
        After the change, the original token must be invalid — re-injecting it into storage
        and reloading the account page must redirect back to /login."""

        # Capture the auth token that was valid before the password change.
        old_token = self.driver.execute_script(
            "return window.localStorage.getItem('token') || window.sessionStorage.getItem('token');"
        )
        assert old_token, "Expected an auth token in browser storage before the password change"

        new_password = "newpassword"
        self.user_settings_utils.change_password_button.click()
        self.user_settings_utils.current_password.send_keys(self.user.plain_password)
        self.set_text(self.user_settings_utils.new_password, new_password)
        self.set_text(self.user_settings_utils.confirm_password, new_password)
        self.user_settings_utils.confirm_password_change_button.click()
        self.wait_for_page("login")
        self.assert_toast_message("Password has been successfully updated. Please log in again.")
        assert verify_password(new_password, self.db_user.password)
        self.driver.refresh()
        self.wait_for_page("login")
        self.wait_for_disappear("loading-spinner")

    def test_change_password_incorrect_current(self) -> None:
        """Test changing the password with the wrong current password shows an inline field error"""

        self.user_settings_utils.change_password_button.click()
        self.user_settings_utils.current_password.send_keys("wrong")
        self.set_text(self.user_settings_utils.new_password, "newpassword")
        self.set_text(self.user_settings_utils.confirm_password, "newpassword")
        self.user_settings_utils.confirm_password_change_button.click()
        self.user_settings_utils.assert_password_error_message("The current password is incorrect.")
        assert verify_password(self.user.plain_password, self.db_user.password)

    def test_change_password_invalid(self) -> None:
        """Test changing the password to one shorter than the minimum length"""

        self.user_settings_utils.change_password_button.click()
        self.user_settings_utils.current_password.send_keys(self.user.plain_password)
        self.set_text(self.user_settings_utils.new_password, "n")
        self.set_text(self.user_settings_utils.confirm_password, "n")
        self.user_settings_utils.confirm_password_change_button.click()
        self.user_settings_utils.assert_new_password_error_message("New password must be at least 8 characters long")

        # Adding 1 more character fixes the error
        self.user_settings_utils.new_password.send_keys("a")
        self.user_settings_utils.assert_no_new_password_error_message()

        assert verify_password(self.user.plain_password, self.db_user.password)

    def test_change_password_nonmatching(self) -> None:
        """Test changing the password when the confirmation doesn't match"""

        self.user_settings_utils.change_password_button.click()
        self.user_settings_utils.current_password.send_keys(self.user.plain_password)
        self.set_text(self.user_settings_utils.new_password, "testpassword")
        self.set_text(self.user_settings_utils.confirm_password, "n")
        self.user_settings_utils.confirm_password_change_button.click()
        self.user_settings_utils.assert_confirm_password_error_message("Passwords do not match")

        # Adding 1 more character fixes the error
        self.user_settings_utils.confirm_password.send_keys("a")
        self.user_settings_utils.assert_no_confirm_password_error_message()

        assert verify_password(self.user.plain_password, self.db_user.password)
