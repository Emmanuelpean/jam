"""Utilities for interacting with data tables."""

import re
import time

from selenium.common import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait

from select_utils import Select
from utilities.base_utils import BaseUtils


class DataTableUtils(BaseUtils):
    """Base class for testing data tables"""

    def __init__(self, entry_type: str, **kwargs):
        self._init(**kwargs)
        self.entry_type = entry_type

    # ----------------------------------------------------- TABLES -----------------------------------------------------

    @property
    def table_rows(self) -> list[WebElement]:
        """Get all table rows on the page"""

        time.sleep(0.5)
        try:
            self.get_element(f"[id^='table-row-{self.entry_type}-']", By.CSS_SELECTOR, 1)
        except AssertionError:
            return []
        return self.driver.find_elements(By.CSS_SELECTOR, f"[id^='table-row-{self.entry_type}-']")

    def table_row(self, item_id: int, *args, **kwargs) -> WebElement:
        """Get a specific table row by its ID"""

        return self.get_element(f"table-row-{self.entry_type}-{item_id}", *args, **kwargs)

    def table_context_menu(self, entity_id: int, choice: str) -> None:
        """Row context menu"""

        self.context_menu(self.table_row(entity_id), choice)

    def check_row_exist(self, column: str, name: str, expected_count: int = 1) -> None:
        """Check that a specific row with a specific name exists in the table
        :param column: Name of the column to check
        :param name: Name of the column
        :param expected_count: Expected number of rows with that name"""

        assert (
            self.get_column_values(column).count(name) == expected_count
        ), f"Expected {expected_count} rows with name '{name}'"

    def get_column_values(self, column_key: str | None = None) -> list[str] | list[dict[str, str]]:
        """Get values from a specific table column via the column key
        (matched using id attributes starting with 'table-header-').
        :param column_key: The key of the column. If None, returns all rows as list of dicts.
        :return: List of values from that column, or list of row dicts if no key provided.
        """
        # Find all elements where id starts with 'table-header-'
        header_elements = self.driver.find_elements(By.XPATH, "//*[@id[starts-with(., 'table-header-')]]")
        header_keys = []
        for header in header_elements:
            th_id = header.get_attribute("id")
            # Ensure only ids with "table-header-" are considered
            if th_id and th_id.startswith("table-header-"):
                header_keys.append(th_id[len("table-header-") :])

        # If no column_key provided, return all rows as list of dicts
        if column_key is None:
            rows_data = []
            for row in self.table_rows:
                row_dict = {}
                cells = row.find_elements(By.TAG_NAME, "td")
                for i, key in enumerate(header_keys):
                    if i < len(cells):
                        row_dict[key] = cells[i].text
                rows_data.append(row_dict)
            return rows_data

        if column_key not in header_keys:
            raise ValueError(f"Column key '{column_key}' not found. Available keys: {header_keys}")

        column_index = header_keys.index(column_key)
        return [row.find_elements(By.TAG_NAME, "td")[column_index].text for row in self.table_rows]

    def wait_for_table_load(self, timeout: int | float = 0.1) -> None:
        """Wait for loading spinner to disappear"""

        try:
            WebDriverWait(self.driver, timeout).until(
                ec.invisibility_of_element_located((By.CSS_SELECTOR, "spinner-border"))
            )
        except TimeoutException:
            pass

    def get_row_id(self, index: int) -> int:
        """Get the entry ID of a table row by its index (0-based)
        :param index: Index of the table row"""

        pattern = rf"table-row-{self.entry_type}-(\d+)"
        row_id = self.get_attribute(self.table_rows[index], "id")
        match = re.search(pattern, row_id)
        if not match:
            raise ValueError(f"Could not find ID for table row at index {index}")
        return int(match.group(1))

    def check_id_in_table(self, entry_id: int, **kwargs) -> bool:
        """Check if an ID is in the table"""

        try:
            self.get_element(f"[id^='table-row-{self.entry_type}-']", By.CSS_SELECTOR, **kwargs)
        except AssertionError:
            return False
        rows = self.driver.find_elements(By.CSS_SELECTOR, f"[id^='table-row-{self.entry_type}-']")
        return any(row.get_attribute("id") == f"table-row-{self.entry_type}-{entry_id}" for row in rows)

    def check_id_not_in_table(self, entry_id: int) -> bool:
        """Check if an ID is not in the table"""

        return not self.check_id_in_table(entry_id, timeout=2)

    def set_search(self, search_text: str) -> None:
        """Set the search input to the given text"""

        self.set_text(self.get_element("search-input"), search_text)
        time.sleep(0.2)

    # ----------------------------------------------------- BUTTONS ----------------------------------------------------

    @property
    def add_entity_button(self) -> WebElement:
        """Get the Add Entity button"""

        return self.get_element(f"add-{self.entry_type}-button")

    @property
    def deadline_toggle(self) -> WebElement:
        """Get the Deadline Toggle button"""

        return self.get_element("show-past-deadline-toggle")

    def set_page_item_select(self, value: str) -> None:
        """Set the number of items to display per page
        :param value: Value to select (e.g. "20", "40")"""

        if len(self.table_rows) >= 20:
            Select(self.get_element("page-items-select")).select_by_visible_text(f"Show {value} Entries")

    def table_row_click(self, row_index: int) -> None:
        """Click on a table row by its index (0-based)"""

        element = self.table_row(row_index)
        self.driver.execute_script("arguments[0].click();", element)

    # --------------------------------------------------- FILTERS -----------------------------------------------------

    def get_row_count(self) -> int:
        """Return the number of currently visible table rows"""

        return len(self.table_rows)

    def is_filter_sidebar_open(self) -> bool:
        """Return True if the filter sidebar has the 'open' CSS class"""

        sidebar = self.get_element("filter-sidebar", enabled=False)
        section_classes = sidebar.get_attribute("class")
        if section_classes:
            return "open" in section_classes
        else:
            return False

    def open_filter_sidebar(self) -> None:
        """Click the filter toggle button and wait for the sidebar to render"""

        self.get_element("filter-toggle-btn").click()
        self.get_element("filter-clear-btn", enabled=False)

    def toggle_expired_jobs(self) -> None:
        """Open the filter sidebar, flip the 'Show expired jobs' toggle, then close the sidebar."""

        self.open_filter_sidebar()
        self.deadline_toggle.click()
        self.get_element("filter-close-btn").click()

    def is_section_active(self, column_key: str) -> bool:
        """Return True if the filter section for the given column key is highlighted as active"""

        section = self.get_element(f"filter-section-{column_key}", enabled=False)
        section_classes = section.get_attribute("class")
        if section_classes:
            return "filter-section--active" in section_classes
        else:
            return False

    def get_filter_pills(self) -> list:
        """Return all visible filter pill span elements"""

        return self.driver.find_elements(By.CLASS_NAME, "header-filter-pill")

    def get_active_count_from_sidebar(self) -> int:
        """Return the count shown in the sidebar header badge (0 if the badge is absent)"""

        badges = self.driver.find_elements(By.CLASS_NAME, "filter-sidebar-count")
        if not badges:
            return 0
        try:
            return int(badges[0].text)
        except (ValueError, IndexError):
            return 0

    def select_from_react_select_filter(self, column_key: str, visible_text: str) -> None:
        """Select an option from a react-select filter by its visible label"""

        section = self.get_element(f"filter-section-{column_key}", enabled=False)
        select_container = section.find_element(By.CLASS_NAME, "jam-select")
        rs = Select(select_container)
        rs.select_by_visible_text(visible_text)
        time.sleep(0.5)
