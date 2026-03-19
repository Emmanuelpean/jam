from test_maintenance import MaintenanceTestBase

class TestMaintenanceModeAuthEndpoints(MaintenanceTestBase):
    """Auth endpoints (login, register, verify-email, password reset) are blocked during maintenance."""

    MAINTENANCE_MSG = "Service is currently under maintenance."

    def test_login_blocked_during_maintenance(self, test_regular_user) -> None:
        """Non-admin users cannot log in when maintenance is active."""

        past_time = self._get_past_timestamp(minutes=5)
        self._set_maintenance_scheduled_at(past_time)
        self.auth_utils.login_user(test_regular_user.email, test_regular_user.plain_password)
        self.auth_utils.assert_toast_message(self.MAINTENANCE_MSG)
        self._clear_maintenance_scheduled_at()

    def test_register_blocked_during_maintenance(self) -> None:
        """Registration is blocked when maintenance is active."""

        past_time = self._get_past_timestamp(minutes=5)
        self._set_maintenance_scheduled_at(past_time)
        self.auth_utils.register_user("newuser@test.com", "Test123!")
        self.auth_utils.assert_toast_message(self.MAINTENANCE_MSG)
        self._clear_maintenance_scheduled_at()

    def test_email_verification_blocked_during_maintenance(self, test_unverified_token_user) -> None:
        """Email verification is blocked when maintenance is active."""

        past_time = self._get_past_timestamp(minutes=5)
        self._set_maintenance_scheduled_at(past_time)
        self.auth_utils.go_to_verification_url(test_unverified_token_user.plain_verification_token)
        self.auth_utils.assert_toast_message(self.MAINTENANCE_MSG)
        self._clear_maintenance_scheduled_at()

    def test_password_reset_request_blocked_during_maintenance(self, test_regular_user) -> None:
        """Password reset requests are blocked when maintenance is active."""

        past_time = self._get_past_timestamp(minutes=5)
        self._set_maintenance_scheduled_at(past_time)
        self.auth_utils.go_to_login()
        self.auth_utils.switch_to_forgot_password()
        self.auth_utils.set_email(test_regular_user.email)
        self.auth_utils.confirm()
        self.auth_utils.assert_toast_message(self.MAINTENANCE_MSG)
        self._clear_maintenance_scheduled_at()

    def test_password_reset_confirm_blocked_during_maintenance(self, test_regular_user) -> None:
        """Submitting a new password via a reset token is blocked when maintenance is active."""

        self.auth_utils.clear_test_emails()
        self.auth_utils.go_to_login()
        self.auth_utils.switch_to_forgot_password()
        self.auth_utils.set_email(test_regular_user.email)
        self.auth_utils.confirm()
        self.auth_utils.assert_toast_message("Password reset email sent successfully")
        reset_url = self.auth_utils.get_reset_link_from_email(test_regular_user.email)

        past_time = self._get_past_timestamp(minutes=5)
        self._set_maintenance_scheduled_at(past_time)
        self.driver.get(reset_url)
        self.auth_utils.set_password("NewPassword123!")
        self.auth_utils.set_confirm_password("NewPassword123!")
        self.auth_utils.confirm()
        self.auth_utils.assert_toast_message(self.MAINTENANCE_MSG)
        self._clear_maintenance_scheduled_at()
