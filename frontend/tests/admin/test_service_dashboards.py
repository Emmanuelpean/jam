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

from selenium.webdriver.common.by import By

from frontend_base_test import BaseTest


class ServiceDashboardBase(BaseTest):
    """Shared helpers for service dashboard tests."""

    user_fixture = "test_admin_user"
    page_url = "admin"


class TestJobScrapingDashboard(ServiceDashboardBase):
    """Tests for the Job Scraping dashboard modal."""

    def setup_function(self, request) -> None:
        # The Service config row is normally seeded at backend startup, but the per-test DB
        # truncation wipes it, so the status control needs it created explicitly.
        self.create_service(self.db, name="email_scraper_service", display_name="Job Email Scraping")
        self.create_email_scraping_service_log(self.db, run_duration=45.2)
        self.login()

    def test_page_renders(self) -> None:
        """All static elements render correctly on the Job Scraping dashboard."""

        self.service_dashboard_utils.open_scraping()

        # Data cards in the modal body
        assert self.service_dashboard_utils.latest_run_progress.is_displayed()
        assert self.service_dashboard_utils.error_summary_card.is_displayed()
        assert self.service_dashboard_utils.history_filters.is_displayed()

        # Status control in the modal header: the run-status icon
        icons = self.service_dashboard_utils.service_status_icons
        assert len(icons.find_elements(By.CLASS_NAME, "service-status-icon")) >= 1

        # Opening the status control reveals the config fields and the run-now button
        self.service_dashboard_utils.open_status_control()
        assert self.service_dashboard_utils.run_now_button
        assert self.service_dashboard_utils.period_hours_field.is_displayed()
        assert self.service_dashboard_utils.min_timedelta_days_field.is_displayed()
        assert self.service_dashboard_utils.max_timedelta_days_field.is_displayed()

    def test_interactive_elements(self) -> None:
        """Log viewer and error view toggle work correctly."""

        self.service_dashboard_utils.open_scraping()
        self.service_dashboard_utils.assert_log_viewer_toggles()
        self.service_dashboard_utils.assert_error_view_toggles()


class TestJobRatingDashboard(ServiceDashboardBase):
    """Tests for the Job Rating dashboard modal."""

    def setup_function(self, request) -> None:
        # The Service config row is normally seeded at backend startup, but the per-test DB
        # truncation wipes it, so the status control needs it created explicitly.
        self.create_service(self.db, name="job_rating_service", display_name="Job Rating")
        self.create_job_rating_service_log(self.db, run_duration=12.5)
        self.login()

    def test_page_renders(self) -> None:
        """All static elements render correctly on the Job Rating dashboard."""

        self.service_dashboard_utils.open_rating()

        # Data cards in the modal body
        assert self.service_dashboard_utils.latest_run_progress.is_displayed()
        assert self.service_dashboard_utils.error_summary_card.is_displayed()
        assert self.service_dashboard_utils.history_filters.is_displayed()

        # Status control: only period_hours (no min/max_timedelta_days for rating)
        self.service_dashboard_utils.open_status_control()
        assert self.service_dashboard_utils.run_now_button
        assert self.service_dashboard_utils.period_hours_field.is_displayed()
        self.service_dashboard_utils.assert_no_min_timedelta_days_field()

    def test_interactive_elements(self) -> None:
        """Log viewer and error view toggle work correctly on the rating modal."""

        self.service_dashboard_utils.open_rating()
        self.service_dashboard_utils.assert_log_viewer_toggles()
        self.service_dashboard_utils.assert_error_view_toggles()


class TestJobScrapingDashboardErrors(ServiceDashboardBase):
    """Tests that critical, service and scraping errors display correctly."""

    CRITICAL_ERROR = "Critical: database connection pool exhausted"
    SERVICE_ERROR = "Failed to connect to LinkedIn API: Connection timed out"
    SCRAPING_ERROR = "Page not found - job posting has been removed"

    def setup_function(self, request) -> None:
        # Service log with today's date (the model default) so it appears in the default date range
        service_log = self.create_email_scraping_service_log(self.db, run_duration=30.0)

        # Run-level critical error: no scraped_job_id, level=critical (drives is_success/Critical Errors column)
        self.create_service_error(
            self.db,
            message=self.CRITICAL_ERROR,
            level="critical",
            job_email_scraping_service_log_id=service_log.id,
        )

        # Run-level (non-critical) error, appears in the "Service Errors" column
        self.create_service_error(
            self.db,
            message=self.SERVICE_ERROR,
            job_email_scraping_service_log_id=service_log.id,
        )

        # Per-job error (scraped_job_id set), appears in the "Scraping Errors" column
        scraped_job = self.user.create_scraped_job(service_log=service_log)
        self.create_service_error(
            self.db,
            message=self.SCRAPING_ERROR,
            job_email_scraping_service_log_id=service_log.id,
            scraped_job_id=scraped_job.id,
        )
        self.login()

    def test_errors_display(self) -> None:
        """Critical, service and scraping errors all appear in the Error Summary card."""

        self.service_dashboard_utils.open_scraping()
        error_text = self.service_dashboard_utils.wait_for_error_summary_containing(
            self.CRITICAL_ERROR, self.SERVICE_ERROR, self.SCRAPING_ERROR
        )

        # Critical Errors column: run-level errors with level=critical
        assert self.CRITICAL_ERROR in error_text

        # Service Errors column: run-level errors with level != critical
        assert self.SERVICE_ERROR in error_text

        # Scraping Errors column: errors linked to a scraped job
        assert self.SCRAPING_ERROR in error_text


class TestJobRatingDashboardErrors(ServiceDashboardBase):
    """Tests that critical and rating errors display correctly on the rating modal."""

    CRITICAL_ERROR = "Critical: rating service crashed unexpectedly"
    RATING_ERROR = "Failed to rate job: API timeout after 30 seconds"

    def setup_function(self, request) -> None:
        # Rating service log with today's date (the model default) so it appears in the default date range
        rating_log = self.create_job_rating_service_log(self.db, run_duration=20.0)

        # Run-level critical error: no job_rating_id, level=critical (drives is_success/Critical Errors column)
        self.create_service_error(
            self.db,
            message=self.CRITICAL_ERROR,
            level="critical",
            job_rating_service_log_id=rating_log.id,
        )

        # Failed job rating linked to the run via job_rating_service_log_id, and to the
        # per-job error via job_rating_id (appears in the "Job Rating Errors" column)
        rating = self.user.create_job_rating(status="failed", llm_model="claude-sonnet-4-6")
        self.create_service_error(
            self.db,
            message=self.RATING_ERROR,
            job_rating_service_log_id=rating_log.id,
            job_rating_id=rating.id,
        )
        self.login()

    def test_errors_display(self) -> None:
        """Critical and rating errors both appear in the Error Summary card."""

        self.service_dashboard_utils.open_rating()
        error_text = self.service_dashboard_utils.wait_for_error_summary_containing(
            self.CRITICAL_ERROR, self.RATING_ERROR
        )

        # Critical Errors column: rating service logs with a critical-level error
        assert self.CRITICAL_ERROR in error_text

        # Job Rating Errors column: failed job ratings with an error linked via job_rating_id
        assert self.RATING_ERROR in error_text
