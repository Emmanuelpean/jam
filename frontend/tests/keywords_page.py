import platform
import time
from datetime import datetime
from typing import Generator

import pytest
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait

from react_select import ReactSelect
from conftest import contiguous_subdicts, contiguous_subdicts_with_required


class TestPage:
    """Base class for testING pages"""

    driver = None
    wait = None
    base_url = ""
    test_entries = None
    test_entry = None

    # Parameters needed
    endpoint = ""
    entry_name = ""
    page_url = ""
    test_fixture = ""
    test_data = {}
    required_fields = []
    duplicate_fields = []
    columns = []

    @pytest.fixture(autouse=True)
    def setup_method(self, frontend_base_url, request, api_base_url, authorised_clients) -> Generator[None, None, None]:
        """Set up the test environment before each test with test data"""
        try:
            # Configure Chrome options to disable password prompts
            chrome_options = Options()
            prefs = {
                "profile.password_manager_leak_detection": False,
                "credentials_enable_service": False,
                "password_manager_enabled": False,
                "profile.password_manager_enabled": False,
            }
            chrome_options.add_experimental_option("prefs", prefs)

            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.maximize_window()
            self.wait = WebDriverWait(self.driver, 5)
            self.base_url = frontend_base_url
            if isinstance(self.test_fixture, str):
                self.test_fixture = [self.test_fixture]
            self.test_entries, *self.add_test_entries = [
                request.getfixturevalue(fixture) for fixture in self.test_fixture
            ]
            self.test_entry = self.test_entries[0]
            self.client = authorised_clients[0]
            self.backend_url = api_base_url

            # Login and navigate to the page page
            self.login()
            self.driver.get(f"{self.base_url}/{self.page_url}")
            self.wait_for_table_load()

        except Exception:
            if hasattr(self, "driver"):
                try:
                    self.driver.quit()
                except:
                    pass
            raise

        yield  # This allows the test to run

        # Teardown
        try:
            if hasattr(self, "driver"):
                self.driver.quit()
        except Exception as e:
            print(f"Error during teardown: {e}")

    def login(self) -> None:
        """Helper method to login to the application"""

        login_url = f"{self.base_url}/login"
        self.driver.get(login_url)
        self.get_element("email").send_keys("test_user@test.com")
        self.get_element("password").send_keys("test_password")
        self.get_element("log-button").click()
        self.wait.until(ec.url_contains("/dashboard"))

    # ------------------------------------------------ GET/WAIT ELEMENTS -----------------------------------------------

    def wait_for_table_load(self, timeout: int | float = 0.1) -> None:
        """Wait for loading spinner to disappear"""

        try:
            WebDriverWait(self.driver, timeout).until(
                ec.invisibility_of_element_located((By.CSS_SELECTOR, ".spinner-border"))
            )
        except TimeoutException:
            pass

    def get_all_element_ids(self) -> list[str]:
        """Get all element IDs present on the current page"""

        # Find all elements that have an ID attribute
        elements_with_id = self.driver.find_elements(By.XPATH, "//*[@id]")

        # Extract the ID values
        element_ids = []
        for element in elements_with_id:
            element_id = element.get_attribute("id")
            if element_id:
                element_ids.append(element_id)

        return sorted(element_ids)

    def get_element(
        self,
        element_id: str,
        selector: str = By.ID,
    ) -> WebElement:
        """Get an element by its ID
        :param element_id: ID of the element to get
        :param selector: Selector to use for finding the element"""

        try:
            return self.wait.until(ec.element_to_be_clickable((selector, element_id)))
        except:
            raise AssertionError(f"Could not find element {element_id}\nPossible IDs: {self.get_all_element_ids()}")

    def wait_for_disappear(
        self,
        element_id: str,
        selector: str = By.ID,
    ) -> None:
        """Wait for an element to disappear from the DOM
        :param element_id: ID of the element to get
        :param selector: Selector to use for finding the element"""

        try:
            self.wait.until(ec.invisibility_of_element_located((selector, element_id)))
        except TimeoutException:
            raise AssertionError(f"Element {element_id} did not disappear")

    # ----------------------------------------------------- MODALS -----------------------------------------------------

    def _wait_for_modal_close(self, name: str) -> None:
        """Wait for the modal to close"""

        self.wait.until(ec.invisibility_of_element_located((By.ID, name)))

    def wait_for_view_modal_close(self) -> None:
        """Wait for the view modal to close"""

        self._wait_for_modal_close(f"modal-formview-view-{self.entry_name}")

    def wait_for_edit_modal_close(self) -> None:
        """Wait for the view modal to close"""

        self._wait_for_modal_close(f"modal-formview-edit-{self.entry_name}")

    def wait_for_delete_modal_close(self) -> None:
        """Wait for the delete modal to close"""

        self._wait_for_modal_close("modal-confirmation")

    def wait_for_view_modal(self) -> WebElement:
        """Wait for the view modal to appear"""

        return self.get_element(f"modal-formview-view-{self.entry_name}")

    def wait_for_edit_modal(self) -> WebElement:
        """Wait for the edit modal to appear"""

        return self.get_element(f"modal-formview-edit-{self.entry_name}")

    def wait_for_delete_modal(self) -> WebElement:
        """Wait for the delete modal to appear"""

        return self.get_element("modal-confirmation")

    # ----------------------------------------------------- TABLES -----------------------------------------------------

    @property
    def table_rows(self) -> list[WebElement]:
        """Get all table rows on the page"""

        return self.driver.find_elements(By.CLASS_NAME, "table-row-clickable")

    def table_row(self, item_id: int, *args, **kwargs) -> WebElement:
        """Get a specific table row by its ID"""

        return self.get_element(f"table-row-{item_id}", *args, **kwargs)

    def context_menu(self, entity_id: int, choice: str) -> None:
        """Row context menu"""

        actions = ActionChains(self.driver)
        actions.context_click(self.table_row(entity_id)).perform()
        self.get_element(f"context-menu-{choice}").click()

    def check_rows(self, column: str, name: str, expected_count: int = 1) -> None:
        """Check that a specific row with a specific name exists in the table
        :param column: Name of the column to check
        :param name: Name of the column
        :param expected_count: Expected number of rows with that name"""

        assert (
            self.get_column_values(column).count(name) == expected_count
        ), f"Expected {expected_count} rows with name '{name}'"

    def get_column_values(self, column_key: str = None) -> list[str] | list[dict[str, str]]:
        """
        Get values from a specific table column via the column key
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
    def confirm_button(self) -> WebElement:
        """Get the confirm button on the modal"""

        return self.get_element("confirm-button")

    @property
    def cancel_button(self) -> WebElement:
        """Get the cancel button on the modal"""

        return self.get_element("cancel-button")

    @property
    def edit_button(self) -> WebElement:
        """Get the edit button on the modal"""

        return self.get_element("edit-button")

    # ---------------------------------------------------- UTILITIES ---------------------------------------------------

    @staticmethod
    def clear(element: WebElement, text: str = "") -> None:
        """Clears the input element"""

        modifier_key = Keys.COMMAND if platform.system() == "Darwin" else Keys.CONTROL
        element.send_keys(modifier_key, "a")
        element.send_keys(Keys.DELETE)
        element.send_keys(text)

    @property
    def test_name(self) -> str:
        """Get the name of the test entity"""

        return f"Test_{int(time.time())}"

    # ----------------------------------------------- DISPLAY/VIEW TESTS -----------------------------------------------

    def test_display_entries(self) -> None:
        """Test that entries are displayed correctly"""

        # Default 20 entries display
        entries = [entry for entry in self.test_entries if entry.owner_id == 1]
        assert len(self.table_rows) == min([20, len(entries)]), "The table rows should match the entries"

        # Increase to 40
        Select(self.get_element("page-items-select")).select_by_value("40")
        self.wait_for_table_load()
        entries = [entry for entry in self.test_entries if entry.owner_id == 1]
        assert len(self.table_rows) == min([40, len(entries)]), "The table rows should match the entries"

    def _test_sort_functionality(self, key: str, display_function=None) -> None:
        """Test sorting functionality
        :param key: The key of the column to sort by."""

        if key == "url":
            display_function = lambda x: x.replace("https://", "").replace("http://", "") if x else x
        else:
            display_function = lambda x: x
        if display_function is None:
            display_function = lambda x: x

        def convert(entity) -> str | None:
            """Converts an attribute value of an entity using a display function."""
            value = getattr(entity, key, None)
            return display_function(value) if value is not None else ""

        # Click to sort and give time for UI update
        self.get_element(f"table-header-{key}").click()
        time.sleep(0.2)

        # Prepare sorted, displayable, lowercased values (non-empty first)
        converted = [convert(entity) for entity in self.test_entries]
        expected = sorted((v for v in converted if v), key=lambda x: x.lower())

        # Pad 'Not Provided' for entries with empty values
        missing_count = len(converted) - len(expected)
        expected.extend(["Not Provided"] * missing_count)

        # Fetch table column values and compare
        values = self.get_column_values(key)
        assert values == expected[:20], "Expected sorted results"

    def _test_search_functionality(self, text: str, *keys) -> None:
        """Test the search functionality"""

        entries = []
        for key in keys:
            entries += [entry for entry in self.test_entries if text.lower() in (getattr(entry, key, "") or "").lower()]
        entries = set(entries)
        print("expected", entries)
        self.clear(self.get_element("search-input"), text)
        time.sleep(10.2)  # Allow time for search to filter
        print("got", self.table_rows)
        assert len(self.table_rows) == len(entries), "Expected search to filter results"

    def _test_view_modal(self) -> None:
        """Helper method to test the view modal for an entry"""

        pass

    def test_view_entry(self) -> None:
        """Test viewing an entry details by clicking on a table row"""

        self.table_row(self.test_entry.id).click()
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
        self.confirm_button.click()
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
            if key == "country":
                select = ReactSelect(self.get_element("country"))
                select.open_menu()
                select.select_by_visible_text("United Kingdom")
            else:
                self.clear(self.get_element(key), value)

    def test_add_valid_entry(self) -> None:
        """Test adding a new entry"""

        values = contiguous_subdicts_with_required(self.test_data, self.required_fields)
        n_entries = len(self.client.get(f"{self.backend_url}/{self.endpoint}/").json())
        for d in values:
            new_d = {
                key: (value + str(time.time()) if key in self.duplicate_fields else value) for key, value in d.items()
            }
            keys = list(new_d.keys())
            initial_count = self.get_column_values(keys[0]).count(new_d[keys[0]])
            self.add_entity_button.click()
            self.wait_for_edit_modal()
            self._fill_modal(**new_d)
            self.confirm_button.click()
            self.wait_for_edit_modal_close()
            self.check_rows(keys[0], new_d[keys[0]], initial_count + 1)
            n_entries_new = len(self.client.get(f"{self.backend_url}/{self.endpoint}/").json())
            assert n_entries_new == n_entries + 1, "Expected entry to be added to database"
            n_entries += 1

    def test_add_duplicate_entry(self) -> None:
        """Test that adding a new entry with an existing name shows validation error"""

        self.add_entity_button.click()
        self.wait_for_edit_modal()
        self._fill_modal(**{key: getattr(self.test_entry, key) for key in self.duplicate_fields})
        self.confirm_button.click()
        self.get_element(".invalid-feedback", By.CSS_SELECTOR)
        self.cancel_button.click()
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
            self.confirm_button.click()
            self.get_element(".invalid-feedback", By.CSS_SELECTOR)
            self.cancel_button.click()
            self.wait_for_edit_modal_close()

    # ---------------------------------------------------- EDIT TEST ---------------------------------------------------

    def test_edit_entry_through_view_modal(self) -> None:
        """Test editing an entry through the view modal's edit button"""

        keys = list(self.test_data.keys())
        initial_count = self.get_column_values(keys[0]).count(self.test_data[keys[0]])
        self.table_row(self.test_entry.id).click()
        self.wait_for_view_modal()
        self.edit_button.click()
        self._fill_modal(**self.test_data)
        self.confirm_button.click()
        self.wait_for_edit_modal_close()
        self.cancel_button.click()
        self.check_rows(keys[0], self.test_data[keys[0]], initial_count + 1)

    def test_edit_entry_through_right_click_context_menu(self) -> None:
        """Test editing an entry through right-click context menu"""

        keys = list(self.test_data.keys())
        initial_count = self.get_column_values(keys[0]).count(self.test_data[keys[0]])
        self.context_menu(self.test_entry.id, "edit")
        self._fill_modal(**self.test_data)
        self.confirm_button.click()
        self.wait_for_edit_modal_close()
        self.check_rows(keys[0], self.test_data[keys[0]], initial_count + 1)

    def test_search_functionality(self) -> None:
        """Test the search functionality"""

        for column in self.columns:
            self._test_search_functionality(getattr(self.test_entry, column)[3:], column)

    def test_sort_functionality(self) -> None:
        """Test sorting functionality"""

        for column in self.columns:
            self._test_sort_functionality(column)


