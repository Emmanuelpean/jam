"""Tests for the Bright Data fetchers (daily usage + balance snapshot)."""

import datetime as dt
from collections.abc import Iterator
from unittest.mock import patch, MagicMock

import pytest
from sqlalchemy.orm import Session

from app import models
from app.provider_monitoring.brightdata.fetch import (
    BrightdataBalance,
    fetch_brightdata_balance,
    fetch_brightdata_daily_usage,
)

LINKEDIN_DATASET_ID = "gd_lpfll7v5hcqtkxl6l"
INDEED_DATASET_ID = "gd_lpfbbndm1xnopbrcr0"


def _response(payload) -> MagicMock:
    """Build a mock HTTP response whose ``.json()`` returns the given payload."""
    return MagicMock(json=MagicMock(return_value=payload))


@pytest.fixture
def costs_payload() -> dict:
    """Trimmed payload mirroring the /costs/export/json shape — daily-keyed dataset costs plus
    a `total` summary that the fetcher must skip."""

    return {
        "2026-06-02": {LINKEDIN_DATASET_ID: 0.0075},
        "total": {LINKEDIN_DATASET_ID: 0.081, INDEED_DATASET_ID: 0.0075},
        "2026-06-07": {LINKEDIN_DATASET_ID: 0.003, INDEED_DATASET_ID: 0.0075},
        "2026-06-16": {LINKEDIN_DATASET_ID: 0.009},
    }


@pytest.fixture
def balance_payload() -> dict:
    """Trimmed payload mirroring /customer/balance."""

    return {"balance": 42.75, "pending_costs": 1.20}


@pytest.fixture
def mock_settings() -> Iterator[MagicMock]:
    """Stub the API key used by both endpoints."""

    with patch("app.provider_monitoring.brightdata.fetch.settings") as mock:
        mock.brightdata_api_key = "test-key"
        yield mock


@pytest.fixture
def mock_request() -> Iterator[MagicMock]:
    """Patch the Bright Data fetcher's HTTP call (request_with_retry)."""
    with patch("app.provider_monitoring.brightdata.fetch.request_with_retry") as mock:
        yield mock


@pytest.fixture
def mock_dataset_labels() -> Iterator[dict[str, str]]:
    """`DATASET_LABELS` is built at module import time from the scraper class dataset IDs, so
    patching those later has no effect. Patch the module-level dict directly instead."""

    labels = {LINKEDIN_DATASET_ID: "LinkedIn", INDEED_DATASET_ID: "Indeed"}
    with patch("app.provider_monitoring.brightdata.fetch.DATASET_LABELS", labels):
        yield labels


def _month_window() -> tuple[str, str]:
    """The window the fetcher computes from `today` — matches the inline logic in fetch.py."""

    today = dt.date.today()
    start = today.replace(day=1)
    end = (start + dt.timedelta(days=32)).replace(day=1)
    return start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")


class TestFetchBrightdataBalance:
    def test_parses_balance_snapshot(
        self, mock_request: MagicMock, mock_settings: MagicMock, balance_payload: dict
    ) -> None:
        mock_request.return_value = _response(balance_payload)

        balance = fetch_brightdata_balance()

        assert isinstance(balance, BrightdataBalance)
        assert balance.balance_usd == pytest.approx(42.75)
        assert balance.pending_costs_usd == pytest.approx(1.20)

    def test_uses_bearer_auth(self, mock_request: MagicMock, mock_settings: MagicMock, balance_payload: dict) -> None:
        mock_request.return_value = _response(balance_payload)

        fetch_brightdata_balance()

        args, kwargs = mock_request.call_args
        assert args[1] == "https://api.brightdata.com/customer/balance"
        assert kwargs["service"] == "brightdata"
        assert kwargs["headers"] == {"Authorization": "Bearer test-key"}

    def test_missing_fields_default_to_none(self, mock_request: MagicMock, mock_settings: MagicMock) -> None:
        """If the balance endpoint returns {}, both fields default to None."""

        mock_request.return_value = _response({})

        balance = fetch_brightdata_balance()

        assert balance.balance_usd is None
        assert balance.pending_costs_usd is None

    def test_null_payload_treated_as_empty(self, mock_request: MagicMock, mock_settings: MagicMock) -> None:
        """`resp.json()` returning None is coerced to {} — no AttributeError."""

        mock_request.return_value = _response(None)

        balance = fetch_brightdata_balance()

        assert balance.balance_usd is None
        assert balance.pending_costs_usd is None

    def test_raises_when_http_error(self, mock_request: MagicMock, mock_settings: MagicMock) -> None:
        response = MagicMock()
        response.raise_for_status.side_effect = RuntimeError("boom")
        mock_request.return_value = response

        with pytest.raises(RuntimeError, match="boom"):
            fetch_brightdata_balance()

    def test_persists_snapshot_when_db_passed(
        self, mock_request: MagicMock, mock_settings: MagicMock, balance_payload: dict, session: Session
    ) -> None:
        """Passing a db session writes a BrightdataBalance snapshot row."""

        mock_request.return_value = _response(balance_payload)

        fetch_brightdata_balance(session)

        rows = session.query(models.BrightdataBalance).all()
        assert len(rows) == 1
        assert rows[0].balance_usd == pytest.approx(42.75)
        assert rows[0].pending_costs_usd == pytest.approx(1.2)


