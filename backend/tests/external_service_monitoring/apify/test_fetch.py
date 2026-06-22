"""Tests for the Apify fetchers (daily usage + cycle balance snapshot)."""

import datetime as dt
from unittest.mock import patch, MagicMock

import pytest

from app import models
from app.external_service_monitoring.apify.fetch import (
    ApifyBalance,
    ApifyDailyUsage,
    fetch_apify_balance,
    fetch_apify_daily_usage,
)


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
def mock_settings():
    with patch("app.external_service_monitoring.apify.fetch.settings") as mock:
        mock.apify_api_key = "test-key"
        yield mock


class TestFetchApifyBalance:
    @patch("app.external_service_monitoring.apify.fetch.request_with_retry")
    def test_returns_balance_with_monthly_credits_limit(self, mock_get, mock_settings, user_payload) -> None:
        mock_get.return_value = MagicMock(json=MagicMock(return_value=user_payload))

        balance = fetch_apify_balance(None)

        assert isinstance(balance, ApifyBalance)
        assert balance.limit_usd == pytest.approx(50.0)

    @patch("app.external_service_monitoring.apify.fetch.request_with_retry")
    def test_falls_back_to_max_monthly_usage(self, mock_get, mock_settings) -> None:
        """If `monthlyUsageCreditsUsd` is absent, fall back to `maxMonthlyUsageUsd`."""

        payload = {"data": {"plan": {"maxMonthlyUsageUsd": 100.0}}}
        mock_get.return_value = MagicMock(json=MagicMock(return_value=payload))

        balance = fetch_apify_balance(None)

        assert balance.limit_usd == pytest.approx(100.0)

    @patch("app.external_service_monitoring.apify.fetch.request_with_retry")
    def test_limit_none_when_both_limit_fields_missing(self, mock_get, mock_settings) -> None:
        """A non-empty plan with no limit fields yields limit_usd=None (don't fabricate a value)."""

        payload = {"data": {"plan": {"id": "free"}}}
        mock_get.return_value = MagicMock(json=MagicMock(return_value=payload))

        balance = fetch_apify_balance(None)

        assert balance.limit_usd is None

    @patch("app.external_service_monitoring.apify.fetch.request_with_retry")
    def test_raises_when_plan_missing(self, mock_get, mock_settings) -> None:
        """No `plan` key at all → RuntimeError (the API is supposed to always return one)."""

        mock_get.return_value = MagicMock(json=MagicMock(return_value={"data": {}}))

        with pytest.raises(RuntimeError, match="without a plan"):
            fetch_apify_balance(None)

    @patch("app.external_service_monitoring.apify.fetch.request_with_retry")
    def test_raises_when_plan_empty(self, mock_get, mock_settings) -> None:
        """An empty plan dict is treated the same as a missing plan."""

        mock_get.return_value = MagicMock(json=MagicMock(return_value={"data": {"plan": {}}}))

        with pytest.raises(RuntimeError, match="without a plan"):
            fetch_apify_balance(None)

    @patch("app.external_service_monitoring.apify.fetch.request_with_retry")
    def test_uses_bearer_authorization_header(self, mock_get, mock_settings, user_payload) -> None:
        mock_get.return_value = MagicMock(json=MagicMock(return_value=user_payload))

        fetch_apify_balance(None)

        args, kwargs = mock_get.call_args
        assert args[1] == "https://api.apify.com/v2/users/me"
        assert kwargs["service"] == "apify"
        assert kwargs["headers"] == {"Authorization": "Bearer test-key"}

    @patch("app.external_service_monitoring.apify.fetch.request_with_retry")
    def test_raises_when_http_error(self, mock_get, mock_settings) -> None:
        response = MagicMock()
        response.raise_for_status.side_effect = RuntimeError("boom")
        mock_get.return_value = response

        with pytest.raises(RuntimeError, match="boom"):
            fetch_apify_balance(None)

    @patch("app.external_service_monitoring.apify.fetch.request_with_retry")
    def test_persists_snapshot_when_db_passed(self, mock_get, mock_settings, user_payload, session) -> None:
        """Passing a db session writes an ApifyBalance snapshot row."""

        mock_get.return_value = MagicMock(json=MagicMock(return_value=user_payload))

        fetch_apify_balance(session)

        rows = session.query(models.ApifyBalance).all()
        assert len(rows) == 1
        assert rows[0].limit_usd == pytest.approx(50.0)


