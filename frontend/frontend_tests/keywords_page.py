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


class TestKeywordsPage:
    """
    Test class for Keywords Page functionality including:
    - Displaying keyword entries
    - Adding new keywords (with and without name)
    - Viewing keyword entries
    - Editing keywords (through view mode and right-click)
    - Deleting keyword entries
    """

    @pytest.fixture(autouse=True)
    def setup_method(self, test_keywords, frontend_base_url):
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
            self.test_keywords = test_keywords

            # Login and navigate to Keywords page
            self.login()
            self.driver.get(f"{self.base_url}/keywords")
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

    def wait_for_table_load(self, timeout: int | float = 10) -> None:
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

        try:
            element = self.wait.until(ec.element_to_be_clickable((selector, element_id)))
            if etype is None:
                return element
            elif etype == "select":
                return Select(element)
        except:
            raise AssertionError(f"Could not find element {element_id}\nPossible IDs: {self.get_all_element_ids()}")

    def wait_for_modal_close(self):
        """Wait for the modal to close"""

        self.wait.until(ec.invisibility_of_element_located((By.CSS_SELECTOR, ".modal")))

    def _wait_for_modal(self, string: str) -> WebElement:

        self.wait.until(ec.text_to_be_present_in_element((By.CSS_SELECTOR, ".modal-title"), string))
        return self.get_element(".modal", By.CSS_SELECTOR)

    def wait_for_view_modal(self) -> WebElement:

        return self._wait_for_modal("Details")

    def wait_for_edit_modal(self) -> WebElement:

        return self._wait_for_modal("Edit")

    def wait_for_delete_modal(self) -> WebElement:

        return self._wait_for_modal("Delete")

    def wait_for_add_modal(self) -> WebElement:

        return self._wait_for_modal("Add")

    @property
    def table_rows(self) -> list[WebElement]:

        return self.driver.find_elements(By.CLASS_NAME, "table-row-clickable")

    def table_row(self, item_id: int, *args, **kwargs) -> WebElement:

        return self.get_element(f"table-row-{item_id}", *args, **kwargs)

    def test_display_keywords_entries(self, frontend_test_keywords):
        """Test that keywords entries are displayed correctly"""

        keywords = [keyword for keyword in frontend_test_keywords if keyword.owner_id == 1]
        assert len(self.table_rows) == min([20, len(keywords)]), "The table rows should match the keyword entries"

    def test_display_keywords_40max_entries(self, frontend_test_keywords):
        """Test that keywords entries are displayed correctly after changing the max display to 40"""

        self.get_element("page-items-select", etype="select").select_by_value("40")
        self.wait_for_table_load()
        keywords = [keyword for keyword in frontend_test_keywords if keyword.owner_id == 1]
        assert len(self.table_rows) == min([40, len(keywords)]), "The table rows should match the keyword entries"

    @property
    def add_entity_button(self) -> WebElement:

        return self.get_element("add-entity-button")

    @property
    def confirm_button(self) -> WebElement:

        return self.get_element("confirm-button")

    @property
    def cancel_button(self) -> WebElement:

        return self.get_element("cancel-button")

    @property
    def edit_button(self) -> WebElement:

        return self.get_element("edit-button")

    def test_add_keyword_with_valid_name(self):
        """Test adding a new keyword with a valid name"""

        test_keyword_name = f"TestKeyword_{int(time.time())}"
        self.add_entity_button.click()
        self.wait_for_add_modal()
        self.get_element("name").send_keys(test_keyword_name)
        self.confirm_button.click()
        self.wait_for_modal_close()

        # Verify the keyword was added to the table
        self.wait.until(ec.presence_of_element_located((By.XPATH, f"//td[contains(text(), '{test_keyword_name}')]")))

    def test_add_keyword_without_name_shows_error(self):
        """Test that adding a keyword without a name shows validation error"""

        self.add_entity_button.click()
        self.wait_for_add_modal()
        self.confirm_button.click()
        self.get_element(".invalid-feedback", By.CSS_SELECTOR)

        # Close modal
        self.cancel_button.click()
        self.wait_for_modal_close()

    def test_add_keyword_same_name_shows_error(self):
        """Test that adding a keyword with an existing name shows validation error"""

        self.add_entity_button.click()
        self.wait_for_add_modal()
        self.get_element("name").send_keys(self.test_keywords[0].name)
        self.confirm_button.click()
        self.get_element(".invalid-feedback", By.CSS_SELECTOR)

        # Close modal
        self.cancel_button.click()
        self.wait_for_modal_close()

    def test_view_keyword_entry(self):
        """Test viewing a keyword entry details"""

        # Use the first test keyword from conftest
        test_keyword = self.test_keywords[0]
        self.table_row(test_keyword.id).click()
        modal = self.wait_for_view_modal()

        # Verify modal contains the keyword information
        date = datetime.strftime(test_keyword.created_at, "%d/%m/%Y")
        expected = f"Keyword Details\nName\n{test_keyword.name}\nDate Added\n{date}\nModified On\n{date}\nClose\nEdit"
        assert modal.text == expected

        # Close modal
        close_button = self.driver.find_element(By.CSS_SELECTOR, ".modal .btn-close, .modal .close")
        close_button.click()
        self.wait.until(ec.invisibility_of_element_located((By.CSS_SELECTOR, ".modal")))

    @staticmethod
    def clear(element: WebElement) -> None:
        """Clears the input element"""

        element.send_keys(Keys.CONTROL, "a")
        element.send_keys(Keys.DELETE)

    def check_rows(self, name: str, expected_count: int = 1) -> None:

        rows = self.driver.find_elements(By.XPATH, f"//td[contains(text(), '{name}')]")
        assert len(rows) == expected_count, f"Expected {expected_count} rows with name '{name}', found {len(rows)}"

    def test_edit_keyword_through_view_modal(self):
        """Test editing a keyword through the view modal's edit button"""

        # Use the first test keyword from conftest
        test_keyword = self.test_keywords[0]
        original_name = test_keyword.name
        new_name = f"EditedKeyword_{int(time.time())}"

        # Click on keyword row to open view modal
        self.table_row(test_keyword.id).click()
        self.wait_for_edit_modal()
        self.edit_button.click()
        self.wait_for_edit_modal()
        name_input = self.get_element("name")
        self.clear(name_input)
        name_input.send_keys(new_name)
        self.confirm_button.click()
        self.wait_for_view_modal()
        self.cancel_button.click()
        self.wait_for_modal_close()

        # Verify the keyword was updated
        self.get_element(f"//td[contains(text(), '{new_name}')]", By.XPATH)

        # Verify old name is no longer present
        self.check_rows(original_name, 0)

    def context_menu(self, entity_id: int, choice: str):
        """Row context menu"""

        # Click on keyword row to open view modal
        actions = ActionChains(self.driver)
        actions.context_click(self.table_row(entity_id)).perform()

        edit_option = self.get_element(f"context-menu-{choice}")
        edit_option.click()

    def test_edit_keyword_through_right_click_context_menu(self):
        """Test editing a keyword through right-click context menu"""

        # Use the first test keyword from conftest
        test_keyword = self.test_keywords[0]
        original_name = test_keyword.name
        new_name = f"EditedKeyword_{int(time.time())}"

        self.context_menu(test_keyword.id, "edit")
        self.wait_for_edit_modal()
        name_input = self.get_element("name")
        self.clear(name_input)
        name_input.send_keys(new_name)
        self.confirm_button.click()
        self.wait_for_modal_close()

        # Verify the keyword was updated
        self.get_element(f"//td[contains(text(), '{new_name}')]", By.XPATH)

        # Verify old name is no longer present
        self.check_rows(original_name, 0)

    def test_delete_keyword_entry(self, test_keywords):
        """Test deleting a keyword entry - creates a new one to avoid affecting other tests"""

        # Create a test keyword for deletion
        test_keyword = test_keywords[0]

        # Click on keyword row to open view modal
        self.context_menu(test_keyword.id, "delete")

        # Handle confirmation dialog if present
        self.wait_for_delete_modal()
        self.confirm_button.click()
        self.wait_for_modal_close()

        # Verify the keyword was deleted
        rows = self.driver.find_elements(By.XPATH, f"//td[contains(text(), '{test_keyword.name}')]")
        print(rows)

        self.check_rows(test_keyword.name, 0)

    def test_search_functionality(self, test_keywords):
        """Test the search functionality for keywords"""

        string = test_keywords[0].name[3:5]
        print([f.name for f in test_keywords if string in f.name])
        n = len([f for f in test_keywords if string in f.name])

        # Find search input
        search_input = self.get_element("search-input")
        self.clear(search_input)
        search_input.send_keys(string)
        time.sleep(1)  # Allow time for search to filter
        assert len(self.table_rows) == n, "Expected search to filter results"

    def get_column_values(self, column_index: int) -> list[str]:
        """Get values from a specific column in the table
        :param column_index: Index of the column (0-based)
        :return: List of values from that column
        """

        return [row.find_elements(By.TAG_NAME, "td")[column_index].text for row in self.table_rows]

    def test_sort_functionality(self):
        """Test sorting functionality for the keyword table"""

        # Find and click the Name column header to sort
        self.get_element("table-header-name").click()
        time.sleep(1)  # Wait for sort to complete

        # Get all visible keyword names
        values = self.get_column_values(0)
        assert (
            values == sorted([entity.name for entity in self.test_keywords], key=lambda x: x.lower())[:20]
        ), "Expected sorted results"
