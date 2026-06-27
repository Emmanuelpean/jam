"""HTTP-level tests for the generic /services configuration router."""

import datetime as dt

import pytest
from starlette import status
from starlette.testclient import TestClient

from app.models import Service


@pytest.fixture
def seeded_services(session) -> list[Service]:
    """Two scheduled services: one disabled with no schedule, one enabled and due."""

    now = dt.datetime.now(dt.timezone.utc)
    rows = [
        Service(
            name="email_scraper_service",
            display_name="Job Email Scraping",
            run_period_hours=3.0,
            parameters={"timedelta_days": 3},
            is_enabled=False,
            is_running=False,
            next_run_at=None,
        ),
        Service(
            name="job_rating_service",
            display_name="Job Rating",
            run_period_hours=3.0,
            parameters={},
            is_enabled=True,
            is_running=False,
            next_run_at=now,
        ),
    ]
    session.add_all(rows)
    session.commit()
    for row in rows:
        session.refresh(row)
    return rows


class TestListServices:
    endpoint = "/services/"

    def test_admin_lists_all_services(self, admin_client, seeded_services) -> None:
        resp = admin_client.get(self.endpoint)
        assert resp.status_code == status.HTTP_200_OK
        body = resp.json()
        assert {s["name"] for s in body} == {"email_scraper_service", "job_rating_service"}

    def test_empty_db_returns_empty_list(self, admin_client) -> None:
        resp = admin_client.get(self.endpoint)
        assert resp.status_code == status.HTTP_200_OK
        assert resp.json() == []

    def test_non_admin_forbidden(self, regular_user_client, seeded_services) -> None:
        assert regular_user_client.get(self.endpoint).status_code == status.HTTP_403_FORBIDDEN

    def test_unauthenticated(self, client: TestClient) -> None:
        assert client.get(self.endpoint).status_code == status.HTTP_401_UNAUTHORIZED


class TestUpdateService:
    def test_admin_updates_period_and_parameters(self, admin_client, seeded_services) -> None:
        resp = admin_client.patch(
            "/services/email_scraper_service",
            json={"run_period_hours": 6, "parameters": {"timedelta_days": 7}},
        )
        assert resp.status_code == status.HTTP_200_OK
        body = resp.json()
        assert body["run_period_hours"] == 6
        assert body["parameters"] == {"timedelta_days": 7}

    def test_enabling_seeds_next_run_at(self, admin_client, seeded_services) -> None:
        """Enabling a service with no schedule seeds next_run_at so it runs soon."""

        resp = admin_client.patch("/services/email_scraper_service", json={"is_enabled": True})
        assert resp.status_code == status.HTTP_200_OK
        body = resp.json()
        assert body["is_enabled"] is True
        assert body["next_run_at"] is not None

    def test_disabling_service(self, admin_client, seeded_services) -> None:
        resp = admin_client.patch("/services/job_rating_service", json={"is_enabled": False})
        assert resp.status_code == status.HTTP_200_OK
        assert resp.json()["is_enabled"] is False

    def test_rejects_non_positive_period(self, admin_client, seeded_services) -> None:
        resp = admin_client.patch("/services/email_scraper_service", json={"run_period_hours": 0})
        assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_unknown_service_404(self, admin_client) -> None:
        resp = admin_client.patch("/services/nope", json={"is_enabled": True})
        assert resp.status_code == status.HTTP_404_NOT_FOUND

    def test_non_admin_forbidden(self, regular_user_client, seeded_services) -> None:
        resp = regular_user_client.patch("/services/job_rating_service", json={"is_enabled": False})
        assert resp.status_code == status.HTTP_403_FORBIDDEN

    def test_unauthenticated(self, client: TestClient, seeded_services) -> None:
        resp = client.patch("/services/job_rating_service", json={"is_enabled": False})
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED


class TestRunNow:
    def test_admin_can_trigger_run_now(self, admin_client, seeded_services) -> None:
        """run-now sets next_run_at to (approximately) now."""

        before = dt.datetime.now(dt.timezone.utc)
        resp = admin_client.post("/services/email_scraper_service/run-now")
        assert resp.status_code == status.HTTP_200_OK
        next_run = dt.datetime.fromisoformat(resp.json()["next_run_at"])
        assert abs((next_run - before).total_seconds()) < 60

    def test_unknown_service_404(self, admin_client) -> None:
        assert admin_client.post("/services/nope/run-now").status_code == status.HTTP_404_NOT_FOUND

    def test_non_admin_forbidden(self, regular_user_client, seeded_services) -> None:
        resp = regular_user_client.post("/services/job_rating_service/run-now")
        assert resp.status_code == status.HTTP_403_FORBIDDEN

    def test_unauthenticated(self, client: TestClient, seeded_services) -> None:
        assert client.post("/services/job_rating_service/run-now").status_code == status.HTTP_401_UNAUTHORIZED