class TestFetchApifyDailyUsage:
    @patch("app.external_service_monitoring.apify.fetch.request_with_retry")
    def test_returns_one_entry_per_daily_service_usage(self, mock_get, mock_settings, usage_payload) -> None:
        mock_get.return_value = MagicMock(json=MagicMock(return_value=usage_payload))

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

    @patch("app.external_service_monitoring.apify.fetch.request_with_retry")
    def test_returns_empty_when_no_daily_usages(self, mock_get, mock_settings) -> None:
        payload = {"data": {"dailyServiceUsages": [], "totalUsageCreditsUsdAfterVolumeDiscount": 0.0}}
        mock_get.return_value = MagicMock(json=MagicMock(return_value=payload))

        assert fetch_apify_daily_usage(None) == []

    @patch("app.external_service_monitoring.apify.fetch.request_with_retry")
    def test_returns_empty_when_data_missing(self, mock_get, mock_settings) -> None:
        """Defensive: a payload with no `data` key yields no entries (don't crash)."""

        mock_get.return_value = MagicMock(json=MagicMock(return_value={}))

        assert fetch_apify_daily_usage(None) == []

    @patch("app.external_service_monitoring.apify.fetch.request_with_retry")
    def test_returns_empty_when_daily_service_usages_null(self, mock_get, mock_settings) -> None:
        """`dailyServiceUsages: null` should be treated the same as an empty list."""

        mock_get.return_value = MagicMock(json=MagicMock(return_value={"data": {"dailyServiceUsages": None}}))

        assert fetch_apify_daily_usage(None) == []

    @patch("app.external_service_monitoring.apify.fetch.request_with_retry")
    def test_uses_bearer_authorization_header(self, mock_get, mock_settings, usage_payload) -> None:
        mock_get.return_value = MagicMock(json=MagicMock(return_value=usage_payload))

        fetch_apify_daily_usage(None)

        args, kwargs = mock_get.call_args
        assert args[1] == "https://api.apify.com/v2/users/me/usage/monthly"
        assert kwargs["service"] == "apify"
        assert kwargs["headers"] == {"Authorization": "Bearer test-key"}

    @patch("app.external_service_monitoring.apify.fetch.request_with_retry")
    def test_raises_when_http_error(self, mock_get, mock_settings) -> None:
        response = MagicMock()
        response.raise_for_status.side_effect = RuntimeError("boom")
        mock_get.return_value = response

        with pytest.raises(RuntimeError, match="boom"):
            fetch_apify_daily_usage(None)

    @patch("app.external_service_monitoring.apify.fetch.request_with_retry")
    def test_persists_rows_when_db_passed(self, mock_get, mock_settings, usage_payload, session) -> None:
        """Passing a db session upserts into the ApifyDailyUsage ORM table."""

        mock_get.return_value = MagicMock(json=MagicMock(return_value=usage_payload))

        fetch_apify_daily_usage(session)

        rows = session.query(models.ApifyDailyUsage).order_by(models.ApifyDailyUsage.date).all()
        assert [r.date for r in rows] == [dt.date(2026, 5, 23), dt.date(2026, 5, 24), dt.date(2026, 6, 16)]

    @patch("app.external_service_monitoring.apify.fetch.request_with_retry")
    def test_upsert_overwrites_existing_day(self, mock_get, mock_settings, session) -> None:
        """Re-running for the same day overwrites the prior row rather than duplicating it."""

        def _payload(amount: float) -> dict:
            return {
                "data": {
                    "dailyServiceUsages": [
                        {"date": "2026-06-02T00:00:00.000Z", "serviceUsage": {}, "totalUsageCreditsUsd": amount}
                    ]
                }
            }

        mock_get.return_value = MagicMock(json=MagicMock(return_value=_payload(0.1)))
        fetch_apify_daily_usage(session)
        mock_get.return_value = MagicMock(json=MagicMock(return_value=_payload(0.9)))
        fetch_apify_daily_usage(session)

        rows = session.query(models.ApifyDailyUsage).all()
        assert [(r.date, r.usage_usd) for r in rows] == [(dt.date(2026, 6, 2), pytest.approx(0.9))]
