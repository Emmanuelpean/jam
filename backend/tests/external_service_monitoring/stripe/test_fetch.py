"""Tests for the Stripe daily-income fetcher."""

import datetime as dt
from unittest.mock import patch, MagicMock

import pytest

from app import models
from app.external_service_monitoring.stripe.fetch import (
    StripeDailyIncome,
    fetch_stripe_daily_income,
)


def _txn(*, created: int, amount: int, net: int, currency: str | None = "gbp") -> MagicMock:
    """A minimal stand-in for a Stripe BalanceTransaction object."""
    t = MagicMock()
    t.created = created
    t.amount = amount
    t.net = net
    t.currency = currency
    return t


def _ts(d: dt.datetime) -> int:
    return int(d.replace(tzinfo=dt.timezone.utc).timestamp())


@pytest.fixture
def mock_window():
    """Pin the period to June 2026 so we can assert request params."""
    with patch("app.external_service_monitoring.stripe.fetch.current_month_window") as mock_w:
        mock_w.return_value = (
            dt.datetime(2026, 6, 1, tzinfo=dt.timezone.utc),
            dt.datetime(2026, 7, 1, tzinfo=dt.timezone.utc),
        )
        yield mock_w


def _patch_balance_txn_lists(by_type: dict[str, list]) -> MagicMock:
    """Build a side_effect that returns a different paging iterator per `type=` call."""

    def fake_list(**kwargs):
        result = MagicMock()
        result.auto_paging_iter.return_value = iter(by_type.get(kwargs["type"], []))
        return result

    return MagicMock(side_effect=fake_list)


