"""Tests for the dashboard table widgets (Follow-up Required and Upcoming Deadlines)."""

import datetime as dt
import json
import time

from base_models import ProcessingStatus
from helpers.dashboard_utils import DashboardUtils

NOW = dt.datetime.now(dt.timezone.utc)
PAST = NOW - dt.timedelta(days=3)
TEN_DAYS_AGO = NOW - dt.timedelta(days=10)  # hidden by the default 14-day chase threshold
LONG_PAST = NOW - dt.timedelta(days=20)  # > 14-day default chase threshold → triggers follow-up
SOON = NOW + dt.timedelta(days=3)  # within 7-day default deadline threshold → upcoming deadline
FAR_FUTURE = NOW + dt.timedelta(days=14)  # beyond 7-day threshold → not upcoming


class TestFollowUpTable(DashboardUtils):
    """Tests for the Follow-up Required table widget.

    Shows pending applications whose last activity was > 14 days ago
    (the default chase threshold, configurable per widget in dashboard edit mode).
    """

    def setup_function(self, request) -> None:
        self._set_dashboard_widgets({"type": "table", "source": "follow_up"})
        self.login()

    def test_follow_up_table_empty_state_with_no_data(self) -> None:
        """With no data the empty state is shown."""

        assert self._empty_state_visible(self.FOLLOW_UP_TABLE)
        self._assert_row_count(self.FOLLOW_UP_TABLE, 0)

    def test_follow_up_table_badge_reflects_row_count(self) -> None:
        """Badge count matches the number of overdue applications."""

        self.user.create_job(title="Old App A", application_date=LONG_PAST, application_status="applied")
        self.user.create_job(title="Old App B", application_date=LONG_PAST, application_status="applied")
        self._reload()
        self._assert_row_count(self.FOLLOW_UP_TABLE, 2)
        rows = self._rows(self.FOLLOW_UP_TABLE)
        assert "Old App A" in rows[0].text
        assert "Old App B" in rows[1].text

    def test_follow_up_table_excludes_recent_application(self) -> None:
        """A recently updated application is not shown."""

        self.user.create_job(title="Recent", application_date=PAST, application_status="applied")
        self._reload()
        self._assert_row_count(self.FOLLOW_UP_TABLE, 0)

    def test_follow_up_table_excludes_rejected_and_offer(self) -> None:
        """Rejected applications are never shown."""

        self.user.create_job(title="Rejected", application_date=LONG_PAST, application_status="rejected")
        self.user.create_job(title="Offer", application_date=LONG_PAST, application_status="offer")
        self._reload()
        self._assert_row_count(self.FOLLOW_UP_TABLE, 0)

    def test_follow_up_table_mixed_data(self) -> None:
        """Only overdue pending applications appear; recent and terminal ones are excluded."""

        self.user.create_job(title="Overdue", application_date=LONG_PAST, application_status="applied")
        self.user.create_job(title="Recent", application_date=PAST, application_status="applied")
        self.user.create_job(title="Rejected", application_date=LONG_PAST, application_status="rejected")
        self._reload()
        self._assert_row_count(self.FOLLOW_UP_TABLE, 1)

    def test_follow_up_table_high_config_threshold_excludes_application(self) -> None:
        """A 10-day-old application is hidden when the widget's chase threshold is above 10."""

        self._set_dashboard_widgets({"type": "table", "source": "follow_up", "chaseThreshold": 30})
        self.login()
        self.user.create_job(title="Not Yet", application_date=TEN_DAYS_AGO, application_status="applied")
        self._reload()
        self._assert_row_count(self.FOLLOW_UP_TABLE, 0)

    def test_follow_up_table_config_change_persists_across_reload(self) -> None:
        """Lowering the threshold in the config sidebar surfaces the application, persists, and survives reload."""

        # 10 days old: hidden by the default 14-day threshold.
        self.user.create_job(title="Chase Me", application_date=TEN_DAYS_AGO, application_status="applied")
        self._reload()
        self._assert_row_count(self.FOLLOW_UP_TABLE, 0)

        self.dashboard_edit_utils.enter_edit_mode()
        self.dashboard_edit_utils.config_button(self.TEST_WIDGET_ID).click()
        time.sleep(0.3)  # allow the sidebar slide transition
        self.set_text(self.dashboard_edit_utils.widget_config_field(self.FOLLOW_UP_TABLE, "chaseThreshold"), "5")

        # Lowering the threshold to 5 surfaces the 10-day-old application live.
        assert len(self._rows(self.FOLLOW_UP_TABLE)) == 1

        self.dashboard_edit_utils.save()

        layout = json.loads(self.db_user.preferences.dashboard_layout)
        assert layout["widgets"][0]["config"]["chaseThreshold"] == 5

        self._reload()
        self._assert_row_count(self.FOLLOW_UP_TABLE, 1)


