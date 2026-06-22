"""HTTP-level tests for the external-service-monitoring service routers.

Covers:
- The service router (`/external-service-monitoring-service/*`): start / stop / status / logs — driven by a mocked
  `service_monitoring_runner`.
- The service-log router (`/external-service-monitoring-service-logs/*`): date-range query and `/latest`."""

import datetime as dt
import os
import tempfile
from unittest.mock import patch

import pytest
from starlette import status
from starlette.testclient import TestClient

from app import models

# --------------------------------------------------- SERVICE ROUTER ---------------------------------------------------


@pytest.fixture
def mock_runner():
    """Patch the module-level `service_monitoring_runner` so we can drive start/stop/status
    without touching the real ServiceRunner singleton (which spawns a thread)."""

    with patch("app.external_service_monitoring.service.routers.service_monitoring_runner") as m:
        m.status.return_value = {
            "service_runner_status": "stopped",
            "service_running": False,
            "service_kwargs": {},
            "period_hours": 24,
            "sleep_until": None,
            "last_log": None,
        }
        yield m


class TestServiceStart:
    endpoint = "/external-service-monitoring-service/start"

    def test_admin_can_start(self, admin_client, mock_runner) -> None:
        resp = admin_client.post(self.endpoint)
        assert resp.status_code == status.HTTP_200_OK
        assert resp.json() == {"detail": "Service runner started (period_hours=24)"}
        mock_runner.start_runner.assert_called_once_with(period_hours=24)

    def test_runner_exception_propagates_as_500(self, admin_client, mock_runner) -> None:
        mock_runner.start_runner.side_effect = RuntimeError("boom")
        resp = admin_client.post(self.endpoint)
        assert resp.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "boom" in resp.json()["detail"]

    def test_non_admin_forbidden(self, regular_user_client, mock_runner) -> None:
        resp = regular_user_client.post(self.endpoint)
        assert resp.status_code == status.HTTP_403_FORBIDDEN
        mock_runner.start_runner.assert_not_called()

    def test_unauthenticated(self, client: TestClient) -> None:
        assert client.post(self.endpoint).status_code == status.HTTP_401_UNAUTHORIZED


class TestServiceStop:
    endpoint = "/external-service-monitoring-service/stop"

    def test_admin_can_stop(self, admin_client, mock_runner) -> None:
        resp = admin_client.post(self.endpoint)
        assert resp.status_code == status.HTTP_200_OK
        assert resp.json() == {"detail": "Service runner stopped"}
        mock_runner.stop_runner.assert_called_once()

    def test_runner_exception_propagates_as_500(self, admin_client, mock_runner) -> None:
        mock_runner.stop_runner.side_effect = RuntimeError("nope")
        resp = admin_client.post(self.endpoint)
        assert resp.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "nope" in resp.json()["detail"]

    def test_non_admin_forbidden(self, regular_user_client, mock_runner) -> None:
        assert regular_user_client.post(self.endpoint).status_code == status.HTTP_403_FORBIDDEN
        mock_runner.stop_runner.assert_not_called()

    def test_unauthenticated(self, client: TestClient) -> None:
        assert client.post(self.endpoint).status_code == status.HTTP_401_UNAUTHORIZED


class TestServiceStatus:
    endpoint = "/external-service-monitoring-service/status"

    def test_admin_gets_status(self, admin_client, mock_runner) -> None:
        resp = admin_client.get(self.endpoint)
        assert resp.status_code == status.HTTP_200_OK
        assert resp.json()["service_runner_status"] == "stopped"
        mock_runner.status.assert_called_once()

    def test_non_admin_forbidden(self, regular_user_client, mock_runner) -> None:
        assert regular_user_client.get(self.endpoint).status_code == status.HTTP_403_FORBIDDEN
        mock_runner.status.assert_not_called()

    def test_unauthenticated(self, client: TestClient) -> None:
        assert client.get(self.endpoint).status_code == status.HTTP_401_UNAUTHORIZED


class TestServiceLogs:
    endpoint = "/external-service-monitoring-service/logs"

    def test_returns_tail_of_log_file(self, admin_client) -> None:
        log_lines = [f"line {i}" for i in range(10)]
        with tempfile.TemporaryDirectory() as tmpdir:
            log_path = os.path.join(tmpdir, "service_monitoring_service.log")
            with open(log_path, "w", encoding="utf-8") as f:
                f.write("\n".join(log_lines) + "\n")

            with patch("app.service_runner.routers.settings") as mock_settings:
                mock_settings.log_directory = tmpdir
                resp = admin_client.get(f"{self.endpoint}?lines=3")

        assert resp.status_code == status.HTTP_200_OK
        body = resp.json()
        assert body["total_lines"] == 10
        assert body["lines"] == log_lines[-3:]

    def test_returns_empty_when_log_missing(self, admin_client) -> None:
        with tempfile.TemporaryDirectory() as tmpdir, patch("app.service_runner.routers.settings") as mock_settings:
            mock_settings.log_directory = tmpdir
            resp = admin_client.get(self.endpoint)

        assert resp.status_code == status.HTTP_200_OK
        assert resp.json() == {"lines": [], "total_lines": 0}

    def test_rejects_out_of_range_lines(self, admin_client) -> None:
        """`lines` is validated as `ge=1, le=10000` by the Query declaration."""

        assert admin_client.get(f"{self.endpoint}?lines=0").status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert admin_client.get(f"{self.endpoint}?lines=10001").status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_non_admin_forbidden(self, regular_user_client) -> None:
        assert regular_user_client.get(self.endpoint).status_code == status.HTTP_403_FORBIDDEN

    def test_unauthenticated(self, client: TestClient) -> None:
        assert client.get(self.endpoint).status_code == status.HTTP_401_UNAUTHORIZED