class TestFetchBrightdataDailyUsage:
    def test_flattens_daily_buckets_into_rows_per_dataset(
        self,
        mock_request: MagicMock,
        mock_settings: MagicMock,
        mock_dataset_labels: dict[str, str],
        costs_payload: dict,
    ) -> None:
        """Each (date, dataset) pair in the response yields one BrightdataDailyUsage."""

        mock_request.return_value = _response(costs_payload)

        result = fetch_brightdata_daily_usage()

        triples = {(r.date, r.dataset, r.usage_usd) for r in result}
        assert triples == {
            (dt.date(2026, 6, 2), "LinkedIn", 0.0075),
            (dt.date(2026, 6, 7), "LinkedIn", 0.003),
            (dt.date(2026, 6, 7), "Indeed", 0.0075),
            (dt.date(2026, 6, 16), "LinkedIn", 0.009),
        }

    def test_skips_total_row(
        self,
        mock_request: MagicMock,
        mock_settings: MagicMock,
        mock_dataset_labels: dict[str, str],
        costs_payload: dict,
    ) -> None:
        """The summary `total` key in the payload must not become a usage entry."""

        mock_request.return_value = _response(costs_payload)

        result = fetch_brightdata_daily_usage()

        for r in result:
            assert isinstance(r.date, dt.date)

    def test_skips_unknown_dataset_ids(
        self, mock_request: MagicMock, mock_settings: MagicMock, mock_dataset_labels: dict[str, str]
    ) -> None:
        """A dataset_id that doesn't match the configured LinkedIn/Indeed IDs is dropped."""

        mock_request.return_value = _response({"2026-06-02": {"gd_unknown_dataset": 0.5, LINKEDIN_DATASET_ID: 0.01}})

        result = fetch_brightdata_daily_usage()

        assert [(r.dataset, r.usage_usd) for r in result] == [("LinkedIn", 0.01)]

    def test_skips_invalid_date_keys(
        self, mock_request: MagicMock, mock_settings: MagicMock, mock_dataset_labels: dict[str, str]
    ) -> None:
        """A non-date-shaped key (other than `total`) is skipped, not crashed on."""

        payload = {
            "not-a-date": {LINKEDIN_DATASET_ID: 0.5},
            "2026-06-02": {LINKEDIN_DATASET_ID: 0.01},
        }
        mock_request.return_value = _response(payload)

        result = fetch_brightdata_daily_usage()

        assert [(r.date, r.usage_usd) for r in result] == [(dt.date(2026, 6, 2), 0.01)]

    def test_skips_non_dict_values(
        self, mock_request: MagicMock, mock_settings: MagicMock, mock_dataset_labels: dict[str, str]
    ) -> None:
        """If a date key maps to something other than a dict, it's skipped."""

        payload = {
            "2026-06-02": "not-a-dict",
            "2026-06-03": {LINKEDIN_DATASET_ID: 0.01},
        }
        mock_request.return_value = _response(payload)

        result = fetch_brightdata_daily_usage()

        assert [(r.date, r.usage_usd) for r in result] == [(dt.date(2026, 6, 3), 0.01)]

    def test_skips_non_numeric_amounts(
        self, mock_request: MagicMock, mock_settings: MagicMock, mock_dataset_labels: dict[str, str]
    ) -> None:
        """Non-numeric amounts are dropped, not coerced to 0."""

        payload = {
            "2026-06-02": {LINKEDIN_DATASET_ID: "not-a-number", INDEED_DATASET_ID: 0.01},
        }
        mock_request.return_value = _response(payload)

        result = fetch_brightdata_daily_usage()

        assert [(r.dataset, r.usage_usd) for r in result] == [("Indeed", 0.01)]

    def test_sends_correct_request_body(
        self,
        mock_request: MagicMock,
        mock_settings: MagicMock,
        mock_dataset_labels: dict[str, str],
        costs_payload: dict,
    ) -> None:
        """Verify the POST body uses the current calendar month and `web_apis` dimension."""

        mock_request.return_value = _response(costs_payload)

        fetch_brightdata_daily_usage()

        expected_from, expected_to = _month_window()
        args, kwargs = mock_request.call_args
        assert args[0] == "POST"
        assert args[1] == "https://api.brightdata.com/costs/export/json"
        assert kwargs["service"] == "brightdata"
        assert kwargs["headers"]["Authorization"] == "Bearer test-key"
        assert kwargs["headers"]["Content-Type"] == "application/json"
        assert kwargs["json"] == {
            "dimension": "web_apis",
            "filters": {},
            "from": expected_from,
            "to": expected_to,
        }

    def test_returns_empty_when_only_total_present(
        self, mock_request: MagicMock, mock_settings: MagicMock, mock_dataset_labels: dict[str, str]
    ) -> None:
        """Payload with only the `total` key returns an empty list."""

        mock_request.return_value = _response({"total": {LINKEDIN_DATASET_ID: 0.0}})

        assert fetch_brightdata_daily_usage() == []

    def test_returns_empty_when_payload_null(
        self, mock_request: MagicMock, mock_settings: MagicMock, mock_dataset_labels: dict[str, str]
    ) -> None:
        """`resp.json()` returning None is coerced to {} — no AttributeError."""

        mock_request.return_value = _response(None)

        assert fetch_brightdata_daily_usage() == []

    def test_raises_when_http_error(
        self, mock_request: MagicMock, mock_settings: MagicMock, mock_dataset_labels: dict[str, str]
    ) -> None:
        response = MagicMock()
        response.raise_for_status.side_effect = RuntimeError("boom")
        mock_request.return_value = response

        with pytest.raises(RuntimeError, match="boom"):
            fetch_brightdata_daily_usage()

    def test_persists_rows_when_db_passed(
        self,
        mock_request: MagicMock,
        mock_settings: MagicMock,
        mock_dataset_labels: dict[str, str],
        costs_payload: dict,
        session: Session,
    ) -> None:
        """Passing a db session upserts into the BrightdataDailyUsage ORM table."""

        mock_request.return_value = _response(costs_payload)

        fetch_brightdata_daily_usage(session)

        rows = session.query(models.BrightdataDailyUsage).all()
        triples = {(r.date, r.dataset, r.usage_usd) for r in rows}
        assert triples == {
            (dt.date(2026, 6, 2), "LinkedIn", 0.0075),
            (dt.date(2026, 6, 7), "LinkedIn", 0.003),
            (dt.date(2026, 6, 7), "Indeed", 0.0075),
            (dt.date(2026, 6, 16), "LinkedIn", 0.009),
        }

    def test_upsert_overwrites_existing_date_dataset(
        self, mock_request: MagicMock, mock_settings: MagicMock, mock_dataset_labels: dict[str, str], session: Session
    ) -> None:
        """Re-running for the same (date, dataset) overwrites the prior row rather than duplicating it."""

        mock_request.return_value = _response({"2026-06-02": {LINKEDIN_DATASET_ID: 0.01}})
        fetch_brightdata_daily_usage(session)
        mock_request.return_value = _response({"2026-06-02": {LINKEDIN_DATASET_ID: 0.05}})
        fetch_brightdata_daily_usage(session)

        rows = session.query(models.BrightdataDailyUsage).all()
        assert [(r.date, r.dataset, r.usage_usd) for r in rows] == [(dt.date(2026, 6, 2), "LinkedIn", 0.05)]
