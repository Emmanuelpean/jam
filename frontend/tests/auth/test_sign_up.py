"""Tests for the sign-up page."""

from base_test import BaseTest


class TestSignUp(BaseTest):

    def test_mode_switching_buttons(self) -> None:
        """Test switching between login and register modes using the toggle buttons"""

        self.auth_utils.go_to_login()
        self.auth_utils.wait_for_login()
        self.auth_utils.switch_mode()
        self.auth_utils.wait_for_register()
        self.auth_utils.switch_mode()
        self.auth_utils.wait_for_login()

    def test_signup_valid(self) -> None:
        """Test signup with valid data"""

        self.auth_utils.go_to_register()
        test_email, test_password = f"test@test.com", "Test123!"

        # Fill in signup form
        self.auth_utils.set_email(test_email)
        self.auth_utils.set_password(test_password)
        self.auth_utils.set_confirm_password(test_password)
        self.auth_utils.set_terms()
        self.auth_utils.confirm()
        self.auth_utils.set_first_name("Test")
        self.auth_utils.set_last_name("Test")
        self.auth_utils.confirm()

        # Verify redirect to login page
        self.auth_utils.wait_for_login()
        assert self.verify_user_in_database(test_email)
        self.auth_utils.assert_toast_message(
            "Account created! Please check your email inbox to verify your account before logging in."
        )

    def test_signup_existing_email(self, test_users) -> None:
        """Test signup with an already registered email"""

        self.auth_utils.go_to_register()
        test_email, test_password = test_users[0].email, "Test123!"

        # Fill in signup form with existing email
        self.auth_utils.set_email(test_users[0].email)
        self.auth_utils.set_password(test_password)
        self.auth_utils.set_confirm_password(test_password)
        self.auth_utils.set_terms()
        self.auth_utils.confirm()
        self.auth_utils.set_first_name("Test")
        self.auth_utils.set_last_name("Test")
        self.auth_utils.confirm()

        # Verify error message and database
        self.auth_utils.assert_toast_message("Email already registered")
        assert len(self.verify_user_in_database(test_email)) == 1, "Multiple users with the same email found"

    def test_signup_invalid_email(self) -> None:
        """Test signup with invalid email format"""

        self.auth_utils.go_to_register()
        test_email, test_password = "invalid-email", "Test123!"

        # Fill in signup form with invalid email
        self.auth_utils.set_email(test_email)
        self.auth_utils.set_password(test_password)
        self.auth_utils.set_confirm_password(test_password)
        self.auth_utils.set_terms()
        self.auth_utils.confirm()

        # Verify error message and database
        self.auth_utils.assert_email_error_message("Please provide a valid email address")
        self.auth_utils.assert_confirm_button_disabled()

        # Adding 1 more character fixes the error and re-enables the button
        self.auth_utils.get_element("email").send_keys("a")
        self.auth_utils.assert_no_email_error_message()
        self.auth_utils.assert_confirm_button_enabled()

        assert not self.verify_user_in_database(test_email)

    def test_signup_no_email(self) -> None:
        """Test signup with no email"""

        self.auth_utils.go_to_register()
        test_email, test_password = "", "Test123!"

        # Fill in signup form with invalid email
        self.auth_utils.set_email(test_email)
        self.auth_utils.set_password(test_password)
        self.auth_utils.set_confirm_password(test_password)
        self.auth_utils.set_terms()
        self.auth_utils.confirm()

        # Verify error message and database
        self.auth_utils.assert_email_error_message("Please provide a valid email address")
        self.auth_utils.assert_confirm_button_disabled()

        # Adding 1 more character fixes the error and re-enables the button
        self.auth_utils.get_element("email").send_keys("a")
        self.auth_utils.assert_no_email_error_message()
        self.auth_utils.assert_confirm_button_enabled()

        assert not self.verify_user_in_database(test_email)

    def test_signup_no_password(self) -> None:
        """Test signup with no password"""

        self.auth_utils.go_to_register()
        test_email, test_password = "test@test.com", ""

        # Fill in signup form with invalid password
        self.auth_utils.set_email(test_email)
        self.auth_utils.set_password(test_password)
        self.auth_utils.set_confirm_password(test_password)
        self.auth_utils.set_terms()
        self.auth_utils.confirm()

        # Verify error message and database
        self.auth_utils.assert_password_error_message("Password is required")
        self.auth_utils.assert_confirm_password_error_message("Please confirm your password")
        self.auth_utils.assert_confirm_button_disabled()

        # Adding 1 more character to password clears both password and confirm password errors
        self.auth_utils.get_element("password").send_keys("a")
        self.auth_utils.assert_no_password_error_message()
        self.auth_utils.assert_no_confirm_password_error_message()
        self.auth_utils.assert_confirm_button_enabled()

        assert not self.verify_user_in_database(test_email)

    def test_signup_password_mismatch(self) -> None:
        """Test signup with mismatched passwords"""

        self.auth_utils.go_to_register()
        test_email = f"test@test.com"

        # Fill in signup form with non-matching passwords
        self.auth_utils.set_email(test_email)
        self.auth_utils.set_password("Password123")
        self.auth_utils.set_confirm_password("Password124")
        self.auth_utils.set_terms()
        self.auth_utils.confirm()

        # Verify error message and database
        self.auth_utils.assert_confirm_password_error_message("Passwords do not match")
        self.auth_utils.assert_confirm_button_disabled()

        # Adding 1 more character fixes the error and re-enables the button
        self.auth_utils.get_element("confirmPassword").send_keys("a")
        self.auth_utils.assert_no_confirm_password_error_message()
        self.auth_utils.assert_confirm_button_enabled()

        # Submit again and clear the error with a new password
        self.auth_utils.confirm()
        self.auth_utils.assert_confirm_password_error_message("Passwords do not match")
        self.auth_utils.assert_confirm_button_disabled()
        self.auth_utils.set_password("a")
        self.auth_utils.assert_no_confirm_password_error_message()

        assert not self.verify_user_in_database(test_email)

    def test_signup_password_requirement(self) -> None:
        """Test signup with incorrect password length requirement (8 chars)"""

        self.auth_utils.go_to_register()
        test_email = f"test@test.com"

        # Fill in signup form with non-matching passwords
        self.auth_utils.set_email(test_email)
        self.auth_utils.set_password("Passw")
        self.auth_utils.set_confirm_password("Passw")
        self.auth_utils.set_terms()
        self.auth_utils.confirm()

        # Verify error message and database
        self.auth_utils.assert_password_error_message("Password must be at least 8 characters long.")
        self.auth_utils.assert_confirm_button_disabled()

        # Adding 1 more character fixes the error and re-enables the button
        self.auth_utils.get_element("password").send_keys("a")
        self.auth_utils.assert_no_password_error_message()
        self.auth_utils.assert_confirm_button_enabled()

        assert not self.verify_user_in_database(test_email)

    def test_signup_no_tc(self) -> None:
        """Test signup without checking the terms and conditions"""

        self.auth_utils.go_to_register()
        test_email, test_password = f"test@test.com", "Test123!"

        # Fill in signup form with non-matching passwords
        self.auth_utils.set_email(test_email)
        self.auth_utils.set_password(test_password)
        self.auth_utils.set_confirm_password(test_password)
        self.auth_utils.confirm()

        # Verify error message and database
        self.auth_utils.assert_accept_terms_error_message(
            "You must accept the Terms and Conditions and Privacy Policy to register."
        )
        self.auth_utils.assert_confirm_button_disabled()
        assert not self.verify_user_in_database(test_email)

    def test_signup_limited(self) -> None:
        """Test signup when registrations are limited"""

        self._create_setting(name="allowlist", value="")
        self.auth_utils.go_to_register()
        test_email, test_password = f"test@test.com", "Test123!"
        self.auth_utils.set_email(test_email)
        self.auth_utils.set_password(test_password)
        self.auth_utils.set_confirm_password(test_password)
        self.auth_utils.set_terms()
        self.auth_utils.confirm()
        self.auth_utils.set_first_name("Test")
        self.auth_utils.set_last_name("Test")
        self.auth_utils.confirm()

        self.auth_utils.assert_toast_message("You are not allowed to sign up for now.")
        assert not self.verify_user_in_database(test_email)

    def test_register_field_limits(self) -> None:
        """Entering email or password over the limit disables Continue; reducing re-enables it."""

        self.auth_utils.go_to_register()

        # Email over limit (254 char limit)
        self.auth_utils.set_email("a" * 246 + "@test.com")
        self.auth_utils.assert_confirm_button_disabled()

        # Back within limit
        self.auth_utils.set_email("test@test.com")
        self.auth_utils.assert_confirm_button_enabled()

        # Password over limit (128 char limit)
        self.auth_utils.set_password("P" * 129)
        self.auth_utils.assert_confirm_button_disabled()

        # Back within limit
        self.auth_utils.set_password("Password123!")
        self.auth_utils.assert_confirm_button_enabled()
