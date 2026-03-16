"""Tests for the service dashboard pages (Job Scraping and Job Rating).

These tests cover:
1. Tab navigation between Job Scraping and Job Rating dashboards
2. Service status card renders with config fields
3. Log viewer expand/collapse
4. Latest run progress card renders
5. Error summary card renders and error view toggle
6. Proper display of critical, service, scraping and rating errors
"""

import uuid
from datetime import datetime, timezone

from selenium.webdriver.common.by import By

from conftest import BaseTest, models


class ServiceDashboardBase(BaseTest):
    """Shared helpers for service dashboard tests."""

    user_index = 1  # admin user required for service dashboards
    page_url = "service-dashboards"

    def _go_to_scraping_tab(self) -> None:
        self.get_element("tab-scraping").click()

    def _go_to_rating_tab(self) -> None:
        self.get_element("tab-rating").click()

    def _expand_log_viewer(self) -> None:
        self.get_element("log-toggle", selector=By.CLASS_NAME).click()

    def _toggle_error_view(self) -> None:
        self.get_element("errorViewToggle").click()


class TestJobScrapingDashboard(ServiceDashboardBase):
    """Tests for the Job Scraping dashboard tab."""

    def setup_function(self, request) -> None:
        request.getfixturevalue("test_job_scraping_service_logs")
        self.login()

    def test_page_renders(self) -> None:
        """All static elements render correctly on the Job Scraping dashboard."""

        # Tab is selected by default
        assert self.get_element("tab-scraping", enabled=False).is_displayed()

        # Service status card: wait for status to load, then check badges
        self.get_element("confirm-start-button")
        badges = self.driver.find_elements(By.CLASS_NAME, "status-badge")
        assert len(badges) >= 2, "Expected at least two status badges (service runner + scraper)"

        # Config fields
        assert self.get_element("period_hours", selector=By.NAME, enabled=False).is_displayed()
        assert self.get_element("timedelta_days", selector=By.NAME, enabled=False).is_displayed()

        # Data cards
        assert self.get_element("latest-run-progress", enabled=False).is_displayed()
        assert self.get_element("error-summary-card", enabled=False).is_displayed()
        assert self.get_element("history-filters", enabled=False).is_displayed()

    def test_interactive_elements(self) -> None:
        """Log viewer and error view toggle work correctly."""

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
    """Tests for the Job Rating dashboard tab."""

    def setup_function(self, request) -> None:
        request.getfixturevalue("test_job_rating_service_logs")
        self.login()
        self._go_to_rating_tab()

    def test_page_renders(self) -> None:
        """All static elements render correctly on the Job Rating dashboard."""

        # Config field: only period_hours (no timedelta_days)
        assert self.get_element("period_hours", selector=By.NAME, enabled=False).is_displayed()
        assert not self.check_element_exists("timedelta_days", selector=By.NAME), (
            "timedelta_days should not appear on the rating dashboard"
        )

        # Service status card: wait for status to load, then check badges
        self.get_element("confirm-start-button")
        badges = self.driver.find_elements(By.CLASS_NAME, "status-badge")
        assert len(badges) >= 2, "Expected at least two status badges"

        # Data cards
        assert self.get_element("latest-run-progress", enabled=False).is_displayed()
        assert self.get_element("error-summary-card", enabled=False).is_displayed()
        assert self.get_element("history-filters", enabled=False).is_displayed()

        # Switch back to scraping tab: timedelta_days reappears
        self._go_to_scraping_tab()
        assert self.get_element("timedelta_days", selector=By.NAME, enabled=False).is_displayed()

    def test_interactive_elements(self) -> None:
        """Log viewer and error view toggle work correctly on the rating tab."""

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
        service_log = models.JobEmailScrapingServiceLog(
            run_datetime=datetime.now(timezone.utc),
            run_duration=30.0,
            is_success=False,
            error_message=self.CRITICAL_ERROR,
        )
        self.db.add(service_log)
        self.db.commit()
        self.db.refresh(service_log)

        # Service error linked to this log (appears in "Service Errors" column)
        service_error = models.JobEmailScrapingServiceError(
            error_type="ConnectionError",
            message=self.SERVICE_ERROR,
            traceback="Traceback (most recent call last): ...",
            service_log_id=service_log.id,
        )
        self.db.add(service_error)

        # Scraped job with a known error (appears in "Scraping Errors" column)
        scraped_job = models.ScrapedJob(
            external_job_id=str(uuid.uuid4()),
            platform="linkedin",
            owner_id=self.db_user.id,
            is_failed=True,
            is_processed=True,
            scrape_error=[{"datetime": "2026-03-16T10:00:00+00:00", "error": self.SCRAPING_ERROR}],
            service_log_id=service_log.id,
            url="http://test.com",
        )
        self.db.add(scraped_job)
        self.db.commit()
        self.db.refresh(scraped_job)

        # Platform stat referencing the failed job so the hook picks it up
        platform_stat = models.JobEmailScrapingPlatformStat(
            name="linkedin",
            service_log_id=service_log.id,
            job_scrape_failed_ids=[scraped_job.id],
        )
        self.db.add(platform_stat)
        self.db.commit()
        self.login()

    def test_errors_display(self) -> None:
        """Critical, service and scraping errors all appear in the Error Summary card."""

        # Wait for errors to load (card shows a spinner while fetching)
        self.wait.until(
            lambda d: self.CRITICAL_ERROR in d.find_element(By.ID, "error-summary-card").text
        )
        error_card = self.driver.find_element(By.ID, "error-summary-card")

        # Critical Errors column: service logs with error_message within the date range
        assert self.CRITICAL_ERROR in error_card.text

        # Service Errors column: service_errors linked to the latest log
        assert self.SERVICE_ERROR in error_card.text

        # Scraping Errors column: scraped job errors fetched via platform_stats
        assert self.SCRAPING_ERROR in error_card.text


