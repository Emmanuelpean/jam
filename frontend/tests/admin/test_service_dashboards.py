"""Tests for the admin service dashboards (Job Scraping and Job Rating).

The service dashboards are now opened as modals from the admin dashboard (/admin):
1. Clicking a service card opens its dashboard in a large modal.
2. The modal header holds the service status icons; clicking them opens a popover
   with the config fields and the start/stop button.
3. The modal body holds the dashboard cards (latest run, run history, errors).

These tests cover:
1. Opening each service dashboard modal
2. Service status control popover with config fields and start button
3. Log viewer expand/collapse
4. Latest run progress and error summary cards render
5. Proper display of critical, service, scraping and rating errors
"""

from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from base_test import BaseTest


class ServiceDashboardBase(BaseTest):
    """Shared helpers for service dashboard tests."""

    user_index = 1  # admin user required for the admin dashboard
    page_url = "admin"

    def _open_modal(self, card_id: str) -> None:
        """Open a service dashboard modal by clicking its admin card."""

        # Click the title (top of the card) to avoid the sparkline hover overlay.
        card = self.get_element(card_id, enabled=False)
        card.find_element(By.CLASS_NAME, "card-title").click()
        self.get_element("admin-page-modal", enabled=False)

    def _open_scraping(self) -> None:
        self._open_modal("admin-card-job-scraping")

    def _open_rating(self) -> None:
        self._open_modal("admin-card-job-rating")

    def _open_status_control(self) -> None:
        """Open the status-control popover from the modal header."""

        self.get_element("service-status-icons", selector=By.CLASS_NAME).click()

    def _expand_log_viewer(self) -> None:
        self.get_element("log-toggle", selector=By.CLASS_NAME).click()

    def _toggle_error_view(self) -> None:
        self.get_element("errorViewToggle").click()


class TestJobScrapingDashboard(ServiceDashboardBase):
    """Tests for the Job Scraping dashboard modal."""

    def setup_function(self, request) -> None:
        request.getfixturevalue("test_job_scraping_service_logs")
        self.login()

    def test_page_renders(self) -> None:
        """All static elements render correctly on the Job Scraping dashboard."""

        self._open_scraping()

        # Data cards in the modal body
        assert self.get_element("latest-run-progress", enabled=False).is_displayed()
        assert self.get_element("error-summary-card", enabled=False).is_displayed()
        assert self.get_element("history-filters", enabled=False).is_displayed()

        # Status control in the modal header: runner + service icons
        icons = self.get_element("service-status-icons", selector=By.CLASS_NAME, enabled=False)
        assert len(icons.find_elements(By.CLASS_NAME, "service-status-icon")) >= 2

        # Opening the status control reveals the config fields and the start button
        self._open_status_control()
        self.get_element("confirm-start-button")
        assert self.get_element("period_hours", selector=By.NAME, enabled=False).is_displayed()
        assert self.get_element("timedelta_days", selector=By.NAME, enabled=False).is_displayed()

    def test_interactive_elements(self) -> None:
        """Log viewer and error view toggle work correctly."""

        self._open_scraping()

        # Log viewer: collapsed by default, expands on click
        assert not self.check_element_exists("log-viewer", selector=By.CLASS_NAME)
        self._expand_log_viewer()
        assert self.get_element("log-viewer", selector=By.CLASS_NAME, enabled=False).is_displayed()

        # Error view toggle: defaults unchecked, toggles on click
        checkbox = self.get_element("errorViewToggle")
        assert not checkbox.is_selected()
        self._toggle_error_view()
        assert checkbox.is_selected()
        self._toggle_error_view()
        assert not checkbox.is_selected()


class TestJobRatingDashboard(ServiceDashboardBase):
    """Tests for the Job Rating dashboard modal."""

    def setup_function(self, request) -> None:
        request.getfixturevalue("test_job_rating_service_logs")
        self.login()

    def test_page_renders(self) -> None:
        """All static elements render correctly on the Job Rating dashboard."""

        self._open_rating()

        # Data cards in the modal body
        assert self.get_element("latest-run-progress", enabled=False).is_displayed()
        assert self.get_element("error-summary-card", enabled=False).is_displayed()
        assert self.get_element("history-filters", enabled=False).is_displayed()

        # Status control: only period_hours (no timedelta_days for rating)
        self._open_status_control()
        self.get_element("confirm-start-button")
        assert self.get_element("period_hours", selector=By.NAME, enabled=False).is_displayed()
        assert not self.check_element_exists(
            "timedelta_days", selector=By.NAME
        ), "timedelta_days should not appear on the rating dashboard"

    def test_interactive_elements(self) -> None:
        """Log viewer and error view toggle work correctly on the rating modal."""

        self._open_rating()

        # Log viewer: collapsed by default, expands on click
        assert not self.check_element_exists("log-viewer", selector=By.CLASS_NAME)
        self._expand_log_viewer()
        assert self.get_element("log-viewer", selector=By.CLASS_NAME, enabled=False).is_displayed()

        # Error view toggle: defaults unchecked, toggles on click
        checkbox = self.get_element("errorViewToggle")
        assert not checkbox.is_selected()
        self._toggle_error_view()
        assert checkbox.is_selected()
        self._toggle_error_view()
        assert not checkbox.is_selected()


