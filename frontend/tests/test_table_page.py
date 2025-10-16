"""Test the main pages of JAM"""

import datetime
import time

from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.select import Select

from conftest import contiguous_subdicts, models, BaseTest
from react_select import ReactSelect


class TablePage(BaseTest):
    """Base class for testing pages"""

    test_entries = None
    test_entry = None
    user_index = 0

    # Parameters needed
    endpoint = ""  # endpoint of the table, used to query the data
    entry_name = ""  # name of the table entries (e.g. aggregator)
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

        if isinstance(self.test_fixture, str):
            self.test_fixture = [self.test_fixture]
        self.test_entries, *self.add_test_entries = [request.getfixturevalue(fixture) for fixture in self.test_fixture]
        self.test_entries = [entry for entry in self.test_entries if entry.owner_id == self.user.id]
        self.test_entry = self.test_entries[self.test_entry_index]
        if not self.sorting_columns:
            self.sorting_columns = self.columns
        self.login()

    # ----------------------------------------------------- MODALS -----------------------------------------------------

    def _wait_for_modal_close(self, name: str) -> None:
        """Wait for the modal to close"""

        self.wait.until(ec.invisibility_of_element_located((By.ID, name)))

    def wait_for_view_modal_close(self, entry_name: str = "") -> None:
        """Wait for the view modal to close"""

        if not entry_name:
            entry_name = self.entry_name
        self._wait_for_modal_close(f"modal-view-{entry_name}")

    def wait_for_edit_modal_close(self, entry_name: str = "") -> None:
        """Wait for the view modal to close"""

        if not entry_name:
            entry_name = self.entry_name
        try:
            self._wait_for_modal_close(f"modal-edit-{entry_name}")
        except:
            raise AssertionError(f"Element in present in: {self.get_all_element_ids()}")

    def wait_for_delete_modal_close(self) -> None:
        """Wait for the delete modal to close"""

        self._wait_for_modal_close("delete-alert-modal")

    def wait_for_view_modal(self, entry_name: str = "") -> WebElement:
        """Wait for the view modal to appear"""

        if not entry_name:
            entry_name = self.entry_name
        return self.get_element(f"modal-view-{entry_name}")

    def wait_for_edit_modal(self, entry_name: str = "") -> WebElement:
        """Wait for the edit modal to appear"""

        if not entry_name:
            entry_name = self.entry_name
        return self.get_element(f"modal-edit-{entry_name}")

    def wait_for_delete_modal(self) -> WebElement:
        """Wait for the delete modal to appear"""

        return self.get_element("delete-alert-modal")

    # ----------------------------------------------------- TABLES -----------------------------------------------------

    @property
    def table_rows(self) -> list[WebElement]:
        """Get all table rows on the page"""

        self.get_element("table-row-clickable", By.CLASS_NAME)
        return self.driver.find_elements(By.CLASS_NAME, "table-row-clickable")

    def table_row(self, item_id: int, *args, **kwargs) -> WebElement:
        """Get a specific table row by its ID"""

        return self.get_element(f"table-row-{item_id}", *args, **kwargs)

    def context_menu(self, entity_id: int, choice: str) -> None:
        """Row context menu"""

        actions = ActionChains(self.driver)
        actions.context_click(self.table_row(entity_id)).perform()
        self.get_element(f"context-menu-{choice}").click()

    def check_row_exist(self, column: str, name: str, expected_count: int = 1) -> None:
        """Check that a specific row with a specific name exists in the table
        :param column: Name of the column to check
        :param name: Name of the column
        :param expected_count: Expected number of rows with that name"""

        assert (
            self.get_column_values(column).count(name) == expected_count
        ), f"Expected {expected_count} rows with name '{name}'"

    def get_column_values(self, column_key: str | None = None) -> list[str] | list[dict[str, str]]:
        """Get values from a specific table column via the column key
        (matched using id attributes starting with 'table-header-').
        :param column_key: The key of the column. If None, returns all rows as list of dicts.
        :return: List of values from that column, or list of row dicts if no key provided.
        """
        # Find all elements where id starts with 'table-header-'
        header_elements = self.driver.find_elements(By.XPATH, "//*[@id[starts-with(., 'table-header-')]]")
        header_keys = []
        for header in header_elements:
            th_id = header.get_attribute("id")
            # Ensure only ids with "table-header-" are considered
            if th_id and th_id.startswith("table-header-"):
                header_keys.append(th_id[len("table-header-") :])

        # If no column_key provided, return all rows as list of dicts
        if column_key is None:
            rows_data = []
            for row in self.table_rows:
                row_dict = {}
                cells = row.find_elements(By.TAG_NAME, "td")
                for i, key in enumerate(header_keys):
                    if i < len(cells):
                        row_dict[key] = cells[i].text
                rows_data.append(row_dict)
            return rows_data

        if column_key not in header_keys:
            raise ValueError(f"Column key '{column_key}' not found. Available keys: {header_keys}")

        column_index = header_keys.index(column_key)
        return [row.find_elements(By.TAG_NAME, "td")[column_index].text for row in self.table_rows]

    # ----------------------------------------------------- BUTTONS ----------------------------------------------------

    @property
    def add_entity_button(self) -> WebElement:
        """Get the Add Entity button"""

        return self.get_element("add-entity-button")

    @property
    def delete_confirm_button(self) -> WebElement:
        """Get the delete confirm button on the modal"""

        return self.get_element("delete-alert-modal-confirm-button")

    def confirm_button(self, mode: str, entry_name: str | None = None) -> WebElement:
        """Get the confirm button on the modal"""

        if not entry_name:
            entry_name = self.entry_name
        return self.get_element(f"modal-{mode}-{entry_name}-confirm-button")

    def cancel_button(self, mode: str, entry_name: str | None = None) -> WebElement:
        """Get the cancel button on the modal"""

        if not entry_name:
            entry_name = self.entry_name
        return self.get_element(f"modal-{mode}-{entry_name}-cancel-button")

    def edit_button(self, mode: str, entry_name: str | None = None) -> WebElement:
        """Get the edit button on the modal"""

        if not entry_name:
            entry_name = self.entry_name
        return self.get_element(f"modal-{mode}-{entry_name}-edit-button")

    def set_page_item_select(self, value) -> None:
        """Set the number of items to display per page
        :param value: Value to select (e.g. "20", "40")"""

        if len(self.table_rows) >= 20:
            Select(self.get_element("page-items-select")).select_by_value(value)

    def table_row_click(self, row_index: int) -> None:
        """Click on a table row by its index (0-based)"""

        element = self.table_row(row_index)
        self.driver.execute_script("arguments[0].click();", element)

    # ---------------------------------------------------- UTILITIES ---------------------------------------------------

    @property
    def test_name(self) -> str:
        """Get the name of the test entity"""

        return f"Test_{int(time.time())}"

    @staticmethod
    def salary_range(item: models.Job) -> str | None:
        """
        Returns a formatted salary range string based on minimum and maximum salary values.

        Parameters
        ----------
        item : dict | None
            A dictionary that may contain 'salary_min' and 'salary_max' keys.

        Returns
        -------
        str | None
            A formatted salary string such as:
            - "£30,000"
            - "£30,000 - £40,000"
            - "From £30,000"
            - "Up to £40,000"
            or None if no salary values are provided.
        """
        if not item:
            return None

        salary_min = item.salary_min
        salary_max = item.salary_max

        if not salary_min and not salary_max:
            return None

        if salary_min == salary_max and salary_min:
            return f"£{salary_min:,.0f}"

        if salary_min and salary_max:
            return f"£{salary_min:,.0f} - £{salary_max:,.0f}"

        if salary_min:
            return f"From £{salary_min:,.0f}"

        if salary_max:
            return f"Up to £{salary_max:,.0f}"

        return None

    # ----------------------------------------------- DISPLAY/VIEW TESTS -----------------------------------------------

    def test_display_entries(self) -> None:
        """Test that entries are displayed correctly"""

        # Default 20 entries display
        assert len(self.table_rows) == min([20, len(self.test_entries)]), "The table rows should match the entries"

        # Increase to 40
        self.set_page_item_select("40")
        self.wait_for_table_load()
        assert len(self.table_rows) == min([40, len(self.test_entries)]), "The table rows should match the entries"

    def _test_view_modal(self, entry=None) -> None:
        """Helper method to test the view modal for an entry"""

        raise AssertionError("Not implemented")

    def test_view_entry(self) -> None:
        """Test viewing an entry details by clicking on a table row"""

        self.table_row_click(self.test_entry.id)
        self._test_view_modal()

    def test_view_entry_right_click(self) -> None:
        """Test viewing an entry details through the right-click context menu"""

        self.context_menu(self.test_entry.id, "view")
        self._test_view_modal()

    # --------------------------------------------------- DELETE TEST --------------------------------------------------

    def test_delete_entry(self) -> None:
        """Test deleting an entry entry"""

        self.context_menu(self.test_entry.id, "delete")
        self.wait_for_delete_modal()
        self.delete_confirm_button.click()
        self.wait_for_delete_modal_close()
        time.sleep(0.1)
        self.wait_for_disappear(f"table-row-{self.test_entry.id}")
        db_data = self.client.get(f"{self.backend_url}/{self.endpoint}/?id={self.test_entry.id}").json()
        assert len(db_data) == 0, "Expected entry to be deleted from database"

    # ----------------------------------------------------- ADD TEST ---------------------------------------------------

    def _fill_modal(self, **values) -> None:
        """Fill the modal with the given values  (key: key of the input elements, value: value to set)."""

        self.wait_for_edit_modal()
        for key, value in values.items():
            if key in (
                "country",
                "company_id",
                "location_id",
                "job_id",
                "aggregator_id",
                "job_application_id",
                "type",
                "source",
                "attendance_type",
                "applied_via",
            ):
                select = ReactSelect(self.get_element(key))
                select.open_menu()
                select.select_by_visible_text(value)
            elif key in ["date", "application_date"]:
                self.get_element(key + "_set_current").click()
                # element = self.get_element(key)
                # element.send_keys(value.strftime("%d%m%Y"))
                # element.send_keys(Keys.TAB)
                # element.send_keys(value.strftime("%H%M%S"))
            else:
                self.set_text(self.get_element(key), value)

    def test_add_valid_entry(self) -> None:
        """Test adding a new entry"""

        self.set_page_item_select("100")
        # Determine the number of entries in the db and in the table
        n_entries = len(self.client.get(f"{self.backend_url}/{self.endpoint}/").json())
        initial_table_count = len(self.table_rows)

        # Add the new entry
        self.add_entity_button.click()
        self.wait_for_edit_modal()
        self._fill_modal(**self.test_data)
        self.confirm_button("edit").click()
        self.wait_for_edit_modal_close()

        # Check that the new entry was properly added to the db and table
        n_entries_new = len(self.client.get(f"{self.backend_url}/{self.endpoint}/").json())
        assert n_entries_new == n_entries + 1, "Expected entry to be added to database"
        new_table_count = len(self.table_rows)
        assert new_table_count == initial_table_count + 1, "Expected entry to be added to table"

        entries = self.db.query(self.model).all()
        entry_id = max([entry.id for entry in entries])
        entry = [entry for entry in entries if entry.id == entry_id][0]

        # Reopen the modal
        self.table_row(entry_id).click()
        self.wait_for_view_modal()
        self._test_view_modal(entry)
        try:
            self.cancel_button("view").click()
        except:
            pass
        self.wait_for_view_modal_close()

        # Reopen in edit mode
        self.context_menu(entry_id, "edit")
        for key in self.test_data:
            if "date" in key:
                continue
            element = self.get_element(key)
            if element.tag_name == "input":
                value = element.get_attribute("value")
            else:
                value = element.text
            assert str(value) == str(self.test_data[key])

    def test_add_duplicate_entry(self) -> None:
        """Test that adding a new entry with an existing name shows validation error"""

        # Add the new entry
        self.add_entity_button.click()
        self.wait_for_edit_modal()
        self._fill_modal(**self.test_data)
        self.confirm_button("edit").click()
        self.wait_for_edit_modal_close()

        self.add_entity_button.click()
        self.wait_for_edit_modal()
        self._fill_modal(**{key: self.test_data[key] for key in self.duplicate_fields})
        self.confirm_button("edit").click()
        self.get_element(".invalid-feedback", By.CSS_SELECTOR)
        self.cancel_button("edit").click()
        self.wait_for_edit_modal_close()

    def test_add_incomplete_entry(self) -> None:
        """Test that adding a new entry without all required information shows an error"""

        if len(self.required_fields) > 1:
            dictionaries = contiguous_subdicts({key: self.test_data[key] for key in self.required_fields})
        else:
            dictionaries = [dict()]

        for d in dictionaries:
            self.add_entity_button.click()
            self._fill_modal(**d)
            self.confirm_button("edit").click()
            self.get_element(".invalid-feedback", By.CSS_SELECTOR)
            self.cancel_button("edit").click()
            self.wait_for_edit_modal_close()

    def test_add_entry_cancel(self) -> None:
        """Test cancelling a new entry creation."""

        self.add_entity_button.click()
        self.wait_for_edit_modal()
        self.cancel_button("edit").click()
        self.wait_for_edit_modal_close()

    # ---------------------------------------------------- EDIT TEST ---------------------------------------------------

    def test_edit_entry_through_view_modal(self) -> None:
        """Test editing an entry through the view modal's edit button"""

        self.set_page_item_select("100")
        initial_count = len(self.table_rows)
        self.table_row_click(self.test_entry.id)
        self.wait_for_view_modal()
        self.edit_button("view").click()
        self._fill_modal(**self.test_data)
        self.confirm_button("edit").click()
        self.wait_for_edit_modal_close()
        self.cancel_button("view").click()
        assert len(self.table_rows) == initial_count, "Expected table to remain unchanged"

    def test_edit_entry_through_right_click_context_menu(self) -> None:
        """Test editing an entry through right-click context menu"""

        self.set_page_item_select("100")
        initial_count = len(self.table_rows)
        self.context_menu(self.test_entry.id, "edit")
        self._fill_modal(**self.test_data)
        self.confirm_button("edit").click()
        self.wait_for_edit_modal_close()
        assert len(self.table_rows) == initial_count, "Expected table to remain unchanged"

    def test_cancel_edit_view(self) -> None:
        """Test cancelling an entry edit opened via the view modal"""

        self.table_row_click(self.test_entry.id)
        self.wait_for_view_modal()
        self.edit_button("view").click()
        self.cancel_button("edit").click()
        self.wait_for_edit_modal_close()
        self.wait_for_view_modal()

    def test_cancel_edit(self) -> None:
        """Test cancelling an entry edit opened via the edit modal"""

        self.context_menu(self.test_entry.id, "edit")
        self.cancel_button("edit").click()
        self.wait_for_edit_modal_close()

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
            self.set_text(self.get_element("search-input"), search_text)
            time.sleep(0.2)  # Allow time for search to filter
            print("got", self.table_rows)
            assert len(self.table_rows) == len(expected_entries), "Expected search to filter results"

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

    def check_keyword_view_modal(self, entry: models.Keyword) -> None:
        """Helper method to test the view modal for a keyword entry"""

        modal = self.wait_for_view_modal("tag")

        # Verify modal contains the entry information
        expected = f"Tag Details\n{entry.name}\nJobs\n({len(entry.jobs)})\nClose\nEdit"
        assert modal.text == expected

        # Close modal
        self.cancel_button("view", "tag").click()
        self.wait_for_view_modal_close("keyword")

    def check_aggregator_view_modal(self, entry: models.Aggregator) -> None:
        """Helper method to test the view modal for an aggregator entry"""

        modal = self.wait_for_view_modal("aggregator")

        # Verify modal contains the entry information
        expected = (
            f"Aggregator Details\n{entry.name}\nWebsite\n{entry.url.replace('https://', '')}\nJobs\n({len(entry.jobs)})"
            f"\nJob Applications\n({len(entry.job_applications)})\nClose\nEdit"
        )
        assert modal.text == expected

        # Close modal
        self.cancel_button("view", "aggregator").click()
        self.wait_for_view_modal_close("aggregator")

    def check_location_view_modal(self, entry: models.Location) -> None:
        """Helper method to test the view modal for a location entry"""

        modal = self.wait_for_view_modal("location")
        self.wait.until(lambda d: "Finding location on map..." not in modal.text)

        # Verify modal contains the entry information
        expected = (
            f"Location Details\nCity\n{entry.city}\nPostcode\n{entry.postcode}"
            f"\nCountry\n{entry.country}\n"
            f"Location on Map\n+\n−\nLeaflet | © OpenStreetMap\n"
            f"Jobs\n({len(entry.jobs)})\nInterviews\n({len(entry.interviews)})\n"
            f"Close\nEdit"
        )
        assert modal.text == expected

        # Close modal
        self.cancel_button("view", "location").click()
        self.wait_for_view_modal_close("location")

    def check_company_view_modal(self, entry: models.Company) -> None:
        """Helper method to test the view modal for a company entry"""

        modal = self.wait_for_view_modal("company")

        # Verify modal contains the entry information
        expected = (
            f"Company Details\n{entry.name}\nWebsite\n{entry.url.replace("https://", "")}"
            f"\nDescription\n{entry.description}\nJobs\n({len(entry.jobs)})\nPersons\n({len(entry.persons)})\nClose\nEdit"
        )
        assert modal.text == expected

        # Close modal
        self.cancel_button("view", "company").click()
        self.wait_for_view_modal_close("company")

    def check_person_view_modal(self, entry: models.Person) -> None:
        """Helper method to test the view modal for a person entry"""

        modal = self.wait_for_view_modal("person")
        expected = (
            f"Person Details\n{entry.name}\n"
            f"Company\n{entry.company.name.upper()}\nRole\n{entry.role}\n"
            f"Email\n{entry.email}\nPhone\n{entry.phone}\nLinkedIn Profile\nProfile\n"
            f"Interviews\n({len(entry.interviews)})\nJobs\n({len(entry.jobs)})\nClose\nEdit"
        )
        assert modal.text == expected

        # Close modal
        self.cancel_button("view", "person").click()
        self.wait_for_view_modal_close("person")

    def check_interview_view_modal(self, entry: models.Interview) -> None:
        """Helper method to test the view modal for an interview entry"""

        modal = self.wait_for_view_modal("interview")
        display_time = entry.date.astimezone()
        expected = (
            "Interview Details\n"
            "Job\n"
            f"{entry.job.title.upper()}\n"
            "Date & Time\n"
            f"{display_time.strftime("%d/%m/%Y %H:%M")}\n"
            "Type\n"
            f"{entry.type}\n"
        )

        if entry.attendance_type and not entry.location:
            expected += f"Location\n{entry.attendance_type.upper()}\n"
        elif entry.location:
            expected += "Location\n" f"{entry.location.name.upper()} ({entry.attendance_type.upper()})\n"
        else:
            expected += "Location\nNot Provided\n"

        if entry.interviewers:
            expected += (
                "Interviewers\n" f"{', '.join([interviewer.name.upper() for interviewer in entry.interviewers])}\n"
            )
        else:
            expected += "Interviewers\nNot Provided\n"

        if entry.note:
            expected += f"Notes\n{entry.note}\n"
        else:
            expected += "Notes\nNot Provided\n"

        expected += "Close\nEdit"

        assert modal.text == expected

        # Close modal
        self.cancel_button("view", "interview").click()
        self.wait_for_view_modal_close("interview")

    def check_update_view_modal(self, entry: models.JobApplicationUpdate) -> None:
        """Helper method to test the view modal for a job application update entry"""

        modal = self.wait_for_view_modal("update")
        display_time = entry.date.astimezone()
        expected = (
            "Update Details\n"
            "Job\n"
            f"{entry.job.title.upper()}\n"
            "Date & Time\n"
            f"{display_time.strftime("%d/%m/%Y %H:%M")}\n"
            "Type\n"
            f"{entry.type[0].upper() + entry.type[1:]}\n"
            "Notes\n"
            f"{entry.note}\n"
            "Close\n"
            "Edit"
        )
        assert modal.text == expected

        # Close modal
        self.cancel_button("view", "update").click()
        self.wait_for_view_modal_close("update")

    def check_job_view_modal(self, entry: models.Job) -> None:
        """Helper method to test the view modal for a job application update entry"""

        modal = self.wait_for_view_modal("job")
        expected = "Job Details\nJob Details\nJob Application"
        if entry.application_status:
            expected += f" {entry.application_status.upper()}"
        expected += f"\n{entry.title}\n"
        if entry.company:
            expected += f"Company\n{entry.company.name.upper()}\n"
        else:
            expected += "Company\nNot Provided\n"
        if entry.location:
            expected += f"Location\n{entry.location.name.upper()} ({entry.attendance_type.upper()})\n"
        else:
            expected += "Location\nNot Provided\n"
        if entry.description:
            expected += f"Description\n{entry.description}\n"
        else:
            expected += "Description\nNot Provided\n"
        if entry.note:
            expected += f"Notes\n{entry.note}\n"
        else:
            expected += "Notes\nNot Provided\n"
        salary_range = self.salary_range(entry)
        if salary_range:
            expected += f"Salary Range\n{salary_range}\n"
        else:
            expected += "Salary Range\nNot Provided\n"
        expected += "Personal Rating\n"
        if not entry.personal_rating:
            expected += "Not Provided\n"
        if entry.source:
            expected += f"Source Aggregator\n{entry.source.name.upper()}\n"
        else:
            expected += "Source Aggregator\nNot Provided\n"
        if entry.url:
            expected += f"Job URL\n{entry.url.replace('https://', '')}\n"
        else:
            expected += "Job URL\nNot Provided\n"
        if entry.keywords:
            expected += f"Tags\n{'\n'.join([tag.name.upper() for tag in entry.keywords])}\n"
        else:
            expected += "Tags\nNot Provided\n"
        if entry.contacts:
            expected += f"Contacts\n{'\n'.join([person.name.upper() for person in entry.contacts])}\n"
        else:
            expected += "Contacts\nNot Provided\n"
        if entry.deadline:
            expected += f"Application Deadline\n{entry.deadline.strftime('%d/%m/%Y')}\n"
        else:
            expected += "Application Deadline\nNot Provided\n"
        expected += "Close\nEdit"
        assert modal.text == expected

        # Close modal
        self.cancel_button("view", "job").click()
        self.wait_for_view_modal_close("job")


