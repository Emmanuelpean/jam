"""Selenium tests for the Follow-up Email guided tour.

Tour step order (follow-up-email):
  0   follow-up-intro              centre popover — 3 method choices (hideNextButton)
  -- Method 1: right-click job row --
  1a  follow-up-open-via-table     right-click the demo row (hideNextButton, waitForSelector: #follow-up-modal)
  -- Method 2: right-click contact badge --
  1b  follow-up-open-via-badge-1   click demo row to open view modal (hideNextButton, waitForSelector: #job-tab)
  2b  follow-up-open-via-badge-2   right-click contact badge (hideNextButton, waitForSelector: #follow-up-modal)
  -- Method 3: button in Application tab --
  1c  follow-up-open-via-button-1  click demo row to open view modal (hideNextButton, waitForSelector: #application-tab)
  2c  follow-up-open-via-button-2  click Application tab (hideNextButton, waitForSelector: #job-modal-follow-up-button)
  3c  follow-up-open-via-button-3  click Follow-up Email button (hideNextButton, waitForSelector: #follow-up-modal)
  -- All methods converge here --
  ?   follow-up-contact            select a contact (optional, Next button visible)
  ?   follow-up-subject            edit the subject line (optional)
  ?   follow-up-body               edit the body (optional)
  ?   follow-up-send               click Send Email (hideNextButton, waitForSelector: #confirm-alert-modal-buttons)
  ?   follow-up-log-update         Yes/No on confirm dialog (hideNextButton, waitForSelectorGone: #confirm-alert-modal-dialog)
  ?   follow-up-done               summary — click Done

The tour seeds two contacts (Alex Johnson, Sarah Mitchell) and an interview against the demo job.
All seeded data is cleaned up on Done or Skip regardless of how the tour ended.
"""

from app import models
from base_test import BaseTest


TOUR_ID = "follow-up-email"


