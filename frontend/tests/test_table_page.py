"""Test the main pages of JAM"""

import datetime
import time

import pytest
from selenium.webdriver.common.by import By

from conftest import contiguous_subdicts, models, BaseTest, DataModalUtils, DataTableUtils


class BaseTablePage(BaseTest):
    """Base class for testing pages"""

    test_entries = None
    test_entry = None
    user_index = 0
    table_utils = None
    modal_utils = None

    # Parameters needed
    entry_type = ""
    endpoint = ""  # endpoint of the table, used to query the data
    test_fixture = ""  # test fixture to load the test date
    test_data = {}  # test data used to fill the modal (adding entries, adding incorrect entries, editing entries)
    required_fields = (
        []
    )  # required fields for adding entries. if empty, assume that any field is required (at least one)
    duplicate_fields = []  # fields which are required to be unique
    columns = []  # table column keys user for search and sorting
    sorting_columns = []
    test_entry_index = 0
    model = None

    def setup_function(self, request) -> None:
        """Function called during the setup"""

        self.table_utils = DataTableUtils(
            self.driver, self.entry_type, self.frontend_base_url, self.backend_base_url, self.db
        )
        self.modal_utils = DataModalUtils(
            self.driver, self.entry_type, self.frontend_base_url, self.backend_base_url, self.db
        )
        if isinstance(self.test_fixture, str):
            self.test_fixture = [self.test_fixture]
        self.test_entries, *self.add_test_entries = [request.getfixturevalue(fixture) for fixture in self.test_fixture]
        self.test_entries = [entry for entry in self.test_entries if entry.owner_id == self.user.id]
        self.test_entry = self.test_entries[self.test_entry_index]
        if not self.sorting_columns:
            self.sorting_columns = self.columns
        self.login()

    # ----------------------------------------------- DISPLAY/VIEW TESTS -----------------------------------------------

    def test_display_entries(self) -> None:
        """Test that entries are displayed correctly"""

        # Default 20 entries display
        assert len(self.table_utils.table_rows) == min(
            [20, len(self.test_entries)]
        ), "The table rows should match the entries"

        # Increase to 40
        self.table_utils.set_page_item_select("40")
        self.table_utils.wait_for_table_load()
        assert len(self.table_utils.table_rows) == min(
            [40, len(self.test_entries)]
        ), "The table rows should match the entries"

    def _test_view_modal(self, entry=None) -> None:
        """Helper method to test the view modal for an entry"""

        raise AssertionError("Not implemented")

    def test_view_entry(self) -> None:
        """Test viewing an entry details by clicking on a table row"""

        self.table_utils.set_page_item_select("100")
        self.table_utils.table_row_click(self.test_entry.id)
        self._test_view_modal()

    def test_view_entry_right_click(self) -> None:
        """Test viewing an entry details through the right-click context menu"""

        self.table_utils.table_context_menu(self.test_entry.id, "view")
        self._test_view_modal()

    # --------------------------------------------------- DELETE TEST --------------------------------------------------

    def test_delete_entry(self) -> None:
        """Test deleting an entry entry"""

        self.table_utils.table_context_menu(self.test_entry.id, "delete")
        self.modal_utils.wait_for_delete_modal()
        self.table_utils.delete_confirm_button.click()
        self.table_utils.wait_for_delete_modal_close()
        time.sleep(0.1)
        self.table_utils.wait_for_disappear(f"table-row-{self.test_entry.id}")
        db_data = self.db.query(self.model).filter_by(id=self.test_entry.id).first()
        assert db_data is None, "Expected entry to be deleted from database"

    # ----------------------------------------------------- ADD TEST ---------------------------------------------------

    def test_add_valid_entry(self) -> None:
        """Test adding a new entry"""

        self.table_utils.set_page_item_select("100")
        # Determine the number of entries in the db and in the table
        n_entries = len(self.db.query(self.model).filter_by(owner_id=self.user.id).all())
        initial_table_count = len(self.table_utils.table_rows)

        # Add the new entry
        self.table_utils.add_entity_button.click()
        self.modal_utils.wait_for_edit_modal()
        self.modal_utils._fill_modal(**self.test_data)
        self.modal_utils.confirm_button("edit").click()
        self.modal_utils.wait_for_edit_modal_close()

        # Check that the new entry was properly added to the db and table
        n_entries_new = len(self.db.query(self.model).filter_by(owner_id=self.user.id).all())
        assert n_entries_new == n_entries + 1, "Expected entry to be added to database"
        new_table_count = len(self.table_utils.table_rows)
        assert new_table_count == initial_table_count + 1, "Expected entry to be added to table"

        entries = self.db.query(self.model).all()
        entry_id = max([entry.id for entry in entries])
        entry = [entry for entry in entries if entry.id == entry_id][0]

        # Reopen the modal
        self.table_utils.table_row(entry_id).click()
        self.modal_utils.wait_for_view_modal()
        self._test_view_modal(entry)

        # Reopen in edit mode
        self.table_utils.table_context_menu(entry_id, "edit")
        self.check_edit_modal(entry_id, **self.test_data)

    def check_edit_modal(self, entry_id: int, **values) -> None:
        """Check that the modal in edit mode contains the expected data
        :param entry_id: entry ID
        :param values: values to check"""

        if any(isinstance(v, dict) for v in values.values()):
            for tab_key in values:
                self.table_utils.get_element(f"{tab_key}-tab").click()
                self.check_edit_modal(entry_id, **values[tab_key])
        else:
            for key in values:
                if "date" in key:
                    continue
                element = self.table_utils.get_element(key)
                if element.tag_name == "input":
                    value = element.get_attribute("value")
                else:
                    value = element.text
                assert str(value) == str(values[key])

    def test_add_duplicate_entry(self) -> None:
        """Test that adding a new entry with an existing name shows validation error"""

        if self.duplicate_fields:
            # Add the new entry
            self.table_utils.add_entity_button.click()
            self.modal_utils.wait_for_edit_modal()
            self.modal_utils._fill_modal(**self.test_data)
            self.modal_utils.confirm_button("edit").click()
            self.modal_utils.wait_for_edit_modal_close()

            self.table_utils.add_entity_button.click()
            self.modal_utils.wait_for_edit_modal()
            self.modal_utils._fill_modal(**{key: self.test_data[key] for key in self.duplicate_fields})
            self.modal_utils.confirm_button("edit").click()
            self.modal_utils.get_element(".invalid-feedback", By.CSS_SELECTOR)
            self.modal_utils.cancel_button("edit").click()
            self.modal_utils.wait_for_edit_modal_close()
        else:
            pytest.skip("Duplicate entries are allowed")

    def test_add_incomplete_entry(self) -> None:
        """Test that adding a new entry without all required information shows an error"""

        if len(self.required_fields) > 1:
            dictionaries = contiguous_subdicts({key: self.test_data[key] for key in self.required_fields})
        else:
            dictionaries = [dict()]

        for d in dictionaries:
            self.table_utils.add_entity_button.click()
            self.modal_utils._fill_modal(**d)
            self.modal_utils.confirm_button("edit").click()
            self.modal_utils.get_element(".invalid-feedback", By.CSS_SELECTOR)
            self.modal_utils.cancel_button("edit").click()
            self.modal_utils.wait_for_edit_modal_close()

    def test_add_entry_cancel(self) -> None:
        """Test cancelling a new entry creation."""

        self.table_utils.add_entity_button.click()
        self.modal_utils.wait_for_edit_modal()
        self.modal_utils.cancel_button("edit").click()
        self.modal_utils.wait_for_edit_modal_close()

    # ---------------------------------------------------- EDIT TEST ---------------------------------------------------

    def test_edit_entry_through_view_modal(self) -> None:
        """Test editing an entry through the view modal's edit button"""

        self.table_utils.set_page_item_select("100")
        initial_count = len(self.table_utils.table_rows)
        self.table_utils.table_row_click(self.test_entry.id)
        self.modal_utils.wait_for_view_modal()
        self.modal_utils.edit_button("view").click()
        self.modal_utils._fill_modal(**self.test_data)
        self.modal_utils.confirm_button("edit").click()
        self.modal_utils.wait_for_edit_modal_close()
        self.modal_utils.cancel_button("view").click()
        assert len(self.table_utils.table_rows) == initial_count, "Expected table to remain unchanged"

    def test_edit_entry_through_right_click_context_menu(self) -> None:
        """Test editing an entry through right-click context menu"""

        self.table_utils.set_page_item_select("100")
        initial_count = len(self.table_utils.table_rows)
        self.table_utils.table_context_menu(self.test_entry.id, "edit")
        self.modal_utils._fill_modal(**self.test_data)
        self.modal_utils.confirm_button("edit").click()
        self.modal_utils.wait_for_edit_modal_close()
        assert len(self.table_utils.table_rows) == initial_count, "Expected table to remain unchanged"

    def test_cancel_edit_view(self) -> None:
        """Test cancelling an entry edit opened via the view modal"""

        self.table_utils.table_row_click(self.test_entry.id)
        self.modal_utils.wait_for_view_modal()
        self.modal_utils.edit_button("view").click()
        self.modal_utils.cancel_button("edit").click()
        self.modal_utils.wait_for_edit_modal_close()
        self.modal_utils.wait_for_view_modal()

    def test_cancel_edit(self) -> None:
        """Test cancelling an entry edit opened via the edit modal"""

        self.table_utils.table_context_menu(self.test_entry.id, "edit")
        self.modal_utils.cancel_button("edit").click()
        self.modal_utils.wait_for_edit_modal_close()

    def test_search_functionality(self) -> None:
        """Test the search functionality"""

        for key in self.columns:
            print("Testing column:", key)
            search_text = self.get_search_value(self.test_entry, key).lower()[3:]
            print("Search text:", search_text)

            # Get the expected list of entries
            expected_entries = []
            for entry in self.test_entries:
                value = self.get_search_value(entry, key).lower()
                if search_text in value:
                    expected_entries.append(value)

            # entries = set(entries)
            print("expected", expected_entries)
            self.table_utils.set_text(self.table_utils.get_element("search-input"), search_text)
            time.sleep(0.2)  # Allow time for search to filter
            print("got", self.table_utils.table_rows)
            assert len(self.table_utils.table_rows) == len(expected_entries), "Expected search to filter results"

    # def test_sort_functionality(self) -> None:
    #     """Test sorting functionality"""
    #
    #     for key in self.sorting_columns:
    #         # Click to sort and give time for UI update
    #         self.get_element(f"table-header-{key}").click()
    #         time.sleep(0.2)
    #
    #         # Compare with the sorted values
    #         values = self.get_column_values(key)
    #         a = [v.lower() for v in values if v != "Not Provided"]
    #         assert values == sorted([v.lower() for v in values if v != "Not Provided"] + (len(values) - len(a)) * ["Not Provided"])

    @staticmethod
    def get_search_value(value, key: str) -> str:
        """Get the search value for a given column key"""

        result = getattr(value, key)
        if isinstance(result, str):
            return result
        elif isinstance(result, models.Company):
            return result.name
        else:
            return ""

    # --------------------------------------------------- VIEW MODAL ---------------------------------------------------


