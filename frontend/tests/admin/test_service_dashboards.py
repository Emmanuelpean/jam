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

import datetime as dt

from selenium.webdriver.common.by import By

from frontend_base_test import BaseTest


class ServiceDashboardBase(BaseTest):
    """Shared helpers for service dashboard tests."""

    user_fixture = "test_admin_user"
    page_url = "admin"


class TestJobScrapingDashboard(ServiceDashboardBase):
    """Tests for the Job Scraping dashboard modal."""

    def setup_function(self, request) -> None:
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
        """Log viewer toggle works correctly."""

        self.service_dashboard_utils.open_scraping()
        self.service_dashboard_utils.assert_log_viewer_toggles()


class TestJobRatingDashboard(ServiceDashboardBase):
    """Tests for the Job Rating dashboard modal."""

    def setup_function(self, request) -> None:
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
        """Log viewer toggle works correctly on the rating modal."""

        self.service_dashboard_utils.open_rating()
        self.service_dashboard_utils.assert_log_viewer_toggles()


class TestJobScrapingDashboardErrors(ServiceDashboardBase):
    """Tests that critical, service and scraping errors display correctly."""

    CRITICAL_ERROR = "Critical error in scraping workflow."
    SERVICE_ERROR = "Failed to get forwarding emails."
    SCRAPING_ERROR = "Failed to scrape job data."

    def setup_function(self, request) -> None:
        # Service log with today's date (the model default) so it appears in the default date range
        service_log = self.create_email_scraping_service_log(self.db, run_duration=30.0)

        # Run-level critical error: no scraped_job_id, level=critical (drives is_success/Critical Errors column)
        self.create_service_error(
            self.db,
            error_type="OperationalError",
            message=self.CRITICAL_ERROR,
            level="critical",
            job_email_scraping_service_log_id=service_log.id,
        )

        # Run-level (non-critical) error, appears in the "Service Errors" column
        self.create_service_error(
            self.db,
            error_type="TimeoutError",
            message=self.SERVICE_ERROR,
            job_email_scraping_service_log_id=service_log.id,
        )

        # Per-job error (scraped_job_id set), appears in the "Scraping Errors" column
        scraped_job = self.user.create_scraped_job(service_log=service_log)
        self.create_service_error(
            self.db,
            error_type="HTTPError",
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


class TestServiceDashboardRunFilter(ServiceDashboardBase):
    """Clicking a run in the history chart filters the already-loaded errors to that run."""

    OLD_RUN_ERROR = "Failed to search emails for user."
    NEW_RUN_ERROR = "Failed to get forwarding emails."

    def setup_function(self, request) -> None:
        now = dt.datetime.now(dt.timezone.utc)
        # Two runs a day apart (both inside the default 1-week window), each with its own error.
        old_log = self.create_email_scraping_service_log(
            self.db, run_duration=30.0, run_datetime=now - dt.timedelta(days=1)
        )
        new_log = self.create_email_scraping_service_log(self.db, run_duration=20.0, run_datetime=now)
        self.create_service_error(
            self.db, error_type="TimeoutError", message=self.OLD_RUN_ERROR, job_email_scraping_service_log_id=old_log.id
        )
        self.create_service_error(
            self.db, error_type="TimeoutError", message=self.NEW_RUN_ERROR, job_email_scraping_service_log_id=new_log.id
        )
        self.login()

    def test_click_run_filters_errors_to_that_run(self) -> None:
        """Clicking the newest run's chart point shows only that run's error; clearing restores both."""

        self.service_dashboard_utils.open_scraping()

        # Both runs' errors are visible before any selection.
        self.service_dashboard_utils.wait_for_error_summary_containing(self.OLD_RUN_ERROR, self.NEW_RUN_ERROR)

        # Clicking the newest run's point filters the errors to that run and shows the run chip.
        self.service_dashboard_utils.select_run_from_chart(newest=True)
        assert self.service_dashboard_utils.selected_run_filter.is_displayed()
        self.service_dashboard_utils.wait_for_error_summary_filtered(
            contains=self.NEW_RUN_ERROR, excludes=self.OLD_RUN_ERROR
        )

        # Clearing the filter restores errors for all runs.
        self.service_dashboard_utils.clear_run_filter()
        self.service_dashboard_utils.wait_for_error_summary_containing(self.OLD_RUN_ERROR, self.NEW_RUN_ERROR)


class TestServiceDashboardErrorGrouping(ServiceDashboardBase):
    """Errors sharing a type and message collapse into a single group with an occurrence count."""

    FREQUENT_ERROR = "Failed to get forwarding emails."
    OCCASIONAL_ERROR = "Failed to search emails for user."

    def setup_function(self, request) -> None:
        service_log = self.create_email_scraping_service_log(self.db, run_duration=30.0)
        for _ in range(3):
            self.create_service_error(
                self.db,
                error_type="TimeoutError",
                message=self.FREQUENT_ERROR,
                job_email_scraping_service_log_id=service_log.id,
            )
        for _ in range(2):
            self.create_service_error(
                self.db,
                error_type="TimeoutError",
                message=self.OCCASIONAL_ERROR,
                job_email_scraping_service_log_id=service_log.id,
            )
        self.login()

    def test_errors_group_by_message(self) -> None:
        """Five raw errors show as two groups (3 and 2 occurrences), expanding to their rows."""

        self.service_dashboard_utils.open_scraping()
        error_text = self.service_dashboard_utils.wait_for_error_summary_containing(
            self.FREQUENT_ERROR, self.OCCASIONAL_ERROR
        )

        text = error_text.lower()
        assert "service errors (2 unique)" in text
        assert "3 occurrences" in text
        assert "2 occurrences" in text

        assert self.service_dashboard_utils.expand_error_group(self.FREQUENT_ERROR) == 3
        assert self.service_dashboard_utils.expand_error_group(self.OCCASIONAL_ERROR) == 2


class TestJobRatingDashboardErrors(ServiceDashboardBase):
    """Tests that critical and rating errors display correctly on the rating modal."""

    CRITICAL_ERROR = "Critical error in rating workflow"
    RATING_ERROR = "Error scoring job."

    def setup_function(self, request) -> None:
        rating_log = self.create_job_rating_service_log(self.db, run_duration=20.0)

        self.create_service_error(
            self.db,
            error_type="Exception",
            message=self.CRITICAL_ERROR,
            level="critical",
            job_rating_service_log_id=rating_log.id,
        )

        rating = self.user.create_job_rating(status="failed", llm_model="claude-sonnet-4-6")
        self.create_service_error(
            self.db,
            error_type="KeyError",
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
