"""Selenium tests for the Log Application guided tour.

Tour step order (log-application):
  0   log-application-intro              informational — centre popover
  1   log-application-open-job           click demo job row (hideNextButton); auto-advances when modal opens
  2   log-application-tab                click Application tab (hideNextButton); auto-advances when tab loads
  3   log-application-edit               click Edit button (hideNextButton); auto-advances when edit form opens
  4   log-application-date               required date field (waitForInput)
  5   log-application-status             required status selector (waitForInput)
  6   log-application-via                applied_via selector
  7   log-application-aggregator         skipIfSelectorAbsent — only when applied_via = "Aggregator"; nextStepId → url
  7b  log-application-aggregator-filling fill inline aggregator form (only if + clicked)
  8   log-application-url                optional URL field
  9   log-application-cv                 optional CV upload
  10  log-application-cover-letter       optional cover letter; nextStepId → note
  10b log-application-cover-letter-writing  write cover letter text (only if pencil clicked)
  11  log-application-note               optional notes field
  12  log-application-save               click Update (hideNextButton); auto-advances when form closes
  13  log-application-done               informational — Done button; no keep/delete toggle

JAM entities seeded at tour start (all is_tour=True):
  Companies: Meridian Labs
  Jobs:      Software Engineer at Meridian Labs (no application data yet)
"""

from app import models
from frontend_base_test import BaseTest
from helpers.select_utils import Select

TOUR_ID = "log-application"


