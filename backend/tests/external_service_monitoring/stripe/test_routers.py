"""HTTP-level tests for the Stripe history endpoint (`/external-service-monitoring-history/stripe`)."""

import datetime as dt

import pytest
from starlette import status
from starlette.testclient import TestClient

from app import models


@pytest.fixture
def seeded_stripe_income(session) -> list[models.StripeDailyIncome]:
    rows = [
        models.StripeDailyIncome(date=dt.date(2026, 6, 1), gross_gbp=10.0, net_gbp=9.5),
        models.StripeDailyIncome(date=dt.date(2026, 6, 2), gross_gbp=20.0, net_gbp=19.0),
    ]
    session.add_all(rows)
    session.commit()
    return rows


class TestStripeHistory:
    endpoint = "/external-service-monitoring-history/stripe"

    def test_returns_rows_ascending(self, admin_client, seeded_stripe_income) -> None:
        resp = admin_client.get(self.endpoint)
        assert resp.status_code == status.HTTP_200_OK
        body = resp.json()
        assert [row["date"] for row in body] == ["2026-06-01", "2026-06-02"]
        assert body[0]["gross_gbp"] == pytest.approx(10.0)
        assert body[0]["net_gbp"] == pytest.approx(9.5)

    def test_date_filters(self, admin_client, seeded_stripe_income) -> None:
        resp = admin_client.get(f"{self.endpoint}?end_date=2026-06-01")
        assert resp.status_code == status.HTTP_200_OK
        assert [row["date"] for row in resp.json()] == ["2026-06-01"]

    def test_non_admin_forbidden(self, regular_user_client) -> None:
        assert regular_user_client.get(self.endpoint).status_code == status.HTTP_403_FORBIDDEN

    def test_unauthenticated(self, client: TestClient) -> None:
        assert client.get(self.endpoint).status_code == status.HTTP_401_UNAUTHORIZED
