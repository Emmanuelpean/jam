import time

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait
from sqlalchemy.orm import Session
from conftest import models


class TestAuthenticationPage(object):
    """Test class for Authentication functionality including:
    - Login with valid credentials
    - Login with invalid credentials
    - Signup with valid data
    - Signup with invalid data
    - Form validation"""

    @pytest.fixture(autouse=True)
    def setup_method(self, frontend_base_url, session: Session):
        """Override setup_method to avoid auto-login and add db session"""
        try:
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
            self.db = session

        except Exception:
            if hasattr(self, "driver"):
                try:
                    self.driver.quit()
                except:
                    pass
            raise

    def verify_user_in_database(self, email: str) -> bool:
        """Helper method to verify user exists in database"""

        # noinspection PyTypeChecker
        user = self.db.query(models.User).filter(models.User.email == email).first()
        return user

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

    def test_valid_login(self, test_users) -> None:
        """Test login with valid credentials"""

        self.driver.get(f"{self.base_url}/login")

        test_email = test_users[0].email
        test_password = test_users[0].password

        # Fill in login form
        self.get_element("email").send_keys(test_email)
        self.get_element("password").send_keys(test_password)
        self.get_element("log-button").click()

        # Verify redirect to dashboard
        self.wait.until(ec.url_contains("/dashboard"))

        # Verify user exists in database
        assert self.verify_user_in_database(test_email)

    def test_invalid_login(self) -> None:
        """Test login with invalid credentials"""

        self.driver.get(f"{self.base_url}/login")

        wrong_email = "wrong@email.com"
        assert not self.verify_user_in_database(wrong_email)

        # Fill in login form with invalid credentials
        self.get_element("email").send_keys(wrong_email)
        self.get_element("password").send_keys("wrong_password")
        self.get_element("log-button").click()

        # Verify error message
        error_message = self.get_element("error-message")
        assert "Invalid credentials" in error_message.text
        assert "/login" in self.driver.current_url

    def test_signup_valid(self):
        """Test signup with valid data"""
        self.driver.get(f"{self.base_url}/signup")

        # Generate unique email
        test_email = f"test_{int(time.time())}@test.com"

        # Fill in signup form
        self.get_element("firstName").send_keys("Test")
        self.get_element("lastName").send_keys("User")
        self.get_element("email").send_keys(test_email)
        self.get_element("password").send_keys("Test123!")
        self.get_element("confirmPassword").send_keys("Test123!")
        self.get_element("signup-button").click()

        # Verify redirect to login page
        self.wait.until(ec.url_contains("/login"))
        assert "/login" in self.driver.current_url

        # Verify user was created in database
        assert self.verify_user_in_database(test_email)

        # Verify user details in database
        user = self.db.query(models.User).filter(models.User.email == test_email).first()
        assert user is not None
        assert user.email == test_email
        assert user.created_at is not None
        assert user.modified_at is not None

    def test_signup_existing_email(self):
        """Test signup with an already registered email"""
        self.driver.get(f"{self.base_url}/signup")

        existing_email = "test_user@test.com"  # Assuming this user exists

        # Fill in signup form with existing email
        self.get_element("firstName").send_keys("Test")
        self.get_element("lastName").send_keys("User")
        self.get_element("email").send_keys(existing_email)
        self.get_element("password").send_keys("Test123!")
        self.get_element("confirmPassword").send_keys("Test123!")
        self.get_element("signup-button").click()

        # Verify error message
        error_message = self.get_element("error-message")
        assert "Email already registered" in error_message.text
        assert "/signup" in self.driver.current_url

    def test_signup_invalid_email(self):
        """Test signup with invalid email format"""
        self.driver.get(f"{self.base_url}/signup")

        invalid_email = "invalid-email"

        # Fill in signup form with invalid email
        self.get_element("firstName").send_keys("Test")
        self.get_element("lastName").send_keys("User")
        self.get_element("email").send_keys(invalid_email)
        self.get_element("password").send_keys("Test123!")
        self.get_element("confirmPassword").send_keys("Test123!")
        self.get_element("signup-button").click()

        # Verify error message
        error_message = self.get_element("email-error")
        assert "Please enter a valid email address" in error_message.text
        assert "/signup" in self.driver.current_url

        # Verify user was not created in database
        assert not self.verify_user_in_database(invalid_email)

    def test_signup_password_mismatch(self):
        """Test signup with mismatched passwords"""
        self.driver.get(f"{self.base_url}/signup")

        test_email = f"test_{int(time.time())}@test.com"

        # Fill in signup form with mismatched passwords
        self.get_element("firstName").send_keys("Test")
        self.get_element("lastName").send_keys("User")
        self.get_element("email").send_keys(test_email)
        self.get_element("password").send_keys("Test123!")
        self.get_element("confirmPassword").send_keys("Test456!")
        self.get_element("signup-button").click()

        # Verify error message
        error_message = self.get_element("password-error")
        assert "Passwords do not match" in error_message.text
        assert "/signup" in self.driver.current_url

        # Verify user was not created in database
        assert not self.verify_user_in_database(test_email)

    def test_required_fields_validation(self):
        """Test form validation for required fields"""
        self.driver.get(f"{self.base_url}/signup")

        # Click signup without filling any fields
        self.get_element("signup-button").click()

        # Verify error messages for all required fields
        assert "First name is required" in self.get_element("firstName-error").text
        assert "Last name is required" in self.get_element("lastName-error").text
        assert "Email is required" in self.get_element("email-error").text
        assert "Password is required" in self.get_element("password-error").text

        # Verify no user was created in database
        # Count users before and after should be the same
        initial_user_count = self.db.query(models.User).count()
        self.get_element("signup-button").click()
        final_user_count = self.db.query(models.User).count()
        assert initial_user_count == final_user_count
