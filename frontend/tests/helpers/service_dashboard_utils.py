"""Utilities for the admin service dashboard modals (Job Scraping and Job Rating)."""

from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.action_chains import ActionChains
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
    def run_history_card(self) -> WebElement:
        """The Run History card (holds the run-history line charts)."""

        return self.get_element("run-history-card", enabled=False)

    @property
    def selected_run_filter(self) -> WebElement:
        """The chip shown when the errors are filtered to a single run (clicking it clears the filter)."""

        return self.get_element("selected-run-filter")

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

    def assert_log_viewer_toggles(self) -> None:
        """The log viewer is collapsed by default and expands on click.

        The viewer is always in the DOM; the wrapper's `open` class reflects whether
        it is expanded (it collapses via a CSS grid row, not by unmounting)."""

        assert "open" not in self.log_viewer_wrapper.get_attribute("class")
        self.expand_log_viewer()
        self.wait.until(lambda d: "open" in d.find_element(By.CLASS_NAME, "log-viewer-wrapper").get_attribute("class"))

    def assert_no_min_timedelta_days_field(self) -> None:
        """Assert the minimum-age config field is absent (rating dashboard has no per-job age filter)."""

        assert not self.check_element_exists(
            "min_timedelta_days"
        ), "min_timedelta_days should not appear on the rating dashboard"

    def select_run_from_chart(self, newest: bool = True) -> None:
        """Click a data point in the run-history chart to filter errors to that run.

        Clicks the rightmost (newest run) or leftmost (oldest run) data point in the first line chart.
        Recharts derives the clicked point from the real mouse position, and Selenium's move_to_element
        is unreliable on SVG nodes, so the offset from the (reliable) wrapper element to the dot's centre
        is measured via getBoundingClientRect and used for a real ActionChains click.
        :param newest: click the most recent run's point when True, else the oldest."""

        wrapper = self.run_history_card.find_elements(By.CLASS_NAME, "recharts-wrapper")[0]
        dots = wrapper.find_elements(By.CSS_SELECTOR, "circle.recharts-dot")
        assert dots, "expected run-history chart to render data points"
        target = (max if newest else min)(dots, key=lambda dot: float(dot.get_attribute("cx")))
        offset_x, offset_y = self.driver.execute_script(
            """
            const dot = arguments[0].getBoundingClientRect(), wrap = arguments[1].getBoundingClientRect();
            return [(dot.left + dot.width / 2) - (wrap.left + wrap.width / 2),
                    (dot.top + dot.height / 2) - (wrap.top + wrap.height / 2)];
            """,
            target,
            wrapper,
        )
        ActionChains(self.driver).move_to_element_with_offset(wrapper, int(offset_x), int(offset_y)).click().perform()

    def clear_run_filter(self) -> None:
        """Clear the single-run error filter via its chip."""

        self.selected_run_filter.click()

    def error_group(self, message: str) -> WebElement:
        """The grouped-error alert whose message text contains `message`."""

        for group in self.error_summary_card.find_elements(By.CSS_SELECTOR, ".error-list .alert"):
            if message in group.find_element(By.CLASS_NAME, "grouped-error-message").text:
                return group
        raise AssertionError(f"No error group containing {message!r}")

    def expand_error_group(self, message: str) -> int:
        """Expand the group containing `message` and return its number of occurrence rows."""

        self.error_group(message).find_element(By.CLASS_NAME, "grouped-error-message").click()
        occurrences = self.wait.until(
            lambda d: self.error_group(message).find_element(By.CLASS_NAME, "grouped-error-occurrences")
        )
        return len(occurrences.find_elements(By.CLASS_NAME, "grouped-error-occurrence"))

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

    def wait_for_error_summary_filtered(self, *, contains: str, excludes: str) -> str:
        """Wait until the Error Summary card contains `contains` but no longer contains `excludes`.

        Used after selecting a run: the kept run's error stays while the other run's error drops out."""

        captured = {}

        def _filtered(d) -> bool:
            try:
                text = d.find_element(By.ID, "error-summary-card").text
            except StaleElementReferenceException:
                return False
            if contains in text and excludes not in text:
                captured["text"] = text
                return True
            return False

        self.wait.until(_filtered)
        return captured["text"]
