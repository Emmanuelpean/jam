import platform
import time
from datetime import datetime

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
from selenium.webdriver.support.ui import WebDriverWait


class TestPage:
    """Base class for testING pages"""

    driver = None
    wait = None
    base_url = ""
    test_entries = None
    test_entry = None

    # Parameters needed
    entry_name = ""
    page_url = ""
    test_fixture = ""

    @pytest.fixture(autouse=True)
    def setup_method(self, frontend_base_url, request) -> None:
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
            self.test_entries = request.getfixturevalue(self.test_fixture)
            self.test_entry = self.test_entries[0]

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

    def wait_for_table_load(self, timeout: int | float = 5) -> None:
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
        selector: By = By.ID,
        etype: str | None = None,
    ) -> WebElement | Select:
        """Get an element by its ID
        :param element_id: ID of the element to get
        :param selector: Selector to use for finding the element
        :param etype: Type of element to return. If None, returns the WebElement. If "select", returns the Select object.
        """

        try:
            element = self.wait.until(ec.element_to_be_clickable((selector, element_id)))
            if etype is None:
                return element
            elif etype == "select":
                return Select(element)
        except:
            raise AssertionError(f"Could not find element {element_id}\nPossible IDs: {self.get_all_element_ids()}")

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

    def get_column_values(self, column_key: str) -> list[str]:
        """
        Get values from a specific table column via the column key
        (matched using id attributes starting with 'table-header-').
        :param column_key: The key of the column.
        :return: List of values from that column.
        """
        # Find all elements where id starts with 'table-header-'
        header_elements = self.driver.find_elements(By.XPATH, "//*[@id[starts-with(., 'table-header-')]]")
        header_keys = []
        for header in header_elements:
            th_id = header.get_attribute("id")
            # Ensure only ids with "table-header-" are considered
            if th_id and th_id.startswith("table-header-"):
                header_keys.append(th_id[len("table-header-") :])

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

    def test_display_entries(self) -> None:
        """Test that entries are displayed correctly"""

        # Default 20 entries display
        entries = [entry for entry in self.test_entries if entry.owner_id == 1]
        assert len(self.table_rows) == min([20, len(entries)]), "The table rows should match the entries"

        # Increase to 40
        self.get_element("page-items-select", etype="select").select_by_value("40")
        self.wait_for_table_load()
        entries = [entry for entry in self.test_entries if entry.owner_id == 1]
        assert len(self.table_rows) == min([40, len(entries)]), "The table rows should match the entries"

    def _test_sort_functionality(self, key: str, display_function=None) -> None:
        """Test sorting functionality
        :param key: The key of the column to sort by."""

        if display_function is None:
            display_function = lambda x: x

        self.get_element(f"table-header-{key}").click()
        time.sleep(0.2)
        expected = sorted(
            [display_function(getattr(entity, key)) for entity in self.test_entries], key=lambda x: x.lower()
        )[:20]
        values = self.get_column_values(key)
        assert values == expected, "Expected sorted results"

    def _test_search_functionality(self, key: str, text: str) -> None:
        """Test the search functionality"""

        n = len([f for f in self.test_entries if text in getattr(f, key)])
        self.clear(self.get_element("search-input"), text)
        time.sleep(1)  # Allow time for search to filter
        assert len(self.table_rows) == n, "Expected search to filter results"


class TestKeywordsPage(TestPage):
    """Test class for the keywords Page functionality including:
    - Displaying entries
    - Adding entries
    - Viewing entries
    - Editing entries
    - Deleting entries"""

    page_url = "keywords"
    entry_name = "keyword"
    test_fixture = "test_keywords"

    def test_add_entry_with_valid_name(self) -> None:
        """Test adding a new entry with a valid name"""

        test_name = self.test_name
        self.add_entity_button.click()
        self.wait_for_edit_modal()
        self.get_element("name").send_keys(test_name)
        self.confirm_button.click()
        self.wait_for_edit_modal_close()
        self.check_rows("name", test_name, 1)

    def test_add_entry_without_name_shows_error(self) -> None:
        """Test that adding a new entry without a name shows validation error"""

        self.add_entity_button.click()
        self.wait_for_edit_modal()
        self.confirm_button.click()
        self.get_element(".invalid-feedback", By.CSS_SELECTOR)
        self.cancel_button.click()
        self.wait_for_edit_modal_close()

    def test_add_entry_same_name_shows_error(self) -> None:
        """Test that adding a new entry with an existing name shows validation error"""

        self.add_entity_button.click()
        self.wait_for_edit_modal()
        self.get_element("name").send_keys(self.test_entries[0].name)
        self.confirm_button.click()
        self.get_element(".invalid-feedback", By.CSS_SELECTOR)
        self.cancel_button.click()
        self.wait_for_edit_modal_close()

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

    def test_view_entry(self) -> None:
        """Test viewing an entry details by clicking on a table row"""

        self.table_row(self.test_entry.id).click()
        self._test_view_modal()

    def test_view_entry_right_click(self) -> None:
        """Test viewing an entry details through the right-click context menu"""

        self.context_menu(self.test_entry.id, "view")
        self._test_view_modal()

    def test_edit_entry_through_view_modal(self) -> None:
        """Test editing an entry through the view modal's edit button"""

        original_name = self.test_entry.name
        new_name = self.test_name
        self.table_row(self.test_entry.id).click()
        self.wait_for_view_modal()
        self.edit_button.click()
        self.wait_for_edit_modal()
        self.clear(self.get_element("name"), new_name)
        self.confirm_button.click()
        self.wait_for_view_modal()
        self.cancel_button.click()
        self.wait_for_view_modal_close()
        self.check_rows("name", new_name, 1)
        self.check_rows("name", original_name, 0)

    def test_edit_entry_through_right_click_context_menu(self) -> None:
        """Test editing an entry through right-click context menu"""

        original_name = self.test_entry.name
        new_name = self.test_name
        self.context_menu(self.test_entry.id, "edit")
        self.wait_for_edit_modal()
        self.clear(self.get_element("name"), new_name)
        self.confirm_button.click()
        self.wait_for_edit_modal_close()
        self.check_rows("name", new_name, 1)
        self.check_rows("name", original_name, 0)

    def test_delete_entry(self) -> None:
        """Test deleting an entry entry"""

        self.context_menu(self.test_entry.id, "delete")
        self.wait_for_delete_modal()
        self.confirm_button.click()
        self.wait_for_delete_modal_close()
        time.sleep(0.1)
        self.check_rows("name", self.test_entry.name, 0)

    def test_search_functionality(self) -> None:
        """Test the search functionality"""

        self._test_search_functionality("name", self.test_entry.name[3:8])

    def test_sort_functionality(self) -> None:
        """Test sorting functionality"""

        self._test_sort_functionality("name")


