"""Tests for the number of entries a data table shows per page"""

import time

from frontend_base_test import BaseTest

TALL_WINDOW = (1960, 2400)

TABLE_METRICS_SCRIPT = """
const container = document.getElementById('job-data-table');
const header = container.querySelector('thead tr');
const rows = Array.from(container.querySelectorAll('tbody tr'));
return {
    clientHeight: container.clientHeight,
    scrollHeight: container.scrollHeight,
    headerHeight: header.getBoundingClientRect().height,
    rowHeight: rows[0].getBoundingClientRect().height,
    rowsHeight: rows.reduce((total, row) => total + row.getBoundingClientRect().height, 0),
};
"""


class TestTablePageSize(BaseTest):
    """Tests for the page size selector and the fit-to-screen default on the Jobs table"""

    page_url = "jobs"

    def setup_function(self, request) -> None:
        company = self.user.create_company()
        for _ in range(80):
            self.user.create_job(company_id=company.id)
        self.login()

    def test_fit_to_screen_is_the_default(self) -> None:
        """A table with no stored page size fits its rows to the height available"""

        assert self.job_table_utils.page_item_select_value == "Fit to Screen"
        assert self.db_user.preferences.table_page_size is None

    def test_fit_to_screen_fills_the_available_height(self) -> None:
        """Fitted rows leave neither an empty band below the table nor anything to scroll to"""

        self.driver.set_window_size(*TALL_WINDOW)
        time.sleep(1)

        metrics = self.driver.execute_script(TABLE_METRICS_SCRIPT)
        row_height = metrics["rowHeight"]
        empty_space = metrics["clientHeight"] - metrics["headerHeight"] - metrics["rowsHeight"]
        overflow = metrics["scrollHeight"] - metrics["clientHeight"]

        assert self.job_table_utils.get_row_count() > 20, "A tall window should fit more than the default 20 rows"
        assert empty_space < row_height, f"{empty_space}px of empty space left below the last row"
        assert overflow < row_height, f"Rows overflow the visible area by {overflow}px"

    def test_short_window_keeps_the_default_page_size(self) -> None:
        """Fitting never drops below the table default, so short viewports scroll instead"""

        self.driver.set_window_size(1960, 600)
        time.sleep(1)

        assert self.job_table_utils.get_row_count() == 20

    def test_chosen_page_size_is_stored_and_restored(self) -> None:
        """Picking a size stores it against the table and survives a reload"""

        self.job_table_utils.set_page_item_select("30")

        assert self.job_table_utils.get_row_count() == 30
        assert self.db_user.preferences.table_page_size == {"job": 30}

        self.refresh()

        assert self.job_table_utils.page_item_select_value == "Show 30 Entries"
        assert self.job_table_utils.get_row_count() == 30

    def test_fit_to_screen_clears_the_stored_page_size(self) -> None:
        """Switching back to Fit to Screen removes the stored size"""

        self.job_table_utils.set_page_item_select("30")
        assert self.db_user.preferences.table_page_size == {"job": 30}

        self.job_table_utils.set_page_item_select("fit")

        assert self.job_table_utils.page_item_select_value == "Fit to Screen"
        assert self.db_user.preferences.table_page_size is None
