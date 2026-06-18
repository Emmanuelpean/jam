"""HTTP-level tests for the Apify history endpoints (usage history + balance snapshot)."""

import datetime as dt

import pytest
from starlette import status
from starlette.testclient import TestClient

from app import models


@pytest.fixture
def seeded_apify_usage(session) -> list[models.ApifyDailyUsage]:
    rows = [
        models.ApifyDailyUsage(date=dt.date(2026, 6, 1), usage_usd=0.5),
        models.ApifyDailyUsage(date=dt.date(2026, 6, 2), usage_usd=1.5),
    ]
    session.add_all(rows)
    session.commit()
    return rows


@pytest.fixture
def seeded_apify_balances(session) -> list[models.ApifyBalance]:
    """Two balance snapshots — the endpoint should return the most recent by `created_at`.
    Commit one at a time so the server-side `now()` default produces distinct timestamps
    (each commit is its own transaction); a batched commit would tie them."""

    rows = [models.ApifyBalance(limit_usd=50.0), models.ApifyBalance(limit_usd=100.0)]
    for row in rows:
        session.add(row)
        session.commit()
    return rows


class TestApifyHistory:
    endpoint = "/external-service-monitoring-history/apify"

    def test_returns_rows_ascending(self, admin_client, seeded_apify_usage) -> None:
        resp = admin_client.get(self.endpoint)
        assert resp.status_code == status.HTTP_200_OK
        body = resp.json()
        assert [row["date"] for row in body] == ["2026-06-01", "2026-06-02"]
        assert body[0]["usage_usd"] == pytest.approx(0.5)

    def test_date_filters(self, admin_client, seeded_apify_usage) -> None:
        resp = admin_client.get(f"{self.endpoint}?start_date=2026-06-02&end_date=2026-06-02")
        assert resp.status_code == status.HTTP_200_OK
        assert [row["date"] for row in resp.json()] == ["2026-06-02"]

    def test_non_admin_forbidden(self, regular_user_client) -> None:
        assert regular_user_client.get(self.endpoint).status_code == status.HTTP_403_FORBIDDEN

    def test_unauthenticated(self, client: TestClient) -> None:
        assert client.get(self.endpoint).status_code == status.HTTP_401_UNAUTHORIZED


class TestApifyBalance:
    endpoint = "/external-service-monitoring-history/apify/balance"

    def test_returns_most_recent_snapshot(self, admin_client, seeded_apify_balances) -> None:
        resp = admin_client.get(self.endpoint)
        assert resp.status_code == status.HTTP_200_OK
        body = resp.json()
        assert body is not None
        assert body["limit_usd"] == pytest.approx(100.0)

    def test_returns_null_when_no_snapshot(self, admin_client) -> None:
        resp = admin_client.get(self.endpoint)
        assert resp.status_code == status.HTTP_200_OK
        assert resp.json() is None

    def test_non_admin_forbidden(self, regular_user_client) -> None:
        assert regular_user_client.get(self.endpoint).status_code == status.HTTP_403_FORBIDDEN

    def test_unauthenticated(self, client: TestClient) -> None:
        assert client.get(self.endpoint).status_code == status.HTTP_401_UNAUTHORIZED