class TestUpcomingDeadlinesTable(DashboardUtils):
    """Tests for the Upcoming Deadlines table widget.

    Shows jobs with a deadline within the next 7 days (the default deadline
    threshold) that have not been applied to yet.
    """

    def setup_function(self, request) -> None:
        self._set_dashboard_widgets({"type": "table", "source": "upcoming_deadlines"})
        self.login()

    def test_upcoming_deadlines_empty_state_with_no_data(self) -> None:
        """With no data the empty state is shown."""

        assert self._empty_state_visible(self.UPCOMING_DEADLINES_TABLE)
        self._assert_row_count(self.UPCOMING_DEADLINES_TABLE, 0)

    def test_upcoming_deadlines_badge_reflects_row_count(self) -> None:
        """Badge count matches the number of jobs with upcoming deadlines."""

        self.user.create_job(title="Deadline A", deadline=SOON)
        self.user.create_job(title="Deadline B", deadline=SOON + dt.timedelta(days=1))
        self._reload()
        self._assert_row_count(self.UPCOMING_DEADLINES_TABLE, 2)
        rows = self._rows(self.UPCOMING_DEADLINES_TABLE)
        assert "Deadline A" in rows[0].text
        assert "Deadline B" in rows[1].text

    def test_upcoming_deadlines_excludes_far_future_deadline(self) -> None:
        """A job whose deadline is beyond the 7-day threshold is not shown."""

        self.user.create_job(title="Far Out", deadline=FAR_FUTURE)
        self._reload()
        self._assert_row_count(self.UPCOMING_DEADLINES_TABLE, 0)

    def test_upcoming_deadlines_excludes_applied_job_and_no_deadline(self) -> None:
        """A job that has already been applied to is not shown even if its deadline is soon."""

        self.user.create_job(title="Already Applied", deadline=SOON, application_status="applied")
        self.user.create_job(title="No Deadline")
        self.user.create_job(title="Rejected", deadline=SOON, application_status="rejected")
        self.user.create_job(title="Withdrawn", deadline=SOON, application_status="withdrawn")
        self._reload()
        self._assert_row_count(self.UPCOMING_DEADLINES_TABLE, 0)

    def test_upcoming_deadlines_mixed_data(self) -> None:
        """Only unapplied jobs with near deadlines appear."""

        self.user.create_job(title="Upcoming", deadline=SOON)
        self.user.create_job(title="Too Far", deadline=FAR_FUTURE)
        self.user.create_job(title="Applied", deadline=SOON, application_date=PAST, application_status="applied")
        self._reload()
        self._assert_row_count(self.UPCOMING_DEADLINES_TABLE, 1)

    def test_upcoming_deadlines_config_threshold_change_surfaces_job(self) -> None:
        """Raising the deadline threshold in the config sidebar surfaces a distant-deadline job."""

        # Deadline 14 days out: hidden by the default 7-day threshold.
        self.user.create_job(title="Apply Later", deadline=FAR_FUTURE)
        self._reload()
        self._assert_row_count(self.UPCOMING_DEADLINES_TABLE, 0)

        self.dashboard_edit_utils.enter_edit_mode()
        self.dashboard_edit_utils.config_button(self.TEST_WIDGET_ID).click()
        time.sleep(0.3)  # allow the sidebar slide transition
        field = self.dashboard_edit_utils.widget_config_field(self.UPCOMING_DEADLINES_TABLE, "deadlineThreshold")
        self.set_text(field, "20")

        # Raising the threshold to 20 surfaces the 14-day-out job live.
        self._assert_row_count(self.UPCOMING_DEADLINES_TABLE, 1)


