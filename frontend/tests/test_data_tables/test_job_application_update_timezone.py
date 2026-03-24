"""Tests for timezone handling in job application updates.
Verifies that when a user in a given browser timezone submits a job application
update using "Set Current", the datetime captured, stored, and displayed is
self-consistent: the view modal must show the same datetime as the browser
would have displayed at the moment the user clicked "Set Current"."""

import datetime as dt

import pytest

from base_test import BaseTest, models

# Each entry: (cdp_timezone_id, utc_offset_hours, utc_offset_minutes)
# Dates chosen to avoid DST transitions (2025-03-05):
#   - Europe/London -> GMT (BST starts 30 March)
#   - America/New_York -> EST (DST starts 9 March)
#   - Asia/Kolkata -> IST (no DST ever)
#   - Australia/Sydney -> AEDT (DST ends first Sunday of April)
TIMEZONE_TEST_CASES = [
    ("Europe/London", 0, 0),
    ("America/New_York", -5, 0),
    ("Asia/Kolkata", 5, 30),
    ("Australia/Sydney", 11, 0),
]

# A fixed UTC moment used across all tests so clock mocking is deterministic.
FIXED_UTC = dt.datetime(2025, 3, 5, 10, 0, 0, tzinfo=dt.timezone.utc)


class TestJobApplicationUpdateTimezone(BaseTest):
    """Test that job application update datetimes are stored and displayed
    correctly when the browser timezone differs from UTC."""

    page_url = "job-application-updates"

    def setup_function(self, request) -> None:
        """Setup for each test function."""

        test_jobs = request.getfixturevalue("test_jobs")
        # Pick the first job owned by this user
        self.test_job = next(j for j in test_jobs if j.owner_id == self.user.id)
        self.login()
        self.go_to_page(self.page_url)

    def _set_browser_timezone(self, timezone_id: str) -> None:
        """Override the browser timezone via CDP."""

        self.driver.execute_cdp_cmd("Emulation.setTimezoneOverride", {"timezoneId": timezone_id})

    def _mock_browser_clock(self, utc_dt: dt.datetime) -> None:
        """Replace window.Date with a mock that always returns a fixed UTC moment
        when called with no arguments, while leaving Date(value) constructors intact."""

        timestamp_ms = int(utc_dt.timestamp() * 1000)
        self.driver.execute_script(
            """
            const fixedMs = arguments[0];
            const RealDate = window.Date;

            function MockDate(...args) {
                if (this instanceof MockDate) {
                    return args.length ? new RealDate(...args) : new RealDate(fixedMs);
                }
                return RealDate();
            }

            MockDate.prototype = RealDate.prototype;
            MockDate.now    = () => fixedMs;
            MockDate.parse  = RealDate.parse;
            MockDate.UTC    = RealDate.UTC;

            window.Date = MockDate;
            """,
            timestamp_ms,
        )

    def _add_update_via_set_current(self, note: str) -> None:
        """Open the add-update modal, fill it using Set Current for the date, and submit."""

        job_label = f"{self.test_job.title} ({self.test_job.company.name})"
        self.jobApplicationUpdate_table_utils.add_entity_button.click()
        self.jobApplicationUpdate_modal_utils._fill_modal(
            job_id=job_label,
            type="Received",
            date=None,  # value ignored — _fill_modal clicks {field}_set_current
            note=note,
        )
        self.jobApplicationUpdate_modal_utils.confirm_button("edit").click()
        self.jobApplicationUpdate_modal_utils.wait_for_edit_modal_close()

    def _get_db_entry(self, note: str) -> models.JobApplicationUpdate:
        """Return the most recently created update owned by this user with the given note."""

        self.db.expire_all()
        return (
            self.db.query(models.JobApplicationUpdate)
            .filter_by(owner_id=self.user.id, note=note)
            .order_by(models.JobApplicationUpdate.created_at.desc())
            .first()
        )

    # ------------------------------------------------------------------- tests

    @pytest.mark.parametrize(
        "timezone_id,utc_offset_hours,utc_offset_minutes",
        TIMEZONE_TEST_CASES,
        ids=[tz for tz, *_ in TIMEZONE_TEST_CASES],
    )
    def test_set_current_stores_local_time(
        self,
        timezone_id: str,
        utc_offset_hours: int,
        utc_offset_minutes: int,
    ) -> None:
        """Clicking "Set Current" in timezone TZ at a fixed UTC moment stores the
        corresponding local time as a naive UTC value in the database."""

        self._set_browser_timezone(timezone_id)
        self._mock_browser_clock(FIXED_UTC)

        note = f"tz-store-test: {timezone_id}"
        self._add_update_via_set_current(note)

        entry = self._get_db_entry(note)
        assert entry is not None, f"No DB entry found for timezone {timezone_id}"

        # The browser captures local time in TZ: FIXED_UTC expressed in TZ.
        # The frontend sends a naive ISO string (no offset), so the backend stores
        # that local time as-is, treated as UTC by PostgreSQL.
        browser_tz = dt.timezone(dt.timedelta(hours=utc_offset_hours, minutes=utc_offset_minutes))
        expected_local = FIXED_UTC.astimezone(browser_tz).replace(tzinfo=None)

        stored = entry.date.replace(tzinfo=None)
        assert stored == expected_local, f"[{timezone_id}] DB stored {stored}, expected local time {expected_local}"

    @pytest.mark.parametrize(
        "timezone_id,utc_offset_hours,utc_offset_minutes",
        TIMEZONE_TEST_CASES,
        ids=[tz for tz, *_ in TIMEZONE_TEST_CASES],
    )
    def test_view_modal_displays_stored_time_in_browser_timezone(
        self,
        timezone_id: str,
        utc_offset_hours: int,
        utc_offset_minutes: int,
    ) -> None:
        """The view modal renders the stored UTC datetime in the browser's local
        timezone, so the displayed value equals stored_utc.astimezone(browser_tz)."""

        self._set_browser_timezone(timezone_id)
        self._mock_browser_clock(FIXED_UTC)

        note = f"tz-display-test: {timezone_id}"
        self._add_update_via_set_current(note)

        entry = self._get_db_entry(note)
        assert entry is not None, f"No DB entry found for timezone {timezone_id}"

        # The frontend receives the stored UTC value and formats it with
        # Intl.DateTimeFormat(undefined) — which uses the CDP-overridden timezone.
        browser_tz = dt.timezone(dt.timedelta(hours=utc_offset_hours, minutes=utc_offset_minutes))
        expected_display = entry.date.astimezone(browser_tz).strftime("%d/%m/%Y %H:%M")

        # Open the view modal for the freshly added row (first row, newest-first order)
        self.jobApplicationUpdate_table_utils.table_rows[0].click()
        modal = self.jobApplicationUpdate_modal_utils.wait_for_view_modal()

        assert (
            expected_display in modal.text
        ), f"[{timezone_id}] Expected display '{expected_display}' not found in modal:\n{modal.text}"

        self.jobApplicationUpdate_modal_utils.cancel_button("view").click()
        self.jobApplicationUpdate_modal_utils.wait_for_view_modal_close()
