"""Tests for the Apify fetchers (daily usage + cycle balance snapshot)."""

import datetime as dt
from collections.abc import Iterator
from unittest.mock import patch, MagicMock

import pytest
from sqlalchemy.orm import Session

from app import models
from app.provider_monitoring.apify.fetch import (
    ApifyBalance,
    ApifyDailyUsage,
    fetch_apify_balance,
    fetch_apify_daily_usage,
)


def _response(payload: dict) -> MagicMock:
    """Build a mock HTTP response whose ``.json()`` returns the given payload."""
    return MagicMock(json=MagicMock(return_value=payload))


@pytest.fixture
def usage_payload() -> dict:
    """Trimmed /v2/users/me/usage/monthly response — three days + a cycle total."""

    return {
        "data": {
            "usageCycle": {
                "startAt": "2026-05-23T00:00:00.000Z",
                "endAt": "2026-06-22T23:59:59.999Z",
            },
            "dailyServiceUsages": [
                {
                    "date": "2026-05-23T00:00:00.000Z",
                    "serviceUsage": {
                        "DATASET_TIMED_STORAGE_GBYTE_HOURS": {"quantity": 0.003, "baseAmountUsd": 3e-06},
                    },
                    "totalUsageCreditsUsd": 8.157842675528889e-06,
                },
                {
                    "date": "2026-05-24T00:00:00.000Z",
                    "serviceUsage": {
                        "PAID_ACTORS_PER_EVENT": {"quantity": 0.24, "baseAmountUsd": 0.24},
                    },
                    "totalUsageCreditsUsd": 0.24003632773163752,
                },
                {
                    "date": "2026-06-16T00:00:00.000Z",
                    "serviceUsage": {
                        "PAID_ACTORS_PER_EVENT": {"quantity": 0.02925, "baseAmountUsd": 0.02925},
                    },
                    "totalUsageCreditsUsd": 0.029289277107887497,
                },
            ],
            "totalUsageCreditsUsdAfterVolumeDiscount": 1.4737888240966208,
        }
    }


@pytest.fixture
def user_payload() -> dict:
    """Trimmed /v2/users/me response — only the plan info we need."""

    return {"data": {"plan": {"monthlyUsageCreditsUsd": 50.0, "maxMonthlyUsageUsd": 50.0}}}


@pytest.fixture
def mock_settings() -> Iterator[MagicMock]:
    """Stub the API key used by both endpoints."""
    with patch("app.provider_monitoring.apify.fetch.settings") as mock:
        mock.apify_api_key = "test-key"
        yield mock


@pytest.fixture
def mock_request() -> Iterator[MagicMock]:
    """Patch the Apify fetcher's HTTP call (request_with_retry)."""
    with patch("app.provider_monitoring.apify.fetch.request_with_retry") as mock:
        yield mock


class TestFetchApifyBalance:
    def test_returns_balance_with_monthly_credits_limit(
        self, mock_request: MagicMock, mock_settings: MagicMock, user_payload: dict
    ) -> None:
        mock_request.return_value = _response(user_payload)

        balance = fetch_apify_balance(None)

        assert isinstance(balance, ApifyBalance)
        assert balance.limit_usd == pytest.approx(50.0)

    def test_falls_back_to_max_monthly_usage(self, mock_request: MagicMock, mock_settings: MagicMock) -> None:
        """If `monthlyUsageCreditsUsd` is absent, fall back to `maxMonthlyUsageUsd`."""

        mock_request.return_value = _response({"data": {"plan": {"maxMonthlyUsageUsd": 100.0}}})

        balance = fetch_apify_balance(None)

        assert balance.limit_usd == pytest.approx(100.0)

    def test_limit_none_when_both_limit_fields_missing(self, mock_request: MagicMock, mock_settings: MagicMock) -> None:
        """A non-empty plan with no limit fields yields limit_usd=None (don't fabricate a value)."""

        mock_request.return_value = _response({"data": {"plan": {"id": "free"}}})

        balance = fetch_apify_balance(None)

        assert balance.limit_usd is None

    def test_raises_when_plan_missing(self, mock_request: MagicMock, mock_settings: MagicMock) -> None:
        """No `plan` key at all → RuntimeError (the API is supposed to always return one)."""

        mock_request.return_value = _response({"data": {}})

        with pytest.raises(RuntimeError, match="without a plan"):
            fetch_apify_balance(None)

    def test_raises_when_plan_empty(self, mock_request: MagicMock, mock_settings: MagicMock) -> None:
        """An empty plan dict is treated the same as a missing plan."""

        mock_request.return_value = _response({"data": {"plan": {}}})

        with pytest.raises(RuntimeError, match="without a plan"):
            fetch_apify_balance(None)

    def test_uses_bearer_authorization_header(
        self, mock_request: MagicMock, mock_settings: MagicMock, user_payload: dict
    ) -> None:
        mock_request.return_value = _response(user_payload)

        fetch_apify_balance(None)

        args, kwargs = mock_request.call_args
        assert args[1] == "https://api.apify.com/v2/users/me"
        assert kwargs["service"] == "apify"
        assert kwargs["headers"] == {"Authorization": "Bearer test-key"}

    def test_raises_when_http_error(self, mock_request: MagicMock, mock_settings: MagicMock) -> None:
        response = MagicMock()
        response.raise_for_status.side_effect = RuntimeError("boom")
        mock_request.return_value = response

        with pytest.raises(RuntimeError, match="boom"):
            fetch_apify_balance(None)

    def test_persists_snapshot_when_db_passed(
        self, mock_request: MagicMock, mock_settings: MagicMock, user_payload: dict, session: Session
    ) -> None:
        """Passing a db session writes an ApifyBalance snapshot row."""

        mock_request.return_value = _response(user_payload)

        fetch_apify_balance(session)

        rows = session.query(models.ApifyBalance).all()
        assert len(rows) == 1
        assert rows[0].limit_usd == pytest.approx(50.0)