class TestJobAlertsTable(DashboardUtils):
    """Tests for the Job Alerts table widget.

    Shows all scraped jobs belonging to the user, newest first.
    """

    def setup_function(self, request) -> None:
        self._set_dashboard_widgets({"type": "table", "source": "job_alerts"})
        self.login()

    def test_job_alerts_empty_state_with_no_data(self) -> None:
        """With no scraped jobs the empty state is shown."""

        assert self._empty_state_visible(self.JOB_ALERTS_TABLE)
        self._assert_row_count(self.JOB_ALERTS_TABLE, 0)

    def test_job_alerts_badge_reflects_row_count(self) -> None:
        """Badge count matches the number of scraped jobs, and each row shows its title."""

        self.user.create_scraped_job(title="Job A")
        self.user.create_scraped_job(title="Job B")
        self._reload()
        self._assert_row_count(self.JOB_ALERTS_TABLE, 2, "scrapedJob")
        rows = self._rows(self.JOB_ALERTS_TABLE, "scrapedJob")
        assert "Job A" in rows[1].text
        assert "Job B" in rows[0].text

    def test_job_alerts_shows_jobs_from_different_platforms(self) -> None:
        """Jobs from different platforms all appear in the table."""

        self.user.create_scraped_job(title="LinkedIn Job", platform="LinkedIn")
        self.user.create_scraped_job(title="Indeed Job", platform="Indeed")
        self._reload()
        self._assert_row_count(self.JOB_ALERTS_TABLE, 2, "scrapedJob")


class TestFavouritesTable(DashboardUtils):
    """Tests for the Favourite Job Alerts table widget.

    Only shows scraped jobs that match at least one active ScrapingFavouriteFilter.
    If no favourite filters exist the table is always empty.
    """

    def setup_function(self, request) -> None:
        self._set_dashboard_widgets({"type": "table", "source": "favourites"})
        self.login()

    def test_favourites_empty_state_with_no_data(self) -> None:
        """With no scraped jobs and no filters the empty state is shown."""

        assert self._empty_state_visible(self.FAVOURITES_TABLE)
        self._assert_row_count(self.FAVOURITES_TABLE, 0)

    def test_favourites_empty_when_no_filters_defined(self) -> None:
        """A scraped job with no favourite filters → never shown in favourites."""

        self.user.create_scraped_job(title="Python Developer")
        self._reload()
        self._assert_row_count(self.FAVOURITES_TABLE, 0, "scrapedJob")

    def test_favourites_badge_reflects_matching_count(self) -> None:
        """Badge count equals the number of matching jobs, and each row shows its title."""

        self.user.create_scraping_favourite_filter(type="title", operator="contains", value="Engineer")
        self.user.create_scraped_job(title="Software Engineer")
        self.user.create_scraped_job(title="Data Engineer")
        self._reload()
        self._assert_row_count(self.FAVOURITES_TABLE, 2, "scrapedJob")
        rows = self._rows(self.FAVOURITES_TABLE, "scrapedJob")
        assert "Data Engineer" in rows[0].text
        assert "Software Engineer" in rows[1].text

    def test_favourites_excludes_non_matching_and_inactive_filters(self) -> None:
        """Non-matching jobs, and jobs matched only by an inactive filter, are not shown."""

        self.user.create_scraping_favourite_filter(type="title", operator="contains", value="Engineer")
        self.user.create_scraping_favourite_filter(type="title", operator="contains", value="Python", is_active=False)
        self.user.create_scraped_job(title="Java Developer")  # matches no active filter
        self.user.create_scraped_job(title="Python Developer")  # matched only by the inactive filter
        self._reload()
        self._assert_row_count(self.FAVOURITES_TABLE, 0, "scrapedJob")

    def test_favourites_mixed_matching_and_non_matching(self) -> None:
        """Only the job that matches the filter is shown when mixed jobs exist."""

        self.user.create_scraping_favourite_filter(type="title", operator="contains", value="Python")
        self.user.create_scraped_job(title="Python Developer")
        self.user.create_scraped_job(title="Java Developer")
        self._reload()
        self._assert_row_count(self.FAVOURITES_TABLE, 1, "scrapedJob")