class TestKeywordsPage(TestPage):
    """Test class for the keywords Page functionality including:
    - Displaying entries
    - Adding entries
    - Viewing entries
    - Editing entries
    - Deleting entries"""

    endpoint = "keywords"
    page_url = "keywords"
    entry_name = "keyword"
    test_fixture = "test_keywords"
    test_data = {"name": "Test_Name"}
    required_fields = ["name"]
    duplicate_fields = ["name"]

    def _test_view_modal(self) -> None:
        """Helper method to test the view modal for an entry"""

        modal = self.wait_for_view_modal()

        # Verify modal contains the entry information
        date = datetime.strftime(self.test_entry.created_at, "%d/%m/%Y")
        expected = (
            f"Keyword Details\nName\n{self.test_entry.name}\nDate Added\n{date}\nModified On\n{date}\nClose\nEdit"
        )
        assert modal.text == expected

        # Close modal
        self.cancel_button.click()
        self.wait_for_view_modal_close()


class TestAggregatorsPage(TestPage):
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

    def _test_view_modal(self) -> None:
        """Helper method to test the view modal for an entry"""

        modal = self.wait_for_view_modal()

        # Verify modal contains the entry information
        date = datetime.strftime(self.test_entry.created_at, "%d/%m/%Y")
        expected = f"Aggregator Details\nName\n{self.test_entry.name}\nWebsite\n{self.test_entry.url.replace("https://", "")}\nDate Added\n{date}\nModified On\n{date}\nClose\nEdit"
        assert modal.text == expected

        # Close modal
        self.cancel_button.click()
        self.wait_for_view_modal_close()