class TestKeywordsPage(BaseTablePage):
    """Test class for the keywords Page functionality including:
    - Displaying entries
    - Adding entries
    - Viewing entries
    - Editing entries
    - Deleting entries"""

    endpoint = "keywords"
    page_url = "keywords"
    entry_type = "keyword"
    test_fixture = "test_keywords"
    test_data = {"name": "Test_Name"}
    required_fields = ["name"]
    duplicate_fields = ["name"]
    test_entry_index = 14
    model = models.Keyword

    def _test_view_modal(self, entry=None) -> None:
        """Helper method to test the view modal for an entry"""

        if not entry:
            entry = self.test_entry
        self.modal_utils.check_keyword_view_modal(entry)


class TestAggregatorsPage(BaseTablePage):
    """Test class for Aggregators Page functionality including:
    - Displaying entries
    - Adding new entries
    - Viewing entries
    - Editing entries
    - Deleting entries"""

    endpoint = "aggregators"
    page_url = "aggregators"
    entry_type = "aggregator"
    test_fixture = "test_aggregators"
    test_data = {"name": "Test_Name", "url": "https://www.google.com"}
    required_fields = ["name", "url"]
    duplicate_fields = ["name"]
    columns = ["name", "url"]
    model = models.Aggregator

    def _test_view_modal(self, entry=None) -> None:
        """Helper method to test the view modal for an entry"""
        if not entry:
            entry = self.test_entry
        self.modal_utils.check_aggregator_view_modal(entry)


