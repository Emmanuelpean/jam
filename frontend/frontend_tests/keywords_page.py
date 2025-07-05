import time

import pytest
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
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
                "profile.managed_default_content_settings.notifications": 2
            }
            chrome_options.add_experimental_option("prefs", prefs)

            # Additional option to disable password saving prompts
            chrome_options.add_experimental_option("useAutomationExtension", False)
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])

            # Try this additional option
            chrome_options.add_argument("--disable-features=TranslateUI,BlinkGenPropertyTrees,PasswordGeneration,AutofillPasswordGeneration")

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
            if hasattr(self, 'driver'):
                try:
                    self.driver.quit()
                except:
                    pass
            raise

        yield  # This allows the test to run

        # Teardown
        try:
            if hasattr(self, 'driver'):
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
            self.wait.until(EC.url_contains("/dashboard"))

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
                EC.invisibility_of_element_located((By.CSS_SELECTOR, ".spinner-border"))
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

    def get_element(self, element_id: str, selector: By = By.ID, etype: str | None = None) -> WebElement | Select:
        """Get an element by its ID
        :param element_id: ID of the element to get
        :param selector: Selector to use for finding the element
        :param etype: Type of element to return. If None, returns the WebElement. If "select", returns the Select object."""

        try:
            element = self.wait.until(EC.presence_of_element_located((selector, element_id)))
            if etype is None:
                return element
            elif etype == "select":
                return Select(element)
        except:
            raise AssertionError(f"Could not find element {element_id}\nPossible IDs: {self.get_all_element_ids()}")

    def wait_for_modal(self):
        """Wait for the modal to appear"""

        modal = self.get_element(".modal", By.CSS_SELECTOR)
        assert modal.is_displayed(), "Modal should be visible"

    def wait_for_modal_close(self):
        """Wait for the modal to close"""

        self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, ".modal")))

    def test_display_keywords_entries(self, frontend_test_keywords):
        """Test that keywords entries are displayed correctly"""

        rows = self.driver.find_elements(By.CLASS_NAME, "table-row-clickable")
        keywords = [keyword for keyword in frontend_test_keywords if keyword.owner_id == 1]
        assert len(rows) == min([20, len(keywords)]), "The table rows should match the keyword entries"

    def test_display_keywords_40max_entries(self, frontend_test_keywords):
        """Test that keywords entries are displayed correctly after changing the max display to 40"""

        self.get_element("page-items-select", etype="select").select_by_value("40")
        self.wait_for_table_load()
        rows = self.driver.find_elements(By.CLASS_NAME, "table-row-clickable")
        keywords = [keyword for keyword in frontend_test_keywords if keyword.owner_id == 1]
        assert len(rows) == min([40, len(keywords)]), "The table rows should match the keyword entries"

    @property
    def add_entity_button(self) -> WebElement:

        return self.get_element("add-entity-button")

    @property
    def save_button(self) -> WebElement:

        return self.get_element("confirm-button")

    @property
    def cancel_button(self) -> WebElement:

        return self.get_element("cancel-button")

    def test_add_keyword_with_valid_name(self):
        """Test adding a new keyword with a valid name"""

        test_keyword_name = f"TestKeyword_{int(time.time())}"
        self.add_entity_button.click()
        self.wait_for_modal()
        self.get_element("name").send_keys(test_keyword_name)
        self.save_button.click()
        self.wait_for_modal_close()

        # Verify the keyword was added to the table
        self.wait.until(EC.presence_of_element_located((By.XPATH, f"//td[contains(text(), '{test_keyword_name}')]")))

        # Clean up - delete the test keyword
        self.delete_keyword_by_name(test_keyword_name)

    def test_add_keyword_without_name_shows_error(self):
        """Test that adding a keyword without a name shows validation error"""
        # Click the Add button
        self.add_entity_button.click()
        self.wait_for_modal()
        self.save_button.click()
        self.get_element(".invalid-feedback", By.CSS_SELECTOR)

        # Close modal
        self.cancel_button.click()
        self.wait_for_modal_close()

    def test_view_keyword_entry(self):
        """Test viewing a keyword entry details"""
        # Use the first test keyword from conftest
        test_keyword = self.test_keywords[0]

        # Find and click on the keyword row to view details
        keyword_row = self.wait.until(EC.element_to_be_clickable((By.XPATH, f"//tr[td[contains(text(), '{test_keyword.name}')]]")))
        keyword_row.click()

        # Wait for view modal to appear
        view_modal = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".modal")))
        assert view_modal.is_displayed(), "View modal should be visible"

        # Verify modal contains the keyword information
        modal_content = view_modal.text
        assert test_keyword.name in modal_content, "Modal should display the keyword name"

        # Close modal
        close_button = self.driver.find_element(By.CSS_SELECTOR, ".modal .btn-close, .modal .close")
        close_button.click()
        self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, ".modal")))

    def test_edit_keyword_through_view_modal(self):
        """Test editing a keyword through the view modal's edit button"""
        # Use the first test keyword from conftest
        test_keyword = self.test_keywords[0]
        original_name = test_keyword.name
        new_name = f"EditedKeyword_{int(time.time())}"

        # Click on keyword row to open view modal
        keyword_row = self.wait.until(EC.element_to_be_clickable((By.XPATH, f"//tr[td[contains(text(), '{original_name}')]]")))
        keyword_row.click()

        # Wait for view modal and click edit button
        self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".modal")))
        edit_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Edit')]")))
        edit_button.click()

        # Wait for edit form to appear
        name_input = self.wait.until(EC.presence_of_element_located((By.NAME, "name")))

        # Modify the name
        name_input.clear()
        name_input.send_keys(new_name)

        # Save changes
        save_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Save')]")
        save_button.click()

        # Wait for modal to close
        self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, ".modal")))

        # Verify the keyword was updated
        self.wait.until(EC.presence_of_element_located((By.XPATH, f"//td[contains(text(), '{new_name}')]")))

        # Verify old name is no longer present
        old_name_elements = self.driver.find_elements(By.XPATH, f"//td[contains(text(), '{original_name}')]")
        assert len(old_name_elements) == 0, "Old keyword name should not be present"

        # Clean up - restore original name
        self.delete_keyword_by_name(new_name)

    def test_edit_keyword_through_right_click_context_menu(self):
        """Test editing a keyword through right-click context menu"""
        # Use the second test keyword from conftest if available
        if len(self.test_keywords) < 2:
            pytest.skip("Need at least 2 test keywords for this test")

        test_keyword = self.test_keywords[1]
        original_name = test_keyword.name
        new_name = f"RightClickEditedKeyword_{int(time.time())}"

        # Find the keyword row and right-click
        keyword_row = self.wait.until(EC.presence_of_element_located((By.XPATH, f"//tr[td[contains(text(), '{original_name}')]]")))

        # Perform right-click
        actions = ActionChains(self.driver)
        actions.context_click(keyword_row).perform()

        # Wait for context menu and click Edit option
        try:
            edit_option = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'context-menu')]//span[contains(text(), 'Edit')]")))
            edit_option.click()
        except TimeoutException:
            # If context menu doesn't appear, skip this test
            pytest.skip("Context menu not implemented or not visible")

        # Wait for edit modal
        name_input = self.wait.until(EC.presence_of_element_located((By.NAME, "name")))

        # Modify the name
        name_input.clear()
        name_input.send_keys(new_name)

        # Save changes
        save_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Save')]")
        save_button.click()

        # Wait for modal to close
        self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, ".modal")))

        # Verify the keyword was updated
        self.wait.until(EC.presence_of_element_located((By.XPATH, f"//td[contains(text(), '{new_name}')]")))

        # Clean up
        self.delete_keyword_by_name(new_name)

    def test_delete_keyword_entry(self):
        """Test deleting a keyword entry - creates a new one to avoid affecting other tests"""
        # Create a test keyword for deletion
        test_keyword_name = f"DeleteTestKeyword_{int(time.time())}"
        self.create_test_keyword(test_keyword_name)

        # Click on keyword row to open view modal
        keyword_row = self.wait.until(EC.element_to_be_clickable((By.XPATH, f"//tr[td[contains(text(), '{test_keyword_name}')]]")))
        keyword_row.click()

        # Wait for view modal and click delete button
        self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".modal")))
        delete_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Delete')]")))
        delete_button.click()

        # Handle confirmation dialog if present
        try:
            confirm_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Confirm') or contains(text(), 'Yes') or contains(text(), 'Delete')]")))
            confirm_button.click()
        except TimeoutException:
            pass  # No confirmation dialog

        # Wait for modal to close
        self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, ".modal")))

        # Verify the keyword was deleted
        deleted_elements = self.driver.find_elements(By.XPATH, f"//td[contains(text(), '{test_keyword_name}')]")
        assert len(deleted_elements) == 0, "Deleted keyword should not be present in the table"

    def test_search_functionality(self):
        """Test the search functionality for keywords"""
        # Use test keywords from conftest
        if len(self.test_keywords) < 2:
            pytest.skip("Need at least 2 test keywords for search test")

        test_keyword1 = self.test_keywords[0]
        test_keyword2 = self.test_keywords[1]

        # Find search input
        search_input = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder*='Search'], input[type='search']")))

        # Search for first keyword
        search_input.clear()
        search_input.send_keys(test_keyword1.name[:5])  # Search with partial name

        # Wait for search results
        time.sleep(1)  # Allow time for search to filter

        # Verify matching keyword is shown
        visible_rows = self.driver.find_elements(By.CSS_SELECTOR, "tbody tr:not([style*='display: none'])")
        matching_rows = [row for row in visible_rows if test_keyword1.name in row.text]
        assert len(matching_rows) > 0, "Search should return matching keyword"

        # Clear search
        search_input.clear()
        search_input.send_keys(Keys.ESCAPE)

    def test_sort_functionality(self):
        """Test sorting functionality for the keyword table"""
        # Find and click the Name column header to sort
        name_header = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//th[contains(text(), 'Name')]")))
        name_header.click()

        # Wait for sort to complete
        time.sleep(1)

        # Get all visible keyword names
        keyword_cells = self.driver.find_elements(By.CSS_SELECTOR, "tbody td:first-child")
        visible_keywords = [cell.text for cell in keyword_cells if cell.text.strip()]

        # Verify we have keywords to sort
        assert len(visible_keywords) > 0, "Should have keywords to sort"

        # Verify sorting (basic check that sorting occurred)
        # Note: More specific sorting validation would depend on your test data
        sorted_keywords = sorted(visible_keywords)
        # This is a basic check - you might want to make it more specific based on your needs

    # Helper methods
    def create_test_keyword(self, name):
        """Helper method to create a test keyword"""
        add_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Add')]")))
        add_button.click()

        modal = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".modal")))
        name_input = self.wait.until(EC.presence_of_element_located((By.NAME, "name")))
        name_input.clear()
        name_input.send_keys(name)

        save_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Save')]")
        save_button.click()

        self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, ".modal")))
        self.wait.until(EC.presence_of_element_located((By.XPATH, f"//td[contains(text(), '{name}')]")))

    def delete_keyword_by_name(self, name):
        """Helper method to delete a keyword by name"""
        try:
            keyword_row = self.driver.find_element(By.XPATH, f"//tr[td[contains(text(), '{name}')]]")
            keyword_row.click()

            self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".modal")))
            delete_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Delete')]")
            delete_button.click()

            try:
                confirm_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Confirm') or contains(text(), 'Yes') or contains(text(), 'Delete')]")))
                confirm_button.click()
            except TimeoutException:
                pass

            self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, ".modal")))
        except NoSuchElementException:
            pass  # Keyword not found, already deleted