class TestKeywordsPage(TablePage):
    """Test class for the keywords Page functionality including:
    - Displaying entries
    - Adding entries
    - Viewing entries
    - Editing entries
    - Deleting entries"""

    endpoint = "keywords"
    page_url = "keywords"
    entry_name = "tag"
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
        self.check_keyword_view_modal(entry)


class TestAggregatorsPage(TablePage):
    """Test class for Aggregators Page functionality including:
    - Displaying entries
    - Adding new entries
    - Viewing entries
    - Editing entries
    - Deleting entries"""

    endpoint = "aggregators"
    page_url = "aggregators"
    test_fixture = "test_aggregators"
    entry_name = "aggregator"
    test_data = {"name": "Test_Name", "url": "https://www.google.com"}
    required_fields = ["name", "url"]
    duplicate_fields = ["name"]
    columns = ["name", "url"]
    model = models.Aggregator

    def _test_view_modal(self, entry=None) -> None:
        """Helper method to test the view modal for an entry"""
        if not entry:
            entry = self.test_entry
        self.check_aggregator_view_modal(entry)


class TestCompaniesPage(TablePage):
    """Test class for Aggregators Page functionality including:
    - Displaying entries
    - Adding new entries
    - Viewing entries
    - Editing entries
    - Deleting entries"""

    endpoint = "companies"
    page_url = "companies"
    test_fixture = "test_companies"
    entry_name = "company"
    test_data = {"name": "Test_Name", "url": "https://www.google.com", "description": "This is a test description"}
    required_fields = ["name"]
    duplicate_fields = ["name"]
    columns = ["name", "url", "description"]
    model = models.Company

    def _test_view_modal(self, entry=None) -> None:
        """Helper method to test the view modal for an entry"""
        if not entry:
            entry = self.test_entry
        self.check_company_view_modal(entry)