# ------------------------------------------------- SERVICE-LOG ROUTER -------------------------------------------------


@pytest.fixture
def seeded_service_logs(session) -> list[models.ExternalServiceMonitoringServiceLog]:
    """Three completed runs spaced over the past several days, plus one in-progress run
    (run_duration=None) that must be excluded from the date-range endpoint."""

    now = dt.datetime.now(dt.timezone.utc)
    rows = [
        models.ExternalServiceMonitoringServiceLog(
            run_datetime=now - dt.timedelta(days=5),
            run_duration=1.0,
            is_success=True,
            error_message=None,
        ),
        models.ExternalServiceMonitoringServiceLog(
            run_datetime=now - dt.timedelta(days=2),
            run_duration=2.0,
            is_success=True,
            error_message=None,
        ),
        models.ExternalServiceMonitoringServiceLog(
            run_datetime=now - dt.timedelta(hours=1),
            run_duration=0.5,
            is_success=False,
            error_message="apify failed",
        ),
        # In-progress: must not appear in the date-range response.
        models.ExternalServiceMonitoringServiceLog(
            run_datetime=now,
            run_duration=None,
            is_success=None,
            error_message=None,
        ),
    ]
    session.add_all(rows)
    session.commit()
    for row in rows:
        session.refresh(row)
    return rows


class TestServiceLogsByDateRange:
    endpoint = "/external-service-monitoring-service-logs/"

    def test_no_filters_returns_completed_logs_desc(self, admin_client, seeded_service_logs) -> None:
        resp = admin_client.get(self.endpoint)
        assert resp.status_code == status.HTTP_200_OK
        body = resp.json()
        # 3 completed, in-progress excluded.
        assert len(body) == 3
        run_dts = [r["run_datetime"] for r in body]
        assert run_dts == sorted(run_dts, reverse=True)

    def test_delta_days_filter(self, admin_client, seeded_service_logs) -> None:
        """delta_days=3 drops the 5-day-old run, keeps the two recent ones."""

        resp = admin_client.get(f"{self.endpoint}?delta_days=3")
        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.json()) == 2

    def test_limit_caps_results(self, admin_client, seeded_service_logs) -> None:
        resp = admin_client.get(f"{self.endpoint}?limit=1")
        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.json()) == 1

    def test_empty_db_returns_empty_list(self, admin_client) -> None:
        resp = admin_client.get(self.endpoint)
        assert resp.status_code == status.HTTP_200_OK
        assert resp.json() == []

    def test_non_admin_forbidden(self, regular_user_client) -> None:
        assert regular_user_client.get(self.endpoint).status_code == status.HTTP_403_FORBIDDEN

    def test_unauthenticated(self, client: TestClient) -> None:
        assert client.get(self.endpoint).status_code == status.HTTP_401_UNAUTHORIZED


class TestServiceLogsLatest:
    endpoint = "/external-service-monitoring-service-logs/latest"

    def test_returns_most_recent_log(self, admin_client, seeded_service_logs) -> None:
        resp = admin_client.get(self.endpoint)
        assert resp.status_code == status.HTTP_200_OK
        body = resp.json()
        # The fixture's most recent row is the in-progress one (run_datetime=now), and the
        # /latest endpoint is implemented as `order_by(run_datetime desc).first()` — i.e. it
        # does NOT filter on run_duration. So we expect the in-progress row.
        assert body["is_success"] is None
        assert body["run_duration"] is None

    def test_returns_404_when_empty(self, admin_client) -> None:
        resp = admin_client.get(self.endpoint)
        assert resp.status_code == status.HTTP_404_NOT_FOUND
        assert "No service logs found" in resp.json()["detail"]

    def test_non_admin_forbidden(self, regular_user_client) -> None:
        assert regular_user_client.get(self.endpoint).status_code == status.HTTP_403_FORBIDDEN

    def test_unauthenticated(self, client: TestClient) -> None:
        assert client.get(self.endpoint).status_code == status.HTTP_401_UNAUTHORIZED
