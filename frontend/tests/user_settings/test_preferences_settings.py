"""Tests for the User Settings Page"""

from frontend_base_test import BaseTest


class TestPreferenceSettingsPage(BaseTest):
    """Test class for the Preference Settings Page"""

    page_url = "settings/preferences"

    def setup_function(self, request) -> None:
        """Setup function"""

        self.login()

    def test_currency_settings(self) -> None:
        """Test changing the currency settings auto-saves without a confirm button"""

        self.user_settings_utils.currency.select_by_visible_text("US Dollar")
        self.poll_db_value(lambda: self.db_user.preferences.default_currency, "USD")

    def test_theme_settings(self) -> None:
        """Test changing the theme settings"""

        self.user_settings_utils.get_theme("raspberry").click()
        self.poll_db_value(lambda: self.db_user.preferences.theme, "raspberry")

    def test_toggle_dark_model(self) -> None:
        """Toggle Dark Model"""

        self.user_settings_utils.dark_mode_btn.click()
        self.poll_db_value(lambda: self.db_user.preferences.dark_mode, "dark")