class TestJobScrapingDashboardErrors(ServiceDashboardBase):
    """Tests that critical, service and scraping errors display correctly."""

    CRITICAL_ERROR = "Critical: database connection pool exhausted"
    SERVICE_ERROR = "Failed to connect to LinkedIn API: Connection timed out"
    SCRAPING_ERROR = "Page not found - job posting has been removed"

    def setup_function(self, request) -> None:
        # Service log with today's date so it appears in the default "last 1 week" date range
        service_log = self._make_service_log(
            run_duration=30.0,
            is_success=False,
            error_message=self.CRITICAL_ERROR,
        )

        # Service error linked to this log (appears in "Service Errors" column)
        self._make_service_error(service_log=service_log, message=self.SERVICE_ERROR)

        # Scraped job with a known error (appears in "Scraping Errors" column)
        scraped_job = self._make_scraped_job(
            service_log=service_log,
            is_failed=True,
            scrape_error=[{"datetime": "2026-03-16T10:00:00+00:00", "error": self.SCRAPING_ERROR}],
            url="https://test.com",
        )

        # Platform stat referencing the failed job so the hook picks it up
        self._make_platform_stat(service_log=service_log, job_scrape_failed_ids=[scraped_job.id])
        self.login()

    def test_errors_display(self) -> None:
        """Critical, service and scraping errors all appear in the Error Summary card."""

        self._open_scraping()

        # Wait until all errors are present together, capturing that snapshot.
        # The card can flip back to a "Loading..." state during refresh polls, so
        # reading the text in a separate call after the wait is racy.
        captured = {}

        def _errors_loaded(d: WebElement):
            try:
                text = d.find_element(By.ID, "error-summary-card").text
            except StaleElementReferenceException:
                return False
            if self.CRITICAL_ERROR in text and self.SERVICE_ERROR in text and self.SCRAPING_ERROR in text:
                captured["text"] = text
                return True
            return False

        self.wait.until(_errors_loaded)
        error_text = captured["text"]

        # Critical Errors column: service logs with error_message within the date range
        assert self.CRITICAL_ERROR in error_text

        # Service Errors column: service_errors linked to the latest log
        assert self.SERVICE_ERROR in error_text

        # Scraping Errors column: scraped job errors fetched via platform_stats
        assert self.SCRAPING_ERROR in error_text


class TestJobRatingDashboardErrors(ServiceDashboardBase):
    """Tests that critical and rating errors display correctly on the rating modal."""

    CRITICAL_ERROR = "Critical: rating service crashed unexpectedly"
    RATING_ERROR = "Failed to rate job: API timeout after 30 seconds"

    def setup_function(self, request) -> None:
        request.getfixturevalue("test_user_qualifications")

        # Scraping service log needed as FK for the scraped job
        scraping_log = self._make_service_log(run_duration=10.0)

        # Scraped job needed as FK for the job rating
        scraped_job = self._make_scraped_job(service_log=scraping_log, url="https://test.com")

        # Job rating that failed (the error appears in "Job Rating Errors" column)
        rating = self._create_job_rating(
            scraped_job,
            is_success=False,
            error=self.RATING_ERROR,
            llm_model="claude-sonnet-4-6",
        )

        # Rating service log with today's date: error_message for Critical Errors,
        # job_failed_ids referencing the failed rating for the Rating Errors column
        self._make_rating_service_log(
            run_duration=20.0,
            is_success=False,
            error_message=self.CRITICAL_ERROR,
            job_failed_ids=[rating.id],
        )
        self.login()

    def test_errors_display(self) -> None:
        """Critical and rating errors both appear in the Error Summary card."""

        self._open_rating()

        # Wait until both errors are present together, capturing that snapshot.
        # The card can flip back to a "Loading..." state during refresh polls, so
        # reading the text in a separate call after the wait is racy.
        captured = {}

        def _errors_loaded(d):
            try:
                text = d.find_element(By.ID, "error-summary-card").text
            except StaleElementReferenceException:
                return False
            if self.CRITICAL_ERROR in text and self.RATING_ERROR in text:
                captured["text"] = text
                return True
            return False

        self.wait.until(_errors_loaded)
        error_text = captured["text"]

        # Critical Errors column: rating service logs with error_message in the date range
        assert self.CRITICAL_ERROR in error_text

        # Job Rating Errors column: failed job ratings fetched via job_failed_ids
        assert self.RATING_ERROR in error_text
