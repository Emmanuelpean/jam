"""Tests for the non-default dashboard metric cards (Active Applications, Interview Rate, Avg. Response Time).

These cards are absent from the default layout, so each test uses _set_dashboard_widgets()
to inject them into the user's layout before the page is loaded.
"""

import datetime as dt

from dashboard_base import DashboardTestBase

ACTIVE_APPLICATIONS = "stat-card-active_applications"
INTERVIEW_RATE = "stat-card-interview_rate"
AVG_RESPONSE_TIME = "stat-card-avg_response_time"

NOW = dt.datetime.now(dt.timezone.utc)
PAST = NOW - dt.timedelta(days=3)
LONG_PAST = NOW - dt.timedelta(days=20)


class TestExtraMetricsCards(DashboardTestBase):
    """Tests for the three non-default stat cards on the dashboard.

    Cards tested:
      - Active Applications — jobs with a non-rejected/withdrawn application status
      - Interview Rate      — % of applications that have at least one interview
      - Avg. Response Time  — average days from application_date to last activity date
    """

    user_index = 0

    def setup_function(self, request) -> None:
        self._set_dashboard_widgets(
            {"type": "metric", "metric": "active_applications"},
            {"type": "metric", "metric": "interview_rate"},
            {"type": "metric", "metric": "avg_response_time"},
        )
        self.login()

    # --------------------------------------------------- HELPERS ---------------------------------------------------

    def _value(self, card_id: str) -> int:
        """Return the integer value on a plain-number stat card."""
        return int(self.get_element(f"{card_id}-value").text)

    def _pct_value(self, card_id: str) -> int:
        """Return the integer percentage value (strips trailing '%')."""
        return int(self.get_element(f"{card_id}-value").text.rstrip("%"))

    def _days_value(self, card_id: str) -> int:
        """Return the integer days value (strips trailing 'd')."""
        return int(self.get_element(f"{card_id}-value").text.rstrip("d"))

    # ----------------------------------------------- CARD RENDERS -------------------------------------------------

    def test_all_extra_metric_cards_render(self) -> None:
        """All three extra metric cards must be visible after setting a custom layout."""
        for card_id in (ACTIVE_APPLICATIONS, INTERVIEW_RATE, AVG_RESPONSE_TIME):
            assert self.get_element(card_id).is_displayed(), f"{card_id} not visible"

    # ------------------------------------------- ACTIVE APPLICATIONS ----------------------------------------------

    def test_active_applications_is_zero_with_no_data(self) -> None:
        assert self._value(ACTIVE_APPLICATIONS) == 0

    def test_active_applications_counts_applied_status(self) -> None:
        self._create_job(title="Applied", application_date=PAST, application_status="applied")
        self._reload()
        assert self._value(ACTIVE_APPLICATIONS) == 1

    def test_active_applications_counts_offer_status(self) -> None:
        """'offer' is an active status — not rejected or withdrawn."""
        self._create_job(title="Offer", application_date=PAST, application_status="offer")
        self._reload()
        assert self._value(ACTIVE_APPLICATIONS) == 1

    def test_active_applications_excludes_rejected(self) -> None:
        self._create_job(title="Rejected", application_date=PAST, application_status="rejected")
        self._reload()
        assert self._value(ACTIVE_APPLICATIONS) == 0

    def test_active_applications_excludes_withdrawn(self) -> None:
        self._create_job(title="Withdrawn", application_date=PAST, application_status="withdrawn")
        self._reload()
        assert self._value(ACTIVE_APPLICATIONS) == 0

    def test_active_applications_mixed(self) -> None:
        """Only non-terminal statuses are counted."""
        self._create_job(title="Applied", application_date=PAST, application_status="applied")
        self._create_job(title="Offer", application_date=PAST, application_status="offer")
        self._create_job(title="Rejected", application_date=PAST, application_status="rejected")
        self._reload()
        assert self._value(ACTIVE_APPLICATIONS) == 2

    # ---------------------------------------------- INTERVIEW RATE -----------------------------------------------

    def test_interview_rate_is_zero_with_no_data(self) -> None:
        assert self._pct_value(INTERVIEW_RATE) == 0

    def test_interview_rate_is_zero_when_no_interviews(self) -> None:
        """Applications with no interviews yield a 0% interview rate."""
        self._create_job(title="No Interview", application_date=PAST, application_status="applied")
        self._reload()
        assert self._pct_value(INTERVIEW_RATE) == 0

    def test_interview_rate_is_100_when_all_applications_have_interviews(self) -> None:
        """One application with one interview → 100%."""
        job = self._create_job(title="Interviewed", application_date=PAST, application_status="applied")
        self._create_interview(job_id=job.id, date=PAST)
        self._reload()
        assert self._pct_value(INTERVIEW_RATE) == 100

    def test_interview_rate_is_50_for_one_of_two_applications(self) -> None:
        """One of two applications has an interview → 50%."""
        job1 = self._create_job(title="Interviewed", application_date=PAST, application_status="applied")
        self._create_job(title="Not Interviewed", application_date=PAST, application_status="applied")
        self._create_interview(job_id=job1.id, date=PAST)
        self._reload()
        assert self._pct_value(INTERVIEW_RATE) == 50

    def test_interview_rate_counts_job_once_with_multiple_interviews(self) -> None:
        """A job with two interviews still counts as one unique application in the numerator."""
        job = self._create_job(title="Multi Interview", application_date=PAST, application_status="applied")
        self._create_interview(job_id=job.id, date=PAST)
        self._create_interview(job_id=job.id, date=PAST - dt.timedelta(days=1))
        self._reload()
        # 1 unique job with interviews / 1 total application = 100%
        assert self._pct_value(INTERVIEW_RATE) == 100

    # ------------------------------------------- AVG RESPONSE TIME -----------------------------------------------

    def test_avg_response_time_is_zero_with_no_data(self) -> None:
        assert self._days_value(AVG_RESPONSE_TIME) == 0

    def test_avg_response_time_is_zero_with_no_updates(self) -> None:
        """An application with no interviews or updates has last_update_date = application_date → 0 days."""
        self._create_job(title="No Updates", application_date=PAST, application_status="applied")
        self._reload()
        assert self._days_value(AVG_RESPONSE_TIME) == 0

    def test_avg_response_time_with_update(self) -> None:
        """A job application update 2 days after the application → avg response time = 2 days."""
        job = self._create_job(title="With Update", application_date=LONG_PAST, application_status="applied")
        self._create_update(job_id=job.id, date=LONG_PAST + dt.timedelta(days=2))
        self._reload()
        assert self._days_value(AVG_RESPONSE_TIME) == 2

    def test_avg_response_time_with_interview(self) -> None:
        """An interview 3 days after the application → avg response time = 3 days."""
        job = self._create_job(title="With Interview", application_date=LONG_PAST, application_status="applied")
        self._create_interview(job_id=job.id, date=LONG_PAST + dt.timedelta(days=3))
        self._reload()
        assert self._days_value(AVG_RESPONSE_TIME) == 3

    def test_avg_response_time_averaged_across_multiple_applications(self) -> None:
        """Average of a 2-day and a 4-day response = 3 days."""
        job1 = self._create_job(title="Job A", application_date=LONG_PAST, application_status="applied")
        job2 = self._create_job(title="Job B", application_date=LONG_PAST, application_status="applied")
        self._create_update(job_id=job1.id, date=LONG_PAST + dt.timedelta(days=2))
        self._create_update(job_id=job2.id, date=LONG_PAST + dt.timedelta(days=4))
        self._reload()
        assert self._days_value(AVG_RESPONSE_TIME) == 3
