"""Selenium tests for the Add Contact guided tour.

Tour step order (add-contact):
  0  contact-intro          informational — centre popover
  1  contact-add-btn        click Add to open the form (hideNextButton)
  2  contact-first-name     first name (required by waitForInput)
  3  contact-last-name      last name (required by waitForInput)
  4  contact-company        select or create a company (optional, nextStepId: contact-role)
  5  contact-company-filling  fill the inline company form (only if + was clicked)
  6  contact-role           job title (optional)
  7  contact-email          email address (optional, validated if filled)
  8  contact-phone          phone number (optional)
  9  contact-linkedin       LinkedIn profile URL (optional)
  10 contact-recruiter      is-recruiter toggle (optional)
  11 contact-save           click Confirm to persist (hideNextButton)
  12 contact-done           summary / keep-or-delete toggle
"""

from app import models
from base_test import BaseTest
from select_utils import Select


TOUR_ID = "add-contact"


class TestAddContactTour(BaseTest):
    user_index = 0
    page_url = "contacts"

    def setup_function(self, request) -> None:
        self.login()

    # ------------------------------------------------------------------ helpers

    def _start_tour_and_open_form(self) -> None:
        """Start the tour, wait for the contacts page, advance past the intro, and open the add form.

        Returns with the tour popover on step 2 (contact-first-name) and the
        person modal already open.
        """
        self.tour_utils.start_tour(TOUR_ID)
        self.wait_for_page("contacts")

        # Step 0 (contact-intro): informational — click Next
        self.tour_utils.click_next()

        # Step 1 (contact-add-btn): click the highlighted Add button (hideNextButton);
        # the tour auto-advances to step 2 when the modal appears.
        self.person_table_utils.add_entity_button.click()
        self.person_modal_utils.wait_for_edit_modal()

    def _fill_names(self, first: str = "Tour", last: str = "Contact") -> None:
        """Type first and last name into the open person modal and advance past both steps."""
        # Step 2 (contact-first-name): type name, then Next
        self.tour_utils.wait_for_popover()
        self.get_element("first_name").send_keys(first)
        self.tour_utils.click_next()

        # Step 3 (contact-last-name): type name, then Next
        self.tour_utils.wait_for_popover()
        self.get_element("last_name").send_keys(last)
        self.tour_utils.click_next()

    # ------------------------------------------------------------------ tests

    def test_tour_skip_all_optional_delete_data(self) -> None:
        """Complete the tour by filling only the required name fields and skipping everything else.

        hasUserCreatedData is True (person was created) → keep/delete toggle appears.
        Unchecking the toggle removes the person.
        """
        initial_persons = self.db.query(models.Person).filter_by(owner_id=self.user.id).count()

        self._start_tour_and_open_form()
        self._fill_names()

        # Step 4 (contact-company): skip — Next jumps to contact-role
        self.tour_utils.wait_for_popover()
        self.tour_utils.click_next()

        # Step 6 (contact-role): optional — skip
        self.tour_utils.wait_for_popover()
        self.tour_utils.click_next()

        # Step 7 (contact-email): optional — skip
        self.tour_utils.wait_for_popover()
        self.tour_utils.click_next()

        # Step 8 (contact-phone): optional — skip
        self.tour_utils.wait_for_popover()
        self.tour_utils.click_next()

        # Step 9 (contact-linkedin): optional — skip
        self.tour_utils.wait_for_popover()
        self.tour_utils.click_next()

        # Step 10 (contact-recruiter): optional — skip
        self.tour_utils.wait_for_popover()
        self.tour_utils.click_next()

        # Step 11 (contact-save): confirm; tour auto-advances when modal closes
        self.tour_utils.wait_for_popover()
        self.person_modal_utils.confirm_button("edit").click()

        # Step 12 (contact-done): person is user-created → toggle appears, unchecked by default
        self.tour_utils.wait_for_popover()
        toggle = self.get_element("tour-keep-data")
        assert not toggle.is_selected(), "Keep my data toggle should default to unchecked"

        assert "Done" in self.get_element(self.tour_utils.TOUR_NEXT).text
        self.tour_utils.click_next()

        self.tour_utils.wait_for_popover_gone()
        self.wait_for_page(self.page_url)

        # Person must be removed
        self.tour_utils.poll_db_count(models.Person, self.user.id, initial_persons)

    def test_tour_skip_all_optional_keep_data(self) -> None:
        """Complete the tour by filling only required fields, then keep the person.

        The keep/delete toggle defaults to checked. Leaving it keeps the person.
        """
        initial_persons = self.db.query(models.Person).filter_by(owner_id=self.user.id).count()

        self._start_tour_and_open_form()
        self._fill_names(first="Keep", last="Person")

        # Step 4 (contact-company): skip
        self.tour_utils.wait_for_popover()
        self.tour_utils.click_next()

        # Steps 6-10: skip all optional fields
        for _ in range(5):
            self.tour_utils.wait_for_popover()
            self.tour_utils.click_next()

        # Step 11 (contact-save): confirm
        self.tour_utils.wait_for_popover()
        self.person_modal_utils.confirm_button("edit").click()

        # Step 12 (contact-done): check toggle to keep
        self.tour_utils.wait_for_popover()
        toggle = self.get_element("tour-keep-data")
        assert not toggle.is_selected(), "Keep my data toggle should default to unchecked"
        toggle.click()  # check → keep

        assert "Done" in self.get_element(self.tour_utils.TOUR_NEXT).text
        self.tour_utils.click_next()

        self.tour_utils.wait_for_popover_gone()
        self.wait_for_page(self.page_url)

        # Person must survive
        self.tour_utils.poll_db_count(models.Person, self.user.id, initial_persons + 1)

    def test_tour_new_company_all_fields_keep_data(self) -> None:
        """Complete the tour by creating a new company and filling all optional fields.

        hasUserCreatedData is True (person + company created) → toggle appears.
        Leaving toggle checked keeps both the person and the company.
        """
        initial_persons = self.db.query(models.Person).filter_by(owner_id=self.user.id).count()
        initial_companies = self.db.query(models.Company).filter_by(owner_id=self.user.id).count()

        self._start_tour_and_open_form()
        self._fill_names(first="Full", last="Fields")

        # Step 4 (contact-company): click + to open the inline company form;
        # tour auto-advances to step 5 (contact-company-filling).
        self.tour_utils.wait_for_popover()
        self.person_modal_utils.add_company_button.click()
        self.company_modal_utils.wait_for_edit_modal()

        # Step 5 (contact-company-filling): fill and confirm;
        # tour auto-advances back to contact-company (step 4) — same as speculative tour.
        self.get_element("name").send_keys("Tour Company")
        self.company_modal_utils.confirm_button("edit").click()
        self.company_modal_utils.wait_for_edit_modal_close()

        # Step 4 again (contact-company): new company is auto-selected → click Next
        self.tour_utils.wait_for_popover()
        self.tour_utils.click_next()

        # Step 6 (contact-role): fill
        self.tour_utils.wait_for_popover()
        self.get_element("role").send_keys("Hiring Manager")
        self.tour_utils.click_next()

        # Step 7 (contact-email): fill a valid email
        self.tour_utils.wait_for_popover()
        self.get_element("email").send_keys("tour@example.com")
        self.tour_utils.click_next()

        # Step 8 (contact-phone): fill
        self.tour_utils.wait_for_popover()
        self.get_element("phone").send_keys("+44 7700 900000")
        self.tour_utils.click_next()

        # Step 9 (contact-linkedin): fill
        self.tour_utils.wait_for_popover()
        self.get_element("linkedin_url").send_keys("https://linkedin.com/in/tourcontact")
        self.tour_utils.click_next()

        # Step 10 (contact-recruiter): check the is-recruiter checkbox
        self.tour_utils.wait_for_popover()
        self.get_element("is_recruiter").click()
        self.tour_utils.click_next()

        # Step 11 (contact-save): confirm
        self.tour_utils.wait_for_popover()
        self.person_modal_utils.confirm_button("edit").click()

        # Step 12 (contact-done): toggle appears, check to keep
        self.tour_utils.wait_for_popover()
        toggle = self.get_element("tour-keep-data")
        assert not toggle.is_selected(), "Keep my data toggle should default to unchecked"
        toggle.click()  # check → keep

        assert "Done" in self.get_element(self.tour_utils.TOUR_NEXT).text
        self.tour_utils.click_next()

        self.tour_utils.wait_for_popover_gone()
        self.wait_for_page(self.page_url)

        # Person and company must both survive
        self.tour_utils.poll_db_count(models.Person, self.user.id, initial_persons + 1)
        self.tour_utils.poll_db_count(models.Company, self.user.id, initial_companies + 1)

    def test_tour_new_company_all_fields_delete_data(self) -> None:
        """Create a company and fill all fields, then delete everything.

        Unchecking the toggle removes the person and the company.
        """
        initial_persons = self.db.query(models.Person).filter_by(owner_id=self.user.id).count()
        initial_companies = self.db.query(models.Company).filter_by(owner_id=self.user.id).count()

        self._start_tour_and_open_form()
        self._fill_names(first="Delete", last="Me")

        # Step 4 (contact-company): create a new company inline
        self.tour_utils.wait_for_popover()
        self.person_modal_utils.add_company_button.click()
        self.company_modal_utils.wait_for_edit_modal()

        self.get_element("name").send_keys("Delete Company")
        self.company_modal_utils.confirm_button("edit").click()
        self.company_modal_utils.wait_for_edit_modal_close()

        # Step 4 again (contact-company): new company is auto-selected → click Next
        self.tour_utils.wait_for_popover()
        self.tour_utils.click_next()

        # Steps 6-10: skip all optional fields
        for _ in range(5):
            self.tour_utils.wait_for_popover()
            self.tour_utils.click_next()

        # Step 11 (contact-save): confirm
        self.tour_utils.wait_for_popover()
        self.person_modal_utils.confirm_button("edit").click()

        # Step 12 (contact-done): toggle is unchecked by default → delete
        self.tour_utils.wait_for_popover()
        toggle = self.get_element("tour-keep-data")
        assert not toggle.is_selected(), "Keep my data toggle should default to unchecked"

        assert "Done" in self.get_element(self.tour_utils.TOUR_NEXT).text
        self.tour_utils.click_next()

        self.tour_utils.wait_for_popover_gone()
        self.wait_for_page(self.page_url)

        # Both person and company must be removed
        self.tour_utils.poll_db_count(models.Person, self.user.id, initial_persons)
        self.tour_utils.poll_db_count(models.Company, self.user.id, initial_companies)

    def test_skip_with_open_modal_does_not_show_discard_dialog(self) -> None:
        """Skipping the tour while the person form is partially filled must not trigger
        the 'Unsaved Changes' confirmation dialog — endTour clicks the Cancel button
        (which calls handleHideImmediate) rather than the X (which calls handleCloseWithConfirmation).
        """
        initial_persons = self.db.query(models.Person).filter_by(owner_id=self.user.id).count()

        self._start_tour_and_open_form()

        # Partially fill the form so unsaved changes exist
        self.tour_utils.wait_for_popover()
        self.get_element("first_name").send_keys("Should Not Be Saved")

        # Skip the tour — the person modal is still open with unsaved data
        self.tour_utils.click_skip()

        # The discard-confirmation dialog must NOT appear
        assert not self.check_element_exists(
            "delete-alert-modal"
        ), "Discard confirmation dialog must not appear when skipping the tour"

        self.tour_utils.wait_for_popover_gone()
        self.wait_for_page(self.page_url)

        # No person should have been persisted
        self.tour_utils.poll_db_count(models.Person, self.user.id, initial_persons)

    def test_back_button_closes_company_modal(self) -> None:
        """Clicking Back while the inline company modal is open must close the modal
        (via backActionSelector) and return to the company step — without persisting
        any data from the inline form.
        """
        initial_companies = self.db.query(models.Company).filter_by(owner_id=self.user.id).count()

        self._start_tour_and_open_form()
        self._fill_names()

        # Step 4 (contact-company): click + to open the inline company modal
        self.tour_utils.wait_for_popover()
        self.person_modal_utils.add_company_button.click()
        self.company_modal_utils.wait_for_edit_modal()

        # Partially fill the company form — this data must NOT be saved
        self.get_element("name").send_keys("Should Not Be Saved")

        # Click Back: the tour step (contact-company-filling) has backActionSelector
        # pointing at the company modal's Cancel button → modal closes, tour goes back
        self.tour_utils.click_back()
        self.company_modal_utils.wait_for_edit_modal_close()

        # Tour is back on contact-company (step 4)
        self.tour_utils.wait_for_popover()
        assert self.tour_utils.popover_title() == "Company"

        # No company was created
        self.tour_utils.poll_db_count(models.Company, self.user.id, initial_companies + 2)

        # Clean up by skipping the tour
        self.tour_utils.click_skip()
        self.tour_utils.wait_for_popover_gone()

    def test_pre_existing_company_not_visible_as_own_entry(self) -> None:
        """The tour is isolated — entities created before the tour are hidden from all
        dropdowns.  This test verifies the behaviour for the company dropdown: a company
        created before the tour must not appear as an option during the tour.
        """
        pre_existing_company = self._make_company(name="Pre-Existing Company")
        initial_companies = self.db.query(models.Company).filter_by(owner_id=self.user.id).count()

        self._start_tour_and_open_form()
        self._fill_names()

        # Step 4 (contact-company): open the company ReactSelect and check the pre-existing
        # company is absent (filtered out by the tour snapshot).
        self.tour_utils.wait_for_popover()
        company_select = Select(self.get_element("company_id"))
        company_select.open_menu()
        option_texts = [opt.text for opt in company_select.options]
        assert not any(pre_existing_company.name in text for text in option_texts), (
            f"Pre-existing company '{pre_existing_company.name}' must not appear in the "
            f"company dropdown during the tour; visible options: {option_texts}"
        )
        company_select._close_menu()

        # Skip the tour; pre-existing company must be unaffected
        self.tour_utils.click_skip()
        self.tour_utils.wait_for_popover_gone()
        self.wait_for_page(self.page_url)

        self.tour_utils.poll_db_count(models.Company, self.user.id, initial_companies)