class TestFetchApifyDailyUsage:
    def test_returns_one_entry_per_daily_service_usage(
        self, mock_request: MagicMock, mock_settings: MagicMock, usage_payload: dict
    ) -> None:
        mock_request.return_value = _response(usage_payload)

        result = fetch_apify_daily_usage(None)

        assert [type(r) for r in result] == [ApifyDailyUsage] * 3
        assert [r.date for r in result] == [
            dt.date(2026, 5, 23),
            dt.date(2026, 5, 24),
            dt.date(2026, 6, 16),
        ]
        assert result[0].usage_usd == pytest.approx(8.157842675528889e-06)
        assert result[1].usage_usd == pytest.approx(0.24003632773163752)
        assert result[2].usage_usd == pytest.approx(0.029289277107887497)

    def test_returns_empty_when_no_daily_usages(self, mock_request: MagicMock, mock_settings: MagicMock) -> None:
        mock_request.return_value = _response(
            {"data": {"dailyServiceUsages": [], "totalUsageCreditsUsdAfterVolumeDiscount": 0.0}}
        )

        assert fetch_apify_daily_usage(None) == []

    def test_returns_empty_when_data_missing(self, mock_request: MagicMock, mock_settings: MagicMock) -> None:
        """Defensive: a payload with no `data` key yields no entries (don't crash)."""

        mock_request.return_value = _response({})

        assert fetch_apify_daily_usage(None) == []

    def test_returns_empty_when_daily_service_usages_null(
        self, mock_request: MagicMock, mock_settings: MagicMock
    ) -> None:
        """`dailyServiceUsages: null` should be treated the same as an empty list."""

        mock_request.return_value = _response({"data": {"dailyServiceUsages": None}})

        assert fetch_apify_daily_usage(None) == []

    def test_uses_bearer_authorization_header(
        self, mock_request: MagicMock, mock_settings: MagicMock, usage_payload: dict
    ) -> None:
        mock_request.return_value = _response(usage_payload)

        fetch_apify_daily_usage(None)

        args, kwargs = mock_request.call_args
        assert args[1] == "https://api.apify.com/v2/users/me/usage/monthly"
        assert kwargs["service"] == "apify"
        assert kwargs["headers"] == {"Authorization": "Bearer test-key"}

    def test_raises_when_http_error(self, mock_request: MagicMock, mock_settings: MagicMock) -> None:
        response = MagicMock()
        response.raise_for_status.side_effect = RuntimeError("boom")
        mock_request.return_value = response

        with pytest.raises(RuntimeError, match="boom"):
            fetch_apify_daily_usage(None)

    def test_persists_rows_when_db_passed(
        self, mock_request: MagicMock, mock_settings: MagicMock, usage_payload: dict, session: Session
    ) -> None:
        """Passing a db session upserts into the ApifyDailyUsage ORM table."""

        mock_request.return_value = _response(usage_payload)

        fetch_apify_daily_usage(session)

        rows = session.query(models.ApifyDailyUsage).order_by(models.ApifyDailyUsage.date).all()
        assert [r.date for r in rows] == [dt.date(2026, 5, 23), dt.date(2026, 5, 24), dt.date(2026, 6, 16)]

    def test_upsert_overwrites_existing_day(
        self, mock_request: MagicMock, mock_settings: MagicMock, session: Session
    ) -> None:
        """Re-running for the same day overwrites the prior row rather than duplicating it."""

        def _payload(amount: float) -> dict:
            return {
                "data": {
                    "dailyServiceUsages": [
                        {"date": "2026-06-02T00:00:00.000Z", "serviceUsage": {}, "totalUsageCreditsUsd": amount}
                    ]
                }
            }

        mock_request.return_value = _response(_payload(0.1))
        fetch_apify_daily_usage(session)
        mock_request.return_value = _response(_payload(0.9))
        fetch_apify_daily_usage(session)

        rows = session.query(models.ApifyDailyUsage).all()
        assert [(r.date, r.usage_usd) for r in rows] == [(dt.date(2026, 6, 2), pytest.approx(0.9))]
