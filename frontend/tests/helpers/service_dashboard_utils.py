"""Utilities for the admin service dashboard modals (Job Scraping and Job Rating)."""

from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from helpers.admin_page_utils import AdminPageUtils


class ServiceDashboardUtils(AdminPageUtils):
    """Test class for the Job Scraping / Job Rating dashboard modals opened from /admin."""

    # ------------------------------------------------- ELEMENTS -------------------------------------------------

    @property
    def service_status_icons(self) -> WebElement:
        """The status-control popover trigger in the modal header."""

        return self.get_element("service-status-icons", selector=By.CLASS_NAME, enabled=False)

    @property
    def log_toggle(self) -> WebElement:
        """The control that expands/collapses the log viewer."""

        return self.get_element("log-toggle", selector=By.CLASS_NAME)

    @property
    def log_viewer_wrapper(self) -> WebElement:
        """The log viewer's wrapper; its `open` class reflects expanded/collapsed state."""

        return self.get_element("log-viewer-wrapper", selector=By.CLASS_NAME, enabled=False)

    @property
    def error_view_toggle(self) -> WebElement:
        """The checkbox toggling between current-run and previous-run errors."""

        return self.get_element("errorViewToggle")

    @property
    def latest_run_progress(self) -> WebElement:
        """The Latest Run Progress card in the modal body."""

        return self.get_element("latest-run-progress", enabled=False)

    @property
    def error_summary_card(self) -> WebElement:
        """The Error Summary card in the modal body."""

        return self.get_element("error-summary-card", enabled=False)

    @property
    def history_filters(self) -> WebElement:
        """The run-history time filter in the modal body."""

        return self.get_element("history-filters", enabled=False)

    @property
    def run_now_button(self) -> WebElement:
        """The button in the status-control popover that triggers an immediate run."""

        return self.get_element("run-now-button")

    @property
    def period_hours_field(self) -> WebElement:
        """The run-period config field in the status-control popover."""

        return self.get_element("period_hours", enabled=False)

    @property
    def min_timedelta_days_field(self) -> WebElement:
        """The minimum-age config field, scraping dashboard only."""

        return self.get_element("min_timedelta_days", enabled=False)

    @property
    def max_timedelta_days_field(self) -> WebElement:
        """The maximum-age config field, scraping dashboard only."""

        return self.get_element("max_timedelta_days", enabled=False)

    # -------------------------------------------------- HELPERS --------------------------------------------------

    def open_scraping(self) -> None:
        """Open the Job Scraping dashboard modal."""

        self.open_card("admin-card-job-scraping")

    def open_rating(self) -> None:
        """Open the Job Rating dashboard modal."""

        self.open_card("admin-card-job-rating")

    def open_status_control(self) -> None:
        """Open the status-control popover from the modal header."""

        self.service_status_icons.click()

    def expand_log_viewer(self) -> None:
        """Click the log viewer toggle."""

        self.log_toggle.click()

    def toggle_error_view(self) -> None:
        """Click the error view checkbox."""

        self.error_view_toggle.click()

    def assert_log_viewer_toggles(self) -> None:
        """The log viewer is collapsed by default and expands on click.

        The viewer is always in the DOM; the wrapper's `open` class reflects whether
        it is expanded (it collapses via a CSS grid row, not by unmounting)."""

        assert "open" not in self.log_viewer_wrapper.get_attribute("class")
        self.expand_log_viewer()
        self.wait.until(lambda d: "open" in d.find_element(By.CLASS_NAME, "log-viewer-wrapper").get_attribute("class"))

    def assert_error_view_toggles(self) -> None:
        """The error view toggle defaults unchecked and flips on click."""

        checkbox = self.error_view_toggle
        assert not checkbox.is_selected()
        self.toggle_error_view()
        assert checkbox.is_selected()
        self.toggle_error_view()
        assert not checkbox.is_selected()

    def assert_no_min_timedelta_days_field(self) -> None:
        """Assert the minimum-age config field is absent (rating dashboard has no per-job age filter)."""

        assert not self.check_element_exists(
            "min_timedelta_days"
        ), "min_timedelta_days should not appear on the rating dashboard"

    def wait_for_error_summary_containing(self, *messages: str) -> str:
        """Wait until the Error Summary card's text contains every given message, then return that text.

        The card can flip back to a "Loading..." state during refresh polls, so reading the text in a
        separate call after the wait is racy; this captures the snapshot that satisfied the wait."""

        captured = {}

        def _errors_loaded(d) -> bool:
            try:
                text = d.find_element(By.ID, "error-summary-card").text
            except StaleElementReferenceException:
                return False
            if all(message in text for message in messages):
                captured["text"] = text
                return True
            return False

        self.wait.until(_errors_loaded)
        return captured["text"]
