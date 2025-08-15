import platform

import pytest
from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait
from sqlalchemy.orm import Session
from app.utils import verify_password
from conftest import models


class TestAuthenticationPage(object):
    """Test class for Authentication functionality including:
    - Login with valid credentials
    - Login with invalid credentials
    - Signup with valid data
    - Signup with invalid data
    - Form validation"""

    @pytest.fixture(autouse=True)
    def setup_method(self, frontend_base_url, session: Session, test_users):
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
            self.user = test_users[1]
            assert not self.user.is_admin
            self.login()

        except Exception:
            if hasattr(self, "driver"):
                try:
                    self.driver.quit()
                except:
                    pass
            raise

        yield

        # Teardown
        try:
            if hasattr(self, "driver"):
                self.driver.quit()
        except Exception as e:
            print(f"Error during teardown: {e}")

    def verify_user_in_database(self, email: str) -> bool:
        """Helper method to verify user exists in database"""

        return self.db.query(models.User).filter(models.User.email == email).all()

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

    def login(self) -> None:
        """Helper method to login to the application"""

        self.driver.get(f"{self.base_url}/login")
        self.get_element("email").send_keys(self.user.email)
        self.get_element("password").send_keys(self.user.password)
        self.get_element("confirm-button").click()
        self.wait.until(ec.url_contains("/dashboard"))
        self.driver.get(f"{self.base_url}/settings")

    @staticmethod
    def set_text(element: WebElement, text: str = "") -> None:
        """Clears the input element"""

        modifier_key = Keys.COMMAND if platform.system() == "Darwin" else Keys.CONTROL
        element.send_keys(modifier_key, "a")
        element.send_keys(Keys.DELETE)
        element.send_keys(text)

    @property
    def current_password(self):

        return self.get_element("currentPassword")

    @property
    def email(self):
        """Set the email field to the given value"""

        return self.get_element("email")

    @property
    def new_password(self):
        """Set the new password field to the given value"""

        return self.get_element("newPassword")

    @property
    def confirm_password(self):
        """Set the confirm password field to the given value"""

        return self.get_element("confirmPassword")

    def confirm(self):
        """Confirm the form submission"""

        return self.get_element("confirm-button").click()

    def assert_toast(self, message):

        assert message in self.get_element("toast").text, f"Message not found: {message}"

    def _assert_message(self, key: str, message: str) -> None:
        """Assert that the given message is displayed on the page
        :param key: Key to use for finding the error message element
        :param message: Message to check for"""

        assert message in self.get_element(key + "error-message").text, f"Message not found: {message}"

    def assert_email_error_message(self, error_message: str) -> None:
        """Assert that the given error message is displayed on the page"""

        self._assert_message("email-", error_message)

    def assert_password_error_message(self, error_message: str) -> None:
        """Assert that the given error message is displayed on the page"""

        self._assert_message("currentPassword-", error_message)

    def assert_new_password_error_message(self, error_message: str) -> None:
        """Assert that the given error message is displayed on the page"""

        self._assert_message("newPassword-", error_message)

    def assert_confirm_password_error_message(self, error_message: str) -> None:
        """Assert that the given error message is displayed on the page"""

        self._assert_message("confirmPassword-", error_message)

    @property
    def db_user(self):
        """Get the user from the database"""

        return self.db.query(models.User).filter(models.User.id == self.user.id).first()

    def test_no_password(self):
        """Test updating email without current password"""

        self.set_text(self.current_password, "")
        self.set_text(self.email, self.user.email)
        self.confirm()
        self.assert_password_error_message("Current password is required to update email or password")

    def test_incorrect_password(self):
        """Test updating email without current password"""

        self.set_text(self.current_password, "wrong")
        self.set_text(self.email, self.user.email)
        self.confirm()
        self.assert_toast("Current password is incorrect. Please try again.")

    # ------------------------------------------------- UPDATING EMAIL -------------------------------------------------

    def test_change_email_success(self, test_users) -> None:
        """Test changing the email address"""

        self.set_text(self.current_password, test_users[1].password)
        self.set_text(self.email, "newemail@email.com")
        self.confirm()
        self.assert_toast("User data updated successfully.")
        assert self.db_user.email == "newemail@email.com"

    def test_change_email_already_exist(self, test_users) -> None:
        """Test changing the email address"""

        self.set_text(self.current_password, self.user.password)
        self.set_text(self.email, test_users[2].email)
        self.confirm()
        self.assert_toast("Email is already in use. Please try a different email.")
        assert self.db_user.email == self.user.email

    def test_change_email_incorrect_format(self, test_users) -> None:
        """Test changing the email address"""

        self.set_text(self.current_password, self.user.password)
        self.set_text(self.email, "f")
        self.confirm()
        self.assert_email_error_message("Email format is invalid")
        assert self.db_user.email == self.user.email

    # ------------------------------------------------ UPDATING PASSWORD -----------------------------------------------

    def test_change_password_success(self, test_users) -> None:
        """Test changing the password"""

        self.current_password.send_keys(test_users[1].password)
        self.set_text(self.new_password, "newpassword")
        self.set_text(self.confirm_password, "newpassword")
        self.confirm()
        self.assert_toast("User data updated successfully.")
        assert verify_password("newpassword", self.db_user.password)

    def test_change_password_invalid(self, test_users) -> None:
        """Test changing the password"""

        self.current_password.send_keys(test_users[1].password)
        self.set_text(self.new_password, "n")
        self.set_text(self.confirm_password, "n")
        self.confirm()
        self.assert_new_password_error_message("New password must be at least 8 characters long")
        assert verify_password(self.user.password, self.db_user.password)

    def test_change_password_nonmatching(self, test_users) -> None:
        """Test changing the password"""

        self.current_password.send_keys(test_users[1].password)
        self.set_text(self.new_password, "testpassword")
        self.set_text(self.confirm_password, "n")
        self.confirm()
        self.assert_confirm_password_error_message("Passwords do not match")
        assert verify_password(self.user.password, self.db_user.password)
