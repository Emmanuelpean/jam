"""Utilities for the Column Configuration sidebar shown on data-table pages."""

import time

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from helpers.jam_test_utils import JamTestUtils


class ColumnConfigSidebarUtils(JamTestUtils):
    """Test class for the Column Configuration sidebar (column visibility + sort direction)."""

    def __init__(self, **kwargs):
        self._init(**kwargs)

    # ------------------------------------------------- ELEMENTS -------------------------------------------------

    @property
    def sidebar(self) -> WebElement:
        """The column config sidebar."""

        return self.get_element("column-config-sidebar", enabled=False)

    @property
    def toggle_button(self) -> WebElement:
        """The gear button that opens the sidebar."""

        return self.get_element("column-config-toggle-btn")

    @property
    def close_button(self) -> WebElement:
        """The button that closes the sidebar."""

        return self.get_element("column-config-close-btn")

    @property
    def reset_button(self) -> WebElement:
        """The 'Reset to Defaults' button."""

        return self.get_element("column-config-reset-btn")

    @property
    def sort_direction_button(self) -> WebElement:
        """The sort-direction toggle button."""

        return self.get_element("column-config-sort-direction-btn")

    def column_toggle(self, key: str) -> WebElement:
        """The visibility checkbox for the given column key."""

        return self.get_element(f"col-toggle-{key}")

    # -------------------------------------------------- HELPERS --------------------------------------------------

    def is_open(self) -> bool:
        """Return True if the sidebar has the 'open' class."""

        class_attr = self.sidebar.get_attribute("class")
        assert class_attr is not None, "Sidebar element should have a class attribute"
        return "open" in class_attr

    def open(self) -> None:
        """Open the sidebar via the gear button and wait for its content to appear."""

        self.toggle_button.click()
        self.get_element("col-toggle-title")  # wait for sidebar content to appear

    def close(self) -> None:
        """Close the sidebar via the close button."""

        self.close_button.click()
        time.sleep(0.5)

    def toggle_column(self, key: str) -> None:
        """Toggle a column's visibility checkbox and wait for the async save."""

        self.column_toggle(key).click()
        time.sleep(0.5)

    def reset_to_defaults(self) -> None:
        """Click 'Reset to Defaults' and wait for the async save."""

        self.reset_button.click()
        time.sleep(0.5)

    def toggle_sort_direction(self) -> None:
        """Click the sort-direction toggle and wait for the async save."""

        self.sort_direction_button.click()
        time.sleep(0.5)

    def visible_table_columns(self) -> list[str]:
        """Return column keys currently shown in the table header."""

        headers = self.driver.find_elements(By.XPATH, "//*[@id[starts-with(., 'table-header-')]]")
        columns = []
        for header in headers:
            id_attr = header.get_attribute("id")
            if id_attr:
                columns.append(id_attr.removeprefix("table-header-"))
        return columns