class TestCompaniesPage(BaseTablePage):
    """Test class for Aggregators Page functionality including:
    - Displaying entries
    - Adding new entries
    - Viewing entries
    - Editing entries
    - Deleting entries"""

    endpoint = "companies"
    page_url = "companies"
    entry_type = "company"
    test_fixture = "test_companies"
    test_data = {"name": "Test_Name", "url": "https://www.google.com", "description": "This is a test description"}
    required_fields = ["name"]
    duplicate_fields = ["name"]
    columns = ["name", "url", "description"]
    model = models.Company

    def _test_view_modal(self, entry=None) -> None:
        """Helper method to test the view modal for an entry"""
        if not entry:
            entry = self.test_entry
        self.modal_utils.check_company_view_modal(entry)


class TestLocationsPage(BaseTablePage):
    """Test class for Aggregators Page functionality including:
    - Displaying entries
    - Adding new entries
    - Viewing entries
    - Editing entries
    - Deleting entries"""

    endpoint = "locations"
    page_url = "locations"
    entry_type = "location"
    test_fixture = "test_locations"
    test_data = {"city": "Oxford", "postcode": "OX1", "country": "United Kingdom"}
    required_fields = []
    columns = ["city", "postcode", "country"]
    duplicate_fields = ["city", "postcode", "country"]
    model = models.Location

    def _test_view_modal(self, entry=None) -> None:
        """Helper method to test the view modal for an entry"""
        if not entry:
            entry = self.test_entry
        self.modal_utils.check_location_view_modal(entry)


