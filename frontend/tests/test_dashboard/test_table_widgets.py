"""Tests for the dashboard table widgets (Follow-up Required and Upcoming Deadlines)."""

import datetime as dt

from selenium.webdriver.common.by import By

from app import models
from dashboard_base import DashboardTestBase

FOLLOW_UP_TABLE = "table-card-follow_up"
UPCOMING_DEADLINES_TABLE = "table-card-upcoming_deadlines"
JOB_ALERTS_TABLE = "table-card-job_alerts"
FAVOURITES_TABLE = "table-card-favourites"
FAVOURITE_JOBS_TABLE = "table-card-favourite_jobs"
FAILED_JOBS_TABLE = "table-card-error_jobs"


NOW = dt.datetime.now(dt.timezone.utc)
PAST = NOW - dt.timedelta(days=3)
LONG_PAST = NOW - dt.timedelta(days=20)  # > 14-day chase_threshold → triggers follow-up
SOON = NOW + dt.timedelta(days=3)  # within 7-day deadline_threshold → upcoming deadline
FAR_FUTURE = NOW + dt.timedelta(days=14)  # beyond 7-day threshold → not upcoming


class TestFollowUpTable(DashboardTestBase):
    """Tests for the Follow-up Required table widget.

    Shows pending applications whose last activity was > 14 days ago
    (configurable via UserPreferences.chase_threshold).
    """

    user_index = 0

    def setup_function(self, request) -> None:
        self._set_dashboard_widgets({"type": "table", "source": "follow_up"})
        self.login()

    # --------------------------------------------------- HELPERS ---------------------------------------------------

    def _badge_count(self) -> int:
        return int(self.get_element(f"{FOLLOW_UP_TABLE}-badge").text)

    def _rows(self):
        card = self.get_element(FOLLOW_UP_TABLE)
        return card.find_elements(By.CSS_SELECTOR, "[id^='table-row-job-']")

    def _empty_state_visible(self) -> bool:
        return self.check_element_exists(f"{FOLLOW_UP_TABLE}-empty")

    # ---------------------------------------------------- TESTS ----------------------------------------------------

    def test_follow_up_table_renders(self) -> None:
        """The Follow-up table card must be visible on a dashboard with the widget configured."""
        assert self.get_element(FOLLOW_UP_TABLE).is_displayed()

    def test_follow_up_table_empty_state_with_no_data(self) -> None:
        """With no data the empty state is shown."""
        assert self._empty_state_visible()

    def test_follow_up_table_badge_is_zero_with_no_data(self) -> None:
        assert self._badge_count() == 0

    def test_follow_up_table_shows_overdue_application(self) -> None:
        """An application overdue for a chase appears as one row."""
        self._create_job(title="Old App", application_date=LONG_PAST, application_status="applied")
        self._reload()
        assert len(self._rows()) == 1

    def test_follow_up_table_badge_reflects_row_count(self) -> None:
        """Badge count matches the number of overdue applications."""
        self._create_job(title="Old App A", application_date=LONG_PAST, application_status="applied")
        self._create_job(title="Old App B", application_date=LONG_PAST, application_status="applied")
        self._reload()
        assert self._badge_count() == 2
        assert len(self._rows()) == 2

    def test_follow_up_table_excludes_recent_application(self) -> None:
        """A recently updated application is not shown."""
        self._create_job(title="Recent", application_date=PAST, application_status="applied")
        self._reload()
        assert len(self._rows()) == 0

    def test_follow_up_table_excludes_rejected(self) -> None:
        """Rejected applications are never shown."""
        self._create_job(title="Rejected", application_date=LONG_PAST, application_status="rejected")
        self._reload()
        assert len(self._rows()) == 0

    def test_follow_up_table_excludes_offer(self) -> None:
        """Applications with an offer are not shown."""
        self._create_job(title="Offer", application_date=LONG_PAST, application_status="offer")
        self._reload()
        assert len(self._rows()) == 0

    def test_follow_up_table_row_displays_job_title(self) -> None:
        """Each row must contain the job title."""
        self._create_job(title="Chase Me", application_date=LONG_PAST, application_status="applied")
        self._reload()
        row = self._rows()[0]
        assert "Chase Me" in row.text

    def test_follow_up_table_mixed_data(self) -> None:
        """Only overdue pending applications appear; recent and terminal ones are excluded."""
        self._create_job(title="Overdue", application_date=LONG_PAST, application_status="applied")
        self._create_job(title="Recent", application_date=PAST, application_status="applied")
        self._create_job(title="Rejected", application_date=LONG_PAST, application_status="rejected")
        self._reload()
        assert len(self._rows()) == 1


