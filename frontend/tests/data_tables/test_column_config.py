"""Tests for the Column Configuration sidebar feature"""

from frontend_base_test import BaseTest

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
        company = self.user.create_company()
        for _ in range(3):
            self.user.create_job(company_id=company.id)
        self.login()

    def test_open_and_close_sidebar(self) -> None:
        """Gear button opens the sidebar; the close button dismisses it"""
        assert not self.column_config_utils.is_open()

        self.column_config_utils.open()
        assert self.column_config_utils.is_open()

        self.column_config_utils.close()
        assert not self.column_config_utils.is_open()

    def test_all_columns_listed_in_sidebar(self) -> None:
        """All registered job columns (visible and hidden) appear as toggles in the sidebar"""
        self.column_config_utils.open()
        for key in ALL_JOB_COLUMNS:
            assert self.check_element_exists(f"col-toggle-{key}"), f"Toggle not found for column key '{key}'"

    def test_default_visible_columns_checked(self) -> None:
        """Default visible columns are checked; non-default columns are unchecked"""
        self.column_config_utils.open()
        for key in DEFAULT_VISIBLE_JOB_COLUMNS:
            assert self.column_config_utils.column_toggle(
                key
            ).is_selected(), f"Expected column '{key}' to be checked by default"
        for key in set(ALL_JOB_COLUMNS) - set(DEFAULT_VISIBLE_JOB_COLUMNS):
            assert not self.column_config_utils.column_toggle(
                key
            ).is_selected(), f"Expected column '{key}' to be unchecked by default"

    def test_reset_button_enabled_after_hiding_column(self) -> None:
        """Reset button becomes enabled once at least one column is hidden"""
        self.column_config_utils.open()
        self.column_config_utils.toggle_column("url")

        assert self.column_config_utils.reset_button.is_enabled()

    def test_hide_column_removes_table_header(self) -> None:
        """Unchecking a default-visible column removes its header from the table"""
        self.column_config_utils.open()
        self.column_config_utils.toggle_column("application_status")

        assert "application_status" not in self.column_config_utils.visible_table_columns()

    def test_hide_column_persists_to_db(self) -> None:
        """Hidden column list is saved to the user's preferences"""
        self.column_config_utils.open()
        self.column_config_utils.toggle_column("application_status")

        saved = self.db_user.preferences.table_columns
        assert saved is not None, "table_columns preference was not saved"
        assert "job" in saved, "No 'job' key in table_columns preference"
        assert (
            "application_status" not in saved["job"]
        ), "'application_status' should be absent from the saved column list"

    def test_show_hidden_column_restores_table_header(self) -> None:
        """Re-checking a hidden column restores its header in the table"""
        self.column_config_utils.open()
        self.column_config_utils.toggle_column("application_status")
        assert "application_status" not in self.column_config_utils.visible_table_columns()

        self.column_config_utils.toggle_column("application_status")
        assert "application_status" in self.column_config_utils.visible_table_columns()

    def test_show_hidden_column_updates_db(self) -> None:
        """Re-enabling a hidden column adds it back to saved preferences"""
        self.column_config_utils.open()
        self.column_config_utils.toggle_column("application_status")
        assert "application_status" not in self.db_user.preferences.table_columns["job"]

        self.column_config_utils.toggle_column("application_status")
        assert "application_status" in self.db_user.preferences.table_columns["job"]

    def test_reset_to_defaults_restores_all_columns(self) -> None:
        """Reset to Defaults restores default columns and clears the DB preference"""
        self.column_config_utils.open()
        self.column_config_utils.toggle_column("application_status")
        self.column_config_utils.toggle_column("url")

        assert "application_status" not in self.column_config_utils.visible_table_columns()
        assert "url" not in self.column_config_utils.visible_table_columns()

        self.column_config_utils.reset_to_defaults()

        # Sidebar closes after reset — verify table directly
        headers = self.column_config_utils.visible_table_columns()
        for key in DEFAULT_VISIBLE_JOB_COLUMNS:
            assert key in headers, f"Column '{key}' should be visible after reset"

        saved = self.db_user.preferences.table_columns
        assert saved is None or "job" not in saved, "table_columns preference should be cleared after reset"

    def test_hidden_columns_persist_across_reload(self) -> None:
        """Hidden columns are restored from preferences on page reload"""
        self.column_config_utils.open()
        self.column_config_utils.toggle_column("application_status")
        self.column_config_utils.toggle_column("url")

        self.login()  # reloads the page and re-fetches user preferences

        headers = self.column_config_utils.visible_table_columns()
        assert "application_status" not in headers, "'application_status' should still be hidden after reload"
        assert "url" not in headers, "'url' should still be hidden after reload"
        assert "title" in headers, "'title' should still be visible after reload"

    def test_multiple_hidden_columns_all_saved(self) -> None:
        """Hiding multiple columns saves all of them to preferences"""
        self.column_config_utils.open()
        self.column_config_utils.toggle_column("application_status")
        self.column_config_utils.toggle_column("url")
        self.column_config_utils.toggle_column("salary_min")

        saved = self.db_user.preferences.table_columns["job"]
        assert "application_status" not in saved
        assert "url" not in saved
        assert "salary_min" not in saved
        assert "title" in saved  # visible columns remain in the list

    def test_sort_direction_toggle(self) -> None:
        """Sort direction button toggles between Asc and Desc"""
        self.column_config_utils.open()
        initial_text = self.column_config_utils.sort_direction_button.text

        self.column_config_utils.toggle_sort_direction()

        new_text = self.column_config_utils.sort_direction_button.text
        assert initial_text != new_text, "Sort direction label should change after clicking"

    def test_sort_direction_persists_to_db(self) -> None:
        """Changing sort direction saves it to the user's table_sort preference"""
        self.column_config_utils.open()
        initial_text = self.column_config_utils.sort_direction_button.text

        self.column_config_utils.toggle_sort_direction()

        saved_sort = self.db_user.preferences.table_sort
        assert saved_sort is not None, "table_sort preference was not saved"
        assert "job" in saved_sort, "No 'job' key in table_sort preference"
        expected_direction = "desc" if "Asc" in initial_text else "asc"
        assert saved_sort["job"]["direction"] == expected_direction