class TestPersonsPage(BaseTablePage):
    """Test class for Aggregators Page functionality including:
    - Displaying entries
    - Adding new entries
    - Viewing entries
    - Editing entries
    - Deleting entries"""

    endpoint = "persons"
    page_url = "persons"
    entry_type = "person"
    test_fixture = ["test_persons", "test_companies"]
    test_data = {
        "first_name": "Test_firstname",
        "last_name": "Test_lastname",
        "email": "test_email@test.com",
        "company_id": "Tech Corp",
        "phone": "000000000",
        "linkedin_url": "https://www.linkedin.com/company/websolutions-ltd/",
        "role": "Test_role",
    }
    required_fields = ["last_name", "first_name"]
    duplicate_fields = ["last_name", "first_name", "company_id"]
    columns = ["last_name", "email", "company", "phone", "linkedin_url", "role"]
    sorting_columns = ["name", "company", "role", "email", "created_at"]
    model = models.Person

    def _test_view_modal(self, entry=None) -> None:
        """Helper method to test the view modal for an entry"""
        if not entry:
            entry = self.test_entry
        self.modal_utils.check_person_view_modal(entry)

    def test_table_company_badge(self) -> None:
        """Test that the company badge is displayed correctly"""

        self.get_element("table-row-1-CompanyBadge").click()
        self.company_modal_utils.check_company_view_modal(self.test_entry.company)

    def test_add_company(self) -> None:
        """Test adding a new person with a new company"""

        self.table_utils.add_entity_button.click()
        self.modal_utils._fill_modal(first_name="John", last_name="Doe")
        self.get_element("add-button").click()
        self.company_modal_utils.add_entry(name="Company")
        assert self.get_element("first_name").get_attribute("value") == "John"
        assert self.get_element("last_name").get_attribute("value") == "Doe"
        assert self.get_element("company_id").text == "Company"

    def test_modify_company(self) -> None:
        """Test modifying the company of an existing person"""

        self.table_utils.table_row_click(self.test_entry.id)
        self.get_element("modal-view-person-CompanyBadge").click()
        self.company_modal_utils.edit_button("view").click()
        self.company_modal_utils.wait_for_edit_modal()
        assert self.get_element("name").get_attribute("value") == self.test_entry.company.name
        self.company_modal_utils._fill_modal(name="New Company Name")
        self.company_modal_utils.confirm_button("edit").click()
        assert "New Company Name" in self.company_modal_utils.wait_for_view_modal().text
        self.company_modal_utils.cancel_button("view").click()
        assert self.get_element("modal-view-person-CompanyBadge").text == "New Company Name".upper()


class TestJobApplicationUpdatesPage(BaseTablePage):
    """Test class for Job Application Update Page functionalities"""

    endpoint = "job-application-updates"
    page_url = "job-application-updates"
    entry_type = "jobApplicationUpdate"
    test_fixture = ["test_job_application_updates", "test_jobs"]
    required_fields = ["job_id", "type", "date"]
    test_data = {
        "date": datetime.datetime(year=2025, month=3, day=5, hour=3, minute=30, tzinfo=datetime.timezone.utc),
        "job_id": "Senior Python Developer (Tech Corp)",
        "note": "Received automated confirmation email",
        "type": "Received",
    }
    model = models.JobApplicationUpdate

    def _test_view_modal(self, entry=None) -> None:
        """Helper method to test the view modal for an entry"""
        if not entry:
            entry = self.test_entry
        self.modal_utils.check_update_view_modal(entry)


