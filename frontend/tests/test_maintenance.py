"""Tests for the maintenance mode functionality.

These tests cover:
1. Maintenance countdown banner displayed to authenticated users
2. Maintenance error_banner displayed when scheduled time is reached
3. Maintenance error banner displayed when maintenance_scheduled_at is in the past (no maintenance page)
4. Admin users see a banner and can still use the app

The tests create/update the `maintenance_scheduled_at` Setting via the backend API.
In test mode the frontend polls every 2s instead of 30s.
"""

import time
from datetime import datetime, timedelta, timezone

from conftest import BaseTest

# Timeout that comfortably exceeds the 2s test-mode poll interval
POLL_TIMEOUT = 5


class MaintenanceTestBase(BaseTest):
    """Shared helpers for maintenance tests."""

    _setting_id = None

    def _set_maintenance_scheduled_at(self, iso_timestamp: str) -> None:
        """Create or update the maintenance_scheduled_at setting via the API."""

        if self._setting_id is None:
            response = self.client.post("/settings/", json={"name": "maintenance_scheduled_at", "value": iso_timestamp})
            assert response.status_code == 201
            self._setting_id = response.json()["id"]
        else:
            response = self.client.put(f"/settings/{self._setting_id}", json={"value": iso_timestamp})
            assert response.status_code == 200

    def _clear_maintenance_scheduled_at(self) -> None:
        """Delete the maintenance_scheduled_at setting if it exists."""

        if self._setting_id is not None:
            self.client.delete(f"/settings/{self._setting_id}")
            self._setting_id = None

    @staticmethod
    def _get_future_timestamp(minutes: int | float = 30) -> str:
        """Get an ISO 8601 timestamp for a time in the future."""

        future_time = datetime.now(timezone.utc) + timedelta(minutes=minutes)
        return future_time.isoformat()

    @staticmethod
    def _get_past_timestamp(minutes: int | float = 5) -> str:
        """Get an ISO 8601 timestamp for a time in the past."""

        past_time = datetime.now(timezone.utc) - timedelta(minutes=minutes)
        return past_time.isoformat()


class TestMaintenanceBanner(MaintenanceTestBase):
    """Tests for the maintenance banner functionality."""

    page_url = "dashboard"

    def test_countdown_banner_shows_countdown_when_under_one_hour(self) -> None:
        """Test that the countdown banner is displayed when maintenance is scheduled."""

        self.login()
        future_time = self._get_future_timestamp(minutes=30)
        self._set_maintenance_scheduled_at(future_time)
        banner = self.get_element("maintenance-countdown-banner", timeout=POLL_TIMEOUT)
        text = banner.text.lower()
        assert "maintenance" in text, f"Banner text should mention maintenance: {text}"
        assert "m" in text and "s" in text, f"Countdown should show minutes and seconds: {text}"
        self._clear_maintenance_scheduled_at()

    def test_countdown_banner_shows_scheduled_time_when_over_one_hour(self) -> None:
        """Test that the banner shows the scheduled date/time when more than 1 hour away."""

        self.login()
        future_time = self._get_future_timestamp(minutes=120)
        self._set_maintenance_scheduled_at(future_time)
        banner = self.get_element("maintenance-countdown-banner", timeout=POLL_TIMEOUT)
        text = banner.text.lower()
        assert "scheduled maintenance on" in text, f"Banner should show scheduled date when >1 hour away: {text}"
        self._clear_maintenance_scheduled_at()

    def test_error_banner_appears_when_maintenance_time_reached(self) -> None:
        """Test that the maintenance error_banner appears when the scheduled time is reached."""

        self.login()
        future_time = self._get_future_timestamp(minutes=1 / 60)
        self._set_maintenance_scheduled_at(future_time)
        time.sleep(3)
        self.check_element_exists("maintenance-error-banner", timeout=POLL_TIMEOUT)
        self._clear_maintenance_scheduled_at()

    def test_banner_shown_when_not_authenticated(self) -> None:
        """Test that the banner is not shown to unauthenticated users."""

        self.auth_utils.go_to_login()
        future_time = self._get_future_timestamp(minutes=30)
        self._set_maintenance_scheduled_at(future_time)
        banner_exists = self.check_element_exists("maintenance-countdown-banner", timeout=POLL_TIMEOUT)
        assert banner_exists, "Maintenance banner should not appear for unauthenticated users"
        self._clear_maintenance_scheduled_at()

    def test_maintenance_banner_displayed_when_mode_enabled(self) -> None:
        """Test that the maintenance error banner is displayed to regular users when maintenance is active."""

        self.login()
        past_time = self._get_past_timestamp(minutes=5)
        self._set_maintenance_scheduled_at(past_time)
        banner_exists = self.check_element_exists("maintenance-error-banner", timeout=POLL_TIMEOUT)
        assert banner_exists, "Maintenance error banner should be displayed when maintenance mode is enabled"


class TestAdminMaintenanceBanner(MaintenanceTestBase):
    """Tests that admin users see a maintenance banner instead of the maintenance page."""

    page_url = "dashboard"
    user_index = 1  # admin user

    def test_admin_sees_banner_and_can_use_app(self) -> None:
        """Test that an admin user sees the maintenance banner and can still use the app."""

        self.login()
        past_time = self._get_past_timestamp(minutes=5)
        self._set_maintenance_scheduled_at(past_time)

        banner_exists = self.check_element_exists("maintenance-error-banner", timeout=POLL_TIMEOUT)
        assert banner_exists, "Admin should see the maintenance active banner"

        self._clear_maintenance_scheduled_at()
