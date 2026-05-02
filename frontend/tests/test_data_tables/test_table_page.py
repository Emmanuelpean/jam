"""Test the main pages of JAM"""

import datetime as dt
import time

import pytest
from selenium.webdriver.common.by import By

from base_test import models, BaseTest, contiguous_subdicts
from tests.utils.test_data import ADMIN_USER_INDEX


class BaseTablePage(BaseTest):
    """Base class for testing pages"""

    test_entries = None
    test_entry = None
    user_index = 0
    table_utils = None
    modal_utils = None

    # Parameters needed
    entry_type = ""  # entry type, used to get the correct utils
    endpoint = ""  # endpoint of the table, used to query the data
    test_fixture = ""  # test fixture to load the test date
    test_data = {}  # test data used to fill the modal (adding entries, adding incorrect entries, editing entries)
    required_fields = []  # required fields for adding entries. if empty, assume that any field is required
    duplicate_fields = []  # fields which are required to be unique
    columns = []  # table column keys user for search and sorting
    sorting_columns = []  # columns which can be sorted, if empty assume all columns can be sorted
    test_entry_index = 0  # index of the test entry to use for view/edit/delete tests
    model = None  # database model class for the entry type

    def setup_function(self, request) -> None:
        """Function called during the setup"""

        self.table_utils = getattr(self, f"{self.entry_type}_table_utils")
        self.modal_utils = getattr(self, f"{self.entry_type}_modal_utils")
        self.test_fixture = [self.test_fixture] if isinstance(self.test_fixture, str) else self.test_fixture
        self.test_entries, *self.add_test_entries = [request.getfixturevalue(fixture) for fixture in self.test_fixture]
        if hasattr(self.test_entries[0], "owner_id"):
            self.test_entries = [entry for entry in self.test_entries if entry.owner_id == self.user.id]
        self.test_entry = self.test_entries[self.test_entry_index]
        self.sorting_columns = self.columns if not self.sorting_columns else None
        self.login()

    # ------------------------------------------------------ TABLE -----------------------------------------------------

    def test_display_entries(self) -> None:
        """Test that entries are displayed correctly"""

        if hasattr(self.test_entries[0], "application_status"):
            test_entries = [
                entry for entry in self.test_entries if entry.application_status not in ["rejected", "withdrawn"]
            ]
        else:
            test_entries = self.test_entries

        # Default 20 entries display
        assert len(self.table_utils.table_rows) == min([20, len(test_entries)])

        # Increase to 40
        self.table_utils.set_page_item_select("40")
        self.table_utils.wait_for_table_load()
        assert len(self.table_utils.table_rows) == min([40, len(test_entries)])

    # def test_search_functionality(self) -> None:
    #     """Test the search functionality"""
    #
    #     for key in self.columns:
    #         search_text = self.get_search_value(self.test_entry, key).lower()[:-1]
    #         self.table_utils.set_search(search_text)
    #         values = self.table_utils.get_column_values()
    #         print(values)
    #         for row in values:
    #             row_values = ",".join([row[key_] for key_ in self.columns]).lower()
    #             assert search_text in row_values

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
    #         assert values == sorted(
    #             [v.lower() for v in values if v != "Not Provided"] + (len(values) - len(a)) * ["Not Provided"]
    #         )

    @staticmethod
    def get_search_value(value, key: str) -> str:
        """Get the search value for a given column key"""

        if key == "companyBadge":
            return value.company.name
        elif key == "jobBadge":
            return value.job.title + " (" + value.job.company.name + ")"
        result = getattr(value, key)
        if isinstance(result, str):
            return result
        elif isinstance(result, dt.datetime):
            return result.strftime("%d/%m/%Y")
        else:
            return ""

    def get_entries_count(self) -> int:
        """Get the number of entries in the database"""

        if hasattr(self.test_entries[0], "owner_id"):
            return len(self.db.query(self.model).filter_by(owner_id=self.user.id).all())
        else:
            return len(self.db.query(self.model).all())

    # --------------------------------------------------- VIEW TESTS ---------------------------------------------------

    def test_view_entry(self) -> None:
        """Test viewing an entry details by clicking on a table row"""

        self.table_utils.set_page_item_select("100")
        self.table_utils.table_row_click(self.test_entry.id)
        self.modal_utils.test_view_modal(self.test_entry)

    def test_view_entry_right_click(self) -> None:
        """Test viewing an entry details through the right-click context menu"""

        self.table_utils.table_context_menu(self.test_entry.id, "view")
        self.modal_utils.test_view_modal(self.test_entry)

    # --------------------------------------------------- DELETE TEST --------------------------------------------------

    def test_delete_entry(self) -> None:
        """Test deleting an entry entry"""

        self.table_utils.table_context_menu(self.test_entry.id, "delete")
        self.modal_utils.wait_for_delete_modal()
        self.delete_modal.confirm_button.click()
        self.delete_modal.wait_for_modal_close()
        time.sleep(0.1)
        self.table_utils.wait_for_disappear(f"table-row-{self.test_entry.id}")

        # Check that the entry was deleted from the database
        db_data = self.db.query(self.model).filter_by(id=self.test_entry.id).first()
        assert db_data is None, "Expected entry to be deleted from database"

    def test_view_delete_entry(self) -> None:
        """Test deleting an entry entry"""

        self.table_utils.table_row_click(self.test_entry.id)
        self.modal_utils.wait_for_view_modal()
        self.modal_utils.edit_button("view").click()
        self.modal_utils.wait_for_edit_modal()
        self.modal_utils.delete_button("edit").click()
        self.modal_utils.wait_for_delete_modal()
        self.delete_modal.confirm_button.click()
        self.delete_modal.wait_for_modal_close()
        time.sleep(0.1)
        self.table_utils.wait_for_disappear(f"table-row-{self.test_entry.id}")

        # Check that the entry was deleted from the database
        db_data = self.db.query(self.model).filter_by(id=self.test_entry.id).first()
        assert db_data is None, "Expected entry to be deleted from database"

    # ----------------------------------------------------- ADD TEST ---------------------------------------------------

    def test_add_valid_entry(self) -> None:
        """Test adding a new entry"""

        self.table_utils.set_page_item_select("100")

        # Determine the number of entries in the db and in the table
        n_entries = self.get_entries_count()
        initial_table_count = len(self.table_utils.table_rows)

        # Add the new entry
        self.table_utils.add_entity_button.click()
        self.modal_utils._fill_modal(**self.test_data)
        self.modal_utils.confirm_button("edit").click()
        self.modal_utils.wait_for_edit_modal_close()

        # Check that the new entry was properly added to the db and table
        n_entries_new = self.get_entries_count()
        assert n_entries_new == n_entries + 1, "Expected entry to be added to database"
        new_table_count = len(self.table_utils.table_rows)
        assert new_table_count == initial_table_count + 1, "Expected entry to be added to table"

        entries = self.db.query(self.model).all()
        entry_id = max([entry.id for entry in entries])
        entry = [entry for entry in entries if entry.id == entry_id][0]

        # Reopen the modal in view mode and check contents
        self.table_utils.table_row_click(entry_id)
        self.modal_utils.wait_for_view_modal()
        self.modal_utils.test_view_modal(entry)

        # Reopen in edit mode and check contents
        self.table_utils.table_context_menu(entry_id, "edit")
        self.modal_utils.check_edit_modal(**self.test_data)

    def test_add_duplicate_entry(self) -> None:
        """Test that adding a new entry with an existing name shows validation error"""

        if self.duplicate_fields:
            # Add the new entry
            self.table_utils.add_entity_button.click()
            self.modal_utils.wait_for_edit_modal()
            self.modal_utils._fill_modal(**self.test_data)
            self.modal_utils.confirm_button("edit").click()
            self.modal_utils.wait_for_edit_modal_close()

            # Try to add the same entry again
            self.table_utils.add_entity_button.click()
            self.modal_utils.wait_for_edit_modal()
            self.modal_utils._fill_modal(duplicate_fields=self.duplicate_fields, **self.test_data)
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
    columns = ["name", "created_at"]
    test_entry_index = 14
    model = models.Keyword


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
    columns = ["name", "url", "created_at"]
    model = models.Aggregator


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
    columns = ["name", "url", "description", "created_at"]
    model = models.Company


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
    columns = ["name", "email", "companyBadge", "phone", "role", "created_at"]
    sorting_columns = ["name", "companyBadge", "role", "email", "created_at"]
    model = models.Person

    def test_table_company_badge(self) -> None:
        """Test that the company badge is displayed correctly"""

        self.get_element("table-row-1-companyBadge").click()
        self.company_modal_utils.check_company_view_modal(self.test_entry.company)

    def test_add_company(self) -> None:
        """Test adding a new person with a new company"""

        self.table_utils.add_entity_button.click()
        self.modal_utils._fill_modal(first_name="John", last_name="Doe")
        self.get_element("add-button-company").click()
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
    columns = ["jobBadge", "date", "note", "created_at"]
    test_data = {
        "date": dt.datetime(year=2025, month=3, day=5, hour=3, minute=30, tzinfo=dt.timezone.utc),
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
    columns = ["jobBadge", "type", "date", "created_at"]
    test_data = {
        "date": dt.datetime(year=2025, month=3, day=5, hour=3, minute=30, tzinfo=dt.timezone.utc),
        "job_id": "Senior Python Developer (Tech Corp)",
        "note": "Received automated confirmation email",
        "attendance_type": "On-site",
        "type": "HR",
    }
    model = models.Interview

    def test_table_interviewers_badge(self) -> None:
        """Test that the person badge is displayed correctly in the table"""

        self.get_element("table-row-1-interviewerBadges-0").click()
        self.person_modal_utils.check_person_view_modal(self.test_entry.interviewers[0])

    def test_modal_interviewers_badge(self) -> None:
        """Test that the person badge is displayed correctly in the modal"""

        self.table_utils.table_row_click(self.test_entry.id)
        self.modal_utils.wait_for_view_modal()
        self.get_element("modal-view-interview-person-0").click()
        self.person_modal_utils.check_person_view_modal(self.test_entry.interviewers[0])


class TestJobPage(BaseTablePage):
    """Test class for Job Application Update Page functionalities"""

    endpoint = "jobs"
    page_url = "jobs"
    entry_type = "job"
    test_fixture = ["test_jobs"]
    required_fields = ["title"]
    columns = ["title", "company", "location", "created_at"]
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
            "application_date": dt.datetime.now(),
            "application_url": "https://techcorp.com/apply/senior-python",
            "application_status": "Applied",
            "applied_via": "Aggregator",
            "application_note": "Submitted application with cover letter",
        },
    }
    duplicate_fields = ["url"]
    model = models.Job

    def test_add_interview(self) -> None:
        """Test adding an interview through the job view modal"""

        interview_data = dict(
            date=dt.datetime(year=2025, month=4, day=10, hour=10, minute=0, tzinfo=dt.timezone.utc),
            type="HR",
            attendance_type="On-site",
            note="Initial HR screening interview",
        )

        self.table_utils.table_row_click(self.test_entry.id)
        self.modal_utils.wait_for_view_modal()
        self.get_element("application-tab").click()
        interview_count = len(self.interview_table_utils.table_rows)
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
            type="Technical",
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
            date=dt.datetime(year=2025, month=4, day=15, hour=14, minute=0, tzinfo=dt.timezone.utc),
            type="Received",
            note="Scheduled first round interview",
        )

        self.table_utils.table_row_click(self.test_entry.id)
        self.modal_utils.wait_for_view_modal()
        self.get_element("application-tab").click()
        update_count = len(self.jobApplicationUpdate_table_utils.table_rows)
        self.jobApplicationUpdate_table_utils.add_entity_button.click()
        self.jobApplicationUpdate_modal_utils._fill_modal(**update_data)
        self.jobApplicationUpdate_modal_utils.confirm_button("edit").click()
        self.jobApplicationUpdate_modal_utils.wait_for_edit_modal_close()
        assert len(self.jobApplicationUpdate_table_utils.table_rows) == update_count + 1
        self.jobApplicationUpdate_table_utils.table_rows[0].click()
        update_id = self.jobApplicationUpdate_table_utils.get_row_id(0)
        update = self.db.query(models.JobApplicationUpdate).filter(models.JobApplicationUpdate.id == update_id).first()
        self.jobApplicationUpdate_modal_utils.check_update_view_modal(update, False)

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
        update_id = self.jobApplicationUpdate_table_utils.get_row_id(0)
        self.jobApplicationUpdate_table_utils.table_rows[0].click()

        # Switch to edit mode and modify the update
        self.jobApplicationUpdate_modal_utils.edit_button("view").click()
        self.jobApplicationUpdate_modal_utils._fill_modal(**update_data)
        self.jobApplicationUpdate_modal_utils.confirm_button("edit").click()
        self.jobApplicationUpdate_modal_utils.wait_for_edit_modal_close()

        # Check the db entry to ensure the modifications were saved
        self.db.expire_all()
        update = self.db.query(models.JobApplicationUpdate).filter(models.JobApplicationUpdate.id == update_id).first()
        assert update.type == "sent"
        assert update.note == update_data["note"]

        # Verify the update view modal displays the updated information
        self.jobApplicationUpdate_modal_utils.check_update_view_modal(update, False)


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


class TestSettingsPage(BaseTablePage):
    """Test class for Job Application Update Page functionalities"""

    endpoint = "settings"
    page_url = "app/settings"
    test_fixture = "test_settings"
    entry_type = "setting"
    required_fields = ["name", "value"]
    test_data = {"name": "test_name", "value": "test_value"}
    duplicate_fields = ["name"]
    model = models.Setting
    user_index = ADMIN_USER_INDEX
