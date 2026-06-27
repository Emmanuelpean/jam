"""HTTP-level tests for the external-service-monitoring service-log router.

Covers the service-log router (`/service-logs/service_monitoring_service/*`): date-range query and
`/latest`. Run control now lives on the generic `/services` router (see
`tests/service/test_service_routers.py`)."""

import datetime as dt

import pytest
from starlette import status
from starlette.testclient import TestClient

from app import models


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
        ),
        models.ExternalServiceMonitoringServiceLog(
            run_datetime=now - dt.timedelta(days=2),
            run_duration=2.0,
        ),
        models.ExternalServiceMonitoringServiceLog(
            run_datetime=now - dt.timedelta(hours=1),
            run_duration=0.5,
        ),
        # In-progress: must not appear in the date-range response.
        models.ExternalServiceMonitoringServiceLog(
            run_datetime=now,
            run_duration=None,
        ),
    ]
    session.add_all(rows)
    session.commit()
    for row in rows:
        session.refresh(row)
    return rows


class TestServiceLogsByDateRange:
    endpoint = "/service-logs/service_monitoring_service/"

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
    endpoint = "/service-logs/service_monitoring_service/latest"

    def test_returns_most_recent_log(self, admin_client, seeded_service_logs) -> None:
        resp = admin_client.get(self.endpoint)
        assert resp.status_code == status.HTTP_200_OK
        body = resp.json()
        # The fixture's most recent row is the in-progress one (run_datetime=now), and the
        # /latest endpoint is implemented as `order_by(run_datetime desc).first()` — i.e. it
        # does NOT filter on run_duration. So we expect the in-progress row. is_success is derived
        # from run_datetime + critical errors, so an in-progress run with no errors reads True.
        assert body["is_success"] is True
        assert body["run_duration"] is None

    def test_returns_404_when_empty(self, admin_client) -> None:
        resp = admin_client.get(self.endpoint)
        assert resp.status_code == status.HTTP_404_NOT_FOUND
        assert "No service logs found" in resp.json()["detail"]

    def test_non_admin_forbidden(self, regular_user_client) -> None:
        assert regular_user_client.get(self.endpoint).status_code == status.HTTP_403_FORBIDDEN

    def test_unauthenticated(self, client: TestClient) -> None:
        assert client.get(self.endpoint).status_code == status.HTTP_401_UNAUTHORIZED