class TestJobRatingDashboardErrors(ServiceDashboardBase):
    """Tests that critical and rating errors display correctly on the rating tab."""

    CRITICAL_ERROR = "Critical: rating service crashed unexpectedly"
    RATING_ERROR = "Failed to rate job: API timeout after 30 seconds"

    def setup_function(self, request) -> None:
        request.getfixturevalue("test_user_qualifications")

        # Scraping service log needed as FK for the scraped job
        scraping_log = models.JobEmailScrapingServiceLog(
            run_datetime=datetime.now(timezone.utc),
            run_duration=10.0,
        )
        self.db.add(scraping_log)
        self.db.commit()
        self.db.refresh(scraping_log)

        # Scraped job needed as FK for the job rating
        scraped_job = models.ScrapedJob(
            external_job_id=str(uuid.uuid4()),
            platform="linkedin",
            owner_id=self.db_user.id,
            is_processed=True,
            service_log_id=scraping_log.id,
            url="http://test.com",
        )
        self.db.add(scraped_job)
        self.db.commit()
        self.db.refresh(scraped_job)

        qualification = self.db.query(models.UserQualification).filter_by(owner_id=self.db_user.id).first()

        # Job rating that failed (the error appears in "Job Rating Errors" column)
        rating = models.JobRating(
            scraped_job_id=scraped_job.id,
            owner_id=self.db_user.id,
            user_qualification_id=qualification.id,
            is_success=False,
            error=self.RATING_ERROR,
            llm_model="claude-sonnet-4-6",
        )
        self.db.add(rating)
        self.db.commit()
        self.db.refresh(rating)

        # Rating service log with today's date: error_message for Critical Errors,
        # job_failed_ids referencing the failed rating for the Rating Errors column
        rating_log = models.JobRatingServiceLog(
            run_datetime=datetime.now(timezone.utc),
            run_duration=20.0,
            is_success=False,
            error_message=self.CRITICAL_ERROR,
            job_failed_ids=[rating.id],
        )
        self.db.add(rating_log)
        self.db.commit()
        self.login()
        self._go_to_rating_tab()

    def test_errors_display(self) -> None:
        """Critical and rating errors both appear in the Error Summary card."""

        # Wait for errors to load
        self.wait.until(
            lambda d: self.CRITICAL_ERROR in d.find_element(By.ID, "error-summary-card").text
        )
        error_card = self.driver.find_element(By.ID, "error-summary-card")

        # Critical Errors column: rating service logs with error_message in the date range
        assert self.CRITICAL_ERROR in error_card.text

        # Job Rating Errors column: failed job ratings fetched via job_failed_ids
        assert self.RATING_ERROR in error_card.text
