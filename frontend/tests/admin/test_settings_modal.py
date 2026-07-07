"""Test the main pages of JAM"""

from selenium.webdriver.common.by import By

from base_test import models
from helpers.table_page import BaseTablePage


class TestSettingsPage(BaseTablePage):
    """Test class for the admin Settings table (opened via the admin dashboard modal)."""

    endpoint = "settings"
    page_url = "admin"
    entry_type = "setting"
    required_fields = ["name", "value"]
    test_data = {"name": "test_name", "value": "test_value"}
    duplicate_fields = ["name"]
    model = models.Setting
    user_fixture = "test_admin_user"

    def setup_function(self, request) -> None:
        super().setup_function(request)
        self._open_settings_modal()

    def _open_settings_modal(self) -> None:
        """Open the settings table modal from the admin dashboard."""

        card = self.get_element("admin-card-settings", enabled=False)
        card.find_element(By.CLASS_NAME, "card-title").click()
        self.get_element("admin-page-modal", enabled=False)

    def reload_page(self) -> None:
        """Reload the admin page and reopen the settings modal so new entries appear."""

        self.refresh()
        self._open_settings_modal()

    def create_entries(self, count: int = 1) -> list[models.Setting]:
        """Create setting entries"""

        return [
            self.create_setting(self.db, name=f"setting_{i}", value=f"value_{i}")
            for i in range(count)
        ]
