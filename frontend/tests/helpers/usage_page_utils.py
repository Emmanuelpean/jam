"""Utilities for the admin Provider Monitoring (Usage) dashboard modal."""

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from helpers.admin_page_utils import AdminPageUtils


class UsagePageUtils(AdminPageUtils):
    """Test class for the Provider Monitoring dashboard modal opened from /admin."""

    # ------------------------------------------------- ELEMENTS -------------------------------------------------

    @property
    def history_filters(self) -> WebElement:
        """The time filter in the modal body."""

        return self.get_element("history-filters", enabled=False)

    @property
    def usage_log_viewer(self) -> WebElement:
        """The log viewer section in the modal body."""

        return self.get_element("usage-log-viewer", enabled=False)

    @property
    def log_toggle(self) -> WebElement:
        """The control that expands/collapses the log viewer."""

        return self.get_element("log-toggle", selector=By.CLASS_NAME)

    @property
    def summary_cards(self) -> list[WebElement]:
        """The per-service spend/income/net-balance summary cards."""

        return self.get_elements("usage-summary-card", selector=By.CLASS_NAME)

    @property
    def service_status_icons(self) -> WebElement:
        """The status-control popover trigger in the modal header."""

        return self.get_element("service-status-icons", selector=By.CLASS_NAME, enabled=False)

    @property
    def run_now_button(self) -> WebElement:
        """The button in the status-control popover that triggers an immediate run."""

        return self.get_element("run-now-button")

    # -------------------------------------------------- HELPERS --------------------------------------------------

    def open(self) -> None:
        """Open the Provider Monitoring modal from the admin dashboard."""

        self.open_card("admin-card-usage")

    def open_status_control(self) -> None:
        """Open the status-control popover from the modal header."""

        self.service_status_icons.click()

    def wait_for_modal_text_containing(self, text: str) -> str:
        """Wait until the modal body's text contains the given substring, then return that text.

        Summary/chart data is fetched asynchronously once the time filter emits its default
        range, so the modal starts without it."""

        modal = self.admin_page_modal
        self.wait.until(lambda d: text in modal.text)
        return modal.text