class TestAggregatorsPage(TestPage):
    """Test class for Aggregators Page functionality including:
    - Displaying entries
    - Adding new entries
    - Viewing entries
    - Editing entries
    - Deleting entries"""

    page_url = "aggregators"
    test_fixture = "test_aggregators"
    entry_name = "aggregator"

    def test_add_valid_entry(self) -> None:
        """Test adding a new entry with a valid name"""

        name = self.test_name
        self.add_entity_button.click()
        self.wait_for_edit_modal()
        self.get_element("name").send_keys(name)
        self.get_element("url").send_keys("https://www.google.com")
        self.confirm_button.click()
        self.wait_for_edit_modal_close()
        self.check_rows("name", name, 1)

    def test_add_invalid_entry(self) -> None:
        """Test that adding an entry without the required fields shows validation error"""

        name = self.test_name
        self.add_entity_button.click()
        self.wait_for_edit_modal()

        # With none
        self.confirm_button.click()
        self.get_element(".invalid-feedback", By.CSS_SELECTOR)

        # With just the name
        self.get_element("name").send_keys(name)
        self.confirm_button.click()
        self.get_element(".invalid-feedback", By.CSS_SELECTOR)

        # With just the url
        self.clear(self.get_element("name"))
        self.get_element("url").send_keys("https://www.google.com")
        self.confirm_button.click()
        self.get_element(".invalid-feedback", By.CSS_SELECTOR)

        self.cancel_button.click()
        self.wait_for_edit_modal_close()

    def test_add_duplicate_entry(self) -> None:
        """Test that adding an entry with a duplicate name shows validation error"""

        self.add_entity_button.click()
        self.wait_for_edit_modal()
        self.get_element("name").send_keys(self.test_entry.name)
        self.get_element("url").send_keys("https://www.google.com")
        self.confirm_button.click()
        self.get_element(".invalid-feedback", By.CSS_SELECTOR)
        self.cancel_button.click()
        self.wait_for_edit_modal_close()

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

    def test_view_entry(self) -> None:
        """Test viewing an entry details by clicking on a table row"""

        self.table_row(self.test_entry.id).click()
        self._test_view_modal()

    def test_view_entry_right_click(self) -> None:
        """Test viewing an entry details through the right-click context menu"""

        self.context_menu(self.test_entry.id, "view")
        self._test_view_modal()

    def test_edit_entry_through_view_modal(self) -> None:
        """Test editing an entry through the view modal's edit button"""

        original_name = self.test_entry.name
        new_name = self.test_name
        self.table_row(self.test_entry.id).click()
        self.wait_for_view_modal()
        self.edit_button.click()
        self.wait_for_edit_modal()
        self.clear(self.get_element("name"), new_name)
        self.confirm_button.click()
        self.wait_for_view_modal()
        self.cancel_button.click()
        self.wait_for_view_modal_close()
        self.check_rows("name", new_name, 1)
        self.check_rows("name", original_name, 0)

    def test_edit_entry_through_right_click_context_menu(self) -> None:
        """Test editing an entry through right-click context menu"""

        original_name = self.test_entry.url
        new_name = self.test_name
        self.context_menu(self.test_entry.id, "edit")
        self.wait_for_edit_modal()
        self.clear(self.get_element("url"), new_name)
        self.confirm_button.click()
        self.wait_for_edit_modal_close()
        self.check_rows("url", new_name, 1)
        self.check_rows("url", original_name, 0)

    def test_delete_entry(self) -> None:
        """Test deleting an entry"""

        self.context_menu(self.test_entry.id, "delete")
        self.wait_for_delete_modal()
        self.confirm_button.click()
        self.wait_for_edit_modal_close()
        time.sleep(0.1)
        self.check_rows("name", self.test_entry.name, 0)

    def test_search_functionality(self) -> None:
        """Test the search functionality"""

        self._test_search_functionality("name", self.test_entry.name[3:6])
        self._test_search_functionality("url", self.test_entry.url)

    def test_sort_functionality(self) -> None:
        """Test sorting functionality"""

        self._test_sort_functionality("name")
        self._test_sort_functionality("url", lambda x: x[8:])
