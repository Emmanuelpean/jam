"""Tests for the dashboard activity feed widgets (Recent Activity and Upcoming Interviews)."""

import datetime as dt

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from dashboard_base import DashboardTestBase

# IDs used in the rendered DOM (set in ActivityFeed.tsx / DashboardCard.tsx)
RECENT_ACTIVITY = "activity-card-recent_activity"
UPCOMING_INTERVIEWS = "activity-card-upcoming_interviews"

NOW = dt.datetime.now(dt.timezone.utc)
PAST = NOW - dt.timedelta(days=3)
FUTURE = NOW + dt.timedelta(days=7)


class TestActivityWidget(DashboardTestBase):
    """Tests for the ActivityFeedCard widgets on the dashboard.

    The default dashboard layout includes two timeline widgets:
      - Recent Activity  (applications, past interviews, past status updates)
      - Upcoming Interviews (future-dated interviews)
    """

    user_fixture = "test_regular_user"

    def setup_function(self, request) -> None:
        self.login()

    # --------------------------------------------------- HELPERS ---------------------------------------------------

    def _card(self, card_id: str) -> WebElement:
        return self.get_element(card_id)

    def _badge_count(self, card_id: str) -> int:
        return int(self.get_element(f"{card_id}-badge").text)

    def _activity_items(self, card_id: str) -> list[WebElement]:
        return self._card(card_id).find_elements(By.CSS_SELECTOR, ".activity-item")

    def _empty_state_visible(self, card_id: str) -> bool:
        return self.check_element_exists(f"{card_id}-empty")

    # ----------------------------------------------- RECENT ACTIVITY ----------------------------------------------

    def test_recent_activity_empty_state(self) -> None:
        """With no data, Recent Activity should show its empty state."""
        assert self._empty_state_visible(RECENT_ACTIVITY)

    def test_recent_activity_empty_badge_is_zero(self) -> None:
        """With no data, the Recent Activity badge count should be 0."""
        assert self._badge_count(RECENT_ACTIVITY) == 0

    def test_recent_activity_shows_one_application(self) -> None:
        """A single job application appears as exactly one item in Recent Activity."""
        self.user.create_job(application_date=PAST, application_status="applied")
        self._reload()
        assert len(self._activity_items(RECENT_ACTIVITY)) == 1

    def test_recent_activity_badge_reflects_application_count(self) -> None:
        """Badge count equals the number of job applications."""
        self.user.create_job(title="Job A", application_date=PAST, application_status="applied")
        self.user.create_job(title="Job B", application_date=PAST - dt.timedelta(days=1), application_status="applied")
        self._reload()
        assert self._badge_count(RECENT_ACTIVITY) == 2

    def test_recent_activity_item_shows_title_and_date(self) -> None:
        """Each activity item must render a non-empty title and a formatted date."""
        self.user.create_job(application_date=PAST, application_status="applied")
        self._reload()
        item = self._activity_items(RECENT_ACTIVITY)[0]
        assert item.find_element(By.CSS_SELECTOR, ".activity-title").text.strip() != ""
        assert item.find_element(By.CSS_SELECTOR, ".activity-date").text.strip() != ""

    def test_recent_activity_shows_application_type_label(self) -> None:
        """Application items should display 'Application' as their type label."""
        self.user.create_job(application_date=PAST, application_status="applied")
        self._reload()
        titles = [
            i.find_element(By.CSS_SELECTOR, ".activity-title").text for i in self._activity_items(RECENT_ACTIVITY)
        ]
        assert any("Application" in t for t in titles)

    def test_recent_activity_includes_past_interview(self) -> None:
        """A past interview is included in Recent Activity alongside the application."""
        job = self.user.create_job(application_date=PAST, application_status="applied")
        self.user.create_interview(job, date=PAST - dt.timedelta(days=1))
        self._reload()
        # 1 application + 1 past interview = 2 items
        assert self._badge_count(RECENT_ACTIVITY) == 2

    def test_recent_activity_includes_past_update(self) -> None:
        """A past status update is included in Recent Activity alongside the application."""
        job = self.user.create_job(application_date=PAST, application_status="applied")
        self.user.create_job_application_update(job, date=PAST - dt.timedelta(days=1))
        self._reload()
        # 1 application + 1 past update = 2 items
        assert self._badge_count(RECENT_ACTIVITY) == 2

    def test_recent_activity_future_interview_not_shown(self) -> None:
        """A future interview must NOT appear in Recent Activity."""
        job = self.user.create_job(application_date=PAST, application_status="applied")
        self.user.create_interview(job, date=FUTURE)
        self._reload()
        # Only the application; the future interview is excluded
        assert self._badge_count(RECENT_ACTIVITY) == 1

    def test_recent_activity_connector_line_between_items(self) -> None:
        """Non-last items have a connector line; the last item does not."""
        self.user.create_job(title="Job A", application_date=PAST, application_status="applied")
        self.user.create_job(title="Job B", application_date=PAST - dt.timedelta(days=1), application_status="applied")
        self._reload()
        items = self._activity_items(RECENT_ACTIVITY)
        assert len(items) == 2

        first_id = items[0].get_attribute("id")
        assert len(self.driver.find_elements(By.ID, f"{first_id}-line")) == 1

        last_id = items[-1].get_attribute("id")
        assert len(self.driver.find_elements(By.ID, f"{last_id}-line")) == 0

    # --------------------------------------------- UPCOMING INTERVIEWS -------------------------------------------

    def test_upcoming_interviews_empty_state(self) -> None:
        """With no interviews, Upcoming Interviews should show its empty state."""
        assert self._empty_state_visible(UPCOMING_INTERVIEWS)

    def test_upcoming_interviews_empty_badge_is_zero(self) -> None:
        """With no interviews, the Upcoming Interviews badge count should be 0."""
        assert self._badge_count(UPCOMING_INTERVIEWS) == 0

    def test_upcoming_interviews_shows_one_item(self) -> None:
        """A single future interview appears as exactly one item in Upcoming Interviews."""
        job = self.user.create_job(application_date=PAST, application_status="applied")
        self.user.create_interview(job, date=FUTURE)
        self._reload()
        assert len(self._activity_items(UPCOMING_INTERVIEWS)) == 1

    def test_upcoming_interviews_badge_reflects_count(self) -> None:
        """Badge count equals the number of future interviews."""
        job = self.user.create_job(application_date=PAST, application_status="applied")
        self.user.create_interview(job, date=FUTURE)
        self.user.create_interview(job, date=FUTURE + dt.timedelta(days=3))
        self._reload()
        assert self._badge_count(UPCOMING_INTERVIEWS) == 2

    def test_upcoming_interviews_past_interview_not_shown(self) -> None:
        """A past interview must NOT appear in Upcoming Interviews."""
        job = self.user.create_job(application_date=PAST, application_status="applied")
        self.user.create_interview(job, date=PAST - dt.timedelta(days=1))
        self._reload()
        assert self._badge_count(UPCOMING_INTERVIEWS) == 0

    def test_upcoming_interviews_item_shows_date(self) -> None:
        """Each upcoming interview item must display a non-empty formatted date."""
        job = self.user.create_job(application_date=PAST, application_status="applied")
        self.user.create_interview(job, date=FUTURE)
        self._reload()
        item = self._activity_items(UPCOMING_INTERVIEWS)[0]
        assert item.find_element(By.CSS_SELECTOR, ".activity-date").text.strip() != ""

    def test_upcoming_interviews_item_shows_type_and_number(self) -> None:
        """Item title should be '{type} (interview #1)' for a single interview on a job.
        The number is the interview's sequential position (sorted by date) within its job."""

        job = self.user.create_job(application_date=PAST, application_status="applied")
        self.user.create_interview(job, date=FUTURE, type="Technical")
        self._reload()
        title = self._activity_items(UPCOMING_INTERVIEWS)[0].find_element(By.CSS_SELECTOR, ".activity-title").text
        assert "interview #1" in title.lower(), f"Unexpected title: '{title}'"

    def test_upcoming_interviews_connector_line_between_items(self) -> None:
        """Non-last items have a connector line; the last item does not."""
        job = self.user.create_job(application_date=PAST, application_status="applied")
        self.user.create_interview(job, date=FUTURE)
        self.user.create_interview(job, date=FUTURE + dt.timedelta(days=3))
        self._reload()
        items = self._activity_items(UPCOMING_INTERVIEWS)
        assert len(items) == 2

        first_id = items[0].get_attribute("id")
        assert len(self.driver.find_elements(By.ID, f"{first_id}-line")) == 1

        last_id = items[-1].get_attribute("id")
        assert len(self.driver.find_elements(By.ID, f"{last_id}-line")) == 0
