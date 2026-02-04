"""Tests for the maintenance mode functionality.

These tests cover:
1. Maintenance countdown banner displayed to authenticated users
2. Maintenance error_banner displayed when scheduled time is reached
3. Maintenance page displayed when MAINTENANCE_MODE is enabled

The tests use JavaScript injection to dynamically set the maintenance scheduled time,
allowing tests to run without requiring specific environment variables.
"""

import time
from datetime import datetime, timedelta, timezone

from conftest import BaseTest


class TestMaintenanceCountdownBanner(BaseTest):
    """Tests for the maintenance countdown banner functionality.
    These tests dynamically inject the maintenance scheduled time via JavaScript,
    so they can run without any special environment configuration."""

    page_url = "dashboard"

    def _set_maintenance_scheduled_at(self, iso_timestamp: str) -> None:
        """Inject the maintenance scheduled time via JavaScript.
        This sets window.__TEST_MAINTENANCE_SCHEDULED_AT__ which the
        MaintenanceBanner component checks for test overrides."""

        self.driver.execute_script(
            "window.__TEST_MAINTENANCE_SCHEDULED_AT__ = arguments[0];",
            iso_timestamp,
        )

    @staticmethod
    def _get_future_timestamp(minutes: int | float = 30) -> str:
        """Get an ISO 8601 timestamp for a time in the future."""

        future_time = datetime.now(timezone.utc) + timedelta(minutes=minutes)
        return future_time.isoformat()

    def test_countdown_banner_shows_countdown_when_under_one_hour(self) -> None:
        """Test that the countdown banner is displayed when maintenance is scheduled."""

        self.login()
        future_time = self._get_future_timestamp(minutes=30)
        self._set_maintenance_scheduled_at(future_time)
        banner = self.get_element("maintenance-countdown-banner", timeout=5)
        text = banner.text.lower()
        assert "maintenance" in text, f"Banner text should mention maintenance: {text}"
        assert "m" in text and "s" in text, f"Countdown should show minutes and seconds: {text}"

    def test_countdown_banner_shows_scheduled_time_when_over_one_hour(self) -> None:
        """Test that the banner shows the scheduled date/time when more than 1 hour away."""

        self.login()
        future_time = self._get_future_timestamp(minutes=120)
        self._set_maintenance_scheduled_at(future_time)
        banner = self.get_element("maintenance-countdown-banner", timeout=5)
        text = banner.text.lower()
        assert "scheduled maintenance on" in text, f"Banner should show scheduled date when >1 hour away: {text}"

    def test_error_banner_appears_when_maintenance_time_reached(self) -> None:
        """Test that the maintenance error_banner appears when the scheduled time is reached."""

        self.login()
        future_time = self._get_future_timestamp(minutes=1 / 60)
        self._set_maintenance_scheduled_at(future_time)
        self.get_element("maintenance-countdown-banner", timeout=5)
        time.sleep(3)
        self.check_element_exists("maintenance-error-banner", timeout=5)

    def test_banner_not_shown_when_not_authenticated(self) -> None:
        """Test that the banner is not shown to unauthenticated users."""

        self.auth_utils.go_to_login()
        future_time = self._get_future_timestamp(minutes=30)
        self._set_maintenance_scheduled_at(future_time)
        banner_exists = self.check_element_exists("maintenance-countdown-banner", timeout=2)
        assert not banner_exists, "Maintenance banner should not appear for unauthenticated users"


class TestMaintenancePage(BaseTest):
    """Tests for the maintenance page when MAINTENANCE_MODE is enabled.
    These tests dynamically inject maintenance mode via JavaScript,
    so they can run without any special environment configuration."""

    def _set_maintenance_mode(self, enabled: bool) -> None:
        """Inject the maintenance mode via JavaScript.

        This sets window.__TEST_MAINTENANCE_MODE__ which the
        App component checks for test overrides.
        """
        self.driver.execute_script(
            "window.__TEST_MAINTENANCE_MODE__ = arguments[0];",
            enabled,
        )

    def test_maintenance_page_displayed_when_mode_enabled(self) -> None:
        """Test that the maintenance page is displayed when maintenance mode is enabled."""

        self._set_maintenance_mode(True)
        for page in ["login", "register"]:
            self.go_to_page(f"{self.frontend_base_url}/{page}")
            maintenance_page_exists = self.check_element_exists("maintenance-page", timeout=5)
            assert maintenance_page_exists, "Maintenance page should be displayed when maintenance mode is enabled"
