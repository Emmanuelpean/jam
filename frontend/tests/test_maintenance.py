"""Tests for the maintenance mode functionality.

These tests cover:
1. Maintenance countdown banner displayed to authenticated users
2. Maintenance error_banner displayed when scheduled time is reached
3. Maintenance page displayed when maintenance_mode setting is enabled

The tests create/update Setting records via the backend API so the
StatusContext polling picks up the changes.
"""

import time
from datetime import datetime, timedelta, timezone

from conftest import BaseTest


class TestMaintenanceCountdownBanner(BaseTest):
    """Tests for the maintenance countdown banner functionality.
    These tests create a `maintenance_scheduled_at` setting via the API,
    which the StatusContext polls and the MaintenanceBanner reads."""

    page_url = "dashboard"
    _setting_id = None

    def _set_maintenance_scheduled_at(self, iso_timestamp: str) -> None:
        """Create or update the maintenance_scheduled_at setting via the API."""

        if self._setting_id is None:
            response = self.client.post(
                "/settings/",
                json={"name": "maintenance_scheduled_at", "value": iso_timestamp},
            )
            assert response.status_code == 201
            self._setting_id = response.json()["id"]
        else:
            response = self.client.put(
                f"/settings/{self._setting_id}",
                json={"value": iso_timestamp},
            )
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

    def test_countdown_banner_shows_countdown_when_under_one_hour(self) -> None:
        """Test that the countdown banner is displayed when maintenance is scheduled."""

        self.login()
        future_time = self._get_future_timestamp(minutes=30)
        self._set_maintenance_scheduled_at(future_time)
        banner = self.get_element("maintenance-countdown-banner", timeout=35)
        text = banner.text.lower()
        assert "maintenance" in text, f"Banner text should mention maintenance: {text}"
        assert "m" in text and "s" in text, f"Countdown should show minutes and seconds: {text}"
        self._clear_maintenance_scheduled_at()

    def test_countdown_banner_shows_scheduled_time_when_over_one_hour(self) -> None:
        """Test that the banner shows the scheduled date/time when more than 1 hour away."""

        self.login()
        future_time = self._get_future_timestamp(minutes=120)
        self._set_maintenance_scheduled_at(future_time)
        banner = self.get_element("maintenance-countdown-banner", timeout=35)
        text = banner.text.lower()
        assert "scheduled maintenance on" in text, f"Banner should show scheduled date when >1 hour away: {text}"
        self._clear_maintenance_scheduled_at()

    def test_error_banner_appears_when_maintenance_time_reached(self) -> None:
        """Test that the maintenance error_banner appears when the scheduled time is reached."""

        self.login()
        future_time = self._get_future_timestamp(minutes=1 / 60)
        self._set_maintenance_scheduled_at(future_time)
        time.sleep(5)
        self.check_element_exists("maintenance-error-banner", timeout=35)
        self._clear_maintenance_scheduled_at()

    def test_banner_not_shown_when_not_authenticated(self) -> None:
        """Test that the banner is not shown to unauthenticated users."""

        self.auth_utils.go_to_login()
        future_time = self._get_future_timestamp(minutes=30)
        self._set_maintenance_scheduled_at(future_time)
        banner_exists = self.check_element_exists("maintenance-countdown-banner", timeout=35)
        assert not banner_exists, "Maintenance banner should not appear for unauthenticated users"
        self._clear_maintenance_scheduled_at()


class TestMaintenancePage(BaseTest):
    """Tests for the maintenance page when maintenance_mode setting is enabled.
    These tests create a `maintenance_mode` setting via the API."""

    _setting_id = None

    def _set_maintenance_mode(self, enabled: bool) -> None:
        """Create or update the maintenance_mode setting via the API."""

        value = "true" if enabled else "false"
        if self._setting_id is None:
            response = self.client.post(
                "/settings/",
                json={"name": "maintenance_mode", "value": value},
            )
            assert response.status_code == 201
            self._setting_id = response.json()["id"]
        else:
            response = self.client.put(
                f"/settings/{self._setting_id}",
                json={"value": value},
            )
            assert response.status_code == 200

    def _clear_maintenance_mode(self) -> None:
        """Delete the maintenance_mode setting if it exists."""

        if self._setting_id is not None:
            self.client.delete(f"/settings/{self._setting_id}")
            self._setting_id = None

    def test_maintenance_page_displayed_when_mode_enabled(self) -> None:
        """Test that the maintenance page is displayed when maintenance mode is enabled."""

        self._set_maintenance_mode(True)
        for page in ["login", "register"]:
            self.go_to_page(f"{self.frontend_base_url}/{page}")
            maintenance_page_exists = self.check_element_exists("maintenance-page", timeout=35)
            assert maintenance_page_exists, "Maintenance page should be displayed when maintenance mode is enabled"
        self._clear_maintenance_mode()
