"""HTTP-level tests for the Anthropic history endpoint (`/provider-monitoring-history/anthropic`)."""

import datetime as dt

import pytest
from starlette import status
from starlette.testclient import TestClient

from app import models


@pytest.fixture
def seeded_anthropic_usage(session) -> list[models.AnthropicDailyUsage]:
    """Three days of Anthropic spend, intentionally inserted out of order to prove the
    endpoint sorts ascending via `filter_by_date`."""

    rows = [
        models.AnthropicDailyUsage(date=dt.date(2026, 6, 3), usage_usd=3.0),
        models.AnthropicDailyUsage(date=dt.date(2026, 6, 1), usage_usd=1.0),
        models.AnthropicDailyUsage(date=dt.date(2026, 6, 2), usage_usd=2.0),
    ]
    session.add_all(rows)
    session.commit()
    return rows


class TestAnthropicHistory:
    endpoint = "/provider-monitoring-history/anthropic"

    def test_returns_rows_in_ascending_date_order(self, admin_client, seeded_anthropic_usage) -> None:
        resp = admin_client.get(self.endpoint)
        assert resp.status_code == status.HTTP_200_OK
        dates = [row["date"] for row in resp.json()]
        assert dates == ["2026-06-01", "2026-06-02", "2026-06-03"]

    def test_start_date_filter(self, admin_client, seeded_anthropic_usage) -> None:
        resp = admin_client.get(f"{self.endpoint}?start_date=2026-06-02")
        assert resp.status_code == status.HTTP_200_OK
        assert [row["date"] for row in resp.json()] == ["2026-06-02", "2026-06-03"]

    def test_end_date_filter(self, admin_client, seeded_anthropic_usage) -> None:
        resp = admin_client.get(f"{self.endpoint}?end_date=2026-06-02")
        assert resp.status_code == status.HTTP_200_OK
        assert [row["date"] for row in resp.json()] == ["2026-06-01", "2026-06-02"]

    def test_empty_db_returns_empty_list(self, admin_client) -> None:
        resp = admin_client.get(self.endpoint)
        assert resp.status_code == status.HTTP_200_OK
        assert resp.json() == []

    def test_non_admin_forbidden(self, regular_user_client) -> None:
        assert regular_user_client.get(self.endpoint).status_code == status.HTTP_403_FORBIDDEN

    def test_unauthenticated(self, client: TestClient) -> None:
        assert client.get(self.endpoint).status_code == status.HTTP_401_UNAUTHORIZED
