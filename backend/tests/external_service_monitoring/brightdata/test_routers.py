"""HTTP-level tests for the Bright Data history endpoints (usage history + balance snapshot)."""

import datetime as dt

import pytest
from starlette import status
from starlette.testclient import TestClient

from app import models


@pytest.fixture
def seeded_brightdata_usage(session) -> list[models.BrightdataDailyUsage]:
    rows = [
        models.BrightdataDailyUsage(date=dt.date(2026, 6, 1), dataset="LinkedIn", usage_usd=0.01),
        models.BrightdataDailyUsage(date=dt.date(2026, 6, 1), dataset="Indeed", usage_usd=0.02),
        models.BrightdataDailyUsage(date=dt.date(2026, 6, 2), dataset="LinkedIn", usage_usd=0.03),
    ]
    session.add_all(rows)
    session.commit()
    return rows


@pytest.fixture
def seeded_brightdata_balances(session) -> list[models.BrightdataBalance]:
    """See `seeded_apify_balances` — same per-row commit pattern for distinct `created_at`."""

    rows = [
        models.BrightdataBalance(balance_usd=10.0, pending_costs_usd=0.5),
        models.BrightdataBalance(balance_usd=42.75, pending_costs_usd=1.2),
    ]
    for row in rows:
        session.add(row)
        session.commit()
    return rows


class TestBrightdataHistory:
    endpoint = "/external-service-monitoring-history/brightdata"

    def test_returns_one_row_per_date_dataset(self, admin_client, seeded_brightdata_usage) -> None:
        resp = admin_client.get(self.endpoint)
        assert resp.status_code == status.HTTP_200_OK
        body = resp.json()
        assert len(body) == 3
        pairs = {(row["date"], row["dataset"]) for row in body}
        assert pairs == {
            ("2026-06-01", "LinkedIn"),
            ("2026-06-01", "Indeed"),
            ("2026-06-02", "LinkedIn"),
        }

    def test_date_filters(self, admin_client, seeded_brightdata_usage) -> None:
        resp = admin_client.get(f"{self.endpoint}?start_date=2026-06-02")
        assert resp.status_code == status.HTTP_200_OK
        assert all(row["date"] == "2026-06-02" for row in resp.json())

    def test_non_admin_forbidden(self, regular_user_client) -> None:
        assert regular_user_client.get(self.endpoint).status_code == status.HTTP_403_FORBIDDEN

    def test_unauthenticated(self, client: TestClient) -> None:
        assert client.get(self.endpoint).status_code == status.HTTP_401_UNAUTHORIZED


class TestBrightdataBalance:
    endpoint = "/external-service-monitoring-history/brightdata/balance"

    def test_returns_most_recent_snapshot(self, admin_client, seeded_brightdata_balances) -> None:
        resp = admin_client.get(self.endpoint)
        assert resp.status_code == status.HTTP_200_OK
        body = resp.json()
        assert body["balance_usd"] == pytest.approx(42.75)
        assert body["pending_costs_usd"] == pytest.approx(1.2)

    def test_returns_null_when_no_snapshot(self, admin_client) -> None:
        resp = admin_client.get(self.endpoint)
        assert resp.status_code == status.HTTP_200_OK
        assert resp.json() is None

    def test_non_admin_forbidden(self, regular_user_client) -> None:
        assert regular_user_client.get(self.endpoint).status_code == status.HTTP_403_FORBIDDEN

    def test_unauthenticated(self, client: TestClient) -> None:
        assert client.get(self.endpoint).status_code == status.HTTP_401_UNAUTHORIZED
