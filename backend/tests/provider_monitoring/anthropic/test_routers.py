"""HTTP-level tests for the Anthropic history endpoint (`/provider-monitoring-history/anthropic`)."""

import datetime as dt

import pytest
from sqlalchemy.orm import Session
from starlette import status
from starlette.testclient import TestClient

from app import models
from tests.base_test import BaseTest
from tests.fixtures.users import FixtureUser


@pytest.fixture
def seeded_anthropic_usage(session: Session) -> list[models.AnthropicDailyUsage]:
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


class TestAnthropicHistory(BaseTest):
    endpoint = "/provider-monitoring-history/anthropic"

    def test_returns_rows_in_ascending_date_order(
        self,
        seeded_anthropic_usage: list[models.AnthropicDailyUsage],
        test_admin_user: FixtureUser,
    ) -> None:
        resp = test_admin_user.client.get(self.endpoint)
        assert resp.status_code == status.HTTP_200_OK
        dates = [row["date"] for row in resp.json()]
        assert dates == ["2026-06-01", "2026-06-02", "2026-06-03"]

    def test_start_date_filter(
        self,
        seeded_anthropic_usage: list[models.AnthropicDailyUsage],
        test_admin_user: FixtureUser,
    ) -> None:
        resp = test_admin_user.client.get(f"{self.endpoint}?start_date=2026-06-02")
        assert resp.status_code == status.HTTP_200_OK
        assert [row["date"] for row in resp.json()] == ["2026-06-02", "2026-06-03"]

    def test_end_date_filter(
        self,
        seeded_anthropic_usage: list[models.AnthropicDailyUsage],
        test_admin_user: FixtureUser,
    ) -> None:
        resp = test_admin_user.client.get(f"{self.endpoint}?end_date=2026-06-02")
        assert resp.status_code == status.HTTP_200_OK
        assert [row["date"] for row in resp.json()] == ["2026-06-01", "2026-06-02"]

    def test_empty_db_returns_empty_list(self, test_admin_user: FixtureUser) -> None:
        resp = test_admin_user.client.get(self.endpoint)
        assert resp.status_code == status.HTTP_200_OK
        assert resp.json() == []

    def test_non_admin_forbidden(self, test_regular_user: FixtureUser) -> None:
        assert test_regular_user.client.get(self.endpoint).status_code == status.HTTP_403_FORBIDDEN

    def test_unauthenticated(self, client: TestClient) -> None:
        assert client.get(self.endpoint).status_code == status.HTTP_401_UNAUTHORIZED
