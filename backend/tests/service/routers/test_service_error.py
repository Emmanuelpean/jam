"""HTTP-level tests for the unified service-error endpoints (/service-errors)."""

import pytest
from sqlalchemy.orm import Session
from starlette import status
from starlette.testclient import TestClient

from app import models
from tests.base_test import BaseTest
from tests.fixtures.users import FixtureUser


@pytest.fixture
def seeded_service_errors(session: Session) -> list[models.ServiceError]:
    """Seed a mix of acknowledged / unacknowledged errors across services."""

    scraping_log = BaseTest.create_email_scraping_service_log(session)
    rating_log = BaseTest.create_job_rating_service_log(session)

    return [
        BaseTest.create_service_error(
            session,
            error_type="RuntimeError",
            message="scrape boom",
            job_email_scraping_service_log_id=scraping_log.id,
        ),
        BaseTest.create_service_error(
            session,
            error_type="ValueError",
            message="rating boom",
            job_rating_service_log_id=rating_log.id,
        ),
        BaseTest.create_service_error(
            session,
            error_type="TimeoutError",
            message="fetch boom",
            is_acknowledged=True,
        ),
    ]


class TestListServiceErrors(BaseTest):
    endpoint = "/service-errors/"

    def test_returns_all_newest_first(
        self, seeded_service_errors: list[models.ServiceError], test_admin_user: FixtureUser
    ) -> None:
        resp = test_admin_user.client.get(self.endpoint)
        assert resp.status_code == status.HTTP_200_OK
        body = resp.json()
        assert len(body) == 3
        ids = [row["id"] for row in body]
        assert ids == sorted(ids, reverse=True)

    def test_filter_by_service(
        self, seeded_service_errors: list[models.ServiceError], test_admin_user: FixtureUser
    ) -> None:
        rating_log_id = seeded_service_errors[1].job_rating_service_log_id
        resp = test_admin_user.client.get(self.endpoint, params={"job_rating_service_log_id": rating_log_id})
        assert resp.status_code == status.HTTP_200_OK
        body = resp.json()
        assert len(body) == 1
        assert body[0]["message"] == "rating boom"

    def test_filter_by_acknowledged(
        self, seeded_service_errors: list[models.ServiceError], test_admin_user: FixtureUser
    ) -> None:
        resp = test_admin_user.client.get(self.endpoint, params={"is_acknowledged": "false"})
        assert resp.status_code == status.HTTP_200_OK
        body = resp.json()
        assert len(body) == 2
        assert all(not row["is_acknowledged"] for row in body)

    def test_non_admin_forbidden(self, test_regular_user: FixtureUser) -> None:
        assert test_regular_user.client.get(self.endpoint).status_code == status.HTTP_403_FORBIDDEN

    def test_unauthenticated(self, client: TestClient) -> None:
        assert client.get(self.endpoint).status_code == status.HTTP_401_UNAUTHORIZED


class TestAcknowledgeServiceErrors(BaseTest):
    endpoint = "/service-errors/acknowledge"

    def test_acknowledges_errors(
        self, session: Session, seeded_service_errors: list[models.ServiceError], test_admin_user: FixtureUser
    ) -> None:
        ids = [seeded_service_errors[0].id, seeded_service_errors[1].id]
        resp = test_admin_user.client.put(self.endpoint, json={"ids": ids, "is_acknowledged": True})
        assert resp.status_code == status.HTTP_200_OK
        assert all(row["is_acknowledged"] for row in resp.json())

        for error_id in ids:
            error = self.get_by_id(session, models.ServiceError, error_id)
            session.refresh(error)
            assert error.is_acknowledged is True

    def test_unacknowledge(
        self, session: Session, seeded_service_errors: list[models.ServiceError], test_admin_user: FixtureUser
    ) -> None:
        already_ack = seeded_service_errors[2].id
        resp = test_admin_user.client.put(self.endpoint, json={"ids": [already_ack], "is_acknowledged": False})
        assert resp.status_code == status.HTTP_200_OK
        assert resp.json()[0]["is_acknowledged"] is False

    def test_non_admin_forbidden(self, test_regular_user: FixtureUser) -> None:
        resp = test_regular_user.client.put(self.endpoint, json={"ids": [1], "is_acknowledged": True})
        assert resp.status_code == status.HTTP_403_FORBIDDEN