class TestFavouriteJobsTable(DashboardUtils):
    """Tests for the Favourite Jobs table widget.

    Shows every Job owned by the user that has is_favourite=True,
    regardless of application status or date.
    """

    def setup_function(self, request) -> None:
        self._set_dashboard_widgets({"type": "table", "source": "favourite_jobs"})
        self.login()

    def test_favourite_jobs_empty_state_with_no_data(self) -> None:
        """With no jobs the empty state is shown."""

        assert self._empty_state_visible(self.FAVOURITE_JOBS_TABLE)
        self._assert_row_count(self.FAVOURITE_JOBS_TABLE, 0)

    def test_favourite_jobs_badge_reflects_row_count(self) -> None:
        """Badge count matches the number of favourite jobs, and each row shows its title."""

        self.user.create_job(title="Fav A", is_favourite=True)
        self.user.create_job(title="Fav B", is_favourite=True)
        self._reload()
        self._assert_row_count(self.FAVOURITE_JOBS_TABLE, 2)
        rows = self._rows(self.FAVOURITE_JOBS_TABLE)
        assert "Fav A" in rows[0].text
        assert "Fav B" in rows[1].text

    def test_favourite_jobs_excludes_non_favourite_job(self) -> None:
        """A job with is_favourite=False (the default) is not shown."""

        self.user.create_job(title="Not Favourite")
        self._reload()
        self._assert_row_count(self.FAVOURITE_JOBS_TABLE, 0)

    def test_favourite_jobs_mixed_favourite_and_non_favourite(self) -> None:
        """Only jobs with is_favourite=True appear."""

        self.user.create_job(title="Favourite", is_favourite=True)
        self.user.create_job(title="Not Favourite")
        self._reload()
        self._assert_row_count(self.FAVOURITE_JOBS_TABLE, 1)

    def test_favourite_jobs_includes_applied_and_rejected_favourite(self) -> None:
        """Favourite jobs are shown regardless of application status."""

        self.user.create_job(
            title="Applied Fav", is_favourite=True, application_date=PAST, application_status="applied"
        )
        self.user.create_job(
            title="Rejected Fav", is_favourite=True, application_date=PAST, application_status="rejected"
        )
        self._reload()
        self._assert_row_count(self.FAVOURITE_JOBS_TABLE, 2)


class TestFailedJobsWidget(DashboardUtils):
    """Tests for the Failed Jobs table widget.

    Shows scraped jobs where status=ProcessingStatus.FAILED (permanent scrape failure)
    or job_rating.status=ProcessingStatus.FAILED (AI rating failure).
    Normal, successfully-scraped-and-rated jobs are never shown.
    """

    def setup_function(self, request) -> None:
        self._set_dashboard_widgets({"type": "table", "source": "error_jobs"})
        self.login()

    def test_failed_jobs_empty_state_with_no_data(self) -> None:
        """With no failed jobs the empty state is shown."""

        assert self._empty_state_visible(self.FAILED_JOBS_TABLE)
        self._assert_row_count(self.FAILED_JOBS_TABLE, 0)

    def test_failed_jobs_badge_reflects_row_count(self) -> None:
        """Both scrape-failed and rating-failed jobs are shown, with the badge and row titles."""

        self.user.create_scraped_job(title="Failed Scrape A", status=ProcessingStatus.FAILED)
        scraped_job = self.user.create_scraped_job(title="Failed Rating B")
        self.user.create_job_rating(scraped_job, status=ProcessingStatus.FAILED)
        self._reload()
        self._assert_row_count(self.FAILED_JOBS_TABLE, 2, "scrapedJob")
        rows = self._rows(self.FAILED_JOBS_TABLE, "scrapedJob")
        assert "Failed Rating B" in rows[0].text
        assert "Failed Scrape A" in rows[1].text

    def test_failed_jobs_excludes_normal_and_imported_jobs(self) -> None:
        """Successfully-rated jobs and imported failed jobs are not shown."""

        self.user.create_scraped_job(title="Normal Job")
        self.user.create_scraped_job(title="Imported Failed", status=ProcessingStatus.FAILED, is_imported=True)
        self._reload()
        self._assert_row_count(self.FAILED_JOBS_TABLE, 0, "scrapedJob")

    def test_failed_jobs_mixed_normal_and_failed(self) -> None:
        """Only failed jobs are shown when a mix of normal and failed jobs exists."""

        self.user.create_scraped_job(title="Normal Job")
        self.user.create_scraped_job(title="Failed Scrape", status=ProcessingStatus.FAILED)
        self._reload()
        self._assert_row_count(self.FAILED_JOBS_TABLE, 1, "scrapedJob")

    def test_failed_jobs_shows_job_with_past_deadline(self) -> None:
        """Failed jobs with a past deadline are still shown (deadline filter is skipped)."""

        past_deadline = NOW - dt.timedelta(days=5)
        self.user.create_scraped_job(title="Expired Failed", status=ProcessingStatus.FAILED, deadline=past_deadline)
        self._reload()
        self._assert_row_count(self.FAILED_JOBS_TABLE, 1, "scrapedJob")
