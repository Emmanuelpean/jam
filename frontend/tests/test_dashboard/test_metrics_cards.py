"""Tests for the dashboard stat/metrics cards (Total Jobs, Applications, Pending, Need Follow-up)."""

import datetime as dt

from dashboard_base import DashboardTestBase

# Default layout metric card IDs (set in StatCard.tsx / DashboardPage.tsx)
TOTAL_JOBS = "stat-card-total_jobs"
APPLICATIONS = "stat-card-applications"
PENDING = "stat-card-pending"
FOLLOW_UP = "stat-card-follow_up"
ACTIVE_APPLICATIONS = "stat-card-active_applications"
INTERVIEW_RATE = "stat-card-interview_rate"
AVG_RESPONSE_TIME = "stat-card-avg_response_time"

NOW = dt.datetime.now(dt.timezone.utc)
PAST = NOW - dt.timedelta(days=3)
LONG_PAST = NOW - dt.timedelta(days=20)  # > 14-day chase_threshold default


class TestMetricsCards(DashboardTestBase):
    """Tests for metrics cards on the dashboard."""

    def setup_total_jobs(self, request=None) -> None:
        _ = request
        self._set_dashboard_widgets({"type": "metric", "metric": "total_jobs"})
        self.login()

    def setup_applications(self, request=None) -> None:
        _ = request
        self._set_dashboard_widgets({"type": "metric", "metric": "applications"})
        self.login()

    def setup_pending_applications(self, request=None) -> None:
        _ = request
        self._set_dashboard_widgets({"type": "metric", "metric": "pending"})
        self.login()

    def setup_follow_up(self, request=None) -> None:
        _ = request
        self._set_dashboard_widgets({"type": "metric", "metric": "follow_up"})
        self.login()

    def setup_active_applications(self, request=None) -> None:
        _ = request
        self._set_dashboard_widgets({"type": "metric", "metric": "active_applications"})
        self.login()

    def setup_interview_rate(self, request=None) -> None:
        _ = request
        self._set_dashboard_widgets({"type": "metric", "metric": "interview_rate"})
        self.login()

    def setup_avg_response_time(self, request=None) -> None:
        _ = request
        self._set_dashboard_widgets({"type": "metric", "metric": "avg_response_time"})
        self.login()

    # --------------------------------------------------- HELPERS ---------------------------------------------------

    def _value(self, card_id: str) -> int:
        """Return the integer value displayed on the stat card."""
        return int(self.get_element(f"{card_id}-value").text)

    def _pct_value(self, card_id: str) -> int:
        """Return the integer percentage value (strips trailing '%')."""
        return int(self.get_element(f"{card_id}-value").text.rstrip("%"))

    def _days_value(self, card_id: str) -> int:
        """Return the integer days value (strips trailing 'd')."""
        return int(self.get_element(f"{card_id}-value").text.rstrip("d"))

    # ----------------------------------------------- TOTAL JOBS ---------------------------------------------------

    def test_total_jobs_is_zero_with_no_data(self) -> None:
        """Total Jobs is zero when there are no jobs in the database."""

        self.setup_total_jobs()
        assert self._value(TOTAL_JOBS) == 0

    def test_total_jobs_counts_all_jobs(self) -> None:
        """Total Jobs includes every job regardless of application status."""

        self.setup_total_jobs()
        self._create_job(title="Job A")
        self._create_job(title="Job B")
        self._create_job(title="Job C", application_date=PAST, application_status="applied")
        self._reload()
        assert self._value(TOTAL_JOBS) == 3

    def test_total_jobs_includes_unapplied_jobs(self) -> None:
        """Jobs without an application_date still count toward Total Jobs."""

        self.setup_total_jobs()
        self._create_job(title="Saved Job")
        self._reload()
        assert self._value(TOTAL_JOBS) == 1

    # --------------------------------------------- APPLICATIONS --------------------------------------------------

    def test_applications_is_zero_with_no_data(self) -> None:
        """Total application is zero when there are no jobs with application_date set."""

        self.setup_applications()
        assert self._value(APPLICATIONS) == 0

    def test_applications_counts_jobs_with_application_date(self) -> None:
        """Only jobs with application_date set are counted as Applications."""

        self.setup_applications()
        self._create_job(title="Applied Job", application_date=PAST, application_status="applied")
        self._create_job(title="Saved Job")  # no application_date — not counted
        self._reload()
        assert self._value(APPLICATIONS) == 1

    def test_applications_counts_multiple(self) -> None:
        """Total number of jobs with application_date is counted correctly."""

        self.setup_applications()
        self._create_job(title="Job A", application_date=PAST, application_status="applied")
        self._create_job(title="Job B", application_date=PAST - dt.timedelta(days=1), application_status="applied")
        self._reload()
        assert self._value(APPLICATIONS) == 2

    # ----------------------------------------------- PENDING ------------------------------------------------------

    def test_pending_is_zero_with_no_data(self) -> None:
        """Pending applications is zero when there are no jobs with a non-terminal status."""

        self.setup_pending_applications()
        assert self._value(PENDING) == 0

    def test_pending_counts_non_terminal_applications(self) -> None:
        """Applied jobs with a non-terminal status are counted as Pending."""

        self.setup_pending_applications()
        self._create_job(title="Applied", application_date=PAST, application_status="applied")
        self._reload()
        assert self._value(PENDING) == 1

    def test_pending_excludes_rejected(self) -> None:
        """Rejected applications do not count toward Pending."""

        self.setup_pending_applications()
        self._create_job(title="Rejected", application_date=PAST, application_status="rejected")
        self._reload()
        assert self._value(PENDING) == 0

    def test_pending_excludes_withdrawn(self) -> None:
        """Withdrawn applications do not count toward Pending."""

        self.setup_pending_applications()
        self._create_job(title="Withdrawn", application_date=PAST, application_status="withdrawn")
        self._reload()
        assert self._value(PENDING) == 0

    def test_pending_excludes_jobs_without_application_status(self) -> None:
        """Jobs with application_date but no status do not count toward Pending."""

        self.setup_pending_applications()
        self._create_job(title="No Status", application_date=PAST)
        self._reload()
        assert self._value(PENDING) == 0

    def test_pending_mixed(self) -> None:
        """Only the non-terminal application is counted when mixed statuses are present."""

        self.setup_pending_applications()
        self._create_job(title="Active", application_date=PAST, application_status="applied")
        self._create_job(title="Rejected", application_date=PAST, application_status="rejected")
        self._reload()
        assert self._value(PENDING) == 1

    # ---------------------------------------------- NEED FOLLOW-UP -----------------------------------------------

    def test_follow_up_is_zero_with_no_data(self) -> None:
        """Pending applications with no update for > 14 days is zero."""

        self.setup_follow_up()
        assert self._value(FOLLOW_UP) == 0

    def test_follow_up_counts_overdue_application(self) -> None:
        """A pending application with no update for > 14 days counts as needing follow-up."""

        self.setup_follow_up()
        self._create_job(title="Old App", application_date=LONG_PAST, application_status="applied")
        self._reload()
        assert self._value(FOLLOW_UP) == 1

    def test_follow_up_excludes_recent_application(self) -> None:
        """A pending application updated recently (within threshold) is not flagged."""

        self.setup_follow_up()
        self._create_job(title="Recent App", application_date=PAST, application_status="applied")
        self._reload()
        assert self._value(FOLLOW_UP) == 0

    def test_follow_up_excludes_rejected(self) -> None:
        """Rejected applications are never flagged for follow-up."""

        self.setup_follow_up()
        self._create_job(title="Rejected", application_date=LONG_PAST, application_status="rejected")
        self._reload()
        assert self._value(FOLLOW_UP) == 0

    def test_follow_up_excludes_offer(self) -> None:
        """Jobs where an offer has been made are not flagged for follow-up."""

        self.setup_follow_up()
        self._create_job(title="Offer", application_date=LONG_PAST, application_status="offer")
        self._reload()
        assert self._value(FOLLOW_UP) == 0

    # ------------------------------------------- ACTIVE APPLICATIONS ----------------------------------------------

    def test_active_applications_is_zero_with_no_data(self) -> None:
        """Active application is zero when there are no jobs with a non-terminal status."""

        self.setup_active_applications()
        assert self._value(ACTIVE_APPLICATIONS) == 0

    def test_active_applications_counts_applied_status(self) -> None:
        """Active applications are those with a non-terminal status."""

        self.setup_active_applications()
        self._create_job(title="Applied", application_date=PAST, application_status="applied")
        self._reload()
        assert self._value(ACTIVE_APPLICATIONS) == 1

    def test_active_applications_counts_offer_status(self) -> None:
        """'offer' is an active status — not rejected or withdrawn."""

        self.setup_active_applications()
        self._create_job(title="Offer", application_date=PAST, application_status="offer")
        self._reload()
        assert self._value(ACTIVE_APPLICATIONS) == 1

    def test_active_applications_excludes_rejected(self) -> None:
        """Rejected applications are not counted as active applications."""

        self.setup_active_applications()
        self._create_job(title="Rejected", application_date=PAST, application_status="rejected")
        self._reload()
        assert self._value(ACTIVE_APPLICATIONS) == 0

    def test_active_applications_excludes_withdrawn(self) -> None:
        """Withdrawn applications are not counted as active applications."""

        self.setup_active_applications()
        self._create_job(title="Withdrawn", application_date=PAST, application_status="withdrawn")
        self._reload()
        assert self._value(ACTIVE_APPLICATIONS) == 0

    def test_active_applications_mixed(self) -> None:
        """Only non-terminal statuses are counted."""

        self.setup_active_applications()
        self._create_job(title="Applied", application_date=PAST, application_status="applied")
        self._create_job(title="Offer", application_date=PAST, application_status="offer")
        self._create_job(title="Rejected", application_date=PAST, application_status="rejected")
        self._reload()
        assert self._value(ACTIVE_APPLICATIONS) == 2

    # ---------------------------------------------- INTERVIEW RATE -----------------------------------------------

    def test_interview_rate_is_zero_with_no_data(self) -> None:
        """Interview rate is zero when there are no jobs with interviews."""

        self.setup_interview_rate()
        assert self._pct_value(INTERVIEW_RATE) == 0

    def test_interview_rate_is_zero_when_no_interviews(self) -> None:
        """Applications with no interviews yield a 0% interview rate."""

        self.setup_interview_rate()
        self._create_job(title="No Interview", application_date=PAST, application_status="applied")
        self._reload()
        assert self._pct_value(INTERVIEW_RATE) == 0

    def test_interview_rate_is_100_when_all_applications_have_interviews(self) -> None:
        """One application with one interview → 100%."""

        self.setup_interview_rate()
        job = self._create_job(title="Interviewed", application_date=PAST, application_status="applied")
        self._create_interview(job_id=job.id, date=PAST)
        self._reload()
        assert self._pct_value(INTERVIEW_RATE) == 100

    def test_interview_rate_is_50_for_one_of_two_applications(self) -> None:
        """One of two applications has an interview → 50%."""

        self.setup_interview_rate()
        job1 = self._create_job(title="Interviewed", application_date=PAST, application_status="applied")
        self._create_job(title="Not Interviewed", application_date=PAST, application_status="applied")
        self._create_interview(job_id=job1.id, date=PAST)
        self._reload()
        assert self._pct_value(INTERVIEW_RATE) == 50

    def test_interview_rate_counts_job_once_with_multiple_interviews(self) -> None:
        """A job with two interviews still counts as one unique application in the numerator."""

        self.setup_interview_rate()
        job = self._create_job(title="Multi Interview", application_date=PAST, application_status="applied")
        self._create_interview(job_id=job.id, date=PAST)
        self._create_interview(job_id=job.id, date=PAST - dt.timedelta(days=1))
        self._reload()
        # 1 unique job with interviews / 1 total application = 100%
        assert self._pct_value(INTERVIEW_RATE) == 100

    # ------------------------------------------- AVG RESPONSE TIME -----------------------------------------------

    def test_avg_response_time_is_zero_with_no_data(self) -> None:
        """Avg response time is zero when there are no jobs with interviews or updates."""

        self.setup_avg_response_time()
        assert self._days_value(AVG_RESPONSE_TIME) == 0

    def test_avg_response_time_is_zero_with_no_updates(self) -> None:
        """An application with no interviews or updates has last_update_date = application_date → 0 days."""

        self.setup_avg_response_time()
        self._create_job(title="No Updates", application_date=PAST, application_status="applied")
        self._reload()
        assert self._days_value(AVG_RESPONSE_TIME) == 0

    def test_avg_response_time_with_update(self) -> None:
        """A job application update 2 days after the application → avg response time = 2 days."""

        self.setup_avg_response_time()
        job = self._create_job(title="With Update", application_date=LONG_PAST, application_status="applied")
        self._create_update(job_id=job.id, date=LONG_PAST + dt.timedelta(days=2))
        self._reload()
        assert self._days_value(AVG_RESPONSE_TIME) == 2

    def test_avg_response_time_with_interview(self) -> None:
        """An interview 3 days after the application → avg response time = 3 days."""

        self.setup_avg_response_time()
        job = self._create_job(title="With Interview", application_date=LONG_PAST, application_status="applied")
        self._create_interview(job_id=job.id, date=LONG_PAST + dt.timedelta(days=3))
        self._reload()
        assert self._days_value(AVG_RESPONSE_TIME) == 3

    def test_avg_response_time_averaged_across_multiple_applications(self) -> None:
        """Average of a 2-day and a 4-day response = 3 days."""

        self.setup_avg_response_time()
        job1 = self._create_job(title="Job A", application_date=LONG_PAST, application_status="applied")
        job2 = self._create_job(title="Job B", application_date=LONG_PAST, application_status="applied")
        self._create_update(job_id=job1.id, date=LONG_PAST + dt.timedelta(days=2))
        self._create_update(job_id=job2.id, date=LONG_PAST + dt.timedelta(days=4))
        self._reload()
        assert self._days_value(AVG_RESPONSE_TIME) == 3
