"""Utilities for the user settings pages."""

from selenium.webdriver.remote.webelement import WebElement

from helpers.jam_test_utils import JamTestUtils
from helpers.select_utils import Select


class UserSettingsUtils(JamTestUtils):
    """Test class for the User Settings Page"""

    def __init__(self, **kwargs):
        self._init(**kwargs)

    def go_to_account_tab(self) -> None:
        """Get the account tab button"""

        self.get_element("account-tab").click()

    def go_to_preferences_tab(self) -> None:
        """Get the preferences tab button"""

        self.get_element("preferences-tab").click()

    def go_to_qualifications_tab(self) -> None:
        """Get the qualifications tab button"""

        self.get_element("qualifications-tab").click()

    def go_to_premium_tab(self) -> None:
        """Get the premium tab button"""

        self.get_element("premium-tab").click()

    @property
    def change_email_button(self) -> WebElement:
        """Get the Change Email button on the account page"""

        return self.get_element("change-email-button")

    @property
    def change_password_button(self) -> WebElement:
        """Get the Change Password button on the account page"""

        return self.get_element("change-password-button")

    @property
    def confirm_email_change_button(self) -> WebElement:
        """Get the confirm button inside the email change modal"""

        return self.get_element("confirm-email-change-button")

    @property
    def cancel_email_change_button(self) -> WebElement:
        """Get the cancel button inside the email change modal"""

        return self.get_element("cancel-email-change-button")

    @property
    def confirm_password_change_button(self) -> WebElement:
        """Get the confirm button inside the password change modal"""

        return self.get_element("confirm-password-change-button")

    @property
    def cancel_password_change_button(self) -> WebElement:
        """Get the cancel button inside the password change modal"""

        return self.get_element("cancel-password-change-button")

    @property
    def current_password(self) -> WebElement:
        """Get the current password field in the password change modal"""
        return self.get_element("current_password")

    @property
    def email(self) -> WebElement:
        """Get the email field in the email change modal"""

        return self.get_element("email")

    @property
    def new_password(self) -> WebElement:
        """Get the new password field in the password change modal"""

        return self.get_element("new_password")

    @property
    def confirm_password(self) -> WebElement:
        """Get the confirmation password field in the password change modal"""

        return self.get_element("confirm_password")

    @property
    def currency(self) -> Select:
        """Get the currency field"""

        return Select(self.get_element("default_currency"))

    def get_theme(self, theme_key: str) -> WebElement:
        """Get the theme field"""

        return self.get_element(theme_key + "-theme")

    @property
    def tour_shortcut_toggle(self) -> WebElement:
        """Get the 'Show the Take a Tour shortcut in the sidebar' toggle"""

        return self.get_element("tour-shortcut-toggle")

    @property
    def dark_mode_btn(self) -> WebElement:
        """Get the dark mode toggle button"""

        return self.get_element("theme-dark-btn")

    @property
    def light_mode_btn(self) -> WebElement:
        """Get the light mode toggle button"""

        return self.get_element("theme-light-btn")

    @property
    def system_theme_btn(self) -> WebElement:
        """Get the system theme toggle button"""

        return self.get_element("theme-system-btn")

    def confirm(self) -> None:
        """Confirm the form submission"""

        self.get_element("confirm-button").click()

    def assert_email_error_message(self, error_message: str) -> None:
        """Assert that the given error message is displayed on the page"""

        self.assert_error_message("email", error_message)

    def assert_password_error_message(self, error_message: str) -> None:
        """Assert that the given error message is displayed on the page"""

        self.assert_error_message("current_password", error_message)

    def assert_new_password_error_message(self, error_message: str) -> None:
        """Assert that the given error message is displayed on the page"""

        self.assert_error_message("new_password", error_message)

    def assert_confirm_password_error_message(self, error_message: str) -> None:
        """Assert that the given error message is displayed on the page"""

        self.assert_error_message("confirm_password", error_message)

    def assert_no_email_error_message(self) -> None:
        """Assert that the email error message is not displayed on the page"""

        self.wait_for_disappear("email-error-message")

    def assert_no_new_password_error_message(self) -> None:
        """Assert that the new password error message is not displayed on the page"""

        self.wait_for_disappear("new_password-error-message")

    def assert_no_confirm_password_error_message(self) -> None:
        """Assert that the confirm password error message is not displayed on the page"""

        self.wait_for_disappear("confirm_password-error-message")

    def assert_confirm_button_enabled(self) -> None:
        """Wait until the confirm button becomes enabled (clickable)."""

        self.get_element("confirm-button")

    def assert_delete_password_error_message(self, error_message: str) -> None:
        """Assert that the given error message is displayed under the delete password field"""

        self.assert_error_message("delete_password", error_message)

    @property
    def download_data_button(self) -> WebElement:
        """Get the download data button"""

        return self.get_element("download-data-button")

    @property
    def delete_account_button(self) -> WebElement:
        """Get the delete account button"""

        return self.get_element("delete-account-button")

    @property
    def delete_password(self) -> WebElement:
        """Get the delete password field"""

        return self.get_element("delete_password")

    @property
    def delete_account_modal(self) -> WebElement:
        """Get the delete account modal"""

        return self.get_element("delete-account-modal")

    @property
    def cancel_delete_button(self) -> WebElement:
        """Get the cancel delete button in first modal"""

        return self.get_element("cancel-delete-button")

    @property
    def continue_delete_button(self) -> WebElement:
        """Get the continue button in first modal"""

        return self.get_element("continue-delete-button")

    @property
    def confirm_delete_modal(self) -> WebElement:
        """Get the confirmation delete modal"""

        return self.get_element("confirm-delete-modal")

    @property
    def download_data_modal_button(self) -> WebElement:
        """Get the download data button in confirmation modal"""

        return self.get_element("download-data-modal-button")

    @property
    def cancel_confirm_delete_button(self) -> WebElement:
        """Get the cancel button in confirmation modal"""

        return self.get_element("cancel-confirm-delete-button")

    @property
    def final_delete_button(self) -> WebElement:
        """Get the final delete button"""

        return self.get_element("final-delete-button")

    @property
    def experience_input(self) -> WebElement:
        """Get the experience input field"""

        return self.get_element("experience")

    @property
    def skills_input(self) -> WebElement:
        """Get the skills input field"""

        return self.get_element("skills")

    @property
    def qualities_input(self) -> WebElement:
        """Get the qualities input field"""

        return self.get_element("qualities")

    @property
    def education_input(self) -> WebElement:
        """Get the education input field"""

        return self.get_element("education")

    @property
    def interests_input(self) -> WebElement:
        """Get the interests input field"""

        return self.get_element("interests")
