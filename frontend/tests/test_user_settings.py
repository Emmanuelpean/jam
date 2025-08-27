from app.utils import verify_password
from conftest import models, BaseTest


class TestUserSettingsPage(BaseTest):
    """Test class for the User Settings Page"""

    page_url = "settings"

    def setup_function(self, request):
        self.login()

    def verify_user_in_database(self, email: str) -> bool:
        """Helper method to verify user exists in database"""

        return self.db.query(models.User).filter(models.User.email == email).all()

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

    @property
    def theme_hint(self):
        """Get the theme hint text"""

        return self.get_element("theme-hint")

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

    # ------------------------------------------------------ THEME -----------------------------------------------------

    def test_theme_hint(self) -> None:
        """Test theme hint"""

        assert self.theme_hint.text == (
            "Mixed Berry is not your favourite flavour of JAM?! You can easily pick "
            "another flavour by clicking on the JAM logo in the sidebar."
        )
