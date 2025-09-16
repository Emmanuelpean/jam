"""
Authentication End-to-End Tests
This module contains comprehensive Selenium-based tests for the authentication system,
including login, registration, form validation, and mode switching functionality.
"""

from conftest import models, BaseTest


class TestAuthenticationPage(BaseTest):
    """Test class for Authentication functionality including:
    - Login with valid credentials
    - Login with invalid credentials
    - Signup with valid data
    - Signup with invalid data
    - Form validation"""

    def verify_user_in_database(self, email: str) -> bool:
        """Helper method to verify user exists in database"""

        return self.db.query(models.User).filter(models.User.email == email).all()

    # ---------------------------------------------------- ELEMENTS ----------------------------------------------------

    def go_to_login(self) -> None:
        """Go to the login page"""

        self.driver.get(f"{self.frontend_base_url}/login")

    def go_to_register(self) -> None:
        """Go to the register page"""

        self.driver.get(f"{self.frontend_base_url}/register")

    def set_email(self, email: str) -> None:
        """Set the email field to the given value"""

        self.get_element("email").send_keys(email)

    def set_password(self, password: str) -> None:
        """Set the password field to the given value"""

        self.get_element("password").send_keys(password)

    def set_confirm_password(self, password: str) -> None:
        """Set the confirm password field to the given value"""

        self.get_element("confirm_password").send_keys(password)

    def confirm(self) -> None:
        """Confirm the form submission"""

        self.get_element("confirm-button").click()

    def set_terms(self) -> None:
        """Set the accept terms checkbox to True"""

        self.get_element("accept-terms").click()

    def _assert_message(self, key: str, message: str) -> None:
        """Assert that the given message is displayed on the page
        :param key: Key to use for finding the error message element
        :param message: Message to check for"""

        assert message in self.get_element(key + "error-message").text, f"Message not found: {message}"

    def assert_error_message(self, error_message: str) -> None:
        """Assert that the given error message is displayed on the page"""

        assert error_message in self.get_element("toast").text, f"Message not found: {error_message}"

    def assert_email_error_message(self, error_message: str) -> None:
        """Assert that the given error message is displayed on the page"""

        self._assert_message("email-", error_message)

    def assert_password_error_message(self, error_message: str) -> None:
        """Assert that the given error message is displayed on the page"""

        self._assert_message("password-", error_message)

    def assert_confirm_password_error_message(self, error_message: str) -> None:
        """Assert that the given error message is displayed on the page"""

        self._assert_message("confirm_password-", error_message)

    def assert_accept_terms_error_message(self, error_message: str) -> None:
        """Assert that the given error message is displayed on the page"""

        self._assert_message("terms-", error_message)

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

    # -------------------------------------------------- LOG IN TESTS --------------------------------------------------

    def test_valid_login(self, test_users) -> None:
        """Test login with valid credentials"""

        self.go_to_login()
        test_email, test_password = test_users[0].email, test_users[0].password

        # Fill in login form
        self.set_email(test_email)
        self.set_password(test_password)
        self.confirm()

        # Confirm load by checking the dashboard
        self.wait_for_dashboard()

    def test_invalid_login(self) -> None:
        """Test login with invalid credentials"""

        self.go_to_login()
        test_email, test_password = "wrong@email.com", "wrong_password"

        # Fill in login form with invalid credentials
        self.set_email(test_email)
        self.set_password(test_password)
        self.confirm()

        # Verify error message
        self.assert_error_message("Incorrect email or password")

    def test_login_invalid_email(self) -> None:
        """Test login with invalid credentials"""

        self.go_to_login()
        test_email, test_password = "wrong", "wrong_password"

        # Fill in login form with invalid credentials
        self.set_email(test_email)
        self.set_password(test_password)
        self.confirm()

        # Verify error message
        self.assert_email_error_message("Please provide a valid email address")

    def test_login_no_email(self) -> None:
        """Test login with invalid credentials"""

        self.go_to_login()
        test_email, test_password = "", "wrong_password"

        # Fill in login form with invalid credentials
        self.set_email(test_email)
        self.set_password(test_password)
        self.confirm()

        # Verify error message
        self.assert_email_error_message("Please provide a valid email address")

    def test_login_no_password(self) -> None:
        """Test login with invalid credentials"""

        self.go_to_login()
        test_email, test_password = "wrong@email.com", ""

        # Fill in login form with invalid credentials
        self.set_email(test_email)
        self.set_password(test_password)
        self.confirm()

        # Verify error message
        self.assert_password_error_message("Password is required")

    # -------------------------------------------------- SIGN UP TESTS -------------------------------------------------

    def test_mode_switching_buttons(self) -> None:
        """Test switching between login and register modes using the toggle buttons"""

        self.go_to_login()
        self.wait_for_login()
        self.switch_mode()
        self.wait_for_register()
        self.switch_mode()
        self.wait_for_login()

    def test_signup_valid(self) -> None:
        """Test signup with valid data"""

        self.go_to_register()
        test_email, test_password = f"test@test.com", "Test123!"

        # Fill in signup form
        self.set_email(test_email)
        self.set_password(test_password)
        self.set_confirm_password(test_password)
        self.set_terms()
        self.confirm()

        # Verify redirect to login page
        self.wait_for_login()
        assert self.verify_user_in_database(test_email)
        self.assert_error_message("Account created successfully! You can now log in.")

    def test_signup_existing_email(self, test_users) -> None:
        """Test signup with an already registered email"""

        self.go_to_register()
        test_email, test_password = test_users[0].email, "Test123!"

        # Fill in signup form with existing email
        self.set_email(test_users[0].email)
        self.set_password(test_password)
        self.set_confirm_password(test_password)
        self.set_terms()
        self.confirm()

        # Verify error message and database
        self.assert_error_message("Email already registered")
        assert len(self.verify_user_in_database(test_email)) == 1, "Multiple users with the same email found"

    def test_signup_invalid_email(self) -> None:
        """Test signup with invalid email format"""

        self.go_to_register()
        test_email, test_password = "invalid-email", "Test123!"

        # Fill in signup form with invalid email
        self.set_email(test_email)
        self.set_password(test_password)
        self.set_confirm_password(test_password)
        self.set_terms()
        self.confirm()

        # Verify error message and database
        self.assert_email_error_message("Please provide a valid email address")
        assert not self.verify_user_in_database(test_email)

    def test_signup_no_email(self) -> None:
        """Test signup with invalid email format"""

        self.go_to_register()
        test_email, test_password = "", "Test123!"

        # Fill in signup form with invalid email
        self.set_email(test_email)
        self.set_password(test_password)
        self.set_confirm_password(test_password)
        self.set_terms()
        self.confirm()

        # Verify error message and database
        self.assert_email_error_message("Please provide a valid email address")
        assert not self.verify_user_in_database(test_email)

    def test_signup_no_password(self) -> None:
        """Test signup with no password"""

        self.go_to_register()
        test_email, test_password = "test@test.com", ""

        # Fill in signup form with invalid password
        self.set_email(test_email)
        self.set_password(test_password)
        self.set_confirm_password(test_password)
        self.set_terms()
        self.confirm()

        # Verify error message and database
        self.assert_password_error_message("Password is required")
        self.assert_confirm_password_error_message("Please confirm your password")
        assert not self.verify_user_in_database(test_email)

    def test_signup_password_mismatch(self) -> None:
        """Test signup with mismatched passwords"""

        self.go_to_register()
        test_email = f"test@test.com"

        # Fill in signup form with non matching passwords
        self.set_email(test_email)
        self.set_password("Password123")
        self.set_confirm_password("Password124")
        self.set_terms()
        self.confirm()

        # Verify error message and database
        self.assert_confirm_password_error_message("Passwords do not match")
        assert not self.verify_user_in_database(test_email)

    def test_signup_password_requirement(self) -> None:
        """Test signup with mismatched passwords"""

        self.go_to_register()
        test_email = f"test@test.com"

        # Fill in signup form with non matching passwords
        self.set_email(test_email)
        self.set_password("Passw")
        self.set_confirm_password("Passw")
        self.set_terms()
        self.confirm()

        # Verify error message and database
        self.assert_password_error_message("Password must be at least 8 characters long.")
        assert not self.verify_user_in_database(test_email)

    def test_signup_no_tc(self):
        """Test signup without checking the terms and conditions"""

        self.go_to_register()
        test_email, test_password = f"test@test.com", "Test123!"

        # Fill in signup form with non matching passwords
        self.set_email(test_email)
        self.set_password(test_password)
        self.set_confirm_password(test_password)
        self.confirm()

        # Verify error message and database
        self.assert_accept_terms_error_message("You must accept the Terms and Conditions to register")
        assert not self.verify_user_in_database(test_email)
