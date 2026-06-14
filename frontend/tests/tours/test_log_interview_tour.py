"""Selenium tests for the Log Interview guided tour.

Tour step order (log-interview):
  0   interview-intro               informational — centre popover
  1   interview-open-job            click demo job row (hideNextButton; allowedContextMenuActions: ["view"])
  2   interview-application-tab     click Application tab (hideNextButton); auto-advances when tab loads
  3   interview-add                 click Add Interview button (hideNextButton); auto-advances when modal opens
  4   interview-date                required date/time field (waitForInput)
  5   interview-type                required type selector (waitForInput)
  6   interview-attendance          attendance type selector
  7   interview-location            skipIfSelectorAbsent — only when attendance ≠ "Remote"
  8   interview-interviewers        optional; + opens inline person form; nextStepId → note
  8b  interview-interviewer-filling fill inline person form (only if + clicked)
  9   interview-note                optional notes
  10  interview-save                click Save (hideNextButton); auto-advances when modal closes
  11  interview-show-in-table       interview appears in timeline; blockLeftClick; allowedContextMenuActions: []
  12  interview-done                informational — Done button; toggle appears if new person was created

JAM entities seeded at tour start (all is_tour=True):
  Companies: Meridian Labs
  Jobs:      Software Engineer at Meridian Labs (with application_date and application_status="applied")
"""

from app import models
from base_test import BaseTest
from select_utils import Select


TOUR_ID = "log-interview"


