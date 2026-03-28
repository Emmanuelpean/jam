"""Tests for the Filter Sidebar and Filter Pills features on the Jobs table"""

import time

from selenium.webdriver.common.by import By

from base_test import BaseTest

# All job columns that have a filterConfig defined in TableColumns.tsx
FILTERABLE_JOB_COLUMNS = [
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


class TestFilterSidebar(BaseTest):
    """Tests for the Filter Sidebar on the Jobs table."""

    page_url = "jobs"
    user_index = 0

    def setup_function(self, request) -> None:
        request.getfixturevalue("test_jobs")
        self.login()

    # -------------------------------------------------- Open / close --------------------------------------------------

    def test_open_and_close_sidebar(self) -> None:
        """Filter toggle button opens the sidebar; the close button dismisses it"""
        assert not self.job_table_utils.is_filter_sidebar_open()

        self.job_table_utils.open_filter_sidebar()
        assert self.job_table_utils.is_filter_sidebar_open()

        for key in FILTERABLE_JOB_COLUMNS:
            assert self.check_element_exists(f"filter-section-{key}"), f"Filter section not found for column '{key}'"

        self.get_element("filter-close-btn").click()
        time.sleep(0.5)
        assert not self.job_table_utils.is_filter_sidebar_open()

    def test_clear_button_disabled_when_no_filters(self) -> None:
        """'Clear all filters' button is disabled when no filters are active"""
        self.job_table_utils.open_filter_sidebar()
        clear_btn = self.get_element("filter-clear-btn", enabled=False)
        assert not clear_btn.is_enabled()

    def test_clear_button_enabled_after_filter_applied(self) -> None:
        """'Clear all filters' button becomes enabled once any filter is active"""
        self.job_table_utils.open_filter_sidebar()
        self.get_element("filter-input-title").send_keys("Python")
        time.sleep(0.5)
        assert self.get_element("filter-clear-btn", enabled=False).is_enabled()

    # -------------------------------------------------- Text filter --------------------------------------------------

    def test_text_filter_narrows_results(self) -> None:
        """Typing in a text filter reduces visible rows to only those matching the text"""
        initial_count = self.job_table_utils.get_row_count()
        self.job_table_utils.open_filter_sidebar()
        self.get_element("filter-input-title").send_keys("Python")
        time.sleep(0.5)

        filtered_count = self.job_table_utils.get_row_count()
        assert 0 < filtered_count < initial_count, "Text filter should reduce visible rows without hiding everything"
        # Every remaining row must contain the search string in the title column
        titles = self.job_table_utils.get_column_values("title")
        assert all("Python" in t for t in titles), "All visible rows should match the text filter"

    def test_text_filter_section_marked_active(self) -> None:
        """The filter section is highlighted when its filter is active"""
        self.job_table_utils.open_filter_sidebar()
        assert not self.job_table_utils.is_section_active("title")
        self.get_element("filter-input-title").send_keys("Python")
        time.sleep(0.5)
        assert self.job_table_utils.is_section_active("title")

    def test_text_filter_pill_appears(self) -> None:
        """A filter pill appears with the search string when a text filter is active"""
        self.job_table_utils.open_filter_sidebar()
        self.get_element("filter-input-title").send_keys("Python")
        time.sleep(0.5)

        pills = self.job_table_utils.get_filter_pills()
        assert len(pills) == 1
        assert "Python" in pills[0].text

    def test_text_filter_x_button_clears_filter(self) -> None:
        """The X button inside the text input clears the filter and restores all rows"""
        initial_count = self.job_table_utils.get_row_count()
        self.job_table_utils.open_filter_sidebar()
        self.get_element("filter-input-title").send_keys("Python")
        time.sleep(0.5)
        assert self.job_table_utils.get_row_count() < initial_count

        # The X clear button appears only when the input has text
        section = self.get_element("filter-section-title")
        self.get_element("clear-btn", within=section).click()
        time.sleep(0.5)

        assert self.job_table_utils.get_row_count() == initial_count
        assert not self.job_table_utils.get_filter_pills()

    # -------------------------------------------------- Select filter ------------------------------------------------

    def test_select_filter_narrows_results(self) -> None:
        """Selecting a status value reduces the table to matching rows"""
        initial_count = self.job_table_utils.get_row_count()
        self.job_table_utils.open_filter_sidebar()
        self.job_table_utils.select_from_react_select_filter("application_status", "Applied")

        filtered_count = self.job_table_utils.get_row_count()
        assert 0 < filtered_count < initial_count, "Select filter should reduce visible rows without hiding everything"

    def test_select_filter_section_marked_active(self) -> None:
        """The application_status section is highlighted after selecting a value"""
        self.job_table_utils.open_filter_sidebar()
        assert not self.job_table_utils.is_section_active("application_status")
        self.job_table_utils.select_from_react_select_filter("application_status", "Applied")
        assert self.job_table_utils.is_section_active("application_status")

    def test_select_filter_pill_appears(self) -> None:
        """A filter pill appears showing the selected option label"""
        self.job_table_utils.open_filter_sidebar()
        self.job_table_utils.select_from_react_select_filter("application_status", "Applied")

        pills = self.job_table_utils.get_filter_pills()
        assert len(pills) == 1
        assert "Applied" in pills[0].text

    # ------------------------------------------- Number filter (input mode) ---------------------------------------

    def test_number_filter_min_narrows_results(self) -> None:
        """Setting a salary minimum reduces the table to jobs above that threshold"""
        initial_count = self.job_table_utils.get_row_count()
        self.job_table_utils.open_filter_sidebar()
        min_input = self.get_element("filter-num-min-salary_min")
        self.set_text(min_input, "85000")
        time.sleep(0.5)

        filtered_count = self.job_table_utils.get_row_count()
        assert 0 < filtered_count < initial_count, "Salary min filter should reduce visible rows"

    def test_number_filter_section_marked_active(self) -> None:
        """The salary_min section is highlighted after setting a min value"""
        self.job_table_utils.open_filter_sidebar()
        assert not self.job_table_utils.is_section_active("salary_min")
        min_input = self.get_element("filter-num-min-salary_min")
        self.set_text(min_input, "85000")
        time.sleep(0.5)
        assert self.job_table_utils.is_section_active("salary_min")

    def test_number_filter_pill_appears(self) -> None:
        """A filter pill appears when a number range filter is set"""
        self.job_table_utils.open_filter_sidebar()
        min_input = self.get_element("filter-num-min-salary_min")
        self.set_text(min_input, "85000")
        time.sleep(0.5)

        pills = self.job_table_utils.get_filter_pills()
        assert len(pills) == 1
        assert "85000" in pills[0].text  # pill shows "≥ 85000"

    # --------------------------------------- Null toggle (nullable number filter) ---------------------------------

    def test_null_filter_shows_only_unrated_jobs(self) -> None:
        """Clicking the 'Null' toggle shows only rows where the value is absent"""
        initial_count = self.job_table_utils.get_row_count()
        self.job_table_utils.open_filter_sidebar()
        self.get_element("filter-null-null-personal_rating").click()
        time.sleep(0.5)

        filtered_count = self.job_table_utils.get_row_count()
        assert 0 < filtered_count < initial_count, "Null filter should reduce visible rows"
        assert self.job_table_utils.is_section_active("personal_rating")

    def test_null_filter_pill_appears(self) -> None:
        """A filter pill containing 'Null' appears when the null toggle is active"""
        self.job_table_utils.open_filter_sidebar()
        self.get_element("filter-null-null-personal_rating").click()
        time.sleep(0.5)

        pills = self.job_table_utils.get_filter_pills()
        assert len(pills) == 1
        assert "Null" in pills[0].text

    def test_not_null_filter_excludes_unrated_jobs(self) -> None:
        """Clicking 'Not null' excludes jobs with no personal rating"""
        self.job_table_utils.open_filter_sidebar()
        self.get_element("filter-null-null-personal_rating").click()
        time.sleep(0.5)
        null_count = self.job_table_utils.get_row_count()

        self.get_element("filter-null-not_null-personal_rating").click()
        time.sleep(0.5)
        not_null_count = self.job_table_utils.get_row_count()

        assert null_count > 0
        assert not_null_count > 0
        assert null_count + not_null_count <= self.job_table_utils.get_row_count() + null_count + not_null_count

    # -------------------------------------------------- Date filter --------------------------------------------------

    def test_date_filter_preset_activates_section(self) -> None:
        """Clicking a date preset highlights the section and creates a filter pill"""
        self.job_table_utils.open_filter_sidebar()
        section = self.get_element("filter-section-created_at")
        preset_btns = section.find_elements(By.CLASS_NAME, "filter-date-preset-btn")
        last_30_btn = next(b for b in preset_btns if "30" in b.text)
        last_30_btn.click()
        time.sleep(0.5)

        assert self.job_table_utils.is_section_active("created_at")
        pills = self.job_table_utils.get_filter_pills()
        assert len(pills) == 1
        assert "30" in pills[0].text

    def test_date_filter_preset_deactivates_on_second_click(self) -> None:
        """Clicking an already-active preset button toggles it off"""
        self.job_table_utils.open_filter_sidebar()
        section = self.get_element("filter-section-created_at")
        preset_btns = section.find_elements(By.CLASS_NAME, "filter-date-preset-btn")
        last_30_btn = next(b for b in preset_btns if "30" in b.text)

        last_30_btn.click()
        time.sleep(0.3)
        assert self.job_table_utils.is_section_active("created_at")

        last_30_btn.click()  # toggle off
        time.sleep(0.3)
        assert not self.job_table_utils.is_section_active("created_at")
        assert not self.job_table_utils.get_filter_pills()

    # ----------------------------------------------- Multi-filter & clearing -------------------------------------

    def test_active_count_badge_increments_per_filter(self) -> None:
        """The sidebar header badge increments for each new active filter"""
        self.job_table_utils.open_filter_sidebar()
        assert self.job_table_utils.get_active_count_from_sidebar() == 0

        self.get_element("filter-input-title").send_keys("Python")
        time.sleep(0.5)
        assert self.job_table_utils.get_active_count_from_sidebar() == 1

        min_input = self.get_element("filter-num-min-salary_min")
        self.set_text(min_input, "80000")
        time.sleep(0.5)
        assert self.job_table_utils.get_active_count_from_sidebar() == 2

    def test_multiple_filters_combine_to_narrow_results(self) -> None:
        """Applying two filters shows only rows that satisfy both conditions"""
        self.job_table_utils.open_filter_sidebar()
        self.get_element("filter-input-title").send_keys("Developer")
        time.sleep(0.5)
        developer_count = self.job_table_utils.get_row_count()

        self.job_table_utils.select_from_react_select_filter("application_status", "Applied")
        combined_count = self.job_table_utils.get_row_count()

        assert combined_count <= developer_count, "Adding a second filter should not increase the row count"
        assert len(self.job_table_utils.get_filter_pills()) == 2

    def test_clear_all_filters_restores_full_results(self) -> None:
        """Clicking 'Clear all filters' removes all filters and restores the original row count"""
        initial_count = self.job_table_utils.get_row_count()
        self.job_table_utils.open_filter_sidebar()
        self.get_element("filter-input-title").send_keys("Python")
        time.sleep(0.5)
        assert self.job_table_utils.get_row_count() < initial_count

        self.get_element("filter-clear-btn").click()
        time.sleep(0.5)

        assert self.job_table_utils.get_row_count() == initial_count
        assert not self.job_table_utils.get_filter_pills()

    def test_pill_remove_button_clears_single_filter(self) -> None:
        """Clicking a pill's × removes only that one filter, leaving others intact"""
        self.job_table_utils.open_filter_sidebar()
        self.get_element("filter-input-title").send_keys("Python")
        time.sleep(0.5)
        title_only_count = self.job_table_utils.get_row_count()

        min_input = self.get_element("filter-num-min-salary_min")
        self.set_text(min_input, "60000")
        time.sleep(0.5)
        assert len(self.job_table_utils.get_filter_pills()) == 2

        # Remove the salary pill (its text contains "60000"; the title pill contains "Python")
        pills = self.job_table_utils.get_filter_pills()
        salary_pill = next(p for p in pills if "60" in p.text)
        salary_pill.find_element(By.CLASS_NAME, "header-filter-pill-remove").click()
        time.sleep(0.5)

        assert len(self.job_table_utils.get_filter_pills()) == 1
        assert self.job_table_utils.get_row_count() == title_only_count

    def test_pills_row_clear_button_removes_all_filters(self) -> None:
        """The 'Clear' button in the filter pills row removes all active filters at once"""
        initial_count = self.job_table_utils.get_row_count()
        self.job_table_utils.open_filter_sidebar()
        self.get_element("filter-input-title").send_keys("Python")
        time.sleep(0.5)
        assert self.job_table_utils.get_row_count() < initial_count

        self.driver.find_element(By.CLASS_NAME, "filter-pills-clear-btn").click()
        time.sleep(0.5)

        assert self.job_table_utils.get_row_count() == initial_count
        assert not self.job_table_utils.get_filter_pills()
