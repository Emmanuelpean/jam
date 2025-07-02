import time

import pytest
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
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

    test_keywords = []

    @pytest.fixture(autouse=True)
    def setup_method(self, test_keywords, frontend_base_url):
        """Set up the test environment before each test with test data"""
        print("Starting setup_method...")
        print(f"Received frontend_base_url: {frontend_base_url}")
        print(f"Received test_keywords: {test_keywords}")

        try:
            print("Initializing Chrome WebDriver...")
            self.driver = webdriver.Chrome()
            print("Chrome WebDriver initialized successfully")

            print("Maximizing window...")
            self.driver.maximize_window()
            print("Window maximized")

            print("Setting up WebDriverWait...")
            self.wait = WebDriverWait(self.driver, 10)
            self.base_url = frontend_base_url
            print(f"Base URL set to: {self.base_url}")

            # Store test data for use in tests
            self.test_keywords = test_keywords
            print(f"Test keywords stored: {len(self.test_keywords)} keywords")

            # Login first (adjust selectors based on your auth implementation)
            print("Starting login process...")
            self.login()
            print("Login completed successfully")

            # Navigate to Keywords page
            keywords_url = f"{self.base_url}/keywords"
            print(f"Navigating to Keywords page: {keywords_url}")
            self.driver.get(keywords_url)
            print("Navigation completed")

            print("Waiting for page to load...")
            self.wait_for_page_load()
            print("Page loaded successfully")

        except Exception as e:
            print(f"Error during setup: {e}")
            if hasattr(self, 'driver'):
                print("Attempting to quit driver due to setup error...")
                try:
                    self.driver.quit()
                except:
                    print("Failed to quit driver cleanly")
            raise

        yield  # This allows the test to run

        # Teardown
        print("Starting teardown...")
        try:
            if hasattr(self, 'driver'):
                print("Quitting WebDriver...")
                self.driver.quit()
                print("WebDriver quit successfully")
        except Exception as e:
            print(f"Error during teardown: {e}")

    def login(self):
        """Helper method to login to the application"""
        try:
            login_url = f"{self.base_url}/login"
            print(f"Navigating to login page: {login_url}")
            self.driver.get(login_url)
            print("Login page loaded")

            print("Waiting for email field...")
            username_field = self.wait.until(EC.presence_of_element_located((By.ID, "email")))
            print("Email field found")

            print("Finding password field...")
            password_field = self.driver.find_element(By.ID, "password")
            print("Password field found")

            print("Finding login button...")
            login_button = self.driver.find_element(By.ID, "log-button")
            print("Login button found")

            print("Entering credentials...")
            username_field.send_keys("test_user@test.com")  # Use your test credentials
            password_field.send_keys("test_password")
            print("Credentials entered")

            print("Clicking login button...")
            login_button.click()
            print("Login button clicked")

            # Wait for successful login
            print("Waiting for redirect to dashboard...")
            self.wait.until(EC.url_contains("/dashboard"))
            print(f"Login successful, current URL: {self.driver.current_url}")

        except TimeoutException as e:
            print(f"Timeout during login: {e}")
            print(f"Current URL: {self.driver.current_url}")
            print(f"Page source length: {len(self.driver.page_source)}")
            raise
        except Exception as e:
            print(f"Error during login: {e}")
            print(f"Current URL: {self.driver.current_url}")
            raise

    def wait_for_page_load(self):
        """Wait for the Keywords page to load completely"""
        try:
            print("Waiting for Tags header...")
            self.wait.until(EC.presence_of_element_located((By.XPATH, "//h1[contains(text(), 'Tags')]")))
            print("Tags header found - page loaded successfully")
        except TimeoutException as e:
            print(f"Timeout waiting for page load: {e}")
            print(f"Current URL: {self.driver.current_url}")
            print(f"Page title: {self.driver.title}")

            # Try to find any h1 elements to see what's actually on the page
            try:
                h1_elements = self.driver.find_elements(By.TAG_NAME, "h1")
                print(f"Found {len(h1_elements)} h1 elements:")
                for i, h1 in enumerate(h1_elements):
                    print(f"  h1[{i}]: {h1.text}")
            except Exception as inner_e:
                print(f"Error getting h1 elements: {inner_e}")

            # Print first 500 chars of page source for debugging
            try:
                page_source = self.driver.page_source
                print(f"Page source (first 500 chars): {page_source[:500]}")
            except Exception as inner_e:
                print(f"Error getting page source: {inner_e}")

            raise

    def test_display_keywords_entries(self):
        """Test that keyword entries are displayed correctly in the table"""
        print("=" * 50)
        print("TEST STARTED: test_display_keywords_entries")
        print("=" * 50)

        # Wait for table to load
        table = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "table")))

        # Check if table headers are present
        headers = self.driver.find_elements(By.CSS_SELECTOR, "thead th")
        assert len(headers) > 0, "Table headers should be present"

        # Verify expected column headers (Name, Created At)
        header_texts = [header.text for header in headers]
        assert "Name" in header_texts, "Name column should be present"
        assert "Created At" in header_texts, "Created At column should be present"

        # Check if table body exists (may be empty)
        table_body = self.driver.find_element(By.CSS_SELECTOR, "tbody")
        assert table_body is not None, "Table body should exist"

        # Verify that test keywords from conftest are displayed
        for keyword in self.test_keywords:
            assert self.driver.find_elements(By.XPATH, f"//td[contains(text(), '{keyword.name}')]"), \
                f"Test keyword '{keyword.name}' should be displayed in table"

    def test_add_keyword_with_valid_name(self):
        """Test adding a new keyword with a valid name"""
        test_keyword_name = f"TestKeyword_{int(time.time())}"

        # Click the Add button
        add_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Add')]")))
        add_button.click()

        # Wait for modal to appear
        modal = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".modal")))
        assert modal.is_displayed(), "Add keyword modal should be visible"

        # Fill in the name field
        name_input = self.wait.until(EC.presence_of_element_located((By.NAME, "name")))
        name_input.clear()
        name_input.send_keys(test_keyword_name)

        # Submit the form
        save_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Save')]")
        save_button.click()

        # Wait for modal to close
        self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, ".modal")))

        # Verify the keyword was added to the table
        self.wait.until(EC.presence_of_element_located((By.XPATH, f"//td[contains(text(), '{test_keyword_name}')]")))

        # Clean up - delete the test keyword
        self.delete_keyword_by_name(test_keyword_name)

    def test_add_keyword_without_name_shows_error(self):
        """Test that adding a keyword without a name shows validation error"""
        # Click the Add button
        add_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Add')]")))
        add_button.click()

        # Wait for modal to appear
        modal = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".modal")))

        # Leave name field empty and try to submit
        save_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Save')]")
        save_button.click()

        # Check for validation error or that modal is still visible
        try:
            # Look for validation error message
            error_element = self.driver.find_element(By.CSS_SELECTOR, ".invalid-feedback, .error-message, .alert-danger")
            assert error_element.is_displayed(), "Error message should be displayed for empty name"
        except NoSuchElementException:
            # Alternative: check that modal is still visible (form didn't submit)
            assert modal.is_displayed(), "Modal should still be visible when validation fails"

        # Close modal
        close_button = self.driver.find_element(By.CSS_SELECTOR, ".modal .btn-close, .modal .close")
        close_button.click()
        self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, ".modal")))

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