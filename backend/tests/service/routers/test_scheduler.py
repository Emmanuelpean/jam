"""HTTP-level tests for the /service-scheduler status and log endpoints."""

import os
import tempfile
from unittest.mock import patch

from starlette import status
from starlette.testclient import TestClient

from tests.base_test import BaseTest
from tests.fixtures.users import FixtureUser


class TestSchedulerStatus(BaseTest):
    endpoint = "/service-scheduler/status"

    def test_admin_gets_status(self, test_admin_user: FixtureUser) -> None:
        """Admin receives the scheduler's runtime status fields."""

        resp = test_admin_user.client.get(self.endpoint)
        assert resp.status_code == status.HTTP_200_OK
        body = resp.json()
        assert set(body) == {"running", "poll_interval_seconds", "last_log"}
        assert isinstance(body["running"], bool)

    def test_non_admin_forbidden(self, test_regular_user: FixtureUser) -> None:
        assert test_regular_user.client.get(self.endpoint).status_code == status.HTTP_403_FORBIDDEN

    def test_unauthenticated(self, client: TestClient) -> None:
        assert client.get(self.endpoint).status_code == status.HTTP_401_UNAUTHORIZED


class TestSchedulerLogs(BaseTest):
    endpoint = "/service-scheduler/logs"

    def test_admin_gets_log_tail(self, test_admin_user: FixtureUser) -> None:
        """Admin receives the last N lines of the scheduler's log file."""

        log_lines = [f"line {i}" for i in range(10)]
        with tempfile.TemporaryDirectory() as tmpdir:
            with open(os.path.join(tmpdir, "service_scheduler.log"), "w", encoding="utf-8") as f:
                f.write("\n".join(log_lines) + "\n")

            with patch("app.utilities.logger.settings") as mock_settings:
                mock_settings.log_directory = tmpdir
                resp = test_admin_user.client.get(f"{self.endpoint}?lines=3")

        body = resp.json()
        assert body["total_lines"] == 10
        assert body["lines"] == log_lines[-3:]

    def test_returns_empty_when_log_missing(self, test_admin_user: FixtureUser) -> None:
        with tempfile.TemporaryDirectory() as tmpdir, patch("app.utilities.logger.settings") as mock_settings:
            mock_settings.log_directory = tmpdir
            resp = test_admin_user.client.get(self.endpoint)

        assert resp.status_code == status.HTTP_200_OK
        assert resp.json() == {"lines": [], "total_lines": 0}

    def test_rejects_out_of_range_lines(self, test_admin_user: FixtureUser) -> None:
        assert (
            test_admin_user.client.get(f"{self.endpoint}?lines=0").status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        )

    def test_non_admin_forbidden(self, test_regular_user: FixtureUser) -> None:
        assert test_regular_user.client.get(self.endpoint).status_code == status.HTTP_403_FORBIDDEN

    def test_unauthenticated(self, client: TestClient) -> None:
        assert client.get(self.endpoint).status_code == status.HTTP_401_UNAUTHORIZED
