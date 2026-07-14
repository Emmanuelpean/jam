"""HTTP-level tests for the generic /services configuration router."""

import datetime as dt

import pytest
from sqlalchemy.orm import Session
from starlette import status
from starlette.testclient import TestClient

from app.models import Service
from tests.base_test import BaseTest
from tests.fixtures.users import FixtureUser


@pytest.fixture
def seeded_services(session: Session) -> list[Service]:
    """Two scheduled services: one disabled with no schedule, one enabled and due."""

    return [
        BaseTest.create_service(
            session,
            name="email_scraper_service",
            display_name="Job Email Scraping",
            parameters={"timedelta_days": 3},
            is_enabled=False,
            next_run_at=None,
        ),
        BaseTest.create_service(
            session,
            name="job_rating_service",
            display_name="Job Rating",
            next_run_at=dt.datetime.now(dt.timezone.utc),
        ),
    ]


class TestListServices(BaseTest):
    endpoint = "/services/"

    def test_admin_lists_all_services(self, seeded_services: list[Service], test_admin_user: FixtureUser) -> None:
        resp = test_admin_user.client.get(self.endpoint)
        assert resp.status_code == status.HTTP_200_OK
        body = resp.json()
        assert {s["name"] for s in body} == {"email_scraper_service", "job_rating_service"}

    def test_empty_db_returns_empty_list(self, test_admin_user: FixtureUser) -> None:
        resp = test_admin_user.client.get(self.endpoint)
        assert resp.status_code == status.HTTP_200_OK
        assert resp.json() == []

    def test_non_admin_forbidden(self, seeded_services: list[Service], test_regular_user: FixtureUser) -> None:
        assert test_regular_user.client.get(self.endpoint).status_code == status.HTTP_403_FORBIDDEN

    def test_unauthenticated(self, client: TestClient) -> None:
        assert client.get(self.endpoint).status_code == status.HTTP_401_UNAUTHORIZED


class TestUpdateService(BaseTest):
    endpoint = "/services"

    def test_admin_updates_period_and_parameters(
        self, seeded_services: list[Service], test_admin_user: FixtureUser
    ) -> None:
        resp = test_admin_user.client.patch(
            f"{self.endpoint}/email_scraper_service",
            json={"run_period_hours": 6, "parameters": {"timedelta_days": 7}},
        )
        assert resp.status_code == status.HTTP_200_OK
        body = resp.json()
        assert body["run_period_hours"] == 6
        assert body["parameters"] == {"timedelta_days": 7}

    def test_enabling_seeds_next_run_at(self, seeded_services: list[Service], test_admin_user: FixtureUser) -> None:
        """Enabling a service with no schedule seeds next_run_at so it runs soon."""

        resp = test_admin_user.client.patch(f"{self.endpoint}/email_scraper_service", json={"is_enabled": True})
        assert resp.status_code == status.HTTP_200_OK
        body = resp.json()
        assert body["is_enabled"] is True
        assert body["next_run_at"] is not None

    def test_disabling_service(self, seeded_services: list[Service], test_admin_user: FixtureUser) -> None:
        resp = test_admin_user.client.patch(f"{self.endpoint}/job_rating_service", json={"is_enabled": False})
        assert resp.status_code == status.HTTP_200_OK
        assert resp.json()["is_enabled"] is False

    def test_rejects_non_positive_period(self, seeded_services: list[Service], test_admin_user: FixtureUser) -> None:
        resp = test_admin_user.client.patch(f"{self.endpoint}/email_scraper_service", json={"run_period_hours": 0})
        assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_unknown_service_404(self, test_admin_user: FixtureUser) -> None:
        resp = test_admin_user.client.patch(f"{self.endpoint}/nope", json={"is_enabled": True})
        assert resp.status_code == status.HTTP_404_NOT_FOUND

    def test_non_admin_forbidden(self, seeded_services: list[Service], test_regular_user: FixtureUser) -> None:
        resp = test_regular_user.client.patch(f"{self.endpoint}/job_rating_service", json={"is_enabled": False})
        assert resp.status_code == status.HTTP_403_FORBIDDEN

    def test_unauthenticated(self, client: TestClient, seeded_services: list[Service]) -> None:
        resp = client.patch(f"{self.endpoint}/job_rating_service", json={"is_enabled": False})
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED


class TestRunNow(BaseTest):
    endpoint = "/services"

    def test_admin_can_trigger_run_now(self, seeded_services: list[Service], test_admin_user: FixtureUser) -> None:
        """run-now sets next_run_at to (approximately) now."""

        before = dt.datetime.now(dt.timezone.utc)
        resp = test_admin_user.client.post(f"{self.endpoint}/email_scraper_service/run-now")
        assert resp.status_code == status.HTTP_200_OK
        next_run = dt.datetime.fromisoformat(resp.json()["next_run_at"])
        assert abs((next_run - before).total_seconds()) < 60

    def test_unknown_service_404(self, test_admin_user: FixtureUser) -> None:
        assert test_admin_user.client.post(f"{self.endpoint}/nope/run-now").status_code == status.HTTP_404_NOT_FOUND

    def test_non_admin_forbidden(self, seeded_services: list[Service], test_regular_user: FixtureUser) -> None:
        resp = test_regular_user.client.post(f"{self.endpoint}/job_rating_service/run-now")
        assert resp.status_code == status.HTTP_403_FORBIDDEN

    def test_unauthenticated(self, client: TestClient, seeded_services: list[Service]) -> None:
        assert client.post(f"{self.endpoint}/job_rating_service/run-now").status_code == status.HTTP_401_UNAUTHORIZED
