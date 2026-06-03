"""Selenium tests for the First Job guided tour.

Tour step order (first-job):
  0  first-job-intro             informational — centre popover
  1  open-job-modal              click Add Job button (hideNextButton); auto-advances when modal opens
  2  job-title                   required input (waitForInput)
  3  add-company                 optional — Next jumps to job-url; + opens company-filling
  4  company-filling             fill inline company form (only if + clicked)
  5  job-url                     optional URL field (validated if filled)
  6  job-attendance              optional attendance-type selector
  7  job-location                skipIfSelectorAbsent — only visible when attendance is on-site/hybrid
  8  job-salary-min              optional
  9  job-salary-max              optional
  10 job-personal-rating         optional
  11 job-favourite               optional toggle
  12 job-deadline                optional date
  13 job-source                  optional source-type selector
  14 job-source-aggregator       skipIfSelectorAbsent — optional; Next jumps to job-source-recruiter
  15 job-source-aggregator-fill  fill inline aggregator form (only if + clicked)
  16 job-source-recruiter        skipIfSelectorAbsent — optional; Next jumps to job-source-company
  17 job-source-recruiter-fill   fill inline recruiter form (only if + clicked)
  18 job-source-company          skipIfSelectorAbsent — optional; Next jumps to job-tags
  19 job-source-company-fill     fill inline recruitment-company form (only if + clicked)
  20 job-tags                    optional — Next jumps to job-contacts
  21 job-tag-filling             fill inline tag form (only if + clicked)
  22 job-contacts                optional — Next jumps to job-description
  23 job-contact-filling         fill inline contact form (only if + clicked)
  24 job-description             optional
  25 job-notes                   optional
  26 save-job                    click Confirm to persist (hideNextButton)
  27 show-job-in-table           job appears in the table (click Next)
  28 done                        keep/delete toggle (present when hasUserCreatedData)

JAM entities seeded at tour start (all is_tour=True):
  Companies:   Acme Corp, Globex Inc
  Contacts:    Emma Williams, David Chen (both at Acme Corp)
  Tags:        TypeScript, React.js
  Aggregators: LinkedIn Jobs, Indeed
"""

from app import models
from base_test import BaseTest
from select_utils import Select


TOUR_ID = "first-job"


