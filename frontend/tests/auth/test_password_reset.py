from base_test import BaseTest


class TestPasswordReset(BaseTest):

    def test_password_reset_flow(self, test_users) -> None:
        """Test complete password reset flow using test email endpoints"""

        test_email = test_users[0].email
        new_password = "NewPassword123!"

        # Clear any existing test emails
        self.auth_utils.clear_test_emails()

        # Request password reset
        self.auth_utils.go_to_login()
        self.auth_utils.switch_to_forgot_password()
        self.auth_utils.set_email(test_email)
        self.auth_utils.confirm()

        # Verify success message
        self.auth_utils.assert_toast_message("Password reset email sent successfully")

        # Get reset link from test endpoint
        reset_url = self.auth_utils.get_reset_link_from_email(test_email)

        # Visit reset URL
        self.driver.get(reset_url)

        # Set new password
        self.auth_utils.set_password(new_password)
        self.auth_utils.set_confirm_password(new_password)
        self.auth_utils.confirm()

        # Verify success message
        self.auth_utils.assert_toast_message("Password has been reset successfully")

        # Login with new password
        self.auth_utils.wait_for_login()
        self.auth_utils.set_email(test_email)
        self.auth_utils.set_password(new_password)
        self.auth_utils.confirm()
        self.auth_utils.wait_for_dashboard()

    def test_password_reset_invalid_token(self) -> None:
        """Test password reset with invalid token"""

        invalid_reset_url = f"{self.frontend_base_url}/reset-password?token=invalid_token"
        self.driver.get(invalid_reset_url)
        self.auth_utils.set_password("password")
        self.auth_utils.set_confirm_password("password")
        self.auth_utils.confirm()
        self.auth_utils.assert_toast_message("Invalid or expired password reset token")
