"""Tests for app/service/routers/service.py and the generic service-log endpoints.

The service-log endpoints (`/service-logs/{service_name}/` and `/service-logs/{service_name}/latest`)
are a single, registry-driven handler shared by every service, so their behaviour is tested once here
rather than duplicated per service. TestServiceLogList and TestLatestServiceLog are parametrized
over representative services; test_every_registered_service_resolves is a thin smoke check that each
service registered in SERVICE_REGISTRY resolves to its model and serialises against its registered
schema.

The log-file endpoint (`/services/{name}/logs`) has its logic inlined into the route handler, so it is
tested over HTTP in TestGetServiceLogs."""

import datetime as dt
import os
import tempfile
from unittest.mock import patch

import pytest
from starlette import status
from starlette.testclient import TestClient

from app.service.registry import SERVICE_REGISTRY
from tests.conftest import make_undefined_method_params

# The services whose logs are exposed over the generic endpoints. Kept explicit (rather than derived
# from the registry) so that adding or removing a service is a deliberate, reviewed change; the registry
# is asserted to match in test_registry_matches_expected_services.
EXPECTED_SERVICES = {
    "email_scraper_service",
    "job_rating_service",
    "provider_monitoring_service",
}

# Two representative services that the full behavioural suite runs against. The handler is generic, so
# covering it against more than one registered service guards the registry resolution without retesting
# identical logic for every service.
REPRESENTATIVE_SERVICES = ["email_scraper_service", "job_rating_service"]


@pytest.fixture
def seed_service_logs(session):
    """Return a helper that seeds a service's logs: three completed runs spaced over the past several
    days plus one in-progress run (run_duration=None) that the date-range endpoint must exclude."""

    def _seed(service_name: str):
        model = SERVICE_REGISTRY[service_name].log_model
        now = dt.datetime.now(dt.timezone.utc)
        rows = [
            model(run_datetime=now - dt.timedelta(days=5), run_duration=1.0),
            model(run_datetime=now - dt.timedelta(days=2), run_duration=2.0),
            model(run_datetime=now - dt.timedelta(hours=1), run_duration=0.5),
            model(run_datetime=now, run_duration=None),  # in-progress: excluded from the list endpoint
        ]
        session.add_all(rows)
        session.commit()
        for row in rows:
            session.refresh(row)
        return rows

    return _seed


# ----------------------------------------------- GET SERVICE LOGS (FILE) ----------------------------------------


class TestGetServiceLogs:
    def test_returns_empty_when_log_file_missing(self, admin_client) -> None:
        """Returns zero lines when the log file does not exist."""

        with tempfile.TemporaryDirectory() as tmpdir:
            with patch("app.utilities.logger.settings") as mock_settings:
                mock_settings.log_directory = tmpdir
                resp = admin_client.get("/services/nonexistent/logs")

        assert resp.status_code == status.HTTP_200_OK
        assert resp.json() == {"lines": [], "total_lines": 0}

    def test_returns_last_n_lines_of_small_file(self, admin_client) -> None:
        """Returns the correct tail lines from a file under 1 MB."""

        log_lines = [f"line {i}" for i in range(20)]
        with tempfile.TemporaryDirectory() as tmpdir:
            with open(os.path.join(tmpdir, "test_service.log"), "w", encoding="utf-8") as f:
                f.write("\n".join(log_lines) + "\n")

            with patch("app.utilities.logger.settings") as mock_settings:
                mock_settings.log_directory = tmpdir
                resp = admin_client.get("/services/test_service/logs?lines=5")

        body = resp.json()
        assert body["total_lines"] == 20
        assert body["lines"] == log_lines[-5:]

    def test_returns_all_lines_when_fewer_than_requested(self, admin_client) -> None:
        """Returns all lines when the file has fewer lines than requested."""

        log_lines = ["alpha", "beta", "gamma"]
        with tempfile.TemporaryDirectory() as tmpdir:
            with open(os.path.join(tmpdir, "svc.log"), "w", encoding="utf-8") as f:
                f.write("\n".join(log_lines) + "\n")

            with patch("app.utilities.logger.settings") as mock_settings:
                mock_settings.log_directory = tmpdir
                resp = admin_client.get("/services/svc/logs?lines=100")

        body = resp.json()
        assert body["lines"] == log_lines
        assert body["total_lines"] == 3

    def test_rejects_out_of_range_lines(self, admin_client) -> None:
        """`lines` is validated as `ge=1, le=10000` by the Query declaration."""

        assert admin_client.get("/services/svc/logs?lines=0").status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_non_admin_forbidden(self, regular_user_client) -> None:
        """Non-admin users receive 403."""

        assert regular_user_client.get("/services/svc/logs").status_code == status.HTTP_403_FORBIDDEN

    def test_unauthenticated(self, client: TestClient) -> None:
        """Unauthenticated requests receive 401."""

        assert client.get("/services/svc/logs").status_code == status.HTTP_401_UNAUTHORIZED