class TestUpcomingDeadlinesTable(DashboardTestBase):
    """Tests for the Upcoming Deadlines table widget.

    Shows jobs with a deadline within the next 7 days (deadline_threshold)
    that have not been applied to yet.
    """

    user_index = 0

    def setup_function(self, request) -> None:
        self._set_dashboard_widgets({"type": "table", "source": "upcoming_deadlines"})
        self.login()

    # --------------------------------------------------- HELPERS ---------------------------------------------------

    def _badge_count(self) -> int:
        return int(self.get_element(f"{UPCOMING_DEADLINES_TABLE}-badge").text)

    def _rows(self):
        card = self.get_element(UPCOMING_DEADLINES_TABLE)
        return card.find_elements(By.CSS_SELECTOR, "[id^='table-row-job-']")

    def _empty_state_visible(self) -> bool:
        return self.check_element_exists(f"{UPCOMING_DEADLINES_TABLE}-empty")

    # ---------------------------------------------------- TESTS ----------------------------------------------------

    def test_upcoming_deadlines_table_renders(self) -> None:
        """The Upcoming Deadlines card must be visible on a dashboard with the widget configured."""
        assert self.get_element(UPCOMING_DEADLINES_TABLE).is_displayed()

    def test_upcoming_deadlines_empty_state_with_no_data(self) -> None:
        """With no data the empty state is shown."""
        assert self._empty_state_visible()

    def test_upcoming_deadlines_badge_is_zero_with_no_data(self) -> None:
        assert self._badge_count() == 0

    def test_upcoming_deadlines_shows_job_with_imminent_deadline(self) -> None:
        """A job with a deadline within the threshold and no application appears as one row."""
        self._create_job(title="Apply Soon", deadline=SOON)
        self._reload()
        assert len(self._rows()) == 1

    def test_upcoming_deadlines_badge_reflects_row_count(self) -> None:
        """Badge count matches the number of jobs with upcoming deadlines."""
        self._create_job(title="Deadline A", deadline=SOON)
        self._create_job(title="Deadline B", deadline=SOON + dt.timedelta(days=1))
        self._reload()
        assert self._badge_count() == 2
        assert len(self._rows()) == 2

    def test_upcoming_deadlines_excludes_far_future_deadline(self) -> None:
        """A job whose deadline is beyond the 7-day threshold is not shown."""
        self._create_job(title="Far Out", deadline=FAR_FUTURE)
        self._reload()
        assert len(self._rows()) == 0

    def test_upcoming_deadlines_excludes_applied_job(self) -> None:
        """A job that has already been applied to is not shown even if its deadline is soon."""
        self._create_job(title="Already Applied", deadline=SOON, application_date=PAST, application_status="applied")
        self._reload()
        assert len(self._rows()) == 0

    def test_upcoming_deadlines_excludes_job_without_deadline(self) -> None:
        """A saved job with no deadline is not shown."""
        self._create_job(title="No Deadline")
        self._reload()
        assert len(self._rows()) == 0

    def test_upcoming_deadlines_row_displays_job_title(self) -> None:
        """Each row must contain the job title."""
        self._create_job(title="Urgent Role", deadline=SOON)
        self._reload()
        row = self._rows()[0]
        assert "Urgent Role" in row.text

    def test_upcoming_deadlines_mixed_data(self) -> None:
        """Only unapplied jobs with near deadlines appear."""
        self._create_job(title="Upcoming", deadline=SOON)
        self._create_job(title="Too Far", deadline=FAR_FUTURE)
        self._create_job(title="Applied", deadline=SOON, application_date=PAST, application_status="applied")
        self._reload()
        assert len(self._rows()) == 1