class TestCompaniesPage(TestPage):
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

    def _test_view_modal(self) -> None:
        """Helper method to test the view modal for an entry"""

        modal = self.wait_for_view_modal()

        # Verify modal contains the entry information
        date = datetime.strftime(self.test_entry.created_at, "%d/%m/%Y")
        expected = (
            f"Company Details\nName\n{self.test_entry.name}\nWebsite\n{self.test_entry.url.replace("https://", "")}"
            f"\nDescription\n{self.test_entry.description}\nDate Added\n{date}\nModified On\n{date}\nClose\nEdit"
        )
        assert modal.text == expected

        # Close modal
        self.cancel_button.click()
        self.wait_for_view_modal_close()


class TestLocationsPage(TestPage):
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
    test_data = {"city": "Test_City", "postcode": "OX", "country": "United Kingdom"}
    required_fields = []
    columns = ["city", "postcode", "country"]

    def _test_view_modal(self) -> None:
        """Helper method to test the view modal for an entry"""

        modal = self.wait_for_view_modal()

        self.wait.until(lambda d: "location shown" in modal.text, message="Waiting for map data to load in modal")

        # Verify modal contains the entry information
        date = datetime.strftime(self.test_entry.created_at, "%d/%m/%Y")
        expected = (
            f"Location Details\nCity\n{self.test_entry.city}\nPostcode\n{self.test_entry.postcode}"
            f"\nCountry\n{self.test_entry.country}\n"
            f"📍 Location on Map\n+\n−\nLeaflet | © OpenStreetMap contributors © CARTO\n"
            f"📍 1 of 1 location shown\nDate Added\n{date}\nModified On\n{date}\nClose\nEdit"
        )
        assert modal.text == expected

        # Close modal
        self.cancel_button.click()
        self.wait_for_view_modal_close()


class TestPersonsPage(TestPage):
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
        "company": "WebSolutions Ltd",
        "phone": "000000000",
        "linkedin_url": "https://www.linkedin.com/company/websolutions-ltd/",
        "role": "Test_role",
    }
    required_fields = ["first_name", "last_name"]
    duplicate_fields = []

    def _test_view_modal(self) -> None:
        """Helper method to test the view modal for an entry"""

        modal = self.wait_for_view_modal()

        # Verify modal contains the entry information
        date = datetime.strftime(self.test_entry.created_at, "%d/%m/%Y")
        expected = (
            f"Person Details\n"
            f"Full Name\n{self.test_entry.name}\nLinkedIn Profile\nProfile\n"
            f"Company\n{self.test_entry.company.name}\nRole\n{self.test_entry.role}\n"
            f"Email\n{self.test_entry.email}\nPhone\n{self.test_entry.phone}\n"
            f"Date Added\n{date}\nModified On\n{date}\nClose\nEdit"
        )
        assert modal.text == expected

        # Close modal
        self.cancel_button.click()
        self.wait_for_view_modal_close()
