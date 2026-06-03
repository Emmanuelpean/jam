"""Selenium tests for the Speculative Applications guided tour.

Tour step order (speculative-applications):
  0  speculative-intro          sidebar nav highlighted, auto-navigates to the page
  1  speculative-add            click the Add button to open the form (hideNextButton)
  2  speculative-company        select or create a company (required)
  3  speculative-company-filling  fill the inline company form (only if + was clicked)
  4  speculative-date           date field (optional)
  5  speculative-email          contact email (optional)
  6  speculative-contacts       link a person or create one inline (optional)
  7  speculative-contact-filling  fill the inline person form (only if + was clicked)
  8  speculative-note           notes (optional)
  9  speculative-save           click Confirm to persist (hideNextButton)
  10 speculative-done           summary / keep-or-delete toggle
"""

from app import models
from base_test import BaseTest
from select_utils import Select


TOUR_ID = "speculative-applications"


class TestSpeculativeApplicationsTour(BaseTest):
    user_index = 0
    page_url = "speculative-applications"

    def setup_function(self, request) -> None:
        self.login()

    # ------------------------------------------------------------------ helpers

    def _start_tour_and_open_form(self) -> None:
        """Start the tour, wait for the page, advance past the intro, and open the add form.

        Returns with the tour popover on step 2 (speculative-company) and the
        speculative application modal already open.
        """
        self.tour_utils.start_tour(TOUR_ID)
        self.wait_for_page("speculative-applications")

        # Step 0 (speculative-intro): informational — click Next
        self.tour_utils.click_next()

        # Step 1 (speculative-add): click the highlighted Add button (hideNextButton);
        # the tour auto-advances to step 2 when the modal appears.
        self.speculativeApplication_table_utils.add_entity_button.click()
        self.speculativeApplication_modal_utils.wait_for_edit_modal()

    # ------------------------------------------------------------------ tests

    def test_tour_existing_company_with_date(self) -> None:
        """Complete the tour by selecting a JAM-seeded company and setting a date.

        The speculative application's company is JAM-created (Anthropic), so the
        SA cascades when that company is deleted.  hasUserCreatedData is False →
        no keep/delete toggle.  Everything is removed when Done is clicked.
        """
        initial_companies = self.db.query(models.Company).filter_by(owner_id=self.user.id).count()
        initial_sas = self.db.query(models.SpeculativeApplication).filter_by(owner_id=self.user.id).count()

        self._start_tour_and_open_form()

        # Step 2 (speculative-company): select an existing JAM-seeded company then Next.
        # nextStepId jumps directly to speculative-date, skipping company-filling.
        Select(self.get_element("company_id")).select_by_visible_text("Anthropic")
        self.tour_utils.click_next()

        # Step 4 (speculative-date): set the current date-time, then Next
        self.tour_utils.wait_for_popover()
        self.get_element("date_set_current").click()
        self.tour_utils.click_next()

        # Step 5 (speculative-email): optional — skip
        self.tour_utils.wait_for_popover()
        self.tour_utils.click_next()

        # Step 6 (speculative-contacts): optional — skip (nextStepId: speculative-note)
        self.tour_utils.wait_for_popover()
        self.tour_utils.click_next()

        # Step 8 (speculative-note): optional — skip
        self.tour_utils.wait_for_popover()
        self.tour_utils.click_next()

        # Step 9 (speculative-save): click Confirm; tour auto-advances when modal closes
        self.tour_utils.wait_for_popover()
        self.speculativeApplication_modal_utils.confirm_button("edit").click()

        # Step 10 (speculative-done): company is JAM-created → SA cascades → no toggle
        self.tour_utils.wait_for_popover()
        assert not self.check_element_exists(
            "tour-keep-data"
        ), "Keep/delete toggle must not appear when all data is JAM-created"
        assert "Done" in self.get_element(self.tour_utils.TOUR_NEXT).text
        self.tour_utils.click_next()

        self.tour_utils.wait_for_popover_gone()
        self.wait_for_page(self.page_url)

        # JAM-seeded companies (Anthropic, DeepMind) and the SA are all cleaned up
        self.tour_utils.poll_db_count(models.SpeculativeApplication, self.user.id, initial_sas)
        self.tour_utils.poll_db_count(models.Company, self.user.id, initial_companies)

    def test_tour_new_company_and_person_delete_data(self) -> None:
        """Complete the tour by creating a new company and a new contact, then delete all.

        Because the speculative application uses a user-created company, it is
        keepable.  hasUserCreatedData is True → keep/delete toggle appears.
        The user unchecks it so every entity created during the tour is removed.
        """
        initial_companies = self.db.query(models.Company).filter_by(owner_id=self.user.id).count()
        initial_persons = self.db.query(models.Person).filter_by(owner_id=self.user.id).count()
        initial_sas = self.db.query(models.SpeculativeApplication).filter_by(owner_id=self.user.id).count()

        self._start_tour_and_open_form()

        # Step 2 (speculative-company): click + to open the inline company form;
        # tour auto-advances to step 3 (speculative-company-filling).
        self.speculativeApplication_modal_utils.add_company_button.click()
        self.company_modal_utils.wait_for_edit_modal()

        # Step 3 (speculative-company-filling): fill in the name and confirm;
        # tour auto-advances back to step 2 when the company modal closes.
        self.get_element("name").send_keys("Tour Test Company")
        self.company_modal_utils.confirm_button("edit").click()
        self.company_modal_utils.wait_for_edit_modal_close()

        # Step 2 again (speculative-company): new company is auto-selected → Next enabled
        self.tour_utils.wait_for_popover()
        self.tour_utils.click_next()

        # Step 4 (speculative-date): optional — skip
        self.tour_utils.wait_for_popover()
        self.tour_utils.click_next()

        # Step 5 (speculative-email): optional — skip
        self.tour_utils.wait_for_popover()
        self.tour_utils.click_next()

        # Step 6 (speculative-contacts): click + to open the inline person form;
        # tour auto-advances to step 7 (speculative-contact-filling).
        self.tour_utils.wait_for_popover()
        self.speculativeApplication_modal_utils.add_contact_button.click()
        self.person_modal_utils.wait_for_edit_modal()

        # Step 7 (speculative-contact-filling): fill in the name and confirm;
        # tour auto-advances back to step 6 when the person modal closes.
        self.get_element("first_name").send_keys("Tour")
        self.get_element("last_name").send_keys("Contact")
        self.person_modal_utils.confirm_button("edit").click()
        self.person_modal_utils.wait_for_edit_modal_close()

        # Step 6 again (speculative-contacts): skip (nextStepId: speculative-note)
        self.tour_utils.wait_for_popover()
        self.tour_utils.click_next()

        # Step 8 (speculative-note): optional — skip
        self.tour_utils.wait_for_popover()
        self.tour_utils.click_next()

        # Step 9 (speculative-save): confirm; tour auto-advances when modal closes
        self.tour_utils.wait_for_popover()
        self.speculativeApplication_modal_utils.confirm_button("edit").click()

        # Step 10 (speculative-done): user-created company → toggle appears, checked by default
        self.tour_utils.wait_for_popover()
        toggle = self.get_element("tour-keep-data")
        assert toggle.is_selected(), "Keep my data toggle should default to checked"
        toggle.click()  # uncheck → delete all user-created data

        assert "Done" in self.get_element(self.tour_utils.TOUR_NEXT).text
        self.tour_utils.click_next()

        self.tour_utils.wait_for_popover_gone()
        self.wait_for_page(self.page_url)

        # Every entity created during the tour must be gone
        self.tour_utils.poll_db_count(models.SpeculativeApplication, self.user.id, initial_sas)
        self.tour_utils.poll_db_count(models.Company, self.user.id, initial_companies)
        self.tour_utils.poll_db_count(models.Person, self.user.id, initial_persons)

    def test_tour_new_company_and_person_keep_data(self) -> None:
        """Complete the tour by creating a new company and a new contact, then keep all.

        The keep/delete toggle defaults to "keep" (checked).  The user leaves it
        checked so user-created entities survive; only JAM-seeded companies are
        removed.
        """
        initial_companies = self.db.query(models.Company).filter_by(owner_id=self.user.id).count()
        initial_persons = self.db.query(models.Person).filter_by(owner_id=self.user.id).count()
        initial_sas = self.db.query(models.SpeculativeApplication).filter_by(owner_id=self.user.id).count()

        self._start_tour_and_open_form()

        # Step 2 (speculative-company): create a new company inline
        self.speculativeApplication_modal_utils.add_company_button.click()
        self.company_modal_utils.wait_for_edit_modal()

        # Step 3 (speculative-company-filling): fill and save
        self.get_element("name").send_keys("Tour Keep Company")
        self.company_modal_utils.confirm_button("edit").click()
        self.company_modal_utils.wait_for_edit_modal_close()

        # Step 2 again: new company auto-selected — click Next
        self.tour_utils.wait_for_popover()
        self.tour_utils.click_next()

        # Step 4 (speculative-date): optional — skip
        self.tour_utils.wait_for_popover()
        self.tour_utils.click_next()

        # Step 5 (speculative-email): optional — skip
        self.tour_utils.wait_for_popover()
        self.tour_utils.click_next()

        # Step 6 (speculative-contacts): create a new person inline
        self.tour_utils.wait_for_popover()
        self.speculativeApplication_modal_utils.add_contact_button.click()
        self.person_modal_utils.wait_for_edit_modal()

        # Step 7 (speculative-contact-filling): fill and save
        self.get_element("first_name").send_keys("Keep")
        self.get_element("last_name").send_keys("Contact")
        self.person_modal_utils.confirm_button("edit").click()
        self.person_modal_utils.wait_for_edit_modal_close()

        # Step 6 again: skip contacts
        self.tour_utils.wait_for_popover()
        self.tour_utils.click_next()

        # Step 8 (speculative-note): optional — skip
        self.tour_utils.wait_for_popover()
        self.tour_utils.click_next()

        # Step 9 (speculative-save): confirm
        self.tour_utils.wait_for_popover()
        self.speculativeApplication_modal_utils.confirm_button("edit").click()

        # Step 10 (speculative-done): toggle appears; leave it checked (keep data)
        self.tour_utils.wait_for_popover()
        toggle = self.get_element("tour-keep-data")
        assert toggle.is_selected(), "Keep my data toggle should default to checked"
        # Do not click — leave user data intact

        assert "Done" in self.get_element(self.tour_utils.TOUR_NEXT).text
        self.tour_utils.click_next()

        self.tour_utils.wait_for_popover_gone()
        self.wait_for_page(self.page_url)

        # User-created SA, company, and person must all survive
        self.tour_utils.poll_db_count(models.SpeculativeApplication, self.user.id, initial_sas + 1)
        self.tour_utils.poll_db_count(models.Company, self.user.id, initial_companies + 1)
        self.tour_utils.poll_db_count(models.Person, self.user.id, initial_persons + 1)

    def test_skip_with_open_modal_does_not_show_discard_dialog(self) -> None:
        """Skipping the tour while the SA form is partially filled must not trigger
        the 'Unsaved Changes' confirmation dialog — endTour clicks the Cancel button
        (which calls handleHideImmediate) rather than the X (which calls handleCloseWithConfirmation).
        """
        initial_companies = self.db.query(models.Company).filter_by(owner_id=self.user.id).count()

        self._start_tour_and_open_form()

        # Partially fill the SA form so unsaved changes exist
        Select(self.get_element("company_id")).select_by_visible_text("Anthropic")

        # Skip the tour — the SA modal is still open with unsaved data
        self.tour_utils.click_skip()

        # The discard-confirmation dialog must NOT appear
        assert not self.check_element_exists(
            "delete-alert-modal"
        ), "Discard confirmation dialog must not appear when skipping the tour"

        self.tour_utils.wait_for_popover_gone()
        self.wait_for_page(self.page_url)

        # JAM-seeded companies are cleaned up even after a mid-flow skip
        self.tour_utils.poll_db_count(models.Company, self.user.id, initial_companies)

    def test_back_button_closes_inline_modals(self) -> None:
        """Clicking Back while an inline company or person modal is open must close
        that modal (via backActionSelector) and return to the previous tour step —
        without persisting any data from the inline form.
        """
        initial_companies = self.db.query(models.Company).filter_by(owner_id=self.user.id).count()
        initial_persons = self.db.query(models.Person).filter_by(owner_id=self.user.id).count()

        self._start_tour_and_open_form()

        # ── Company modal ────────────────────────────────────────────────────────
        # Step 2 → open company modal
        self.speculativeApplication_modal_utils.add_company_button.click()
        self.company_modal_utils.wait_for_edit_modal()

        # Partially fill the company form — this data must NOT be saved
        self.get_element("name").send_keys("Should Not Be Saved")

        # Click Back: the tour step (speculative-company-filling) has backActionSelector
        # pointing at the company modal's Cancel button → modal closes, tour goes back
        self.tour_utils.click_back()
        self.company_modal_utils.wait_for_edit_modal_close()

        # Tour is back on speculative-company (step 2)
        self.tour_utils.wait_for_popover()
        assert self.tour_utils.popover_title() == "Company"

        # No company was created
        self.tour_utils.poll_db_count(models.Company, self.user.id, initial_companies + 2)  # only the 2 JAM-seeded ones

        # ── Person modal ─────────────────────────────────────────────────────────
        # Advance past company (select existing) and optional fields to reach contacts
        Select(self.get_element("company_id")).select_by_visible_text("Anthropic")
        self.tour_utils.click_next()  # → speculative-date

        self.tour_utils.wait_for_popover()
        self.tour_utils.click_next()  # → speculative-email

        self.tour_utils.wait_for_popover()
        self.tour_utils.click_next()  # → speculative-contacts

        # Step 6 → open person modal
        self.tour_utils.wait_for_popover()
        self.speculativeApplication_modal_utils.add_contact_button.click()
        self.person_modal_utils.wait_for_edit_modal()

        # Partially fill the person form — must NOT be saved
        self.get_element("first_name").send_keys("Should Not Be Saved")

        # Click Back: closes the person modal, tour returns to speculative-contacts
        self.tour_utils.click_back()
        self.person_modal_utils.wait_for_edit_modal_close()

        self.tour_utils.wait_for_popover()
        assert self.tour_utils.popover_title() == "Contacts"

        # No person was created
        self.tour_utils.poll_db_count(models.Person, self.user.id, initial_persons)

        # Clean up by skipping the tour
        self.tour_utils.click_skip()
        self.tour_utils.wait_for_popover_gone()
        self.tour_utils.poll_db_count(models.Company, self.user.id, initial_companies)

    def test_tour_orphan_company_with_jam_company_sa_keep_data(self) -> None:
        """Create a company inline then switch to a JAM-seeded company for the SA.

        The inline-created company is never used by the SA (the user replaces the
        auto-selection with 'Anthropic'), so it becomes an orphan.  Because the orphan
        is user-created, hasUserCreatedData is True and the keep/delete toggle appears.
        Leaving the toggle checked: the SA is deleted (JAM company cascades it) while
        the orphan company survives.
        """
        initial_companies = self.db.query(models.Company).filter_by(owner_id=self.user.id).count()
        initial_sas = self.db.query(models.SpeculativeApplication).filter_by(owner_id=self.user.id).count()

        self._start_tour_and_open_form()

        # Step 2 (speculative-company): click + to open the inline company form
        self.speculativeApplication_modal_utils.add_company_button.click()
        self.company_modal_utils.wait_for_edit_modal()

        # Step 3 (speculative-company-filling): fill in and confirm → orphan company created
        self.get_element("name").send_keys("Orphan Company")
        self.company_modal_utils.confirm_button("edit").click()
        self.company_modal_utils.wait_for_edit_modal_close()

        # Step 2 again: orphan company is auto-selected — override with a JAM-seeded company
        self.tour_utils.wait_for_popover()
        Select(self.get_element("company_id")).select_by_visible_text("Anthropic")
        self.tour_utils.click_next()

        # Step 4 (speculative-date): optional — skip
        self.tour_utils.wait_for_popover()
        self.tour_utils.click_next()

        # Step 5 (speculative-email): optional — skip
        self.tour_utils.wait_for_popover()
        self.tour_utils.click_next()

        # Step 6 (speculative-contacts): optional — skip (nextStepId: speculative-note)
        self.tour_utils.wait_for_popover()
        self.tour_utils.click_next()

        # Step 8 (speculative-note): optional — skip
        self.tour_utils.wait_for_popover()
        self.tour_utils.click_next()

        # Step 9 (speculative-save): confirm; tour auto-advances when modal closes
        self.tour_utils.wait_for_popover()
        self.speculativeApplication_modal_utils.confirm_button("edit").click()

        # Step 10 (speculative-done): orphan company is user-created → toggle appears
        self.tour_utils.wait_for_popover()
        toggle = self.get_element("tour-keep-data")
        assert toggle.is_selected(), "Keep my data toggle should default to checked"
        # Leave toggle checked — orphan company should survive; SA is deleted (JAM company)

        assert "Done" in self.get_element(self.tour_utils.TOUR_NEXT).text
        self.tour_utils.click_next()

        self.tour_utils.wait_for_popover_gone()
        self.wait_for_page(self.page_url)

        # SA is deleted (its company is JAM-seeded → it cascades during cleanup)
        self.tour_utils.poll_db_count(models.SpeculativeApplication, self.user.id, initial_sas)
        # JAM companies (Anthropic, DeepMind) are deleted; orphan company survives
        self.tour_utils.poll_db_count(models.Company, self.user.id, initial_companies + 1)

    def test_pre_existing_person_not_visible_during_tour(self) -> None:
        """A person that existed before the tour starts must not appear in the contacts
        dropdown during the tour.

        The tour snapshot excludes pre-existing entities from visibleData, so the
        ReactSelect for contacts shows only persons created during the tour (none here).
        After the tour ends the pre-existing person is unaffected.
        """
        pre_existing = self._make_person(first_name="Pre", last_name="Existing")
        initial_persons = self.db.query(models.Person).filter_by(owner_id=self.user.id).count()

        self._start_tour_and_open_form()

        # Navigate to the contacts step: company → date → email → contacts
        Select(self.get_element("company_id")).select_by_visible_text("Anthropic")
        self.tour_utils.click_next()  # → speculative-date

        self.tour_utils.wait_for_popover()
        self.tour_utils.click_next()  # → speculative-email

        self.tour_utils.wait_for_popover()
        self.tour_utils.click_next()  # → speculative-contacts

        # Step 6 (speculative-contacts): open the ReactSelect and verify the pre-existing
        # person is absent (filtered out by the tour snapshot).
        self.tour_utils.wait_for_popover()
        contacts_select = Select(self.get_element("contacts"))
        contacts_select.open_menu()
        option_texts = [opt.text for opt in contacts_select.options]
        assert not any(pre_existing.name in text for text in option_texts), (
            f"Pre-existing person '{pre_existing.name}' must not appear in contacts "
            f"dropdown during tour; visible options: {option_texts}"
        )
        contacts_select._close_menu()

        # Skip the tour; JAM companies are cleaned up but the pre-existing person is untouched
        self.tour_utils.click_skip()
        self.tour_utils.wait_for_popover_gone()
        self.wait_for_page(self.page_url)

        # Pre-existing person must still be in the database
        self.tour_utils.poll_db_count(models.Person, self.user.id, initial_persons)