class TestJobAlertsTable(DashboardTestBase):
    """Tests for the Job Alerts table widget.

    Shows all scraped jobs belonging to the user, newest first.
    """

    user_index = 0

    def setup_function(self, request) -> None:
        self._set_dashboard_widgets({"type": "table", "source": "job_alerts"})
        self.login()

    # --------------------------------------------------- HELPERS ---------------------------------------------------

    def _badge_count(self) -> int:
        return int(self.get_element(f"{JOB_ALERTS_TABLE}-badge").text)

    def _rows(self):
        card = self.get_element(JOB_ALERTS_TABLE)
        return card.find_elements(By.CSS_SELECTOR, "[id^='table-row-scrapedJob-']")

    def _empty_state_visible(self) -> bool:
        return self.check_element_exists(f"{JOB_ALERTS_TABLE}-empty")

    # ---------------------------------------------------- TESTS ----------------------------------------------------

    def test_job_alerts_table_renders(self) -> None:
        """The Job Alerts card must be visible on a dashboard with the widget configured."""
        assert self.get_element(JOB_ALERTS_TABLE).is_displayed()

    def test_job_alerts_empty_state_with_no_data(self) -> None:
        """With no scraped jobs the empty state is shown."""
        assert self._empty_state_visible()

    def test_job_alerts_badge_is_zero_with_no_data(self) -> None:
        assert self._badge_count() == 0

    def test_job_alerts_shows_one_scraped_job(self) -> None:
        """A single scraped job appears as one row."""
        self._create_scraped_job(title="Python Developer")
        self._reload()
        assert len(self._rows()) == 1

    def test_job_alerts_badge_reflects_row_count(self) -> None:
        """Badge count matches the number of scraped jobs."""
        self._create_scraped_job(title="Job A")
        self._create_scraped_job(title="Job B")
        self._reload()
        assert self._badge_count() == 2
        assert len(self._rows()) == 2

    def test_job_alerts_row_displays_job_title(self) -> None:
        """Each row must contain the job title."""
        self._create_scraped_job(title="Data Scientist")
        self._reload()
        row = self._rows()[0]
        assert "Data Scientist" in row.text

    def test_job_alerts_shows_jobs_from_different_platforms(self) -> None:
        """Jobs from different platforms all appear in the table."""
        self._create_scraped_job(title="LinkedIn Job", platform="LinkedIn")
        self._create_scraped_job(title="Indeed Job", platform="Indeed")
        self._reload()
        assert len(self._rows()) == 2


class TestFavouritesTable(DashboardTestBase):
    """Tests for the Favourite Job Alerts table widget.

    Only shows scraped jobs that match at least one active ScrapingFavouriteFilter.
    If no favourite filters exist the table is always empty.
    """

    user_index = 0

    def setup_function(self, request) -> None:
        self._set_dashboard_widgets({"type": "table", "source": "favourites"})
        self.login()

    # --------------------------------------------------- HELPERS ---------------------------------------------------

    def _badge_count(self) -> int:
        return int(self.get_element(f"{FAVOURITES_TABLE}-badge").text)

    def _rows(self):
        card = self.get_element(FAVOURITES_TABLE)
        return card.find_elements(By.CSS_SELECTOR, "[id^='table-row-scrapedJob-']")

    def _empty_state_visible(self) -> bool:
        return self.check_element_exists(f"{FAVOURITES_TABLE}-empty")

    # ---------------------------------------------------- TESTS ----------------------------------------------------

    def test_favourites_table_renders(self) -> None:
        """The Favourite Job Alerts card must be visible on a dashboard with the widget configured."""
        assert self.get_element(FAVOURITES_TABLE).is_displayed()

    def test_favourites_empty_state_with_no_data(self) -> None:
        """With no scraped jobs and no filters the empty state is shown."""
        assert self._empty_state_visible()

    def test_favourites_badge_is_zero_with_no_data(self) -> None:
        assert self._badge_count() == 0

    def test_favourites_empty_when_no_filters_defined(self) -> None:
        """A scraped job with no favourite filters → never shown in favourites."""
        self._create_scraped_job(title="Python Developer")
        self._reload()
        assert len(self._rows()) == 0

    def test_favourites_shows_matching_job(self) -> None:
        """A job whose title matches an active favourite filter appears as one row."""
        self._create_favourite_filter(type="title", operator="contains", value="Python")
        self._create_scraped_job(title="Python Developer")
        self._reload()
        assert len(self._rows()) == 1

    def test_favourites_badge_reflects_matching_count(self) -> None:
        """Badge count equals the number of jobs that match the favourite filters."""
        self._create_favourite_filter(type="title", operator="contains", value="Engineer")
        self._create_scraped_job(title="Software Engineer")
        self._create_scraped_job(title="Data Engineer")
        self._reload()
        assert self._badge_count() == 2
        assert len(self._rows()) == 2

    def test_favourites_excludes_non_matching_job(self) -> None:
        """A job that does not match any active filter is not shown."""
        self._create_favourite_filter(type="title", operator="contains", value="Python")
        self._create_scraped_job(title="Java Developer")
        self._reload()
        assert len(self._rows()) == 0

    def test_favourites_mixed_matching_and_non_matching(self) -> None:
        """Only the job that matches the filter is shown when mixed jobs exist."""
        self._create_favourite_filter(type="title", operator="contains", value="Python")
        self._create_scraped_job(title="Python Developer")
        self._create_scraped_job(title="Java Developer")
        self._reload()
        assert len(self._rows()) == 1

    def test_favourites_inactive_filter_is_ignored(self) -> None:
        """An inactive favourite filter does not cause jobs to appear."""
        self._create_favourite_filter(type="title", operator="contains", value="Python", is_active=False)
        self._create_scraped_job(title="Python Developer")
        self._reload()
        assert len(self._rows()) == 0

    def test_favourites_row_displays_job_title(self) -> None:
        """Each matching row must contain the job title."""
        self._create_favourite_filter(type="company", operator="equals", value="Acme Corp")
        self._create_scraped_job(title="Backend Developer", company="Acme Corp")
        self._reload()
        row = self._rows()[0]
        assert "Backend Developer" in row.text