# ------------------------------------------------- LIST (DATE RANGE) --------------------------------------------


@pytest.mark.parametrize("service_name", REPRESENTATIVE_SERVICES)
class TestServiceLogList:
    """The generic GET /service-logs/{service_name}/ listing endpoint."""

    @staticmethod
    def endpoint(service_name: str) -> str:
        return f"/service-logs/{service_name}/"

    def test_no_filters_returns_completed_logs_desc(self, admin_client, seed_service_logs, service_name) -> None:
        """Returns the completed runs newest-first; the in-progress run is excluded."""

        rows = seed_service_logs(service_name)
        in_progress = next(r for r in rows if r.run_duration is None)

        resp = admin_client.get(self.endpoint(service_name))
        assert resp.status_code == status.HTTP_200_OK
        body = resp.json()
        assert len(body) == 3
        ids = [r["id"] for r in body]
        assert in_progress.id not in ids
        run_dts = [r["run_datetime"] for r in body]
        assert run_dts == sorted(run_dts, reverse=True)

    def test_start_date_filter(self, admin_client, seed_service_logs, service_name) -> None:
        """start_date excludes runs older than the cutoff."""

        seed_service_logs(service_name)
        start_date = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=3)).isoformat()
        resp = admin_client.get(self.endpoint(service_name), params={"start_date": start_date})
        assert resp.status_code == status.HTTP_200_OK
        body = resp.json()
        assert len(body) == 2
        assert all(r["run_datetime"] >= start_date for r in body)

    def test_end_date_filter(self, admin_client, seed_service_logs, service_name) -> None:
        """end_date excludes runs newer than the cutoff."""

        seed_service_logs(service_name)
        end_date = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=3)).isoformat()
        resp = admin_client.get(self.endpoint(service_name), params={"end_date": end_date})
        assert resp.status_code == status.HTTP_200_OK
        body = resp.json()
        assert len(body) == 1
        assert all(r["run_datetime"] <= end_date for r in body)

    def test_date_range_filter(self, admin_client, seed_service_logs, service_name) -> None:
        """A start_date/end_date window returns only runs inside it."""

        seed_service_logs(service_name)
        now = dt.datetime.now(dt.timezone.utc)
        start_date = (now - dt.timedelta(days=7)).isoformat()
        end_date = (now - dt.timedelta(days=1)).isoformat()
        resp = admin_client.get(self.endpoint(service_name), params={"start_date": start_date, "end_date": end_date})
        assert resp.status_code == status.HTTP_200_OK
        body = resp.json()
        assert len(body) == 2
        assert all(start_date <= r["run_datetime"] <= end_date for r in body)

    def test_delta_days_filter(self, admin_client, seed_service_logs, service_name) -> None:
        """delta_days=3 drops the 5-day-old run, keeping the two recent ones."""

        seed_service_logs(service_name)
        resp = admin_client.get(self.endpoint(service_name), params={"delta_days": 3})
        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.json()) == 2

    @pytest.mark.parametrize("limit", [1, 2, 3])
    def test_limit_caps_results(self, admin_client, seed_service_logs, service_name, limit) -> None:
        """limit caps the number of returned rows."""

        seed_service_logs(service_name)
        resp = admin_client.get(self.endpoint(service_name), params={"limit": limit})
        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.json()) == limit

    def test_empty_db_returns_empty_list(self, admin_client, service_name) -> None:
        """With no logs the endpoint returns an empty list (not a 404)."""

        resp = admin_client.get(self.endpoint(service_name))
        assert resp.status_code == status.HTTP_200_OK
        assert resp.json() == []

    def test_non_admin_forbidden(self, regular_user_client, service_name) -> None:
        """Non-admin users receive 403."""

        assert regular_user_client.get(self.endpoint(service_name)).status_code == status.HTTP_403_FORBIDDEN

    def test_unauthenticated(self, client: TestClient, service_name) -> None:
        """Unauthenticated requests receive 401."""

        assert client.get(self.endpoint(service_name)).status_code == status.HTTP_401_UNAUTHORIZED


