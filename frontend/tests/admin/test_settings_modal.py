"""Test the main pages of JAM"""

from app import models
from helpers.table_page_utils import BaseTablePage


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
        self.admin_page_utils.open_card("admin-card-settings")

    def reload_page(self) -> None:
        """Reload the admin page and reopen the settings modal so new entries appear."""

        self.refresh()
        self.admin_page_utils.open_card("admin-card-settings")

    def create_entries(self, count: int = 1) -> list[models.Setting]:
        """Create setting entries"""

        return [self.create_setting(self.db, name=f"setting_{i}", value=f"value_{i}") for i in range(count)]
