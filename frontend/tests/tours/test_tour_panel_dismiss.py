"""Selenium tests for dismissing / re-enabling the 'Take a Tour' sidebar shortcut.

Users can hide the shortcut without completing every tour via the tour select panel's
"Don't show this again" button, and bring it back from the Preferences settings tab. While
dismissed, the About page still offers a way to launch a tour.
"""

from frontend_base_test import BaseTest


class TestTourPanelDismiss(BaseTest):
    user_fixture = "test_regular_user"
    page_url = "dashboard"

    def setup_function(self, request) -> None:
        self.login()

    def test_dismiss_from_panel_hides_sidebar_button(self) -> None:
        """'Don't show this again' persists the preference and removes the sidebar shortcut."""
        self.get_element(self.tour_utils.TAKE_A_TOUR_BTN, enabled=False)

        self.tour_utils.dismiss_tour_panel()

        self.poll_db_value(lambda: self.db_user.preferences.tour_panel_dismissed, True)
        self.wait_for_disappear(self.tour_utils.TAKE_A_TOUR_BTN)

    def test_reenable_from_preferences_restores_sidebar_button(self) -> None:
        """Toggling the Preferences switch back on clears the preference and restores the shortcut."""
        self.tour_utils.dismiss_tour_panel()
        self.poll_db_value(lambda: self.db_user.preferences.tour_panel_dismissed, True)

        self.go_to_page("settings/preferences")
        self.wait_for_page("settings/preferences")
        self.user_settings_utils.tour_shortcut_toggle.click()

        self.poll_db_value(lambda: self.db_user.preferences.tour_panel_dismissed, False)
        self.get_element(self.tour_utils.TAKE_A_TOUR_BTN, enabled=False)

    def test_about_page_shows_button_when_dismissed(self) -> None:
        """The About page keeps a 'Take a Tour' button once the sidebar shortcut is dismissed."""
        self.tour_utils.dismiss_tour_panel()
        self.poll_db_value(lambda: self.db_user.preferences.tour_panel_dismissed, True)

        self.go_to_page("about")
        self.wait_for_page("about")
        self.get_element(self.tour_utils.TAKE_A_TOUR_BTN, enabled=False)
