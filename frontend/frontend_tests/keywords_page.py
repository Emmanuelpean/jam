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


def print_backend_pid():
    try:
        import psutil

        backend_processes = []
        for proc in psutil.process_iter(["pid", "name", "cmdline"]):
            try:
                if proc.info["cmdline"] and any("uvicorn" in cmd for cmd in proc.info["cmdline"]):
                    backend_processes.append(f"PID {proc.info['pid']}: {' '.join(proc.info['cmdline'])}")
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

        if backend_processes:
            print(f"Backend processes found: {backend_processes}")
        else:
            print("No backend processes found - backend may have crashed")

    except Exception as e:
        print(f"Error checking backend processes: {e}")


class TestPage:
    """Base class for testING pages"""

    driver = None
    wait = None
    base_url = None
    page_url = ""
    test_data = None
    test_entry = None
    _test_data = None

    @pytest.fixture(autouse=True)
    def setup_method(self, frontend_base_url, request) -> None:
        """Set up the test environment before each test with test data"""
        try:
            # Configure Chrome options to disable password prompts
            chrome_options = Options()
            chrome_options.add_argument("--disable-password-generation")
            chrome_options.add_argument("--disable-password-manager-reauthentication")
            chrome_options.add_argument("--disable-save-password-bubble")
            chrome_options.add_argument("--disable-web-security")
            chrome_options.add_argument("--disable-features=VizDisplayCompositor")
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-password-manager")
            chrome_options.add_argument("--disable-password-generation")
            chrome_options.add_argument("--disable-autofill")
            chrome_options.add_argument("--disable-autofill-keyboard-accessory-view")
            chrome_options.add_argument("--disable-full-form-autofill-ios")

            # Set preferences to disable password manager
            prefs = {
                "profile.password_manager_leak_detection": False,
                "credentials_enable_service": False,
                "password_manager_enabled": False,
                "profile.password_manager_enabled": False,
                "profile.default_content_setting_values.notifications": 2,
                "profile.default_content_settings.popups": 0,
                "autofill.profile_enabled": False,
                "autofill.credit_card_enabled": False,
                "profile.default_content_setting_values.auto_select_certificate": 1,
                "profile.managed_default_content_settings.notifications": 2,
            }
            chrome_options.add_experimental_option("prefs", prefs)

            # Additional option to disable password saving prompts
            chrome_options.add_experimental_option("useAutomationExtension", False)
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])

            # Try this additional option
            chrome_options.add_argument(
                "--disable-features=TranslateUI,BlinkGenPropertyTrees,PasswordGeneration,AutofillPasswordGeneration"
            )

            self.driver = webdriver.Chrome(options=chrome_options)

            self.driver.maximize_window()
            self.wait = WebDriverWait(self.driver, 10)
            self.base_url = frontend_base_url
            self.test_data = request.getfixturevalue(self._test_data)
            self.test_entry = self.test_data[0]
            print_backend_pid()

            # Login and navigate to Keywords page
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
        print_backend_pid()

    def login(self) -> None:
        """Helper method to login to the application"""
        try:
            login_url = f"{self.base_url}/login"
            self.driver.get(login_url)

            self.get_element("email").send_keys("test_user@test.com")
            self.get_element("password").send_keys("test_password")
            self.get_element("log-button").click()
            self.wait.until(ec.url_contains("/dashboard"))

        except TimeoutException as e:
            print(f"Timeout during login: {e}")
            print(f"Current URL: {self.driver.current_url}")
            raise
        except Exception as e:
            print(f"Error during login: {e}")
            print(f"Current URL: {self.driver.current_url}")
            raise

    def wait_for_table_load(self, timeout: int | float = 100) -> None:
        """Wait for loading spinner to disappear"""

        try:
            # Wait for spinner to disappear
            WebDriverWait(self.driver, timeout).until(
                ec.invisibility_of_element_located((By.CSS_SELECTOR, ".spinner-border"))
            )
        except TimeoutException:
            # If spinner was never present, that's also okay
            pass

    def get_all_element_ids(self) -> list[str]:
        """Get all element IDs present on the current page"""

        # Find all elements that have an ID attribute
        elements_with_id = self.driver.find_elements(By.XPATH, "//*[@id]")

        # Extract the ID values
        element_ids = []
        for element in elements_with_id:
            element_id = element.get_attribute("id")
            if element_id:  # Only add non-empty IDs
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

        time.sleep(0.3)
        try:
            element = self.wait.until(ec.element_to_be_clickable((selector, element_id)))
            if etype is None:
                return element
            elif etype == "select":
                return Select(element)
        except:
            raise AssertionError(f"Could not find element {element_id}\nPossible IDs: {self.get_all_element_ids()}")

    def wait_for_modal_close(self) -> None:
        """Wait for the modal to close"""

        self.wait.until(ec.invisibility_of_element_located((By.CSS_SELECTOR, ".modal")))

    def wait_for_delete_modal(self) -> WebElement:
        """Wait for the delete modal to appear"""

        return self.get_element("modal-confirmation")

    @property
    def table_rows(self) -> list[WebElement]:
        """Get all table rows on the page"""

        return self.driver.find_elements(By.CLASS_NAME, "table-row-clickable")

    def table_row(self, item_id: int, *args, **kwargs) -> WebElement:
        """Get a specific table row by its ID"""

        return self.get_element(f"table-row-{item_id}", *args, **kwargs)

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

    @staticmethod
    def clear(element: WebElement, text: str = "") -> None:
        """Clears the input element"""

        element.send_keys(Keys.CONTROL, "a")
        element.send_keys(Keys.DELETE)
        element.send_keys(text)

    def context_menu(self, entity_id: int, choice: str):
        """Row context menu"""

        # Click on keyword row to open view modal
        actions = ActionChains(self.driver)
        actions.context_click(self.table_row(entity_id)).perform()

        edit_option = self.get_element(f"context-menu-{choice}")
        edit_option.click()

    def check_rows(self, name: str, expected_count: int = 1) -> None:
        """Check that a specific row with a specific name exists in the table
        :param name: Name of the row to check
        :param expected_count: Expected number of rows with that name"""

        rows = self.driver.find_elements(By.XPATH, f"//td[contains(text(), '{name}')]")
        assert len(rows) == expected_count, f"Expected {expected_count} rows with name '{name}', found {len(rows)}"

    def get_column_values(self, column_index: int) -> list[str]:
        """Get values from a specific column in the table
        :param column_index: Index of the column (0-based)
        :return: List of values from that column"""

        return [row.find_elements(By.TAG_NAME, "td")[column_index].text for row in self.table_rows]


