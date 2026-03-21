"""Tests for the User Settings Page"""

import time

from base_test import BaseTest


class TestPreferenceSettingsPage(BaseTest):
    """Test class for the Preference Settings Page"""

    page_url = "settings/preferences"

    def setup_function(self, request) -> None:
        """Setup function"""

        self.login()

    def test_dashboard_settings(self) -> None:
        """Test changing the dashboard settings"""

        assert self.user_settings_utils.chase_threshold.get_attribute("value") == str(
            self.db_user.preferences.chase_threshold
        )
        assert self.user_settings_utils.deadline_threshold.get_attribute("value") == str(
            self.db_user.preferences.deadline_threshold
        )
        assert self.user_settings_utils.update_limit.get_attribute("value") == str(
            self.db_user.preferences.update_limit
        )

        self.set_text(self.user_settings_utils.chase_threshold, "100")
        self.set_text(self.user_settings_utils.deadline_threshold, "101")
        self.set_text(self.user_settings_utils.update_limit, "102")
        self.user_settings_utils.confirm()
        self.assert_toast_message("Preferences updated successfully.")

        assert self.db_user.preferences.chase_threshold == 100
        assert self.db_user.preferences.deadline_threshold == 101
        assert self.db_user.preferences.update_limit == 102

    def test_currency_settings(self) -> None:
        """Test changing the currency settings"""

        self.user_settings_utils.currency.select_by_visible_text("US Dollar")
        self.user_settings_utils.confirm()
        self.assert_toast_message("Preferences updated successfully.")
        assert self.db_user.preferences.default_currency == "USD"

    def test_theme_settings(self) -> None:
        """Test changing the theme settings"""

        self.user_settings_utils.get_theme("raspberry").click()
        time.sleep(0.1)
        assert self.db_user.preferences.theme == "raspberry"

    def test_toggle_dark_model(self) -> None:
        """Toggle Dark Model"""

        self.user_settings_utils.dark_mode_btn.click()
        time.sleep(0.1)
        assert self.db_user.preferences.dark_mode
