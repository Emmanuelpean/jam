"""Selenium tests for the Log Update guided tour.

Tour step order (log-update):
  1   update-intro              informational — centre popover
  2   update-open-job           click demo job row (hideNextButton; allowedContextMenuActions: ["view"])
  3   update-application-tab    click Application tab (hideNextButton); auto-advances when tab loads
  4   update-add                click Add Update button (hideNextButton); auto-advances when modal opens
  5   update-date               required date field (waitForInput)
  6   update-type               required type selector (waitForInput)
  7   update-note               optional notes
  8   update-save               click Save (hideNextButton); auto-advances when modal closes
  9   update-show-in-table      update appears in timeline; blockLeftClick; allowedContextMenuActions: []
  10  update-done               informational — Done button; no keep/delete toggle

JAM entities seeded at tour start (all is_tour=True):
  Companies: Meridian Labs
  Jobs:      Software Engineer at Meridian Labs (with application_date and application_status="applied")
"""

from app import models
from frontend_base_test import BaseTest
from helpers.select_utils import Select

TOUR_ID = "log-update"


class TestLogUpdateTour(BaseTest):
    user_fixture = "test_regular_user"
    page_url = "jobs"

    def setup_function(self, request) -> None:
        self.login()

    # ------------------------------------------------------------------ helpers

    def _start_and_open_update_form(self) -> None:
        """Start the tour, open the demo job, switch to Application tab, and open Add Update.

        Returns with the tour popover on step 4 (update-date) and the update edit modal already open."""

        self.tour_utils.start_tour(TOUR_ID)
        self.wait_for_page("jobs")

        # Step 1 (update-intro): informational — click Next
        self.tour_utils.click_next()

        # Step 2 (update-open-job): click the demo job row;
        # tour auto-advances to step 2 when #application-tab appears.
        self.tour_utils.wait_for_popover()
        demo_job = self.db.query(models.Job).filter_by(owner_id=self.user.id, is_tour=True).first()
        self.job_table_utils.table_row_click(demo_job.id)

        # Step 3 (update-application-tab): click Application tab;
        # tour auto-advances to step 3 when #add-jobApplicationUpdate-button appears.
        self.tour_utils.wait_for_popover()
        self.get_element("application-tab").click()

        # Step 4 (update-add): click Add Update button;
        # tour auto-advances to step 4 when #modal-edit-jobApplicationUpdate appears.
        self.tour_utils.wait_for_popover()
        self.get_element("add-jobApplicationUpdate-button").click()
        self.jobApplicationUpdate_modal_utils.wait_for_edit_modal()

    def _fill_date_and_type(self) -> None:
        """Fill the required date and update type fields.

        Assumes the current step is update-date (step 4).
        Leaves the tour on step 7 (update-note).
        """
        # Step 5 (update-date): set today's date
        self.tour_utils.wait_for_popover()
        self.get_element("date_set_current").click()
        self.tour_utils.click_next()

        # Step 6 (update-type): select a type
        self.tour_utils.wait_for_popover()
        Select(self.get_element("type")).select_by_visible_text("Received")
        self.tour_utils.click_next()

    # ------------------------------------------------------------------ tests

    def test_minimal_fields(self) -> None:
        """Fill date and type only, skip the note, then click Done.

        No user-created data → no keep/delete toggle.
        Demo job and company are cleaned up on Done.
        """
        initial_jobs = self.db.query(models.Job).filter_by(owner_id=self.user.id).count()
        initial_companies = self.db.query(models.Company).filter_by(owner_id=self.user.id).count()
        initial_updates = self.db.query(models.JobApplicationUpdate).filter_by(owner_id=self.user.id).count()

        self._start_and_open_update_form()
        self._fill_date_and_type()

        # Step 7 (update-note): skip
        self.tour_utils.wait_for_popover()
        self.tour_utils.click_next()

        # Step 8 (update-save): click Save
        self.tour_utils.wait_for_popover()
        self.jobApplicationUpdate_modal_utils.confirm_button("edit").click()

        # Step 9 (update-show-in-table): update appears — click Next
        self.tour_utils.wait_for_popover()
        self.tour_utils.click_next()

        # Step 10 (update-done): no toggle — click Done
        self.tour_utils.wait_for_popover()
        assert "Done" in self.get_element(self.tour_utils.TOUR_NEXT).text
        assert not self.check_element_exists("tour-keep-data"), "Keep my data toggle must not appear"
        self.tour_utils.click_next()

        self.tour_utils.wait_for_popover_gone()
        self.wait_for_page(self.page_url)

        # Updates, demo job and company all cleaned up
        self.tour_utils.poll_db_count(models.JobApplicationUpdate, self.user.id, initial_updates)
        self.tour_utils.poll_db_count(models.Job, self.user.id, initial_jobs)
        self.tour_utils.poll_db_count(models.Company, self.user.id, initial_companies)

    def test_with_note(self) -> None:
        """Fill date, type, and a note, then save and click Done."""
        initial_updates = self.db.query(models.JobApplicationUpdate).filter_by(owner_id=self.user.id).count()

        self._start_and_open_update_form()
        self._fill_date_and_type()

        # Step 7 (update-note): fill in a note
        self.tour_utils.wait_for_popover()
        self.get_element("note").send_keys("Received rejection email from HR.")
        self.tour_utils.click_next()

        # Step 8 (update-save): click Save
        self.tour_utils.wait_for_popover()
        self.jobApplicationUpdate_modal_utils.confirm_button("edit").click()

        # Step 9 (update-show-in-table): click Next
        self.tour_utils.wait_for_popover()
        self.tour_utils.click_next()

        # Step 10 (update-done): click Done
        self.tour_utils.wait_for_popover()
        assert "Done" in self.get_element(self.tour_utils.TOUR_NEXT).text
        assert not self.check_element_exists("tour-keep-data"), "Keep my data toggle must not appear"
        self.tour_utils.click_next()

        self.tour_utils.wait_for_popover_gone()
        self.wait_for_page(self.page_url)

        self.tour_utils.poll_db_count(models.JobApplicationUpdate, self.user.id, initial_updates)

    def test_skip_tour(self) -> None:
        """Skip the tour after filling date and type — no update is saved.

        All JAM entities (demo job and company) must be cleaned up on skip.
        """
        initial_jobs = self.db.query(models.Job).filter_by(owner_id=self.user.id).count()
        initial_companies = self.db.query(models.Company).filter_by(owner_id=self.user.id).count()
        initial_updates = self.db.query(models.JobApplicationUpdate).filter_by(owner_id=self.user.id).count()

        self._start_and_open_update_form()
        self._fill_date_and_type()

        # Skip during step 7 (update-note)
        self.tour_utils.wait_for_popover()
        self.tour_utils.click_skip()

        self.tour_utils.wait_for_popover_gone()
        self.wait_for_page(self.page_url)

        self.tour_utils.poll_db_count(models.JobApplicationUpdate, self.user.id, initial_updates)
        self.tour_utils.poll_db_count(models.Job, self.user.id, initial_jobs)
        self.tour_utils.poll_db_count(models.Company, self.user.id, initial_companies)