class TestLogApplicationTour(BaseTest):
    user_fixture = "test_regular_user"
    page_url = "jobs"

    def setup_function(self, request) -> None:
        self.login()

    # ------------------------------------------------------------------ helpers

    def _start_and_open_edit_form(self) -> None:
        """Start the tour, open the demo job, switch to Application tab, and open Edit.

        Returns with the tour popover on step 4 (log-application-date) and the
        job edit modal open on the application tab.
        """
        self.tour_utils.start_tour(TOUR_ID)
        self.wait_for_page("jobs")

        # Step 0 (log-application-intro): informational — click Next
        self.tour_utils.click_next()

        # Step 1 (log-application-open-job): click the demo job row;
        # tour auto-advances to step 2 when #application-tab appears in the modal.
        self.tour_utils.wait_for_popover()
        demo_job = self.db.query(models.Job).filter_by(owner_id=self.user.id, is_tour=True).first()
        self.job_table_utils.table_row_click(demo_job.id)

        # Step 2 (log-application-tab): click the Application tab;
        # tour auto-advances to step 3 when #add-interview-button appears.
        self.tour_utils.wait_for_popover()
        self.get_element("application-tab").click()

        # Step 3 (log-application-edit): click Edit;
        # tour auto-advances to step 4 when #application_date-form-group appears.
        self.tour_utils.wait_for_popover()
        self.job_modal_utils.edit_button("view").click()
        self.job_modal_utils.wait_for_edit_modal()

    def _fill_date_and_status(self) -> None:
        """Fill the required application date and status fields.

        Assumes the current step is log-application-date (step 4).
        Leaves the tour on step 6 (log-application-via).
        """
        # Step 4 (log-application-date): set today's date
        self.tour_utils.wait_for_popover()
        self.get_element("application_date_set_current").click()
        self.tour_utils.click_next()

        # Step 5 (log-application-status): select a status
        self.tour_utils.wait_for_popover()
        Select(self.get_element("application_status")).select_by_visible_text("Applied")
        self.tour_utils.click_next()

    def _skip_from_via_to_save(self) -> None:
        """Skip via through notes (no aggregator type selected) and click Update.

        Assumes the current step is log-application-via (step 6).
        Since applied_via is not set to "Aggregator", the aggregator step is
        auto-skipped. Advances through url, cv, cover-letter, and note, then
        clicks the Update button.
        """
        # Step 6 (log-application-via): skip without selecting Aggregator
        self.tour_utils.wait_for_popover()
        self.tour_utils.click_next()

        # Step 8 (log-application-url): aggregator step auto-skipped — skip url
        self.tour_utils.wait_for_popover()
        self.tour_utils.click_next()

        # Step 9 (log-application-cv): skip
        self.tour_utils.wait_for_popover()
        self.tour_utils.click_next()

        # Step 10 (log-application-cover-letter): skip (nextStepId → note)
        self.tour_utils.wait_for_popover()
        self.tour_utils.click_next()

        # Step 11 (log-application-note): skip
        self.tour_utils.wait_for_popover()
        self.tour_utils.click_next()

        # Step 12 (log-application-save): click Update
        self.tour_utils.wait_for_popover()
        self.job_modal_utils.confirm_button("edit").click()

    # ------------------------------------------------------------------ tests

    def test_minimal_fields(self) -> None:
        """Fill only date and status, skip all optional fields, then click Done.

        No keep/delete toggle appears because all entities are JAM-created.
        The demo job and company are cleaned up when Done is clicked.
        """
        initial_jobs = self.db.query(models.Job).filter_by(owner_id=self.user.id).count()
        initial_companies = self.db.query(models.Company).filter_by(owner_id=self.user.id).count()

        self._start_and_open_edit_form()
        self._fill_date_and_status()
        self._skip_from_via_to_save()

        # Step 13 (log-application-done): no toggle — click Done
        self.tour_utils.wait_for_popover()
        assert "Done" in self.get_element(self.tour_utils.TOUR_NEXT).text
        assert not self.check_element_exists("tour-keep-data"), "Keep my data toggle must not appear"
        self.tour_utils.click_next()

        self.tour_utils.wait_for_popover_gone()
        self.wait_for_page(self.page_url)

        self.tour_utils.poll_db_count(models.Job, self.user.id, initial_jobs)
        self.tour_utils.poll_db_count(models.Company, self.user.id, initial_companies)

    def test_pre_existing_aggregator_not_visible(self) -> None:
        """The tour is isolated — aggregators created before the tour are hidden.

        A pre-existing aggregator must not appear in the application_aggregator_id
        dropdown during the tour. After skipping, the aggregator is unaffected.
        """
        pre_existing = self.user.create_aggregator(name="Pre-Existing Board", url="https://www.pre-existing.io")
        initial_aggregators = self.db.query(models.Aggregator).filter_by(owner_id=self.user.id).count()

        self._start_and_open_edit_form()
        self._fill_date_and_status()

        # Step 6 (log-application-via): select Aggregator → aggregator sub-step appears
        self.tour_utils.wait_for_popover()
        Select(self.get_element("applied_via")).select_by_visible_text("Aggregator")
        self.tour_utils.click_next()

        # Step 7 (log-application-aggregator): open the dropdown and verify isolation
        self.tour_utils.wait_for_popover()
        agg_select = Select(self.get_element("application_aggregator_id"))
        agg_select.open_menu()
        option_texts = [opt.text for opt in agg_select.options]
        assert not any(pre_existing.name in text for text in option_texts), (
            f"Pre-existing aggregator '{pre_existing.name}' must not appear in the dropdown "
            f"during the tour; visible options: {option_texts}"
        )
        agg_select._close_menu()

        # Skip the rest of the tour
        self.tour_utils.click_skip()
        self.tour_utils.wait_for_popover_gone()
        self.wait_for_page(self.page_url)

        # Pre-existing aggregator is unaffected
        self.tour_utils.poll_db_count(models.Aggregator, self.user.id, initial_aggregators)

    def test_with_new_aggregator(self) -> None:
        """Select Aggregator for applied_via and create a new aggregator inline.

        The new aggregator is user-created but aggregators are not tracked in
        hasUserCreatedData — no keep/delete toggle appears. The new aggregator is
        cleaned up along with the demo job and company on Done.
        """
        initial_jobs = self.db.query(models.Job).filter_by(owner_id=self.user.id).count()
        initial_aggregators = self.db.query(models.Aggregator).filter_by(owner_id=self.user.id).count()

        self._start_and_open_edit_form()
        self._fill_date_and_status()

        # Step 6 (log-application-via): select Aggregator
        self.tour_utils.wait_for_popover()
        Select(self.get_element("applied_via")).select_by_visible_text("Aggregator")
        self.tour_utils.click_next()

        # Step 7 (log-application-aggregator): click + to open inline aggregator form;
        # tour auto-advances to step 7b when #modal-edit-aggregator appears.
        self.tour_utils.wait_for_popover()
        self.get_element("add-button-aggregator").click()
        self.aggregator_modal_utils.wait_for_edit_modal()

        # Step 7b (log-application-aggregator-filling): fill name and URL, confirm;
        # tour auto-advances back to step 7 (log-application-aggregator) when the modal closes.
        self.get_element("name").send_keys("Jobs Board UK")
        self.get_element("url").send_keys("https://www.jobsboarduk.co.uk")
        self.aggregator_modal_utils.confirm_button("edit").click()
        self.aggregator_modal_utils.wait_for_edit_modal_close()

        # Step 7 again (log-application-aggregator): new aggregator is auto-selected — click Next → url
        self.tour_utils.wait_for_popover()
        self.tour_utils.click_next()

        # url → cv → cover-letter (nextStepId → note) → note
        self.tour_utils.wait_for_popover()
        self.tour_utils.click_next()  # url

        self.tour_utils.wait_for_popover()
        self.tour_utils.click_next()  # cv

        self.tour_utils.wait_for_popover()
        self.tour_utils.click_next()  # cover-letter

        self.tour_utils.wait_for_popover()
        self.tour_utils.click_next()  # note

        # Step 12 (log-application-save)
        self.tour_utils.wait_for_popover()
        self.job_modal_utils.confirm_button("edit").click()

        # Step 13 (log-application-done): no toggle
        self.tour_utils.wait_for_popover()
        assert "Done" in self.get_element(self.tour_utils.TOUR_NEXT).text
        assert not self.check_element_exists("tour-keep-data"), "Keep my data toggle must not appear"
        self.tour_utils.click_next()

        self.tour_utils.wait_for_popover_gone()
        self.wait_for_page(self.page_url)

        # Demo job and new aggregator both cleaned up
        self.tour_utils.poll_db_count(models.Job, self.user.id, initial_jobs)
        self.tour_utils.poll_db_count(models.Aggregator, self.user.id, initial_aggregators)

    def test_write_cover_letter(self) -> None:
        """Click the cover letter pencil button, write text, save, then continue.

        The cover-letter-writing step auto-advances back to cover-letter after saving.
        The written cover letter (stored as a file) is cleaned up with the demo job.
        """
        initial_jobs = self.db.query(models.Job).filter_by(owner_id=self.user.id).count()

        self._start_and_open_edit_form()
        self._fill_date_and_status()

        # Step 6 (log-application-via): skip
        self.tour_utils.wait_for_popover()
        self.tour_utils.click_next()

        # Step 8 (log-application-url): skip
        self.tour_utils.wait_for_popover()
        self.tour_utils.click_next()

        # Step 9 (log-application-cv): skip
        self.tour_utils.wait_for_popover()
        self.tour_utils.click_next()

        # Step 10 (log-application-cover-letter): click pencil to open writing modal;
        # tour auto-advances to step 10b when #cover-letter-text-modal appears.
        self.tour_utils.wait_for_popover()
        self.get_element("cover_letter_id-write-btn").click()

        # Step 10b (log-application-cover-letter-writing): type text and save;
        # tour auto-advances back to step 10 when the modal closes.
        self.tour_utils.wait_for_popover()
        self.get_element("cover_letter_text").send_keys(
            "Dear Hiring Manager,\n\nI am excited to apply for this role.\n\nKind regards"
        )
        self.get_element("cover-letter-text-modal-save-button").click()

        # Step 10 again (log-application-cover-letter): click Next → note
        self.tour_utils.wait_for_popover()
        self.tour_utils.click_next()

        # Step 11 (log-application-note): skip
        self.tour_utils.wait_for_popover()
        self.tour_utils.click_next()

        # Step 12 (log-application-save)
        self.tour_utils.wait_for_popover()
        self.job_modal_utils.confirm_button("edit").click()

        # Step 13 (log-application-done)
        self.tour_utils.wait_for_popover()
        assert "Done" in self.get_element(self.tour_utils.TOUR_NEXT).text
        assert not self.check_element_exists("tour-keep-data"), "Keep my data toggle must not appear"
        self.tour_utils.click_next()

        self.tour_utils.wait_for_popover_gone()
        self.wait_for_page(self.page_url)

        self.tour_utils.poll_db_count(models.Job, self.user.id, initial_jobs)

    def test_skip_tour(self) -> None:
        """Skip the tour after the date step — no application is saved.

        All JAM entities (demo job and company) must be cleaned up on skip.
        hasUserCreatedData is False → no keep/delete toggle before skip.
        """
        initial_jobs = self.db.query(models.Job).filter_by(owner_id=self.user.id).count()
        initial_companies = self.db.query(models.Company).filter_by(owner_id=self.user.id).count()

        self._start_and_open_edit_form()
        self._fill_date_and_status()

        # Skip during step 6 (log-application-via)
        self.tour_utils.wait_for_popover()
        self.tour_utils.click_skip()

        self.tour_utils.wait_for_popover_gone()
        self.wait_for_page(self.page_url)

        # Demo job and company cleaned up
        self.tour_utils.poll_db_count(models.Job, self.user.id, initial_jobs)
        self.tour_utils.poll_db_count(models.Company, self.user.id, initial_companies)

    def test_back_button_closes_aggregator_modal(self) -> None:
        """Clicking Back while the inline aggregator modal is open closes the modal
        without saving any data, and returns to the aggregator step.
        """
        self._start_and_open_edit_form()
        self._fill_date_and_status()

        initial_aggregators = self.db.query(models.Aggregator).filter_by(owner_id=self.user.id).count()

        # Step 6 (log-application-via): select Aggregator
        self.tour_utils.wait_for_popover()
        Select(self.get_element("applied_via")).select_by_visible_text("Aggregator")
        self.tour_utils.click_next()

        # Step 7 (log-application-aggregator): click + to open inline aggregator modal
        self.tour_utils.wait_for_popover()
        self.get_element("add-button-aggregator").click()
        self.aggregator_modal_utils.wait_for_edit_modal()

        # Partially fill — this data must NOT be saved
        self.get_element("name").send_keys("Should Not Be Saved")

        # Click Cancel: backActionSelector points at the aggregator modal's Cancel button
        self.aggregator_modal_utils.cancel_button("edit").click()
        self.aggregator_modal_utils.wait_for_edit_modal_close()

        # Tour is back on aggregator step
        self.tour_utils.wait_for_popover()
        assert self.tour_utils.popover_title() == "Job Board / Aggregator"

        # No aggregator was created
        self.tour_utils.poll_db_count(models.Aggregator, self.user.id, initial_aggregators)

        # Clean up by skipping the tour
        self.tour_utils.click_skip()
        self.tour_utils.wait_for_popover_gone()
