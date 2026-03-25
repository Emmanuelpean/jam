"""Tests for the dashboard stat/metrics cards (Total Jobs, Applications, Pending, Need Follow-up)."""

import datetime as dt

from dashboard_base import DashboardTestBase

# Default layout metric card IDs (set in StatCard.tsx / DashboardPage.tsx)
TOTAL_JOBS = "stat-card-total_jobs"
APPLICATIONS = "stat-card-applications"
PENDING = "stat-card-pending"
FOLLOW_UP = "stat-card-follow_up"

NOW = dt.datetime.now(dt.timezone.utc)
PAST = NOW - dt.timedelta(days=3)
LONG_PAST = NOW - dt.timedelta(days=20)  # > 14-day chase_threshold default


class TestMetricsCards(DashboardTestBase):
    """Tests for the four default stat cards on the dashboard.

    Default layout cards:
      - Total Jobs       — all jobs in the database
      - Applications     — jobs with application_date set
      - Pending          — applications with a non-terminal status
      - Need Follow-up   — pending applications overdue for a chase (> 14 days since last update)
    """

    user_index = 0

    def setup_function(self, request) -> None:
        self.login()

    # --------------------------------------------------- HELPERS ---------------------------------------------------

    def _value(self, card_id: str) -> int:
        """Return the integer value displayed on the stat card."""
        return int(self.get_element(f"{card_id}-value").text)

    # ----------------------------------------------- CARD RENDERS -------------------------------------------------

    def test_all_default_metric_cards_render(self) -> None:
        """All four default metric cards must be visible on the dashboard."""
        for card_id in (TOTAL_JOBS, APPLICATIONS, PENDING, FOLLOW_UP):
            assert self.get_element(card_id).is_displayed(), f"{card_id} not visible"

    # ----------------------------------------------- TOTAL JOBS ---------------------------------------------------

    def test_total_jobs_is_zero_with_no_data(self) -> None:
        assert self._value(TOTAL_JOBS) == 0

    def test_total_jobs_counts_all_jobs(self) -> None:
        """Total Jobs includes every job regardless of application status."""
        self._create_job(title="Job A")
        self._create_job(title="Job B")
        self._create_job(title="Job C", application_date=PAST, application_status="applied")
        self._reload()
        assert self._value(TOTAL_JOBS) == 3

    def test_total_jobs_includes_unapplied_jobs(self) -> None:
        """Jobs without an application_date still count toward Total Jobs."""
        self._create_job(title="Saved Job")
        self._reload()
        assert self._value(TOTAL_JOBS) == 1

    # --------------------------------------------- APPLICATIONS --------------------------------------------------

    def test_applications_is_zero_with_no_data(self) -> None:
        assert self._value(APPLICATIONS) == 0

    def test_applications_counts_jobs_with_application_date(self) -> None:
        """Only jobs with application_date set are counted as Applications."""
        self._create_job(title="Applied Job", application_date=PAST, application_status="applied")
        self._create_job(title="Saved Job")  # no application_date — not counted
        self._reload()
        assert self._value(APPLICATIONS) == 1

    def test_applications_counts_multiple(self) -> None:
        self._create_job(title="Job A", application_date=PAST, application_status="applied")
        self._create_job(title="Job B", application_date=PAST - dt.timedelta(days=1), application_status="applied")
        self._reload()
        assert self._value(APPLICATIONS) == 2

    # ----------------------------------------------- PENDING ------------------------------------------------------

    def test_pending_is_zero_with_no_data(self) -> None:
        assert self._value(PENDING) == 0

    def test_pending_counts_non_terminal_applications(self) -> None:
        """Applied jobs with a non-terminal status are counted as Pending."""
        self._create_job(title="Applied", application_date=PAST, application_status="applied")
        self._reload()
        assert self._value(PENDING) == 1

    def test_pending_excludes_rejected(self) -> None:
        """Rejected applications do not count toward Pending."""
        self._create_job(title="Rejected", application_date=PAST, application_status="rejected")
        self._reload()
        assert self._value(PENDING) == 0

    def test_pending_excludes_withdrawn(self) -> None:
        """Withdrawn applications do not count toward Pending."""
        self._create_job(title="Withdrawn", application_date=PAST, application_status="withdrawn")
        self._reload()
        assert self._value(PENDING) == 0

    def test_pending_excludes_jobs_without_application_status(self) -> None:
        """Jobs with application_date but no status do not count toward Pending."""
        self._create_job(title="No Status", application_date=PAST)
        self._reload()
        assert self._value(PENDING) == 0

    def test_pending_mixed(self) -> None:
        """Only the non-terminal application is counted when mixed statuses are present."""
        self._create_job(title="Active", application_date=PAST, application_status="applied")
        self._create_job(title="Rejected", application_date=PAST, application_status="rejected")
        self._reload()
        assert self._value(PENDING) == 1

    # ---------------------------------------------- NEED FOLLOW-UP -----------------------------------------------

    def test_follow_up_is_zero_with_no_data(self) -> None:
        assert self._value(FOLLOW_UP) == 0

    def test_follow_up_counts_overdue_application(self) -> None:
        """A pending application with no update for > 14 days counts as needing follow-up."""
        self._create_job(title="Old App", application_date=LONG_PAST, application_status="applied")
        self._reload()
        assert self._value(FOLLOW_UP) == 1

    def test_follow_up_excludes_recent_application(self) -> None:
        """A pending application updated recently (within threshold) is not flagged."""
        self._create_job(title="Recent App", application_date=PAST, application_status="applied")
        self._reload()
        assert self._value(FOLLOW_UP) == 0

    def test_follow_up_excludes_rejected(self) -> None:
        """Rejected applications are never flagged for follow-up."""
        self._create_job(title="Rejected", application_date=LONG_PAST, application_status="rejected")
        self._reload()
        assert self._value(FOLLOW_UP) == 0

    def test_follow_up_excludes_offer(self) -> None:
        """Jobs where an offer has been made are not flagged for follow-up."""
        self._create_job(title="Offer", application_date=LONG_PAST, application_status="offer")
        self._reload()
        assert self._value(FOLLOW_UP) == 0
