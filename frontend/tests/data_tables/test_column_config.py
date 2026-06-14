"""Tests for the Column Configuration sidebar feature"""

import time

from base_test import BaseTest

# Columns visible by default (passed as `columns` prop in JobsPage.tsx)
DEFAULT_VISIBLE_JOB_COLUMNS = [
    "title",
    "companyBadge",
    "locationBadge",
    "url",
    "salary_min",
    "personal_rating",
    "application_status",
    "created_at",
]

# All job columns registered in columnRegistry.ts (visible + hidden by default)
ALL_JOB_COLUMNS = [
    "title",
    "companyBadge",
    "locationBadge",
    "url",
    "salary_min",
    "personal_rating",
    "contactBadges",
    "application_status",
    "interviews",
    "updates",
    "deadline",
    "sourceAggregatorBadge",
    "sourceContactBadge",
    "attendance_type",
    "description",
    "note",
    "created_at",
    "keywords",
]


class TestColumnConfig(BaseTest):
    """Tests for the Column Configuration sidebar on the Jobs table"""

    page_url = "jobs"

    def setup_function(self, request) -> None:
        request.getfixturevalue("test_jobs")
        self.login()

    # -------------------------------------------------- Helpers --------------------------------------------------

    def is_column_config_sidebar_open(self) -> bool:
        """Return True if the column config sidebar has the 'open' class"""

        sidebar = self.get_element("column-config-sidebar", enabled=False)
        return "open" in sidebar.get_attribute("class")

    def open_column_config_sidebar(self) -> None:
        """Open the column config sidebar via the gear button"""
        self.get_element("column-config-toggle-btn").click()
        self.get_element("col-toggle-title")  # wait for sidebar content to appear

    def get_visible_table_columns(self) -> list[str]:
        """Return column keys currently shown in the table header"""
        from selenium.webdriver.common.by import By

        headers = self.driver.find_elements(By.XPATH, "//*[@id[starts-with(., 'table-header-')]]")
        return [h.get_attribute("id").removeprefix("table-header-") for h in headers]

    def toggle_column(self, key: str) -> None:
        """Toggle a column's visibility checkbox and wait for the async save"""
        self.get_element(f"col-toggle-{key}").click()
        time.sleep(0.5)

    # -------------------------------------------------- Tests --------------------------------------------------

    def test_open_and_close_sidebar(self) -> None:
        """Gear button opens the sidebar; the close button dismisses it"""
        assert not self.is_column_config_sidebar_open()

        self.open_column_config_sidebar()
        assert self.is_column_config_sidebar_open()

        self.get_element("column-config-close-btn").click()
        time.sleep(0.5)
        assert not self.is_column_config_sidebar_open()

    def test_all_columns_listed_in_sidebar(self) -> None:
        """All registered job columns (visible and hidden) appear as toggles in the sidebar"""
        self.open_column_config_sidebar()
        for key in ALL_JOB_COLUMNS:
            assert self.check_element_exists(f"col-toggle-{key}"), f"Toggle not found for column key '{key}'"

    def test_default_visible_columns_checked(self) -> None:
        """Default visible columns are checked; non-default columns are unchecked"""
        self.open_column_config_sidebar()
        for key in DEFAULT_VISIBLE_JOB_COLUMNS:
            checkbox = self.get_element(f"col-toggle-{key}")
            assert checkbox.is_selected(), f"Expected column '{key}' to be checked by default"
        for key in set(ALL_JOB_COLUMNS) - set(DEFAULT_VISIBLE_JOB_COLUMNS):
            checkbox = self.get_element(f"col-toggle-{key}")
            assert not checkbox.is_selected(), f"Expected column '{key}' to be unchecked by default"

    def test_reset_button_enabled_after_hiding_column(self) -> None:
        """Reset button becomes enabled once at least one column is hidden"""
        self.open_column_config_sidebar()
        self.toggle_column("url")

        assert self.get_element("column-config-reset-btn").is_enabled()

    def test_hide_column_removes_table_header(self) -> None:
        """Unchecking a default-visible column removes its header from the table"""
        self.open_column_config_sidebar()
        self.toggle_column("application_status")

        assert "application_status" not in self.get_visible_table_columns()

    def test_hide_column_persists_to_db(self) -> None:
        """Hidden column list is saved to the user's preferences"""
        self.open_column_config_sidebar()
        self.toggle_column("application_status")

        saved = self.db_user.preferences.table_columns
        assert saved is not None, "table_columns preference was not saved"
        assert "job" in saved, "No 'job' key in table_columns preference"
        assert (
            "application_status" not in saved["job"]
        ), "'application_status' should be absent from the saved column list"

    def test_show_hidden_column_restores_table_header(self) -> None:
        """Re-checking a hidden column restores its header in the table"""
        self.open_column_config_sidebar()
        self.toggle_column("application_status")
        assert "application_status" not in self.get_visible_table_columns()

        self.toggle_column("application_status")
        assert "application_status" in self.get_visible_table_columns()

    def test_show_hidden_column_updates_db(self) -> None:
        """Re-enabling a hidden column adds it back to saved preferences"""
        self.open_column_config_sidebar()
        self.toggle_column("application_status")
        assert "application_status" not in self.db_user.preferences.table_columns["job"]

        self.toggle_column("application_status")
        assert "application_status" in self.db_user.preferences.table_columns["job"]

    def test_reset_to_defaults_restores_all_columns(self) -> None:
        """Reset to Defaults restores default columns and clears the DB preference"""
        self.open_column_config_sidebar()
        self.toggle_column("application_status")
        self.toggle_column("url")

        assert "application_status" not in self.get_visible_table_columns()
        assert "url" not in self.get_visible_table_columns()

        self.get_element("column-config-reset-btn").click()
        time.sleep(0.5)

        # Sidebar closes after reset — verify table directly
        headers = self.get_visible_table_columns()
        for key in DEFAULT_VISIBLE_JOB_COLUMNS:
            assert key in headers, f"Column '{key}' should be visible after reset"

        saved = self.db_user.preferences.table_columns
        assert saved is None or "job" not in saved, "table_columns preference should be cleared after reset"

    def test_hidden_columns_persist_across_reload(self) -> None:
        """Hidden columns are restored from preferences on page reload"""
        self.open_column_config_sidebar()
        self.toggle_column("application_status")
        self.toggle_column("url")

        self.login()  # reloads the page and re-fetches user preferences

        headers = self.get_visible_table_columns()
        assert "application_status" not in headers, "'application_status' should still be hidden after reload"
        assert "url" not in headers, "'url' should still be hidden after reload"
        assert "title" in headers, "'title' should still be visible after reload"

    def test_multiple_hidden_columns_all_saved(self) -> None:
        """Hiding multiple columns saves all of them to preferences"""
        self.open_column_config_sidebar()
        self.toggle_column("application_status")
        self.toggle_column("url")
        self.toggle_column("salary_min")

        saved = self.db_user.preferences.table_columns["job"]
        assert "application_status" not in saved
        assert "url" not in saved
        assert "salary_min" not in saved
        assert "title" in saved  # visible columns remain in the list

    def test_sort_direction_toggle(self) -> None:
        """Sort direction button toggles between Asc and Desc"""
        self.open_column_config_sidebar()
        initial_text = self.get_element("column-config-sort-direction-btn").text

        self.get_element("column-config-sort-direction-btn").click()
        time.sleep(0.3)

        new_text = self.get_element("column-config-sort-direction-btn").text
        assert initial_text != new_text, "Sort direction label should change after clicking"

    def test_sort_direction_persists_to_db(self) -> None:
        """Changing sort direction saves it to the user's table_sort preference"""
        self.open_column_config_sidebar()
        initial_text = self.get_element("column-config-sort-direction-btn").text

        self.get_element("column-config-sort-direction-btn").click()
        time.sleep(0.5)

        saved_sort = self.db_user.preferences.table_sort
        assert saved_sort is not None, "table_sort preference was not saved"
        assert "job" in saved_sort, "No 'job' key in table_sort preference"
        expected_direction = "desc" if "Asc" in initial_text else "asc"
        assert saved_sort["job"]["direction"] == expected_direction