class TestFavouriteJobsTable(DashboardTestBase):
    """Tests for the Favourite Jobs table widget.

    Shows every Job owned by the user that has is_favourite=True,
    regardless of application status or date.
    """

    user_index = 0

    def setup_function(self, request) -> None:
        self._set_dashboard_widgets({"type": "table", "source": "favourite_jobs"})
        self.login()

    # --------------------------------------------------- HELPERS ---------------------------------------------------

    def _badge_count(self) -> int:
        return int(self.get_element(f"{FAVOURITE_JOBS_TABLE}-badge").text)

    def _rows(self):
        card = self.get_element(FAVOURITE_JOBS_TABLE)
        return card.find_elements(By.CSS_SELECTOR, "[id^='table-row-job-']")

    def _empty_state_visible(self) -> bool:
        return self.check_element_exists(f"{FAVOURITE_JOBS_TABLE}-empty")

    # ---------------------------------------------------- TESTS ----------------------------------------------------

    def test_favourite_jobs_table_renders(self) -> None:
        """The Favourite Jobs card must be visible after setting the widget layout."""
        assert self.get_element(FAVOURITE_JOBS_TABLE).is_displayed()

    def test_favourite_jobs_empty_state_with_no_data(self) -> None:
        """With no jobs the empty state is shown."""
        assert self._empty_state_visible()

    def test_favourite_jobs_badge_is_zero_with_no_data(self) -> None:
        assert self._badge_count() == 0

    def test_favourite_jobs_shows_favourite_job(self) -> None:
        """A job with is_favourite=True appears as one row."""
        self._create_job(title="Favourite Role", is_favourite=True)
        self._reload()
        assert len(self._rows()) == 1

    def test_favourite_jobs_excludes_non_favourite_job(self) -> None:
        """A job with is_favourite=False (the default) is not shown."""
        self._create_job(title="Not Favourite")
        self._reload()
        assert len(self._rows()) == 0

    def test_favourite_jobs_badge_reflects_row_count(self) -> None:
        """Badge count matches the number of favourite jobs."""
        self._create_job(title="Fav A", is_favourite=True)
        self._create_job(title="Fav B", is_favourite=True)
        self._reload()
        assert self._badge_count() == 2
        assert len(self._rows()) == 2

    def test_favourite_jobs_mixed_favourite_and_non_favourite(self) -> None:
        """Only jobs with is_favourite=True appear."""
        self._create_job(title="Favourite", is_favourite=True)
        self._create_job(title="Not Favourite")
        self._reload()
        assert len(self._rows()) == 1

    def test_favourite_jobs_includes_applied_favourite(self) -> None:
        """A favourite job that has been applied to is still shown."""
        self._create_job(title="Applied Fav", is_favourite=True, application_date=PAST, application_status="applied")
        self._reload()
        assert len(self._rows()) == 1

    def test_favourite_jobs_includes_rejected_favourite(self) -> None:
        """A favourite job that was rejected is still shown."""
        self._create_job(title="Rejected Fav", is_favourite=True, application_date=PAST, application_status="rejected")
        self._reload()
        assert len(self._rows()) == 1

    def test_favourite_jobs_row_displays_job_title(self) -> None:
        """Each row must contain the job title."""
        self._create_job(title="Dream Job", is_favourite=True)
        self._reload()
        row = self._rows()[0]
        assert "Dream Job" in row.text


