"""Utilities for authentication flows (login, signup, password reset)."""

import time

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.wait import WebDriverWait

from helpers.base_utils import BaseUtils


class AuthentificationUtils(BaseUtils):
    """Test class for Authentication functionality including:
    - Login with valid credentials
    - Login with invalid credentials
    - Signup with valid data
    - Signup with invalid data
    - Form validation"""

    def __init__(self, **kwargs):
        self._init(**kwargs)

    # ----------------------------------------------------- INPUTS -----------------------------------------------------

    def go_to_login(self) -> None:
        """Go to the login page"""

        self.go_to_page("login")

    def go_to_register(self) -> None:
        """Go to the register page"""

        self.go_to_page("register")
        time.sleep(0.5)  # animation

    def go_to_forgot_password(self) -> None:
        """Go to the forgot password page"""

        self.go_to_page("forgot-password")
        time.sleep(0.5)  # animation

    @property
    def try_button(self) -> WebElement:
        """Get the Try button"""

        return self.get_element("try-app-btn")

    def set_email(self, email: str) -> None:
        """Set the email field to the given value"""

        self.set_text(self.get_element("email"), email)

    def set_password(self, password: str) -> None:
        """Set the password field to the given value"""

        self.set_text(self.get_element("password"), password)

    def set_confirm_password(self, password: str) -> None:
        """Set the confirm password field to the given value"""

        self.set_text(self.get_element("confirmPassword"), password)

    def confirm(self) -> None:
        """Confirm the form submission"""

        self.get_element("confirm-button").click()

    def set_terms(self) -> None:
        """Set the accept terms checkbox to True"""

        self.get_element("terms").click()

    def set_privacy(self) -> None:
        """Set the accept privacy policy checkbox to True"""

        self.get_element("privacy").click()

    def wait_for_captcha(self, timeout: float = 10.0) -> None:
        """Wait for the Cloudflare Turnstile widget to auto-solve.

        Selenium tests use Cloudflare's always-pass test site key, which fires its
        success callback shortly after the widget renders. On success Turnstile fills
        a hidden ``cf-turnstile-response`` input inside the widget container — we poll
        for that instead of a blind sleep so slow CI runners don't flake."""

        WebDriverWait(self.driver, timeout).until(
            lambda d: any(
                el.get_attribute("value")
                for el in d.find_elements(By.CSS_SELECTOR, "input[name='cf-turnstile-response']")
            ),
            "Turnstile widget did not auto-solve within timeout",
        )

    def set_remember_me(self) -> None:
        """Check the remember me checkbox"""

        self.get_element("remember-me").click()

    def set_first_name(self, value: str) -> None:
        """Get the first name field"""

        self.get_element("firstName").send_keys(value)

    def set_last_name(self, value: str) -> None:
        """Get the last name field"""

        self.get_element("lastName").send_keys(value)

    def register_user(
        self,
        email: str,
        password: str,
        first_name: str = "First Name",
        last_name: str = "Last Name",
    ) -> None:
        """Register a new user through the three-step register flow."""

        self.go_to_register()
        # Step 1 — credentials
        self.set_email(email)
        self.set_password(password)
        self.set_confirm_password(password)
        self.confirm()
        # Step 2 — name
        self.set_first_name(first_name)
        self.set_last_name(last_name)
        self.confirm()
        # Step 3 — consent + CAPTCHA
        self.set_terms()
        self.set_privacy()
        self.wait_for_captcha()
        self.confirm()

    def login_user(self, email: str, password: str) -> None:
        """Login with given credentials"""

        self.go_to_login()
        self.set_email(email)
        self.set_password(password)
        self.confirm()

    # ----------------------------------------------------- ERRORS -----------------------------------------------------

    def assert_email_error_message(self, error_message: str) -> None:
        """Assert that the given error message is displayed on the page"""

        self.assert_error_message("email", error_message)

    def assert_password_error_message(self, error_message: str) -> None:
        """Assert that the given error message is displayed on the page"""

        self.assert_error_message("password", error_message)

    def assert_confirm_password_error_message(self, error_message: str) -> None:
        """Assert that the given error message is displayed on the page"""

        self.assert_error_message("confirmPassword", error_message)

    def assert_accept_terms_error_message(self, error_message: str) -> None:
        """Assert that the given error message is displayed on the page"""

        self.assert_error_message("terms", error_message)

    def assert_accept_privacy_error_message(self, error_message: str) -> None:
        """Assert that the given error message is displayed on the page"""

        self.assert_error_message("privacy", error_message)

    def assert_no_email_error_message(self) -> None:
        """Assert that the email error message is not displayed on the page"""

        self.assert_not_visible("email-error-message")

    def assert_no_password_error_message(self) -> None:
        """Assert that the password error message is not displayed on the page"""

        self.assert_not_visible("password-error-message")

    def assert_no_confirm_password_error_message(self) -> None:
        """Assert that the confirm password error message is not displayed on the page"""

        self.assert_not_visible("confirmPassword-error-message")

    # ------------------------------------------------------ PAGES -----------------------------------------------------

    def wait_for_dashboard(self) -> None:
        """Wait for the dashboard to load"""

        self.wait_for_page("dashboard")

    def wait_for_login(self) -> None:
        """Wait for the login page to load"""

        self.wait_for_page("login")

    def wait_for_register(self) -> None:
        """Wait for the register page to load"""

        self.wait_for_page("register")

    def switch_mode(self) -> None:
        """Switch between login and register modes"""

        self.get_element("switch-mode-button").click()
        time.sleep(0.5)

    def go_to_verification_url(self, token: str) -> None:
        """Navigate to login page with verification token"""

        self.driver.get(f"{self.frontend_base_url}/verify-email/?token={token}")

    def switch_to_forgot_password(self) -> None:
        """Navigate to forgot password page"""

        self.get_element("forgot-password-link").click()
        time.sleep(0.5)

    def assert_confirm_button_disabled(self) -> None:
        """Wait until the confirm button becomes disabled."""

        WebDriverWait(self.driver, 5).until(
            lambda d: not d.find_element(By.ID, "confirm-button").is_enabled(),
            "Confirm button did not become disabled",
        )

    def assert_confirm_button_enabled(self) -> None:
        """Wait until the confirm button becomes enabled (clickable)."""

        self.get_element("confirm-button")
