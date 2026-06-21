"""Test the main pages of JAM"""

import datetime as dt

from selenium.webdriver.common.by import By

from base_test import models
from helpers.table_page import BaseTablePage
from tests.utils.test_data import ADMIN_USER_INDEX


class TestSettingsPage(BaseTablePage):
    """Test class for the admin Settings table (opened via the admin dashboard modal)."""

    endpoint = "settings"
    page_url = "admin"
    test_fixture = "test_settings"
    entry_type = "setting"
    required_fields = ["name", "value"]
    test_data = {"name": "test_name", "value": "test_value"}
    duplicate_fields = ["name"]
    model = models.Setting
    user_index = ADMIN_USER_INDEX

    def setup_function(self, request) -> None:
        super().setup_function(request)
        # The settings table now lives in a modal opened from the admin dashboard.
        card = self.get_element("admin-card-settings", enabled=False)
        card.find_element(By.CLASS_NAME, "card-title").click()
        self.get_element("admin-page-modal", enabled=False)