class TestFailedJobsWidget(DashboardTestBase):
    """Tests for the Failed Jobs table widget.

    Shows scraped jobs where is_failed=True (permanent scrape failure)
    or job_rating.is_success=False (AI rating failure).
    Normal, successfully-scraped-and-rated jobs are never shown.
    """

    user_index = 0

    def setup_function(self, request) -> None:
        self._set_dashboard_widgets({"type": "table", "source": "error_jobs"})
        self.login()

    # --------------------------------------------------- HELPERS ---------------------------------------------------

    def _badge_count(self) -> int:
        return int(self.get_element(f"{FAILED_JOBS_TABLE}-badge").text)

    def _rows(self):
        card = self.get_element(FAILED_JOBS_TABLE)
        return card.find_elements(By.CSS_SELECTOR, "[id^='table-row-scrapedJob-']")

    def _empty_state_visible(self) -> bool:
        return self.check_element_exists(f"{FAILED_JOBS_TABLE}-empty")

    def _create_scraped_job_with_failed_rating(self, title: str = "Failed Rating Job", **kwargs) -> models.ScrapedJob:
        """Create a scraped job that has a failed JobRating (is_success=False)."""
        job = self._create_scraped_job(title=title, **kwargs)
        rating = models.JobRating(
            owner_id=self.user.id,
            scraped_job_id=job.id,
            is_success=False,
        )
        self.db.add(rating)
        self.db.commit()
        return job

    # ---------------------------------------------------- TESTS ----------------------------------------------------

    def test_failed_jobs_widget_renders(self) -> None:
        """The Failed Jobs card must be visible on a dashboard with the widget configured."""
        assert self.get_element(FAILED_JOBS_TABLE).is_displayed()

    def test_failed_jobs_empty_state_with_no_data(self) -> None:
        """With no failed jobs the empty state is shown."""
        assert self._empty_state_visible()

    def test_failed_jobs_badge_is_zero_with_no_data(self) -> None:
        assert self._badge_count() == 0

    def test_failed_jobs_shows_scrape_failed_job(self) -> None:
        """A job with is_failed=True appears as one row."""
        self._create_scraped_job(title="Scrape Error Job", is_failed=True)
        self._reload()
        assert len(self._rows()) == 1

    def test_failed_jobs_shows_rating_failed_job(self) -> None:
        """A job whose rating has is_success=False appears as one row."""
        self._create_scraped_job_with_failed_rating(title="Rating Error Job")
        self._reload()
        assert len(self._rows()) == 1

    def test_failed_jobs_excludes_normal_job(self) -> None:
        """A successfully scraped job with no rating failure is not shown."""
        self._create_scraped_job(title="Normal Job")
        self._reload()
        assert len(self._rows()) == 0

    def test_failed_jobs_badge_reflects_row_count(self) -> None:
        """Badge count matches the total number of failed jobs."""
        self._create_scraped_job(title="Failed Scrape A", is_failed=True)
        self._create_scraped_job_with_failed_rating(title="Failed Rating B")
        self._reload()
        assert self._badge_count() == 2
        assert len(self._rows()) == 2

    def test_failed_jobs_mixed_normal_and_failed(self) -> None:
        """Only failed jobs are shown when a mix of normal and failed jobs exists."""
        self._create_scraped_job(title="Normal Job")
        self._create_scraped_job(title="Failed Scrape", is_failed=True)
        self._reload()
        assert len(self._rows()) == 1

    def test_failed_jobs_row_displays_job_title(self) -> None:
        """Each row must contain the job title."""
        self._create_scraped_job(title="Broken Scrape", is_failed=True)
        self._reload()
        row = self._rows()[0]
        assert "Broken Scrape" in row.text

    def test_failed_jobs_shows_job_with_past_deadline(self) -> None:
        """Failed jobs with a past deadline are still shown (deadline filter is skipped)."""
        past_deadline = NOW - dt.timedelta(days=5)
        self._create_scraped_job(title="Expired Failed", is_failed=True, deadline=past_deadline)
        self._reload()
        assert len(self._rows()) == 1

    def test_failed_jobs_excludes_imported_failed_job(self) -> None:
        """A failed job that has been imported is not shown (base filter still applies)."""
        self._create_scraped_job(title="Imported Failed", is_failed=True, is_imported=True)
        self._reload()
        assert len(self._rows()) == 0
