"""Tests for the Anthropic daily-usage fetcher."""

import datetime as dt
from unittest.mock import patch, MagicMock

import pytest

from app import models
from app.external_service_monitoring.anthropic.fetch import sum_bucket_amount, fetch_anthropic_daily_usage


def _bucket(date_str: str, amount: str) -> dict:
    return {
        "starting_at": f"{date_str}T00:00:00Z",
        "ending_at": f"{date_str}T23:59:59Z",
        "results": [
            {
                "currency": "USD",
                "amount": amount,
                "workspace_id": None,
                "description": None,
                "cost_type": None,
                "context_window": None,
                "model": None,
                "service_tier": None,
                "token_type": None,
                "inference_geo": None,
            }
        ],
    }


@pytest.fixture
def anthropic_payload() -> dict:
    """Three daily buckets — mirrors the real cost_report shape (no pagination)."""

    return {
        "data": [
            _bucket("2026-06-01", "1.6385"),
            _bucket("2026-06-02", "4.703"),
            _bucket("2026-06-03", "3.9048"),
        ],
        "has_more": False,
        "next_page": None,
    }


@pytest.fixture
def mock_settings_and_window():
    """Stub anthropic_admin_key and pin current_month_window."""

    with (
        patch("app.external_service_monitoring.anthropic.fetch.settings") as mock_settings,
        patch("app.external_service_monitoring.anthropic.fetch.current_month_window") as mock_window,
    ):
        mock_settings.anthropic_admin_key = "test-key"
        mock_window.return_value = (
            dt.datetime(2026, 6, 1, tzinfo=dt.timezone.utc),
            dt.datetime(2026, 7, 1, tzinfo=dt.timezone.utc),
        )
        yield mock_settings, mock_window


class TestSumBucketAmount:
    """sum_bucket_amount divides by 100 (Admin API reports cents per project memory)."""

    def test_sums_single_result(self) -> None:
        bucket = {"results": [{"amount": "1.6385"}]}
        assert sum_bucket_amount(bucket) == pytest.approx(0.016385)

    def test_sums_multiple_results(self) -> None:
        bucket = {"results": [{"amount": "100"}, {"amount": "50"}, {"amount": "25"}]}
        assert sum_bucket_amount(bucket) == pytest.approx(1.75)

    def test_skips_non_numeric_amounts(self) -> None:
        bucket = {"results": [{"amount": "100"}, {"amount": "not-a-number"}, {"amount": None}]}
        assert sum_bucket_amount(bucket) == pytest.approx(1.0)

    def test_returns_zero_for_empty_results(self) -> None:
        assert sum_bucket_amount({"results": []}) == 0.0

    def test_returns_zero_when_results_missing(self) -> None:
        assert sum_bucket_amount({}) == 0.0