class TestInterviewPage(BaseTablePage):
    """Test class for Job Application Update Page functionalities"""

    endpoint = "interviews"
    page_url = "interviews"
    entry_type = "interview"
    test_fixture = ["test_interviews", "test_jobs"]
    required_fields = ["job_id", "type", "date"]
    test_data = {
        "date": datetime.datetime(year=2025, month=3, day=5, hour=3, minute=30, tzinfo=datetime.timezone.utc),
        "job_id": "Senior Python Developer (Tech Corp)",
        "note": "Received automated confirmation email",
        "attendance_type": "On-site",
        "type": "HR Interview",
    }
    model = models.Interview

    def _test_view_modal(self, entry=None) -> None:
        """Helper method to test the view modal for an entry"""
        if not entry:
            entry = self.test_entry
        self.modal_utils.check_interview_view_modal(entry)

    def test_table_interviewers_badge(self) -> None:
        """Test that the person badge is displayed correctly in the table"""

        self.get_element("table-row-1-interviewers-0").click()
        self.person_modal_utils.check_person_view_modal(self.test_entry.interviewers[0])

    def test_modal_interviewers_badge(self) -> None:
        """Test that the person badge is displayed correctly in the modal"""

        self.table_utils.table_row(self.test_entry.id).click()
        self.modal_utils.wait_for_view_modal()
        self.get_element("modal-view-interview-person-0").click()
        self.person_modal_utils.check_person_view_modal(self.test_entry.interviewers[0])

    def test_table_location_badge_table(self) -> None:
        """Test that the location badge is displayed correctly in the table"""

        self.get_element("table-row-1-location").click()
        self.location_modal_utils.check_location_view_modal(self.test_entry.location)

    def test_modal_location_badge(self) -> None:
        """Test that the location badge is displayed correctly in the modal"""

        self.table_utils.table_row(self.test_entry.id).click()
        self.modal_utils.wait_for_view_modal()
        self.get_element("modal-view-interview-location").click()
        self.location_modal_utils.check_location_view_modal(self.test_entry.location)

    # TODO add job view