class TestLogInterviewTour(BaseTest):
    user_index = 0
    page_url = "jobs"

    def setup_function(self, request) -> None:
        self.login()

    # ------------------------------------------------------------------ helpers

    def _start_and_open_interview_form(self) -> None:
        """Start the tour, open the demo job, switch to Application tab, and open Add Interview.

        Returns with the tour popover on step 4 (interview-date) and the
        interview edit modal already open.
        """
        self.tour_utils.start_tour(TOUR_ID)
        self.wait_for_page("jobs")

        # Step 0 (interview-intro): informational — click Next
        self.tour_utils.click_next()

        # Step 1 (interview-open-job): click the demo job row;
        # tour auto-advances to step 2 when #application-tab appears.
        self.tour_utils.wait_for_popover()
        demo_job = self.db.query(models.Job).filter_by(owner_id=self.user.id, is_tour=True).first()
        self.job_table_utils.table_row_click(demo_job.id)

        # Step 2 (interview-application-tab): click Application tab;
        # tour auto-advances to step 3 when #add-interview-button appears.
        self.tour_utils.wait_for_popover()
        self.get_element("application-tab").click()

        # Step 3 (interview-add): click Add Interview button;
        # tour auto-advances to step 4 when #modal-edit-interview appears.
        self.tour_utils.wait_for_popover()
        self.get_element("add-interview-button").click()
        self.interview_modal_utils.wait_for_edit_modal()

    def _fill_date_and_type(self) -> None:
        """Fill the required date and interview type fields.

        Assumes the current step is interview-date (step 4).
        Leaves the tour on step 6 (interview-attendance).
        """
        # Step 4 (interview-date): set today's date
        self.tour_utils.wait_for_popover()
        self.get_element("date_set_current").click()
        self.tour_utils.click_next()

        # Step 5 (interview-type): select a type
        self.tour_utils.wait_for_popover()
        Select(self.get_element("type")).select_by_visible_text("Video")
        self.tour_utils.click_next()

    def _skip_from_attendance_to_save(self) -> None:
        """Skip attendance, location, interviewers, and note, then Save.

        Assumes the current step is interview-attendance (step 6).
        When no attendance type is selected the location field remains visible
        (displayCondition: attendance_type !== "remote"), so step 7 must also
        be clicked through explicitly.
        """
        # Step 6 (interview-attendance): skip without selecting
        self.tour_utils.wait_for_popover()
        self.tour_utils.click_next()

        # Step 7 (interview-location): visible when attendance_type is null — skip
        self.tour_utils.wait_for_popover()
        self.tour_utils.click_next()

        # Step 8 (interview-interviewers): skip interviewers
        self.tour_utils.wait_for_popover()
        self.tour_utils.click_next()

        # Step 9 (interview-note): skip
        self.tour_utils.wait_for_popover()
        self.tour_utils.click_next()

        # Step 10 (interview-save): click Save
        self.tour_utils.wait_for_popover()
        self.interview_modal_utils.confirm_button("edit").click()

    # ------------------------------------------------------------------ tests

    def test_minimal_fields(self) -> None:
        """Fill date and type only, skip all optional fields, then click Done.

        No new persons created → hasUserCreatedData is False → no keep/delete toggle.
        Demo job and company are cleaned up on Done.
        """
        initial_jobs = self.db.query(models.Job).filter_by(owner_id=self.user.id).count()
        initial_companies = self.db.query(models.Company).filter_by(owner_id=self.user.id).count()
        initial_interviews = self.db.query(models.Interview).filter_by(owner_id=self.user.id).count()

        self._start_and_open_interview_form()
        self._fill_date_and_type()
        self._skip_from_attendance_to_save()

        # Step 11 (interview-show-in-table): interview appears — click Next
        self.tour_utils.wait_for_popover()
        self.tour_utils.click_next()

        # Step 12 (interview-done): no toggle — click Done
        self.tour_utils.wait_for_popover()
        assert "Done" in self.get_element(self.tour_utils.TOUR_NEXT).text
        assert not self.check_element_exists("tour-keep-data"), "Keep my data toggle must not appear"
        self.tour_utils.click_next()

        self.tour_utils.wait_for_popover_gone()
        self.wait_for_page(self.page_url)

        # Interviews, demo job and company all cleaned up
        self.tour_utils.poll_db_count(models.Interview, self.user.id, initial_interviews)
        self.tour_utils.poll_db_count(models.Job, self.user.id, initial_jobs)
        self.tour_utils.poll_db_count(models.Company, self.user.id, initial_companies)

    def test_on_site_with_location(self) -> None:
        """Select On-site attendance and fill the location field.

        The interview-location step appears only when attendance ≠ Remote.
        After saving, the interview and demo entities are cleaned up.
        """
        initial_interviews = self.db.query(models.Interview).filter_by(owner_id=self.user.id).count()

        self._start_and_open_interview_form()
        self._fill_date_and_type()

        # Step 6 (interview-attendance): select On-site → location step appears
        self.tour_utils.wait_for_popover()
        Select(self.get_element("attendance_type")).select_by_visible_text("On-site")
        self.tour_utils.click_next()

        # Step 7 (interview-location): fill the location field
        self.tour_utils.wait_for_popover()
        assert self.tour_utils.popover_title() == "Location"
        self.get_element("location").send_keys("123 Tech Street, London")
        self.tour_utils.click_next()

        # Step 8 (interview-interviewers): skip
        self.tour_utils.wait_for_popover()
        self.tour_utils.click_next()

        # Step 9 (interview-note): skip
        self.tour_utils.wait_for_popover()
        self.tour_utils.click_next()

        # Step 10 (interview-save): click Save
        self.tour_utils.wait_for_popover()
        self.interview_modal_utils.confirm_button("edit").click()

        # Step 11 (interview-show-in-table): click Next
        self.tour_utils.wait_for_popover()
        self.tour_utils.click_next()

        # Step 12 (interview-done): no new persons → no toggle
        self.tour_utils.wait_for_popover()
        assert "Done" in self.get_element(self.tour_utils.TOUR_NEXT).text
        assert not self.check_element_exists("tour-keep-data"), "Keep my data toggle must not appear"
        self.tour_utils.click_next()

        self.tour_utils.wait_for_popover_gone()
        self.wait_for_page(self.page_url)

        self.tour_utils.poll_db_count(models.Interview, self.user.id, initial_interviews)

    def test_remote_attendance_skips_location(self) -> None:
        """Select Remote attendance — the location step must be auto-skipped.

        After remote is selected and Next is clicked, the tour jumps directly
        to interview-interviewers without showing interview-location.
        """
        self._start_and_open_interview_form()
        self._fill_date_and_type()

        # Step 6 (interview-attendance): select Remote
        self.tour_utils.wait_for_popover()
        Select(self.get_element("attendance_type")).select_by_visible_text("Remote")
        self.tour_utils.click_next()

        # Step 8 (interview-interviewers): location must have been skipped
        self.tour_utils.wait_for_popover()
        assert (
            self.tour_utils.popover_title() == "Interviewers"
        ), "Expected to land on Interviewers after Remote attendance (location step skipped)"

        # Clean up by skipping the tour
        self.tour_utils.click_skip()
        self.tour_utils.wait_for_popover_gone()

    def test_with_new_interviewer_keep_data(self) -> None:
        """Add a new interviewer inline during the tour, then keep the contact.

        Creating a new person makes hasUserCreatedData True → keep/delete toggle appears.
        Keeping: the person survives; the demo job, company, and interview are cleaned up.
        """
        initial_jobs = self.db.query(models.Job).filter_by(owner_id=self.user.id).count()
        initial_persons = self.db.query(models.Person).filter_by(owner_id=self.user.id).count()

        self._start_and_open_interview_form()
        self._fill_date_and_type()

        # Step 6 (interview-attendance): skip
        self.tour_utils.wait_for_popover()
        self.tour_utils.click_next()

        # Step 7 (interview-location): skip
        self.tour_utils.wait_for_popover()
        self.tour_utils.click_next()

        # Step 8 (interview-interviewers): click + to open inline person form;
        # tour auto-advances to step 8b when #modal-edit-person appears.
        self.tour_utils.wait_for_popover()
        self.get_element("add-button-interviewer").click()
        self.person_modal_utils.wait_for_edit_modal()

        # Step 8b (interview-interviewer-filling): fill name and confirm;
        # tour auto-advances back to step 8 when the modal closes.
        self.get_element("first_name").send_keys("Sarah")
        self.get_element("last_name").send_keys("Connor")
        self.person_modal_utils.confirm_button("edit").click()
        self.person_modal_utils.wait_for_edit_modal_close()

        # Step 8 again (interview-interviewers): new interviewer auto-selected — click Next → note
        self.tour_utils.wait_for_popover()
        self.tour_utils.click_next()

        # Step 9 (interview-note): skip
        self.tour_utils.wait_for_popover()
        self.tour_utils.click_next()

        # Step 10 (interview-save): click Save
        self.tour_utils.wait_for_popover()
        self.interview_modal_utils.confirm_button("edit").click()

        # Step 11 (interview-show-in-table): click Next
        self.tour_utils.wait_for_popover()
        self.tour_utils.click_next()

        # Step 12 (interview-done): new person → toggle appears — check to keep
        self.tour_utils.wait_for_popover()
        assert "Done" in self.get_element(self.tour_utils.TOUR_NEXT).text
        toggle = self.tour_utils.keep_data_toggle
        assert not toggle.is_selected(), "Keep my data toggle should default to unchecked"
        toggle.click()  # check → keep
        self.tour_utils.click_next()

        self.tour_utils.wait_for_popover_gone()
        self.wait_for_page(self.page_url)

        # Person kept; demo job cleaned up
        self.tour_utils.poll_db_count(models.Person, self.user.id, initial_persons + 1)
        self.tour_utils.poll_db_count(models.Job, self.user.id, initial_jobs)

    def test_with_new_interviewer_delete_data(self) -> None:
        """Add a new interviewer inline, then delete all user-created data.

        Unchecking the toggle removes the new person along with the demo entities.
        """
        initial_persons = self.db.query(models.Person).filter_by(owner_id=self.user.id).count()

        self._start_and_open_interview_form()
        self._fill_date_and_type()

        # Step 6 (interview-attendance): skip
        self.tour_utils.wait_for_popover()
        self.tour_utils.click_next()

        # Step 7 (interview-location): skip
        self.tour_utils.wait_for_popover()
        self.tour_utils.click_next()

        # Step 8 (interview-interviewers): add new interviewer inline
        self.tour_utils.wait_for_popover()
        self.get_element("add-button-interviewer").click()
        self.person_modal_utils.wait_for_edit_modal()

        self.get_element("first_name").send_keys("John")
        self.get_element("last_name").send_keys("Smith")
        self.person_modal_utils.confirm_button("edit").click()
        self.person_modal_utils.wait_for_edit_modal_close()

        self.tour_utils.wait_for_popover()
        self.tour_utils.click_next()  # interviewers → note

        self.tour_utils.wait_for_popover()
        self.tour_utils.click_next()  # note → save

        self.tour_utils.wait_for_popover()
        self.interview_modal_utils.confirm_button("edit").click()

        self.tour_utils.wait_for_popover()
        self.tour_utils.click_next()  # show-in-table → done

        # Step 12 (interview-done): toggle is unchecked by default → delete
        self.tour_utils.wait_for_popover()
        toggle = self.tour_utils.keep_data_toggle
        assert not toggle.is_selected(), "Keep my data toggle should default to unchecked"

        self.tour_utils.click_next()

        self.tour_utils.wait_for_popover_gone()
        self.wait_for_page(self.page_url)

        # New person removed along with demo entities
        self.tour_utils.poll_db_count(models.Person, self.user.id, initial_persons)

    def test_skip_tour(self) -> None:
        """Skip the tour after filling date and type — no interview is saved.

        All JAM entities (demo job and company) must be cleaned up on skip.
        """
        initial_jobs = self.db.query(models.Job).filter_by(owner_id=self.user.id).count()
        initial_companies = self.db.query(models.Company).filter_by(owner_id=self.user.id).count()
        initial_interviews = self.db.query(models.Interview).filter_by(owner_id=self.user.id).count()

        self._start_and_open_interview_form()
        self._fill_date_and_type()

        # Skip during step 6 (interview-attendance)
        self.tour_utils.wait_for_popover()
        self.tour_utils.click_skip()

        self.tour_utils.wait_for_popover_gone()
        self.wait_for_page(self.page_url)

        self.tour_utils.poll_db_count(models.Interview, self.user.id, initial_interviews)
        self.tour_utils.poll_db_count(models.Job, self.user.id, initial_jobs)
        self.tour_utils.poll_db_count(models.Company, self.user.id, initial_companies)

    def test_back_button_closes_interviewer_modal(self) -> None:
        """Clicking Back while the inline person modal is open closes it without saving.

        The tour returns to the interviewers step; no new person is created.
        """
        self._start_and_open_interview_form()
        self._fill_date_and_type()

        initial_persons = self.db.query(models.Person).filter_by(owner_id=self.user.id).count()

        # Step 6 (interview-attendance): skip
        self.tour_utils.wait_for_popover()
        self.tour_utils.click_next()

        # Step 7 (interview-location): skip
        self.tour_utils.wait_for_popover()
        self.tour_utils.click_next()

        # Step 8 (interview-interviewers): click + to open inline person modal
        self.tour_utils.wait_for_popover()
        self.get_element("add-button-interviewer").click()
        self.person_modal_utils.wait_for_edit_modal()

        # Partially fill — must NOT be saved
        self.get_element("first_name").send_keys("Ghost")

        # Click Cancel: backActionSelector triggers modal close
        self.person_modal_utils.cancel_button("edit").click()
        self.person_modal_utils.wait_for_edit_modal_close()

        # Tour is back on interviewers step
        self.tour_utils.wait_for_popover()
        assert self.tour_utils.popover_title() == "Interviewers"

        # No person was created
        self.tour_utils.poll_db_count(models.Person, self.user.id, initial_persons)

        # Clean up by skipping the tour
        self.tour_utils.click_skip()
        self.tour_utils.wait_for_popover_gone()