class TestFirstJobTour(BaseTest):
    user_index = 0
    page_url = "jobs"

    def setup_function(self, request) -> None:
        self.login()

    # ------------------------------------------------------------------ helpers

    def _start_tour_and_open_form(self) -> None:
        """Start the tour, navigate to jobs, advance past the intro, and open the add form.

        Returns with the tour popover on step 2 (job-title) and the job modal already open.
        """
        self.tour_utils.start_tour(TOUR_ID)
        self.wait_for_page("jobs")

        # Step 0 (first-job-intro): informational — click Next
        self.tour_utils.click_next()

        # Step 1 (open-job-modal): click the highlighted Add button (hideNextButton);
        # the tour auto-advances to step 2 when the modal appears.
        self.job_table_utils.add_entity_button.click()
        self.job_modal_utils.wait_for_edit_modal()

    def _fill_title(self, title: str = "Software Engineer") -> None:
        """Type a job title and advance past the title step."""
        self.tour_utils.wait_for_popover()
        self.get_element("title").send_keys(title)
        self.tour_utils.click_next()

    def _skip_from_url_to_save(self) -> None:
        """Skip all optional fields from job-url through job-notes, then click Confirm.

        Assumes the current step is job-url (i.e. add-company was already handled).
        job-location, job-source-aggregator, job-source-recruiter, and
        job-source-company are auto-skipped via skipIfSelectorAbsent when the
        corresponding form groups are absent (no attendance type / no source set).
        """
        # job-url → skip
        self.tour_utils.wait_for_popover()
        self.tour_utils.click_next()

        # job-attendance → skip
        self.tour_utils.wait_for_popover()
        self.tour_utils.click_next()

        # location → skip
        self.tour_utils.wait_for_popover()
        self.tour_utils.click_next()

        # job-salary-min → skip
        self.tour_utils.wait_for_popover()
        self.tour_utils.click_next()

        # job-salary-max → skip
        self.tour_utils.wait_for_popover()
        self.tour_utils.click_next()

        # job-personal-rating → skip
        self.tour_utils.wait_for_popover()
        self.tour_utils.click_next()

        # job-favourite → skip
        self.tour_utils.wait_for_popover()
        self.tour_utils.click_next()

        # job-deadline → skip (no source → aggregator/recruiter/company steps auto-skipped)
        self.tour_utils.wait_for_popover()
        self.tour_utils.click_next()

        # job-source → skip
        self.tour_utils.wait_for_popover()
        self.tour_utils.click_next()

        # job-tags → skip
        self.tour_utils.wait_for_popover()
        self.tour_utils.click_next()

        # job-contacts → skip
        self.tour_utils.wait_for_popover()
        self.tour_utils.click_next()

        # job-description → skip
        self.tour_utils.wait_for_popover()
        self.tour_utils.click_next()

        # job-notes → skip
        self.tour_utils.wait_for_popover()
        self.tour_utils.click_next()

    # ------------------------------------------------------------------ tests

    def test_minimal_fields_delete_data(self) -> None:
        """Complete the tour with only the job title and skip all optional fields, then delete.

        hasUserCreatedData is True (job was created) → keep/delete toggle appears.
        Unchecking removes the job. JAM entities are also cleaned up.
        """
        initial_jobs = self.db.query(models.Job).filter_by(owner_id=self.user.id).count()
        initial_companies = self.db.query(models.Company).filter_by(owner_id=self.user.id).count()

        self._start_tour_and_open_form()
        self._fill_title()

        # Step 3 (add-company): skip — Next jumps to job-url
        self.tour_utils.wait_for_popover()
        self.tour_utils.click_next()

        self._skip_from_url_to_save()
        self.job_modal_utils.confirm_button("edit").click()

        self.tour_utils.wait_for_popover()
        self.tour_utils.click_next()

        toggle = self.tour_utils.keep_data_toggle
        assert toggle.is_selected(), "Keep my data toggle should default to checked"
        toggle.click()  # uncheck → delete

        assert "Done" in self.get_element(self.tour_utils.TOUR_NEXT).text
        self.tour_utils.click_next()

        self.tour_utils.wait_for_popover_gone()
        self.wait_for_page(self.page_url)

        # Job must be removed; JAM companies also removed
        self.tour_utils.poll_db_count(models.Job, self.user.id, initial_jobs)
        self.tour_utils.poll_db_count(models.Company, self.user.id, initial_companies)

    def test_minimal_fields_keep_data(self) -> None:
        """Complete the tour with only the job title and skip all optional fields, then keep.

        The keep/delete toggle defaults to checked. Leaving it keeps the job.
        JAM entities (companies, persons, keywords, aggregators) are cleaned up regardless.
        """
        initial_jobs = self.db.query(models.Job).filter_by(owner_id=self.user.id).count()
        initial_companies = self.db.query(models.Company).filter_by(owner_id=self.user.id).count()

        self._start_tour_and_open_form()
        self._fill_title(title="My First Job")
        self.tour_utils.wait_for_popover()
        self.tour_utils.click_next()  # skip add-company

        self._skip_from_url_to_save()
        self.job_modal_utils.confirm_button("edit").click()

        self.tour_utils.wait_for_popover()
        self.tour_utils.click_next()

        assert self.tour_utils.keep_data_toggle.is_selected(), "Keep my data toggle should default to checked"

        assert "Done" in self.get_element(self.tour_utils.TOUR_NEXT).text
        self.tour_utils.click_next()

        self.tour_utils.wait_for_popover_gone()
        self.wait_for_page(self.page_url)

        # Job must survive; JAM companies removed
        self.tour_utils.poll_db_count(models.Job, self.user.id, initial_jobs + 1)
        self.tour_utils.poll_db_count(models.Company, self.user.id, initial_companies)

    def test_with_jam_company_keep_data(self) -> None:
        """Select a JAM-seeded company (Acme Corp), save, then keep the job.

        The job is user-created → hasUserCreatedData = True → toggle appears.
        Keeping the job retains it, but JAM companies are deleted regardless —
        company_id on the job is SET NULL (not CASCADE) so the job survives.
        """
        initial_jobs = self.db.query(models.Job).filter_by(owner_id=self.user.id).count()
        initial_companies = self.db.query(models.Company).filter_by(owner_id=self.user.id).count()

        self._start_tour_and_open_form()
        self._fill_title()

        # Step 3 (add-company): select Acme Corp then Next (jumps to job-url)
        self.tour_utils.wait_for_popover()
        Select(self.get_element("company_id")).select_by_visible_text("Acme Corp")
        self.tour_utils.click_next()

        self._skip_from_url_to_save()
        self.job_modal_utils.confirm_button("edit").click()

        self.tour_utils.wait_for_popover()
        self.tour_utils.click_next()

        assert self.tour_utils.keep_data_toggle.is_selected(), "Keep my data toggle should default to checked"

        assert "Done" in self.get_element(self.tour_utils.TOUR_NEXT).text
        self.tour_utils.click_next()

        self.tour_utils.wait_for_popover_gone()
        self.wait_for_page(self.page_url)

        # Job survives; JAM companies removed (company_id is SET NULL on the job)
        self.tour_utils.poll_db_count(models.Job, self.user.id, initial_jobs + 1)
        self.tour_utils.poll_db_count(models.Company, self.user.id, initial_companies)

    def test_with_new_company_delete_data(self) -> None:
        """Create a new company inline during the tour, then delete everything.

        The user-created company is not a JAM entity → hasUserCreatedData = True.
        Unchecking the toggle removes both the job and the user-created company.
        """
        initial_jobs = self.db.query(models.Job).filter_by(owner_id=self.user.id).count()
        initial_companies = self.db.query(models.Company).filter_by(owner_id=self.user.id).count()

        self._start_tour_and_open_form()
        self._fill_title()

        # Step 3 (add-company): click + to open the inline company form;
        # tour auto-advances to company-filling.
        self.tour_utils.wait_for_popover()
        self.job_modal_utils.add_company_button.click()
        self.company_modal_utils.wait_for_edit_modal()

        # Step 4 (company-filling): fill and confirm;
        # tour auto-advances back to add-company.
        self.get_element("name").send_keys("Tour Company Ltd")
        self.company_modal_utils.confirm_button("edit").click()
        self.company_modal_utils.wait_for_edit_modal_close()

        # Step 3 again (add-company): new company is auto-selected — click Next
        self.tour_utils.wait_for_popover()
        self.tour_utils.click_next()

        self._skip_from_url_to_save()
        self.job_modal_utils.confirm_button("edit").click()

        self.tour_utils.wait_for_popover()
        self.tour_utils.click_next()

        assert self.tour_utils.keep_data_toggle.is_selected(), "Keep my data toggle should default to checked"
        self.tour_utils.keep_data_toggle.click()  # uncheck → delete

        assert "Done" in self.get_element(self.tour_utils.TOUR_NEXT).text
        self.tour_utils.click_next()

        self.tour_utils.wait_for_popover_gone()
        self.wait_for_page(self.page_url)

        # Both job and user-created company must be removed; JAM companies also gone
        self.tour_utils.poll_db_count(models.Job, self.user.id, initial_jobs)
        self.tour_utils.poll_db_count(models.Company, self.user.id, initial_companies)

    def test_with_new_company_keep_data(self) -> None:
        """Create a new company inline during the tour, then keep both the job and the company.

        User-created company + job are both retained. JAM entities are cleaned up.
        """
        initial_jobs = self.db.query(models.Job).filter_by(owner_id=self.user.id).count()
        initial_companies = self.db.query(models.Company).filter_by(owner_id=self.user.id).count()

        self._start_tour_and_open_form()
        self._fill_title(title="Engineer at My Company")

        # Step 3 (add-company): create a new company inline
        self.tour_utils.wait_for_popover()
        self.job_modal_utils.add_company_button.click()
        self.company_modal_utils.wait_for_edit_modal()

        self.get_element("name").send_keys("Keeper Corp")
        self.company_modal_utils.confirm_button("edit").click()
        self.company_modal_utils.wait_for_edit_modal_close()

        # Step 3 again: new company auto-selected — click Next
        self.tour_utils.wait_for_popover()
        self.tour_utils.click_next()

        self._skip_from_url_to_save()
        self.job_modal_utils.confirm_button("edit").click()

        self.tour_utils.wait_for_popover()
        self.tour_utils.click_next()

        assert self.tour_utils.keep_data_toggle.is_selected(), "Keep my data toggle should default to checked"

        assert "Done" in self.get_element(self.tour_utils.TOUR_NEXT).text
        self.tour_utils.click_next()

        self.tour_utils.wait_for_popover_gone()
        self.wait_for_page(self.page_url)

        # Both job and user-created company must survive; JAM companies removed
        self.tour_utils.poll_db_count(models.Job, self.user.id, initial_jobs + 1)
        self.tour_utils.poll_db_count(models.Company, self.user.id, initial_companies + 1)

    def test_with_aggregator_source_keep_data(self) -> None:
        """Select Aggregator as source type and pick the JAM LinkedIn Jobs aggregator, then keep.

        When source_type = Aggregator, job-source-aggregator step appears with JAM aggregators
        visible. Selecting a JAM aggregator does not count as user-created data. The job survives;
        JAM aggregators (and other JAM entities) are cleaned up at tour end.
        """
        initial_jobs = self.db.query(models.Job).filter_by(owner_id=self.user.id).count()
        initial_aggregators = self.db.query(models.Aggregator).filter_by(owner_id=self.user.id).count()

        self._start_tour_and_open_form()
        self._fill_title()

        # Step 3 (add-company): skip
        self.tour_utils.wait_for_popover()
        self.tour_utils.click_next()

        # job-url → skip
        self.tour_utils.wait_for_popover()
        self.tour_utils.click_next()

        # job-attendance → skip
        self.tour_utils.wait_for_popover()
        self.tour_utils.click_next()

        # job-location → skip
        self.tour_utils.wait_for_popover()
        self.tour_utils.click_next()

        # job-salary-min → skip
        self.tour_utils.wait_for_popover()
        self.tour_utils.click_next()

        # job-salary-max → skip
        self.tour_utils.wait_for_popover()
        self.tour_utils.click_next()

        # job-personal-rating → skip
        self.tour_utils.wait_for_popover()
        self.tour_utils.click_next()

        # job-favourite → skip
        self.tour_utils.wait_for_popover()
        self.tour_utils.click_next()

        # job-deadline → skip
        self.tour_utils.wait_for_popover()
        self.tour_utils.click_next()

        # job-source: select "Aggregator" to reveal the aggregator sub-step
        self.tour_utils.wait_for_popover()
        Select(self.get_element("source_type")).select_by_visible_text("Aggregator")
        self.tour_utils.click_next()

        # job-source-aggregator: select LinkedIn Jobs (JAM entity) then Next
        self.tour_utils.wait_for_popover()
        Select(self.get_element("source_aggregator_id")).select_by_visible_text("LinkedIn Jobs")
        self.tour_utils.click_next()

        # job-source-recruiter and job-source-company: auto-skipped
        # (recruiter / recruitment-company form groups absent when source = aggregator)

        # job-tags → skip
        self.tour_utils.wait_for_popover()
        self.tour_utils.click_next()

        # job-contacts → skip
        self.tour_utils.wait_for_popover()
        self.tour_utils.click_next()

        # job-description → skip
        self.tour_utils.wait_for_popover()
        self.tour_utils.click_next()

        # job-notes → skip
        self.tour_utils.wait_for_popover()
        self.tour_utils.click_next()

        # save-job: JS click bypasses the tour backdrop overlay on the tall job modal
        self.tour_utils.wait_for_popover()
        self.job_modal_utils.confirm_button("edit").click()

        self.tour_utils.wait_for_popover()
        self.tour_utils.click_next()

        assert self.tour_utils.keep_data_toggle.is_selected(), "Keep my data toggle should default to checked"

        assert "Done" in self.get_element(self.tour_utils.TOUR_NEXT).text
        self.tour_utils.click_next()

        self.tour_utils.wait_for_popover_gone()
        self.wait_for_page(self.page_url)

        # Job survives; JAM aggregators removed (source_aggregator_id SET NULL'd on the job)
        self.tour_utils.poll_db_count(models.Job, self.user.id, initial_jobs + 1)
        self.tour_utils.poll_db_count(models.Aggregator, self.user.id, initial_aggregators)

    def test_skip_before_saving_job(self) -> None:
        """Skip the tour after entering the title — no job is saved.

        All JAM entities (companies, persons, keywords, aggregators) must be cleaned up.
        hasUserCreatedData is False → no keep/delete toggle appears.
        """
        initial_jobs = self.db.query(models.Job).filter_by(owner_id=self.user.id).count()
        initial_companies = self.db.query(models.Company).filter_by(owner_id=self.user.id).count()
        initial_persons = self.db.query(models.Person).filter_by(owner_id=self.user.id).count()
        initial_keywords = self.db.query(models.Keyword).filter_by(owner_id=self.user.id).count()
        initial_aggregators = self.db.query(models.Aggregator).filter_by(owner_id=self.user.id).count()

        self._start_tour_and_open_form()
        self._fill_title()

        # Partially on add-company step — skip the tour now
        self.tour_utils.wait_for_popover()
        self.tour_utils.click_skip()

        self.tour_utils.wait_for_popover_gone()
        self.wait_for_page(self.page_url)

        # No job created; all JAM entities cleaned up
        self.tour_utils.poll_db_count(models.Job, self.user.id, initial_jobs)
        self.tour_utils.poll_db_count(models.Company, self.user.id, initial_companies)
        self.tour_utils.poll_db_count(models.Person, self.user.id, initial_persons)
        self.tour_utils.poll_db_count(models.Keyword, self.user.id, initial_keywords)
        self.tour_utils.poll_db_count(models.Aggregator, self.user.id, initial_aggregators)

    def test_back_button_closes_company_modal(self) -> None:
        """Clicking Back while the inline company modal is open must close the modal
        without persisting any data, and return to the add-company step.
        """

        self._start_tour_and_open_form()
        self._fill_title()

        initial_companies = self.db.query(models.Company).filter_by(owner_id=self.user.id).count()

        # Step 3 (add-company): click + to open the inline company modal
        self.tour_utils.wait_for_popover()
        self.job_modal_utils.add_company_button.click()
        self.company_modal_utils.wait_for_edit_modal()

        # Partially fill — this data must NOT be saved
        self.get_element("name").send_keys("Should Not Be Saved")

        # Click Back: backActionSelector points at the company modal's Cancel button.
        self.tour_utils.wait_for_popover()
        self.company_modal_utils.cancel_button("edit").click()
        self.company_modal_utils.wait_for_edit_modal_close()

        # Tour is back on add-company step
        self.tour_utils.wait_for_popover()
        assert self.tour_utils.popover_title() == "Company"

        # No company was created
        self.tour_utils.poll_db_count(models.Company, self.user.id, initial_companies)

        # Clean up by skipping the tour
        self.tour_utils.click_skip()
        self.tour_utils.wait_for_popover_gone()

    def test_pre_existing_company_not_visible(self) -> None:
        """The tour is isolated — entities created before the tour are hidden from all dropdowns.

        A company created before the tour must not appear in the company dropdown during the tour.
        """
        pre_existing = self._make_company(name="Pre-Existing Corp")
        initial_companies = self.db.query(models.Company).filter_by(owner_id=self.user.id).count()

        self._start_tour_and_open_form()
        self._fill_title()

        # Step 3 (add-company): open the company ReactSelect and check isolation
        self.tour_utils.wait_for_popover()
        company_select = Select(self.get_element("company_id"))
        company_select.open_menu()
        option_texts = [opt.text for opt in company_select.options]
        assert not any(pre_existing.name in text for text in option_texts), (
            f"Pre-existing company '{pre_existing.name}' must not appear in the company "
            f"dropdown during the tour; visible options: {option_texts}"
        )
        company_select._close_menu()

        # JAM companies (Acme Corp, Globex Inc) must be visible
        company_select.open_menu()
        option_texts = [opt.text for opt in company_select.options]
        assert any(
            "Acme Corp" in text for text in option_texts
        ), f"JAM company 'Acme Corp' must be visible during the tour; options: {option_texts}"
        company_select._close_menu()

        # Skip the tour; pre-existing company must be unaffected
        self.tour_utils.click_skip()
        self.tour_utils.wait_for_popover_gone()
        self.wait_for_page(self.page_url)

        self.tour_utils.poll_db_count(models.Company, self.user.id, initial_companies)
