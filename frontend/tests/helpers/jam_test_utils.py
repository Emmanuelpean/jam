"""Base Selenium utilities shared by all page/component utility classes."""

import time

import requests
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.support.wait import WebDriverWait

from app import models
from helpers.selenium_utils import SeleniumUtils


class JamTestUtils(SeleniumUtils):
    """Base class for selenium utilities"""

    driver: WebDriver = None
    wait: WebDriverWait = None
    frontend_base_url: str = ""
    backend_base_url: str = ""
    db = None
    client = None

    def _init(self, driver: WebDriver, frontend_base_url: str, backend_base_url: str, db, client) -> None:
        """Wire up the shared driver/session/client state used by every utils subclass.
        :param driver: Selenium WebDriver instance.
        :param frontend_base_url: Base URL of the frontend under test.
        :param backend_base_url: Base URL of the backend under test.
        :param db: Database session.
        :param client: Authorised API client for the current user."""

        self.driver = driver
        self.wait = WebDriverWait(self.driver, 10)
        self.frontend_base_url = frontend_base_url
        self.backend_base_url = backend_base_url
        self.db = db
        self.client = client

    def go_to_page(self, page: str) -> None:
        """Helper method to go to a specific page
        :param page: Path relative to the frontend base URL (e.g. "dashboard")."""

        self.go_to_url(f"{self.frontend_base_url}/{page}")

    def wait_for_page(self, page: str, timeout=None) -> None:
        """Wait for the dashboard to load
        :param page: Path relative to the frontend base URL (e.g. "dashboard").
        :param timeout: How long to wait before raising an error."""

        self.wait_for_url(f"{self.frontend_base_url}/{page}", timeout=timeout)

    def poll_db_value(self, getter, expected, timeout: float = 10.0) -> None:
        """Poll the DB until getter() returns expected, or raise.
        :param getter: A callable returning the current value (re-queried each poll).
        :param expected: The value to wait for.
        :param timeout: Maximum time to wait in seconds."""

        deadline = time.time() + timeout
        while time.time() < deadline:
            # rollback() ends the current transaction so the next query gets a fresh
            # READ COMMITTED snapshot and can see rows committed by the backend API process.
            self.db.expire_all()
            self.db.rollback()
            if getter() == expected:
                return
            time.sleep(0.5)
        self.db.expire_all()
        self.db.rollback()
        actual = getter()
        assert actual == expected, f"expected {expected!r}, got {actual!r} after {timeout}s"

    # ----------------------------------------------------- EMAILS -----------------------------------------------------

    def get_verification_token_from_db(self, email: str) -> str:
        """Helper method to get verification token from database
        :param email: Email of the user to get the token for"""

        user = self.db.query(models.User).filter(models.User.email == email).first()
        token = user.verification_token
        assert token is not None, "Verification token not found in database"
        return token

    def get_verification_link_from_email(self, email: str) -> str:
        """Helper method to get verification link from test email endpoint
        :param email: Email address the verification email was sent to."""

        response = requests.get(f"{self.backend_base_url}/test/emails/verification-link/{email}")
        assert response.status_code == 200, f"Failed to get verification link: {response.text}"
        return response.json()["verification_url"]

    def get_reset_link_from_email(self, email: str) -> str:
        """Helper method to get password reset link from test email endpoint
        :param email: Email address the password reset email was sent to."""

        response = requests.get(f"{self.backend_base_url}/test/emails/reset-link/{email}")
        assert response.status_code == 200, f"Failed to get reset link: {response.text}"
        return response.json()["reset_url"]

    def clear_test_emails(self) -> None:
        """Helper method to clear all test emails"""

        response = requests.delete(f"{self.backend_base_url}/test/emails/emails")
        assert response.status_code == 200, "Failed to clear test emails"

    # ---------------------------------------------------- ELEMENTS ----------------------------------------------------

    def close_modal(self):
        """Close the modal"""

        self.get_element("modal-close-btn").click()

    def assert_error_message(self, key: str, message: str) -> None:
        """Assert that the given message is displayed on the page
        :param key: Key to use for finding the error message element
        :param message: Message to check for"""

        assert message in self.get_element(key + "-error-message").text, f"Message not found: {message}"