class TestFetchStripe:
    @patch("app.external_service_monitoring.stripe.fetch.stripe")
    def test_groups_by_utc_date(self, mock_stripe, mock_window) -> None:
        """Two charges on the same UTC day collapse into one StripeDailyIncome row."""

        charges = [
            _txn(created=_ts(dt.datetime(2026, 6, 2, 10, 0)), amount=1000, net=970),
            _txn(created=_ts(dt.datetime(2026, 6, 2, 18, 0)), amount=500, net=485),
            _txn(created=_ts(dt.datetime(2026, 6, 3, 8, 0)), amount=2000, net=1940),
        ]
        mock_stripe.BalanceTransaction.list = _patch_balance_txn_lists({"charge": charges, "refund": []})

        result = fetch_stripe_daily_income(None)

        assert [type(r) for r in result] == [StripeDailyIncome] * 2
        assert result[0].date == dt.date(2026, 6, 2)
        assert result[0].gross_gbp == pytest.approx(15.0)
        assert result[0].net_gbp == pytest.approx(14.55)
        assert result[1].date == dt.date(2026, 6, 3)
        assert result[1].gross_gbp == pytest.approx(20.0)
        assert result[1].net_gbp == pytest.approx(19.40)

    @patch("app.external_service_monitoring.stripe.fetch.stripe")
    def test_refunds_affect_net_only(self, mock_stripe, mock_window) -> None:
        """Refunds reduce `net_gbp` but don't show up in `gross_gbp`."""

        charges = [_txn(created=_ts(dt.datetime(2026, 6, 5, 12, 0)), amount=5000, net=4850)]
        refunds = [_txn(created=_ts(dt.datetime(2026, 6, 5, 14, 0)), amount=-1000, net=-1000)]
        mock_stripe.BalanceTransaction.list = _patch_balance_txn_lists({"charge": charges, "refund": refunds})

        [row] = fetch_stripe_daily_income(None)

        assert row.date == dt.date(2026, 6, 5)
        assert row.gross_gbp == pytest.approx(50.0)
        assert row.net_gbp == pytest.approx(38.50)

    @patch("app.external_service_monitoring.stripe.fetch.stripe")
    def test_refund_only_day_emits_row_with_zero_gross(self, mock_stripe, mock_window) -> None:
        """A refund on a day with no charges still emits a row (gross=0, net<0)."""

        refunds = [_txn(created=_ts(dt.datetime(2026, 6, 9, 12, 0)), amount=-1000, net=-1000)]
        mock_stripe.BalanceTransaction.list = _patch_balance_txn_lists({"charge": [], "refund": refunds})

        [row] = fetch_stripe_daily_income(None)

        assert row.date == dt.date(2026, 6, 9)
        assert row.gross_gbp == pytest.approx(0.0)
        assert row.net_gbp == pytest.approx(-10.0)

    @patch("app.external_service_monitoring.stripe.fetch.stripe")
    def test_skips_non_gbp_transactions(self, mock_stripe, mock_window) -> None:
        """Transactions in other currencies are ignored to keep the chart single-currency."""

        charges = [
            _txn(
                created=_ts(dt.datetime(2026, 6, 2, 10, 0)),
                amount=1000,
                net=970,
                currency="usd",
            ),
            _txn(
                created=_ts(dt.datetime(2026, 6, 2, 11, 0)),
                amount=500,
                net=485,
                currency="gbp",
            ),
        ]
        mock_stripe.BalanceTransaction.list = _patch_balance_txn_lists({"charge": charges, "refund": []})

        [row] = fetch_stripe_daily_income(None)

        assert row.gross_gbp == pytest.approx(5.0)
        assert row.net_gbp == pytest.approx(4.85)

    @patch("app.external_service_monitoring.stripe.fetch.stripe")
    def test_currency_match_is_case_insensitive(self, mock_stripe, mock_window) -> None:
        """Stripe returns lowercase currency codes, but be defensive: `GBP` should still count."""

        charges = [
            _txn(created=_ts(dt.datetime(2026, 6, 2, 10, 0)), amount=500, net=485, currency="GBP"),
        ]
        mock_stripe.BalanceTransaction.list = _patch_balance_txn_lists({"charge": charges, "refund": []})

        [row] = fetch_stripe_daily_income(None)

        assert row.gross_gbp == pytest.approx(5.0)

    @patch("app.external_service_monitoring.stripe.fetch.stripe")
    def test_null_currency_is_skipped(self, mock_stripe, mock_window) -> None:
        """A txn with `currency=None` is skipped without crashing on `.lower()`."""

        charges = [
            _txn(created=_ts(dt.datetime(2026, 6, 2, 10, 0)), amount=1000, net=970, currency=None),
            _txn(created=_ts(dt.datetime(2026, 6, 2, 11, 0)), amount=500, net=485),
        ]
        mock_stripe.BalanceTransaction.list = _patch_balance_txn_lists({"charge": charges, "refund": []})

        [row] = fetch_stripe_daily_income(None)

        assert row.gross_gbp == pytest.approx(5.0)

    @patch("app.external_service_monitoring.stripe.fetch.stripe")
    def test_handles_empty_month(self, mock_stripe, mock_window) -> None:
        """No transactions yields an empty list."""

        mock_stripe.BalanceTransaction.list = _patch_balance_txn_lists({"charge": [], "refund": []})

        assert fetch_stripe_daily_income(None) == []

    @patch("app.external_service_monitoring.stripe.fetch.stripe")
    def test_uses_window_timestamps_in_request(self, mock_stripe, mock_window) -> None:
        """The `created` filter must use the (period_start, period_end) timestamps."""

        mock_stripe.BalanceTransaction.list = _patch_balance_txn_lists({"charge": [], "refund": []})

        fetch_stripe_daily_income(None)

        for call in mock_stripe.BalanceTransaction.list.call_args_list:
            assert call.kwargs["created"] == {
                "gte": int(dt.datetime(2026, 6, 1, tzinfo=dt.timezone.utc).timestamp()),
                "lt": int(dt.datetime(2026, 7, 1, tzinfo=dt.timezone.utc).timestamp()),
            }
            assert call.kwargs["limit"] == 100
        assert sorted(c.kwargs["type"] for c in mock_stripe.BalanceTransaction.list.call_args_list) == [
            "charge",
            "refund",
        ]

    @patch("app.external_service_monitoring.stripe.fetch.stripe")
    def test_days_returned_in_sorted_order(self, mock_stripe, mock_window) -> None:
        """Even if Stripe returns transactions out of order, output dates are ascending."""

        charges = [
            _txn(created=_ts(dt.datetime(2026, 6, 10, 0, 0)), amount=100, net=100),
            _txn(created=_ts(dt.datetime(2026, 6, 2, 0, 0)), amount=200, net=200),
            _txn(created=_ts(dt.datetime(2026, 6, 5, 0, 0)), amount=300, net=300),
        ]
        mock_stripe.BalanceTransaction.list = _patch_balance_txn_lists({"charge": charges, "refund": []})

        dates = [r.date for r in fetch_stripe_daily_income(None)]

        assert dates == [dt.date(2026, 6, 2), dt.date(2026, 6, 5), dt.date(2026, 6, 10)]

    @patch("app.external_service_monitoring.stripe.fetch.stripe")
    def test_persists_rows_when_db_passed(self, mock_stripe, mock_window, session) -> None:
        """Passing a db session upserts into the StripeDailyIncome ORM table (not the schema)."""

        charges = [_txn(created=_ts(dt.datetime(2026, 6, 2, 10, 0)), amount=1000, net=970)]
        mock_stripe.BalanceTransaction.list = _patch_balance_txn_lists({"charge": charges, "refund": []})

        fetch_stripe_daily_income(session)

        rows = session.query(models.StripeDailyIncome).all()
        assert [(r.date, r.gross_gbp, r.net_gbp) for r in rows] == [(dt.date(2026, 6, 2), 10.0, 9.7)]

    @patch("app.external_service_monitoring.stripe.fetch.stripe")
    def test_upsert_overwrites_existing_day(self, mock_stripe, mock_window, session) -> None:
        """Re-running for the same day overwrites the prior row rather than duplicating it."""

        first = [_txn(created=_ts(dt.datetime(2026, 6, 2, 10, 0)), amount=1000, net=970)]
        mock_stripe.BalanceTransaction.list = _patch_balance_txn_lists({"charge": first, "refund": []})
        fetch_stripe_daily_income(session)

        second = [_txn(created=_ts(dt.datetime(2026, 6, 2, 12, 0)), amount=5000, net=4850)]
        mock_stripe.BalanceTransaction.list = _patch_balance_txn_lists({"charge": second, "refund": []})
        fetch_stripe_daily_income(session)

        rows = session.query(models.StripeDailyIncome).all()
        assert [(r.date, r.gross_gbp, r.net_gbp) for r in rows] == [(dt.date(2026, 6, 2), 50.0, 48.5)]
