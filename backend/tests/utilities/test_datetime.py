"""Tests for datetime helper utilities."""

import datetime as dt
import types
from contextlib import AbstractContextManager
from unittest.mock import patch

import pytest
from dateutil.relativedelta import relativedelta

from app.utilities.datetime import current_month_window, to_iso_z


def _freeze(frozen: dt.datetime) -> AbstractContextManager:
    """Patch the module's dt so dt.datetime.now(tz) returns frozen (kept tz-aware)."""

    class FrozenDateTime(dt.datetime):
        """A frozen datetime that always returns the same value."""

        @classmethod
        def now(cls, tz: dt.tzinfo | None = None) -> dt.datetime:
            """Return the frozen value."""

            return frozen.replace(tzinfo=tz)

    return patch(
        "app.utilities.datetime.dt",
        types.SimpleNamespace(datetime=FrozenDateTime, timezone=dt.timezone),
    )


class TestCurrentMonthWindow:

    def test_invariants_against_real_now(self) -> None:
        start, end = current_month_window()
        now = dt.datetime.now(dt.timezone.utc)

        assert start.day == 1
        assert (start.hour, start.minute, start.second, start.microsecond) == (0, 0, 0, 0)
        assert start.tzinfo == dt.timezone.utc
        assert start <= now < end
        assert end == start + relativedelta(months=1)

    @pytest.mark.parametrize(
        "frozen,expected_start,expected_end",
        [
            # Mid-month
            (
                dt.datetime(2026, 6, 15, 13, 45, 30, 123456),
                dt.datetime(2026, 6, 1, tzinfo=dt.timezone.utc),
                dt.datetime(2026, 7, 1, tzinfo=dt.timezone.utc),
            ),
            # First instant of the month
            (
                dt.datetime(2026, 2, 1, 0, 0, 0),
                dt.datetime(2026, 2, 1, tzinfo=dt.timezone.utc),
                dt.datetime(2026, 3, 1, tzinfo=dt.timezone.utc),
            ),
            # December rolls over into the next year
            (
                dt.datetime(2026, 12, 20, 9, 0, 0),
                dt.datetime(2026, 12, 1, tzinfo=dt.timezone.utc),
                dt.datetime(2027, 1, 1, tzinfo=dt.timezone.utc),
            ),
            # February following a leap day -> March (window length is a calendar month, not 30 days)
            (
                dt.datetime(2024, 2, 29, 23, 59, 59),
                dt.datetime(2024, 2, 1, tzinfo=dt.timezone.utc),
                dt.datetime(2024, 3, 1, tzinfo=dt.timezone.utc),
            ),
        ],
    )
    def test_frozen_windows(self, frozen: dt.datetime, expected_start: dt.datetime, expected_end: dt.datetime) -> None:
        with _freeze(frozen):
            start, end = current_month_window()
        assert start == expected_start
        assert end == expected_end


class TestToIsoZ:

    @pytest.mark.parametrize(
        "value,expected",
        [
            (dt.datetime(2026, 6, 15, 13, 45, 30), "2026-06-15T13:45:30Z"),
            (dt.datetime(2026, 1, 1, 0, 0, 0), "2026-01-01T00:00:00Z"),
            (dt.datetime(2026, 12, 31, 23, 59, 59), "2026-12-31T23:59:59Z"),
        ],
    )
    def test_formats_with_trailing_z(self, value: dt.datetime, expected: str) -> None:
        assert to_iso_z(value) == expected

    def test_microseconds_are_dropped(self) -> None:
        assert to_iso_z(dt.datetime(2026, 6, 15, 13, 45, 30, 999999)) == "2026-06-15T13:45:30Z"

    def test_tzinfo_does_not_change_rendered_value(self) -> None:
        # The helper formats the wall-clock fields as-is and always appends a literal Z.
        aware = dt.datetime(2026, 6, 15, 13, 45, 30, tzinfo=dt.timezone.utc)
        assert to_iso_z(aware) == "2026-06-15T13:45:30Z"