class TestLocationsPage(TablePage):
    """Test class for Aggregators Page functionality including:
    - Displaying entries
    - Adding new entries
    - Viewing entries
    - Editing entries
    - Deleting entries"""

    endpoint = "locations"
    page_url = "locations"
    test_fixture = "test_locations"
    entry_name = "location"
    test_data = {"city": "Oxford", "postcode": "OX1", "country": "United Kingdom"}
    required_fields = []
    columns = ["city", "postcode", "country"]
    model = models.Location

    def _test_view_modal(self, entry=None) -> None:
        """Helper method to test the view modal for an entry"""
        if not entry:
            entry = self.test_entry
        self.check_location_view_modal(entry)


class TestPersonsPage(TablePage):
    """Test class for Aggregators Page functionality including:
    - Displaying entries
    - Adding new entries
    - Viewing entries
    - Editing entries
    - Deleting entries"""

    endpoint = "persons"
    page_url = "persons"
    test_fixture = ["test_persons", "test_companies"]
    entry_name = "person"
    test_data = {
        "first_name": "Test_firstname",
        "last_name": "Test_lastname",
        "email": "Test_email@test.com",
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
        self.check_person_view_modal(entry)

    def test_table_company_badge(self) -> None:
        """Test that the company badge is displayed correctly"""

        self.get_element("table-row-1-CompanyBadge").click()
        self.check_company_view_modal(self.test_entry.company)

    def test_add_company(self) -> None:
        """Test adding a new person with a new company"""

        self.add_entity_button.click()
        self._fill_modal(first_name="John", last_name="Doe")
        self.get_element("add-button").click()
        self._fill_modal(name="Company")
        self.get_element("modal-edit-company-confirm-button").click()
        self.wait_for_edit_modal()
        assert self.get_element("first_name").get_attribute("value") == "John"
        assert self.get_element("last_name").get_attribute("value") == "Doe"


class TestJobApplicationUpdatesPage(TablePage):
    """Test class for Job Application Update Page functionalities"""

    endpoint = "jobapplicationupdates"
    page_url = "jobapplicationupdates"
    test_fixture = ["test_job_application_updates", "test_jobs"]
    entry_name = "update"
    required_fields = ["job_id", "type", "date"]
    test_data = {
        "date": datetime.datetime(year=2025, month=3, day=5, hour=3, minute=30, tzinfo=datetime.timezone.utc),
        "job_id": "Senior Python Developer - Tech Corp",
        "note": "Received automated confirmation email",
        "type": "Received",
    }
    model = models.JobApplicationUpdate

    def _test_view_modal(self, entry=None) -> None:
        """Helper method to test the view modal for an entry"""
        if not entry:
            entry = self.test_entry
        self.check_update_view_modal(entry)


class TestInterviewPage(TablePage):
    """Test class for Job Application Update Page functionalities"""

    endpoint = "interviews"
    page_url = "interviews"
    test_fixture = ["test_interviews", "test_jobs"]
    entry_name = "interview"
    required_fields = ["job_id", "type", "date"]
    test_data = {
        "date": datetime.datetime(year=2025, month=3, day=5, hour=3, minute=30, tzinfo=datetime.timezone.utc),
        "job_id": "Senior Python Developer - Tech Corp",
        "note": "Received automated confirmation email",
        "attendance_type": "On-site",
        "type": "HR Interview",
    }
    model = models.Interview

    def _test_view_modal(self, entry=None) -> None:
        """Helper method to test the view modal for an entry"""
        if not entry:
            entry = self.test_entry
        self.check_interview_view_modal(entry)

    def test_table_interviewers_badge(self) -> None:
        """Test that the person badge is displayed correctly in the table"""

        self.get_element("table-row-1-person-0").click()
        self.check_person_view_modal(self.test_entry.interviewers[0])

    def test_modal_interviewers_badge(self) -> None:
        """Test that the person badge is displayed correctly in the modal"""

        self.table_row(self.test_entry.id).click()
        self.wait_for_view_modal()
        self.get_element("modal-view-interview-person-0").click()
        self.check_person_view_modal(self.test_entry.interviewers[0])

    def test_table_location_badge_table(self) -> None:
        """Test that the location badge is displayed correctly in the table"""

        self.get_element("table-row-1-location").click()
        self.check_location_view_modal(self.test_entry.location)

    def test_modal_location_badge(self) -> None:
        """Test that the location badge is displayed correctly in the modal"""

        self.table_row(self.test_entry.id).click()
        self.wait_for_view_modal()
        self.get_element("modal-view-interview-location").click()
        self.check_location_view_modal(self.test_entry.location)

    # TODO add job view


class TestJobPage(TablePage):
    """Test class for Job Application Update Page functionalities"""

    endpoint = "jobs"
    page_url = "jobs"
    test_fixture = ["test_jobs"]
    entry_name = "job"
    required_fields = ["title"]
    test_data = {
        "title": "Senior Python Developer",
        "salary_min": 80000,
        "salary_max": 130000,
        "description": "Lead backend development using Python and modern frameworks. Work with a talented team to build scalable web applications.",
        "url": "https://techcorp.com/jobs/senior_python_developer1",
        "company_id": "Oxford PV",
        "note": "Excellent opportunity for senior developer",
        # "attendance_type": "Hybrid",
        # "location_id": "Oxford, OX1 3PH, United Kingdom",
        # "application_date": datetime.datetime.now(),
        # "application_url": "https://techcorp.com/apply/senior-python",
        # "application_status": "applied",
        # "applied_via": "aggregator",
        # "application_note": "Submitted application with cover letter",
    }
    model = models.Job

    def _test_view_modal(self, entry=None) -> None:
        """Helper method to test the view modal for an entry"""
        if not entry:
            entry = self.test_entry
        self.check_job_view_modal(entry)
