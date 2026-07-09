from datetime import datetime, timezone, timedelta

from fixtures.users import FixtureUser
from frontend_base_test import BaseTest


class MaintenanceTestBase(BaseTest):
    """Shared helpers for maintenance tests."""

    _setting_id = None
    banner_id = "maintenance-countdown-banner"

    def _set_maintenance_scheduled_at(self, iso_timestamp: str, test_admin_user: FixtureUser) -> None:
        """Create or update the maintenance_scheduled_at setting via the API."""

        if self._setting_id is None:
            response = test_admin_user.client.post(
                "/settings/", json={"name": "maintenance_scheduled_at", "value": iso_timestamp}
            )
            assert response.status_code == 201
            self._setting_id = response.json()["id"]
        else:
            response = test_admin_user.client.put(f"/settings/{self._setting_id}", json={"value": iso_timestamp})
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