# -------------------------------------------------- GET LATEST --------------------------------------------------


@pytest.mark.parametrize("service_name", REPRESENTATIVE_SERVICES)
class TestLatestServiceLog:
    """The generic GET /service-logs/{service_name}/latest endpoint."""

    @staticmethod
    def endpoint(service_name: str) -> str:
        return f"/service-logs/{service_name}/latest"

    def test_returns_most_recent_log(self, admin_client, seed_service_logs, service_name) -> None:
        """Returns the single most-recent run. /latest does not filter on run_duration, so the
        in-progress run (the newest row) is returned."""

        rows = seed_service_logs(service_name)
        most_recent = max(rows, key=lambda r: r.run_datetime)
        resp = admin_client.get(self.endpoint(service_name))
        assert resp.status_code == status.HTTP_200_OK
        assert resp.json()["id"] == most_recent.id

    def test_returns_404_when_no_logs(self, admin_client, service_name) -> None:
        """Returns 404 when the service has no log entries."""

        resp = admin_client.get(self.endpoint(service_name))
        assert resp.status_code == status.HTTP_404_NOT_FOUND
        assert "No service logs found" in resp.json()["detail"]

    def test_non_admin_forbidden(self, regular_user_client, service_name) -> None:
        """Non-admin users receive 403."""

        assert regular_user_client.get(self.endpoint(service_name)).status_code == status.HTTP_403_FORBIDDEN

    def test_unauthenticated(self, client: TestClient, service_name) -> None:
        """Unauthenticated requests receive 401."""

        assert client.get(self.endpoint(service_name)).status_code == status.HTTP_401_UNAUTHORIZED


# ----------------------------------------- UNKNOWN SERVICE / REGISTRY -------------------------------------------


class TestUnknownService:
    def test_list_unknown_service_404(self, admin_client) -> None:
        """An unknown service name returns 404 on the list endpoint."""

        resp = admin_client.get("/service-logs/nope/")
        assert resp.status_code == status.HTTP_404_NOT_FOUND
        assert "Unknown service" in resp.json()["detail"]

    def test_latest_unknown_service_404(self, admin_client) -> None:
        """An unknown service name returns 404 on the latest endpoint."""

        assert admin_client.get("/service-logs/nope/latest").status_code == status.HTTP_404_NOT_FOUND


class TestUndefinedMethods:
    DEFINED_ACTIONS = ["GET_ALL"]
    UNDEFINED_ACTIONS = ["PUT", "POST", "GET_ONE", "DELETE"]

    @pytest.mark.parametrize("service_name", REPRESENTATIVE_SERVICES)
    @pytest.mark.parametrize(
        "http_method,path_suffix,expected_status",
        make_undefined_method_params(DEFINED_ACTIONS, UNDEFINED_ACTIONS),
    )
    def test_undefined_methods(self, admin_client, service_name, http_method, path_suffix, expected_status) -> None:
        response = admin_client.request(http_method, f"/service-logs/{service_name}{path_suffix}")
        assert response.status_code == expected_status


# ---------------------------------------- EVERY REGISTERED SERVICE RESOLVES -------------------------------------


def test_registry_matches_expected_services() -> None:
    """Every service exposed over the log endpoints is accounted for; flags drift if one is added/removed."""

    assert set(SERVICE_REGISTRY) == EXPECTED_SERVICES


@pytest.mark.parametrize("service_name", sorted(EXPECTED_SERVICES))
def test_every_registered_service_resolves(admin_client, session, service_name) -> None:
    """Each registered service resolves to its log model and serialises against its registered schema."""

    definition = SERVICE_REGISTRY[service_name]
    row = definition.log_model(run_datetime=dt.datetime.now(dt.timezone.utc), run_duration=1.0)
    session.add(row)
    session.commit()
    session.refresh(row)

    list_resp = admin_client.get(f"/service-logs/{service_name}/")
    assert list_resp.status_code == status.HTTP_200_OK
    body = list_resp.json()
    assert [r["id"] for r in body] == [row.id]
    # The response serialises through the service's registered output schema.
    definition.log_schema.model_validate(body[0])

    latest_resp = admin_client.get(f"/service-logs/{service_name}/latest")
    assert latest_resp.status_code == status.HTTP_200_OK
    assert latest_resp.json()["id"] == row.id
    definition.log_schema.model_validate(latest_resp.json())
