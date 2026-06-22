"""HTTP-level tests for the unified service-error endpoints (/service-errors)."""

import pytest
from starlette import status
from starlette.testclient import TestClient

from app import models


@pytest.fixture
def seeded_service_errors(session, test_job_scraping_service_logs, test_job_rating_service_logs) -> list:
    """Seed a mix of acknowledged / unacknowledged errors across services."""

    rows = [
        models.Error(
            error_type="RuntimeError",
            message="scrape boom",
            job_email_scraping_service_log_id=test_job_scraping_service_logs[0].id,
        ),
        models.Error(
            error_type="ValueError",
            message="rating boom",
            job_rating_service_log_id=test_job_rating_service_logs[0].id,
        ),
        models.Error(
            error_type="TimeoutError",
            message="fetch boom",
            is_acknowledged=True,
        ),
    ]
    session.add_all(rows)
    session.commit()
    for row in rows:
        session.refresh(row)
    return rows


class TestListServiceErrors:
    endpoint = "/service-errors/"

    def test_returns_all_newest_first(self, admin_client, seeded_service_errors) -> None:
        resp = admin_client.get(self.endpoint)
        assert resp.status_code == status.HTTP_200_OK
        body = resp.json()
        assert len(body) == 3
        ids = [row["id"] for row in body]
        assert ids == sorted(ids, reverse=True)

    def test_filter_by_service(self, admin_client, seeded_service_errors, test_job_rating_service_logs) -> None:
        resp = admin_client.get(self.endpoint, params={"job_rating_service_log_id": test_job_rating_service_logs[0].id})
        assert resp.status_code == status.HTTP_200_OK
        body = resp.json()
        assert len(body) == 1
        assert body[0]["message"] == "rating boom"

    def test_filter_by_acknowledged(self, admin_client, seeded_service_errors) -> None:
        resp = admin_client.get(self.endpoint, params={"is_acknowledged": "false"})
        assert resp.status_code == status.HTTP_200_OK
        body = resp.json()
        assert len(body) == 2
        assert all(not row["is_acknowledged"] for row in body)

    def test_non_admin_forbidden(self, regular_user_client) -> None:
        assert regular_user_client.get(self.endpoint).status_code == status.HTTP_403_FORBIDDEN

    def test_unauthenticated(self, client: TestClient) -> None:
        assert client.get(self.endpoint).status_code == status.HTTP_401_UNAUTHORIZED


class TestAcknowledgeServiceErrors:
    endpoint = "/service-errors/acknowledge"

    def test_acknowledges_errors(self, admin_client, session, seeded_service_errors) -> None:
        ids = [seeded_service_errors[0].id, seeded_service_errors[1].id]
        resp = admin_client.patch(self.endpoint, json={"ids": ids, "is_acknowledged": True})
        assert resp.status_code == status.HTTP_200_OK
        assert all(row["is_acknowledged"] for row in resp.json())

        for error_id in ids:
            error = session.get(models.Error, error_id)
            session.refresh(error)
            assert error.is_acknowledged is True

    def test_unacknowledge(self, admin_client, session, seeded_service_errors) -> None:
        already_ack = seeded_service_errors[2].id
        resp = admin_client.patch(self.endpoint, json={"ids": [already_ack], "is_acknowledged": False})
        assert resp.status_code == status.HTTP_200_OK
        assert resp.json()[0]["is_acknowledged"] is False

    def test_non_admin_forbidden(self, regular_user_client) -> None:
        resp = regular_user_client.patch(self.endpoint, json={"ids": [1], "is_acknowledged": True})
        assert resp.status_code == status.HTTP_403_FORBIDDEN