class TestKeywordsPage(TestPage):
    """
    Test class for Keywords Page functionality including:
    - Displaying keyword entries with different entries per page
    - Adding new keywords
    - Viewing keyword entries
    - Editing keywords
    - Deleting keyword entries
    """

    page_url = "keywords"
    _test_data = "test_keywords"

    def wait_for_view_modal(self) -> WebElement:
        """Wait for the view modal to appear"""

        return self.get_element("modal-formview-view-keyword")

    def wait_for_edit_modal(self) -> WebElement:
        """Wait for the edit modal to appear"""

        return self.get_element("modal-formview-edit-keyword")

    def test_display_keywords_entries(self) -> None:
        """Test that keywords entries are displayed correctly"""

        # Default 20 entries display
        keywords = [keyword for keyword in self.test_data if keyword.owner_id == 1]
        assert len(self.table_rows) == min([20, len(keywords)]), "The table rows should match the keyword entries"

        # Increase to 40
        self.get_element("page-items-select", etype="select").select_by_value("40")
        self.wait_for_table_load()
        keywords = [keyword for keyword in self.test_data if keyword.owner_id == 1]
        assert len(self.table_rows) == min([40, len(keywords)]), "The table rows should match the keyword entries"

    def test_add_keyword_with_valid_name(self) -> None:
        """Test adding a new keyword with a valid name"""

        test_keyword_name = f"TestKeyword_{int(time.time())}"
        self.add_entity_button.click()
        self.wait_for_edit_modal()
        self.get_element("name").send_keys(test_keyword_name)
        self.confirm_button.click()
        self.wait_for_modal_close()
        self.check_rows(test_keyword_name, 1)

    def test_add_keyword_without_name_shows_error(self) -> None:
        """Test that adding a keyword without a name shows validation error"""

        self.add_entity_button.click()
        self.wait_for_edit_modal()
        self.confirm_button.click()
        self.get_element(".invalid-feedback", By.CSS_SELECTOR)
        self.cancel_button.click()
        self.wait_for_modal_close()

    def test_add_keyword_same_name_shows_error(self) -> None:
        """Test that adding a keyword with an existing name shows validation error"""

        self.add_entity_button.click()
        self.wait_for_edit_modal()
        self.get_element("name").send_keys(self.test_data[0].name)
        self.confirm_button.click()
        self.get_element(".invalid-feedback", By.CSS_SELECTOR)
        self.cancel_button.click()
        self.wait_for_modal_close()

    def _test_view_modal(self, test_keyword) -> None:
        """Helper method to test the view modal for a keyword entry
        :param test_keyword: Keyword object to test"""

        modal = self.wait_for_view_modal()

        # Verify modal contains the keyword information
        date = datetime.strftime(test_keyword.created_at, "%d/%m/%Y")
        expected = f"Keyword Details\nName\n{test_keyword.name}\nDate Added\n{date}\nModified On\n{date}\nClose\nEdit"
        assert modal.text == expected

        # Close modal
        self.cancel_button.click()
        self.wait_for_modal_close()

    def test_view_keyword_entry(self) -> None:
        """Test viewing a keyword entry details by clicking on a table row"""

        test_keyword = self.test_data[0]
        self.table_row(test_keyword.id).click()
        self._test_view_modal(test_keyword)

    def test_view_keyword_entry_right_click(self) -> None:
        """Test viewing a keyword entry details through the right-click context menu"""

        test_keyword = self.test_data[0]
        self.context_menu(test_keyword.id, "view")
        self._test_view_modal(test_keyword)

    def test_edit_keyword_through_view_modal(self) -> None:
        """Test editing a keyword through the view modal's edit button"""

        test_keyword = self.test_data[0]
        original_name = test_keyword.name
        new_name = f"EditedKeyword_{int(time.time())}"
        self.table_row(test_keyword.id).click()
        self.wait_for_view_modal()
        self.edit_button.click()
        self.wait_for_edit_modal()
        self.clear(self.get_element("name"), new_name)
        self.confirm_button.click()
        self.wait_for_view_modal()
        self.cancel_button.click()
        self.wait_for_modal_close()
        self.check_rows(new_name, 1)
        self.check_rows(original_name, 0)

    def test_edit_keyword_through_right_click_context_menu(self) -> None:
        """Test editing a keyword through right-click context menu"""

        test_keyword = self.test_data[0]
        original_name = test_keyword.name
        new_name = f"EditedKeyword_{int(time.time())}"
        self.context_menu(test_keyword.id, "edit")
        self.wait_for_edit_modal()
        self.clear(self.get_element("name"), new_name)
        self.confirm_button.click()
        self.wait_for_modal_close()
        self.check_rows(new_name, 1)
        self.check_rows(original_name, 0)

    def test_delete_keyword_entry(self) -> None:
        """Test deleting a keyword entry"""

        test_keyword = self.test_data[0]
        self.context_menu(test_keyword.id, "delete")
        self.wait_for_delete_modal()
        self.confirm_button.click()
        self.wait_for_modal_close()
        self.check_rows(test_keyword.name, 0)

    def test_search_functionality(self) -> None:
        """Test the search functionality for keywords"""

        string = self.test_data[0].name[3:5]
        n = len([f for f in self.test_data if string in f.name])

        # Find search input
        self.clear(self.get_element("search-input"), string)
        time.sleep(1)  # Allow time for search to filter
        assert len(self.table_rows) == n, "Expected search to filter results"

    def test_sort_functionality(self) -> None:
        """Test sorting functionality for the keyword table"""

        # Find and click the Name column header to sort
        self.get_element("table-header-name").click()
        time.sleep(0.2)
        expected = sorted([entity.name for entity in self.test_data], key=lambda x: x.lower())[:20]
        values = self.get_column_values(0)
        assert values == expected, "Expected sorted results"