class TestJobPage(BaseTablePage):
    """Test class for Job Application Update Page functionalities"""

    endpoint = "jobs"
    page_url = "jobs"
    entry_type = "job"
    test_fixture = ["test_jobs"]
    required_fields = ["title"]
    test_data = {
        "job": {
            "title": "Senior Python Developer",
            "salary_min": 80000,
            "salary_max": 130000,
            "description": "Lead backend development using Python and modern frameworks. Work with a talented team to build scalable web applications.",
            "url": "https://techcorp.com/jobs/senior_python_developer1",
            "company_id": "Oxford PV",
            "note": "Excellent opportunity for senior developer",
            "attendance_type": "Hybrid",
        },
        "application": {
            "application_date": datetime.datetime.now(),
            "application_url": "https://techcorp.com/apply/senior-python",
            "application_status": "Applied",
            "applied_via": "Aggregator",
            "application_note": "Submitted application with cover letter",
        },
    }
    # duplicate_fields = ["url"]  # TODO not working with tabs
    model = models.Job

    def _test_view_modal(self, entry=None) -> None:
        """Helper method to test the view modal for an entry"""

        if not entry:
            entry = self.test_entry
        self.modal_utils.check_job_view_modal(entry)

    def test_add_interview(self) -> None:
        """Test adding an interview through the job view modal"""

        interview_data = dict(
            date=datetime.datetime(year=2025, month=4, day=10, hour=10, minute=0, tzinfo=datetime.timezone.utc),
            type="HR Interview",
            attendance_type="On-site",
            note="Initial HR screening interview",
        )

        interview_count = len(self.interview_table_utils.table_rows)
        self.table_utils.table_row_click(self.test_entry.id)
        self.modal_utils.wait_for_view_modal()
        self.get_element("application-tab").click()
        self.interview_table_utils.add_entity_button.click()
        self.interview_modal_utils._fill_modal(**interview_data)
        self.interview_modal_utils.confirm_button("edit").click()
        self.interview_modal_utils.wait_for_edit_modal_close()
        assert len(self.interview_table_utils.table_rows) == interview_count + 1
        self.interview_table_utils.table_rows[0].click()
        interview_id = self.interview_table_utils.get_row_id(0)
        interview = self.db.query(models.Interview).filter(models.Interview.id == interview_id).first()
        self.interview_modal_utils.check_interview_view_modal(interview, False)

    def test_modify_interview(self, test_interviews) -> None:
        """Test modifying an interview through the job view modal"""

        interview_data = dict(
            type="Technical Interview",
            attendance_type="Remote",
            note="Technical deep-dive interview",
        )

        # Open job view modal and navigate to the job application tab
        self.driver.refresh()
        self.table_utils.table_row_click(self.test_entry.id)
        self.modal_utils.wait_for_view_modal()
        self.get_element("application-tab").click()

        # Count the number of rows and determine the interview ID
        interview_id = self.interview_table_utils.get_row_id(0)
        self.interview_table_utils.table_rows[0].click()

        # Switch to edit mode and modify the interview
        self.interview_modal_utils.edit_button("view").click()
        self.interview_modal_utils._fill_modal(**interview_data)
        self.interview_modal_utils.confirm_button("edit").click()
        self.interview_modal_utils.wait_for_edit_modal_close()

        # Check the db entry to ensure the modifications were saved
        self.db.expire_all()
        interview = self.db.query(models.Interview).filter(models.Interview.id == interview_id).first()
        assert interview.type == "Technical"
        assert interview.attendance_type == "remote"
        assert interview.note == interview_data["note"]

        # Verify the interview view modal displays the updated information
        self.interview_modal_utils.check_interview_view_modal(interview, False)

    def test_add_job_application_update(self) -> None:
        """Test adding a job application update through the job view modal"""

        update_data = dict(
            date=datetime.datetime(year=2025, month=4, day=15, hour=14, minute=0, tzinfo=datetime.timezone.utc),
            type="Received",
            note="Scheduled first round interview",
        )

        self.table_utils.table_row_click(self.test_entry.id)
        self.modal_utils.wait_for_view_modal()
        self.get_element("application-tab").click()
        update_count = len(self.update_table_utils.table_rows)
        self.update_table_utils.add_entity_button.click()
        self.update_modal_utils._fill_modal(**update_data)
        self.update_modal_utils.confirm_button("edit").click()
        self.update_modal_utils.wait_for_edit_modal_close()
        assert len(self.update_table_utils.table_rows) == update_count + 1
        self.update_table_utils.table_rows[0].click()
        update_id = self.update_table_utils.get_row_id(0)
        update = self.db.query(models.JobApplicationUpdate).filter(models.JobApplicationUpdate.id == update_id).first()
        self.update_modal_utils.check_update_view_modal(update, False)

    def test_modify_job_application_update(self, test_job_application_updates) -> None:
        """Test modifying a job application update through the job view modal"""

        update_data = dict(
            type="Sent",
            note="Rescheduled interview to next week",
        )

        # Open job view modal and navigate to the job application tab
        self.driver.refresh()
        self.table_utils.table_row_click(self.test_entry.id)
        self.modal_utils.wait_for_view_modal()
        self.get_element("application-tab").click()

        # Find the first update row and get its ID
        update_id = self.update_table_utils.get_row_id(0)
        self.update_table_utils.table_rows[0].click()

        # Switch to edit mode and modify the update
        self.update_modal_utils.edit_button("view").click()
        self.update_modal_utils._fill_modal(**update_data)
        self.update_modal_utils.confirm_button("edit").click()
        self.update_modal_utils.wait_for_edit_modal_close()

        # Check the db entry to ensure the modifications were saved
        self.db.expire_all()
        update = self.db.query(models.JobApplicationUpdate).filter(models.JobApplicationUpdate.id == update_id).first()
        assert update.type == "sent"
        assert update.note == update_data["note"]

        # Verify the update view modal displays the updated information
        self.update_modal_utils.check_update_view_modal(update, False)


class TestSpeculativeApplicationPage(BaseTablePage):
    """Test class for Job Application Update Page functionalities"""

    endpoint = "speculative-applications"
    page_url = "speculative-applications"
    entry_type = "speculativeApplication"
    test_fixture = ["test_speculative_applications", "test_persons", "test_companies"]
    required_fields = ["title"]
    test_data = {"company_id": "LocalBiz"}
    duplicate_fields = ["company_id"]
    model = models.SpeculativeApplication

    def _test_view_modal(self, entry=None) -> None:
        """Helper method to test the view modal for an entry"""

        if not entry:
            entry = self.test_entry
        self.modal_utils.check_speculative_application_view_modal(entry)