class TestFetchAnthropic:
    @patch("app.external_service_monitoring.anthropic.fetch.request_with_retry")
    def test_returns_one_entry_per_bucket(self, mock_get, mock_settings_and_window, anthropic_payload) -> None:
        mock_get.return_value = MagicMock(json=MagicMock(return_value=anthropic_payload))

        result = fetch_anthropic_daily_usage()

        assert [r.date for r in result] == [
            dt.date(2026, 6, 1),
            dt.date(2026, 6, 2),
            dt.date(2026, 6, 3),
        ]
        # The current code treats amounts as USD cents and divides by 100.
        assert result[0].usage_usd == pytest.approx(0.016385)
        assert result[1].usage_usd == pytest.approx(0.04703)
        assert result[2].usage_usd == pytest.approx(0.039048)

    @patch("app.external_service_monitoring.anthropic.fetch.request_with_retry")
    def test_sends_correct_headers_and_window(self, mock_get, mock_settings_and_window, anthropic_payload) -> None:
        mock_get.return_value = MagicMock(json=MagicMock(return_value=anthropic_payload))

        fetch_anthropic_daily_usage()

        args, kwargs = mock_get.call_args
        assert args[0] == "GET"
        assert args[1] == "https://api.anthropic.com/v1/organizations/cost_report"
        assert kwargs["service"] == "anthropic"
        assert kwargs["headers"] == {
            "x-api-key": "test-key",
            "anthropic-version": "2023-06-01",
        }
        assert kwargs["params"]["starting_at"] == "2026-06-01T00:00:00Z"
        assert kwargs["params"]["ending_at"] == "2026-07-01T00:00:00Z"
        assert kwargs["params"]["limit"] == 31
        assert "page" not in kwargs["params"]

    @patch("app.external_service_monitoring.anthropic.fetch.request_with_retry")
    def test_follows_pagination(self, mock_get, mock_settings_and_window) -> None:
        """When `has_more=True` and `next_page` is set, the fetcher requests the next page."""

        page1 = {
            "data": [_bucket("2026-06-01", "100")],
            "has_more": True,
            "next_page": "tok-2",
        }
        page2 = {
            "data": [_bucket("2026-06-02", "200")],
            "has_more": False,
            "next_page": None,
        }
        mock_get.side_effect = [
            MagicMock(json=MagicMock(return_value=page1)),
            MagicMock(json=MagicMock(return_value=page2)),
        ]

        result = fetch_anthropic_daily_usage()

        assert mock_get.call_count == 2
        # The second call must include the page token AND re-send the original window.
        second_call_params = mock_get.call_args_list[1].kwargs["params"]
        assert second_call_params["page"] == "tok-2"
        assert second_call_params["starting_at"] == "2026-06-01T00:00:00Z"
        assert [r.date for r in result] == [dt.date(2026, 6, 1), dt.date(2026, 6, 2)]

    @patch("app.external_service_monitoring.anthropic.fetch.request_with_retry")
    def test_stops_paginating_when_next_page_missing(self, mock_get, mock_settings_and_window) -> None:
        """`has_more=True` but a falsy `next_page` still terminates — avoids an infinite loop."""

        payload = {
            "data": [_bucket("2026-06-01", "100")],
            "has_more": True,
            "next_page": None,
        }
        mock_get.return_value = MagicMock(json=MagicMock(return_value=payload))

        result = fetch_anthropic_daily_usage()

        assert mock_get.call_count == 1
        assert len(result) == 1

    @patch("app.external_service_monitoring.anthropic.fetch.request_with_retry")
    def test_returns_empty_for_no_data(self, mock_get, mock_settings_and_window) -> None:
        mock_get.return_value = MagicMock(
            json=MagicMock(return_value={"data": [], "has_more": False, "next_page": None})
        )

        assert fetch_anthropic_daily_usage() == []

    @patch("app.external_service_monitoring.anthropic.fetch.request_with_retry")
    def test_raises_when_http_error(self, mock_get, mock_settings_and_window) -> None:
        response = MagicMock()
        response.raise_for_status.side_effect = RuntimeError("boom")
        mock_get.return_value = response

        with pytest.raises(RuntimeError, match="boom"):
            fetch_anthropic_daily_usage()

    @patch("app.external_service_monitoring.anthropic.fetch.request_with_retry")
    def test_persists_rows_when_db_passed(self, mock_get, mock_settings_and_window, anthropic_payload, session) -> None:
        """Passing a db session upserts into the AnthropicDailyUsage ORM table."""

        mock_get.return_value = MagicMock(json=MagicMock(return_value=anthropic_payload))

        fetch_anthropic_daily_usage(session)

        rows = session.query(models.AnthropicDailyUsage).order_by(models.AnthropicDailyUsage.date).all()
        assert [r.date for r in rows] == [dt.date(2026, 6, 1), dt.date(2026, 6, 2), dt.date(2026, 6, 3)]
        assert rows[0].usage_usd == pytest.approx(0.016385)

    @patch("app.external_service_monitoring.anthropic.fetch.request_with_retry")
    def test_upsert_overwrites_existing_day(self, mock_get, mock_settings_and_window, session) -> None:
        """Re-running for the same day overwrites the prior row rather than duplicating it."""

        first = {"data": [_bucket("2026-06-01", "100")], "has_more": False, "next_page": None}
        mock_get.return_value = MagicMock(json=MagicMock(return_value=first))
        fetch_anthropic_daily_usage(session)

        second = {"data": [_bucket("2026-06-01", "500")], "has_more": False, "next_page": None}
        mock_get.return_value = MagicMock(json=MagicMock(return_value=second))
        fetch_anthropic_daily_usage(session)

        rows = session.query(models.AnthropicDailyUsage).all()
        assert [(r.date, r.usage_usd) for r in rows] == [(dt.date(2026, 6, 1), pytest.approx(5.0))]