class TestAggregatorsPage(TestPage):
    """
    Test class for Aggregators Page functionality including:
    - Displaying entries with different entries per page
    - Adding new entries
    - Viewing entries
    - Editing entries
    - Deleting entries
    """

    page_url = "aggregators"
    _test_data = "test_aggregators"

    def wait_for_view_modal(self) -> WebElement:
        """Wait for the view modal to appear"""

        return self.get_element("modal-formview-view-aggregator")

    def wait_for_edit_modal(self) -> WebElement:
        """Wait for the edit modal to appear"""

        return self.get_element("modal-formview-edit-aggregator")

    def test_display_entries(self) -> None:
        """Test that entries are displayed correctly"""

        # Default 20 entries display
        entries = [entry for entry in self.test_data if entry.owner_id == 1]
        assert len(self.table_rows) == min([20, len(entries)]), "The table rows should match the number of entries"

        # Increase to 40
        self.get_element("page-items-select", etype="select").select_by_value("40")
        self.wait_for_table_load()
        entries = [entry for entry in self.test_data if entry.owner_id == 1]
        assert len(self.table_rows) == min([40, len(entries)]), "The table rows should match the number of entries"

    def test_add_valid_entry(self) -> None:
        """Test adding a new entry with a valid name"""

        test_keyword_name = f"TestKeyword_{int(time.time())}"
        self.add_entity_button.click()
        self.wait_for_edit_modal()
        self.get_element("name").send_keys(test_keyword_name)
        self.get_element("url").send_keys("https://www.google.com")
        self.confirm_button.click()
        self.wait_for_modal_close()
        self.check_rows(test_keyword_name, 1)

    def test_add_invalid_entry(self) -> None:
        """Test that adding an entry without the required fields shows validation error"""

        test_keyword_name = f"TestKeyword_{int(time.time())}"
        self.add_entity_button.click()
        self.wait_for_edit_modal()

        # With none
        self.confirm_button.click()
        self.get_element(".invalid-feedback", By.CSS_SELECTOR)

        # With just the name
        self.get_element("name").send_keys(test_keyword_name)
        self.confirm_button.click()
        self.get_element(".invalid-feedback", By.CSS_SELECTOR)

        # With just the url
        self.clear(self.get_element("name"))
        self.get_element("url").send_keys("https://www.google.com")
        self.confirm_button.click()
        self.get_element(".invalid-feedback", By.CSS_SELECTOR)

        self.cancel_button.click()
        self.wait_for_modal_close()

    def test_add_duplicate_entry(self) -> None:
        """Test that adding an entry with a duplicate name shows validation error"""

        self.add_entity_button.click()
        self.wait_for_edit_modal()
        self.get_element("name").send_keys(self.test_entry.name)
        self.get_element("url").send_keys("https://www.google.com")
        self.confirm_button.click()
        self.get_element(".invalid-feedback", By.CSS_SELECTOR)
        self.cancel_button.click()
        self.wait_for_modal_close()

    def _test_view_modal(self) -> None:
        """Helper method to test the view modal for a keyword entry"""

        modal = self.wait_for_view_modal()

        # Verify modal contains the keyword information
        date = datetime.strftime(self.test_entry.created_at, "%d/%m/%Y")
        expected = f"Aggregator Details\nName\n{self.test_entry.name}\nWebsite\n{self.test_entry.url.replace("https://", "")}\nDate Added\n{date}\nModified On\n{date}\nClose\nEdit"
        assert modal.text == expected

        # Close modal
        self.cancel_button.click()
        self.wait_for_modal_close()

    def test_view_entry(self) -> None:
        """Test viewing an entry details by clicking on a table row"""

        self.table_row(self.test_entry.id).click()
        self._test_view_modal()

    def test_view_entry_right_click(self) -> None:
        """Test viewing a keyword entry details through the right-click context menu"""

        self.context_menu(self.test_entry.id, "view")
        self._test_view_modal()

    def test_edit_entry_through_view_modal(self) -> None:
        """Test editing an entry through the view modal's edit button"""

        original_name = self.test_entry.name
        new_name = f"EditedEntry_{int(time.time())}"
        self.table_row(self.test_entry.id).click()
        self.wait_for_view_modal()
        self.edit_button.click()
        self.wait_for_edit_modal()
        self.clear(self.get_element("name"), new_name)
        self.confirm_button.click()
        self.wait_for_view_modal()
        self.cancel_button.click()
        self.wait_for_modal_close()
        self.check_rows(new_name, 1)
        self.check_rows(original_name, 0)

    def test_edit_entry_through_right_click_context_menu(self) -> None:
        """Test editing an entry through right-click context menu"""

        original_name = self.test_entry.name
        new_name = f"EditedEntry_{int(time.time())}"
        self.context_menu(self.test_entry.id, "edit")
        self.wait_for_edit_modal()
        self.clear(self.get_element("url"), new_name)
        self.confirm_button.click()
        self.wait_for_modal_close()
        self.check_rows(new_name, 1)
        self.check_rows(original_name, 0)

    def test_delete_entry(self) -> None:
        """Test deleting an entry"""

        self.context_menu(self.test_entry.id, "delete")
        self.wait_for_delete_modal()
        self.confirm_button.click()
        self.wait_for_modal_close()
        self.check_rows(self.test_entry.name, 0)

    def test_search_functionality(self) -> None:
        """Test the search functionality for keywords"""

        string = self.test_entry.name[3:5]
        n = len([f for f in self.test_data if string in f.name])
        self.clear(self.get_element("search-input"), string)
        time.sleep(1)  # Allow time for search to filter
        assert len(self.table_rows) == n, "Expected search to filter results"

        string = self.test_entry.url
        n = len([f for f in self.test_data if string in f.url])
        self.clear(self.get_element("search-input"), string)
        time.sleep(1)  # Allow time for search to filter
        assert len(self.table_rows) == n, "Expected search to filter results"

    def test_sort_functionality(self) -> None:
        """Test sorting functionality for the keyword table"""

        self.get_element("table-header-url").click()
        time.sleep(0.2)
        expected = sorted([entity.url[8:] for entity in self.test_data], key=lambda x: x.lower())[:20]
        values = self.get_column_values(1)
        assert values == expected, "Expected sorted results"