class TestFollowUpEmailTour(BaseTest):
    user_index = 0
    page_url = "jobs"

    def setup_function(self, request) -> None:
        self.login()

    # ------------------------------------------------------------------ helpers

    def _start_tour(self) -> None:
        """Start the tour and wait for the intro popover on the jobs page."""
        self.tour_utils.start_tour(TOUR_ID)
        self.wait_for_page("jobs")
        self.tour_utils.wait_for_popover()

    def _demo_job_row(self):
        """Return the demo job row — the only visible row during the tour."""
        return self.job_table_utils.table_rows[0]

    def _open_via_table(self) -> None:
        """Choose Method 1 and open the follow-up modal by right-clicking the demo job row."""
        self.get_element("tour-choice-follow-up-open-via-table").click()

        # follow-up-open-via-table: right-click the demo row
        self.tour_utils.wait_for_popover()
        self.context_menu(self._demo_job_row(), "followup")
        # Tour auto-advances when #follow-up-modal appears
        self.followup_modal.wait_for_modal()

    def _open_via_badge(self) -> None:
        """Choose Method 2: open the job view modal and right-click the first contact badge."""
        self.get_element("tour-choice-follow-up-open-via-badge-1").click()

        # follow-up-open-via-badge-1: click the demo row to open the view modal
        self.tour_utils.wait_for_popover()
        self._demo_job_row().click()
        self.job_modal_utils.wait_for_view_modal()

        # follow-up-open-via-badge-2: right-click the first contact badge
        self.tour_utils.wait_for_popover()
        badge = self.get_element("modal-view-job-person-0")
        self.context_menu(badge, "followup")
        # Tour auto-advances when #follow-up-modal appears
        self.followup_modal.wait_for_modal()

    def _open_via_button(self) -> None:
        """Choose Method 3: open view modal, click Application tab, click the Follow-up button."""
        self.get_element("tour-choice-follow-up-open-via-button-1").click()

        # follow-up-open-via-button-1: click the demo row to open the view modal
        self.tour_utils.wait_for_popover()
        self._demo_job_row().click()
        self.job_modal_utils.wait_for_view_modal()

        # follow-up-open-via-button-2: click the Application tab
        # Tour auto-advances when #job-modal-follow-up-button appears
        self.tour_utils.wait_for_popover()
        self.get_element("application-tab").click()

        # follow-up-open-via-button-3: click the Follow-up Email button
        self.tour_utils.wait_for_popover()
        self.get_element("job-modal-follow-up-button").click()
        # Tour auto-advances when #follow-up-modal appears
        self.followup_modal.wait_for_modal()

    def _complete_modal_steps(self) -> None:
        """Advance through follow-up-contact, follow-up-subject, and follow-up-body steps."""
        # follow-up-contact: optional — click Next
        self.tour_utils.wait_for_popover()
        self.tour_utils.click_next()

        # follow-up-subject: optional — click Next
        self.tour_utils.wait_for_popover()
        self.tour_utils.click_next()

        # follow-up-body: optional — click Next
        self.tour_utils.wait_for_popover()
        self.tour_utils.click_next()

    def _send_and_respond(self, log_update: bool) -> None:
        """Click Send Email, then respond to the log-update confirm dialog.

        The follow-up-send step waits for #confirm-alert-modal-buttons to appear.
        The follow-up-log-update step waits for the dialog to disappear.
        """
        # follow-up-send: click Send Email; tour waits for confirm dialog buttons
        self.tour_utils.wait_for_popover()
        self.followup_modal.send_button.click()

        # follow-up-log-update: confirm dialog is highlighted — click Yes or No
        self.tour_utils.wait_for_popover()
        if log_update:
            self.confirm_modal.confirm_button.click()
        else:
            self.confirm_modal.cancel_button.click()

    def _finish_tour(self) -> None:
        """Click Done on the follow-up-done step and wait for the popover to vanish."""
        self.tour_utils.wait_for_popover()
        assert "Done" in self.get_element(self.tour_utils.TOUR_NEXT).text
        self.tour_utils.click_next()
        self.tour_utils.wait_for_popover_gone()
        self.wait_for_page(self.page_url)

    # ------------------------------------------------------------------ tests

    def test_via_right_click_job_row_no_update(self) -> None:
        """Complete the tour via Method 1 (right-click row) and click No on the log-update dialog.

        All tour-seeded entities (job, persons, interview) are removed on Done.
        """
        initial_jobs = self.db.query(models.Job).filter_by(owner_id=self.user.id).count()
        initial_persons = self.db.query(models.Person).filter_by(owner_id=self.user.id).count()
        initial_interviews = self.db.query(models.Interview).filter_by(owner_id=self.user.id).count()
        initial_updates = self.db.query(models.JobApplicationUpdate).filter_by(owner_id=self.user.id).count()

        self._start_tour()
        self._open_via_table()
        self._complete_modal_steps()
        self._send_and_respond(log_update=False)
        self._finish_tour()

        self.tour_utils.poll_db_count(models.Job, self.user.id, initial_jobs)
        self.tour_utils.poll_db_count(models.Person, self.user.id, initial_persons)
        self.tour_utils.poll_db_count(models.Interview, self.user.id, initial_interviews)
        self.tour_utils.poll_db_count(models.JobApplicationUpdate, self.user.id, initial_updates)

    def test_via_right_click_job_row_yes_update(self) -> None:
        """Complete the tour via Method 1 and click Yes on the log-update dialog.

        Clicking Yes creates a JobApplicationUpdate; the update (and all other
        tour-seeded data) is removed during cleanup on Done.
        """
        initial_jobs = self.db.query(models.Job).filter_by(owner_id=self.user.id).count()
        initial_persons = self.db.query(models.Person).filter_by(owner_id=self.user.id).count()
        initial_updates = self.db.query(models.JobApplicationUpdate).filter_by(owner_id=self.user.id).count()

        self._start_tour()
        self._open_via_table()
        self._complete_modal_steps()
        self._send_and_respond(log_update=True)
        self._finish_tour()

        self.tour_utils.poll_db_count(models.Job, self.user.id, initial_jobs)
        self.tour_utils.poll_db_count(models.Person, self.user.id, initial_persons)
        self.tour_utils.poll_db_count(models.JobApplicationUpdate, self.user.id, initial_updates)

    def test_via_contact_badge(self) -> None:
        """Complete the tour via Method 2 (right-click contact badge)."""
        initial_jobs = self.db.query(models.Job).filter_by(owner_id=self.user.id).count()
        initial_persons = self.db.query(models.Person).filter_by(owner_id=self.user.id).count()

        self._start_tour()
        self._open_via_badge()
        self._complete_modal_steps()
        self._send_and_respond(log_update=False)
        self._finish_tour()

        self.tour_utils.poll_db_count(models.Job, self.user.id, initial_jobs)
        self.tour_utils.poll_db_count(models.Person, self.user.id, initial_persons)

    def test_via_application_tab_button(self) -> None:
        """Complete the tour via Method 3 (Follow-up Email button in Application tab)."""
        initial_jobs = self.db.query(models.Job).filter_by(owner_id=self.user.id).count()
        initial_persons = self.db.query(models.Person).filter_by(owner_id=self.user.id).count()

        self._start_tour()
        self._open_via_button()
        self._complete_modal_steps()
        self._send_and_respond(log_update=False)
        self._finish_tour()

        self.tour_utils.poll_db_count(models.Job, self.user.id, initial_jobs)
        self.tour_utils.poll_db_count(models.Person, self.user.id, initial_persons)

    def test_skip_from_intro_cleans_up_seeded_data(self) -> None:
        """Skipping the tour at the intro step removes all seeded data.

        The two demo contacts (Alex Johnson, Sarah Mitchell) and the demo job
        and interview are all cleaned up even when the user never advanced past step 0.
        """
        initial_jobs = self.db.query(models.Job).filter_by(owner_id=self.user.id).count()
        initial_persons = self.db.query(models.Person).filter_by(owner_id=self.user.id).count()
        initial_interviews = self.db.query(models.Interview).filter_by(owner_id=self.user.id).count()

        self._start_tour()
        self.tour_utils.click_skip()

        self.tour_utils.wait_for_popover_gone()
        self.wait_for_page(self.page_url)

        self.tour_utils.poll_db_count(models.Job, self.user.id, initial_jobs)
        self.tour_utils.poll_db_count(models.Person, self.user.id, initial_persons)
        self.tour_utils.poll_db_count(models.Interview, self.user.id, initial_interviews)

    def test_skip_after_opening_follow_up_modal_cleans_up(self) -> None:
        """Skipping mid-tour (after opening the follow-up modal) still cleans up all seeded data."""
        initial_jobs = self.db.query(models.Job).filter_by(owner_id=self.user.id).count()
        initial_persons = self.db.query(models.Person).filter_by(owner_id=self.user.id).count()

        self._start_tour()
        self._open_via_table()

        # Skip from inside the follow-up modal
        self.tour_utils.click_skip()

        self.tour_utils.wait_for_popover_gone()
        self.wait_for_page(self.page_url)

        self.tour_utils.poll_db_count(models.Job, self.user.id, initial_jobs)
        self.tour_utils.poll_db_count(models.Person, self.user.id, initial_persons)

    def test_pre_existing_job_hidden_during_tour(self) -> None:
        """A job created before the tour starts must not appear in the table during the tour.

        The tour snapshot hides pre-existing entities from visibleData, so only the
        JAM-seeded demo job (1 row) should be visible while the tour is active.
        """
        pre_existing = self._make_job(title="Pre-Existing Job")
        initial_jobs = self.db.query(models.Job).filter_by(owner_id=self.user.id).count()

        self._start_tour()

        # During the tour only the demo job row is visible
        visible_rows = self.job_table_utils.table_rows
        assert len(visible_rows) == 1, (
            f"Expected exactly 1 demo job row during the tour, got {len(visible_rows)}"
        )
        row_texts = [r.text for r in visible_rows]
        assert not any("Pre-Existing" in t for t in row_texts), (
            f"Pre-existing job must not appear during the tour; visible rows: {row_texts}"
        )

        self.tour_utils.click_skip()
        self.tour_utils.wait_for_popover_gone()
        self.wait_for_page(self.page_url)

        # Pre-existing job survives; tour cleanup only removes the demo job
        self.tour_utils.poll_db_count(models.Job, self.user.id, initial_jobs)
