from tests.fixtures.users import FixtureUser
from frontend_base_test import BaseTest


class TestDemoLogin(BaseTest):

    user_fixture = "test_demo_user"

    def setup_function(self, request) -> None:
        """Setup for each test method."""

        self.auth_utils.go_to_login()

    def test_demo_login_shows_banner(self) -> None:
        """Clicking 'Try Demo' must log in and display the demo banner."""

        self.auth_utils.try_button.click()
        self.auth_utils.wait_for_dashboard()

        banner = self.get_element("demo-banner")
        assert "demo account" in banner.text.lower()

    def test_demo_logout_cancel_stays_logged_in(self) -> None:
        """Cancelling the demo logout confirmation must keep the user on the dashboard."""

        self.auth_utils.try_button.click()
        self.auth_utils.wait_for_dashboard()
        self.wait_for_disappear("loading-spinner")

        # Click logout
        self.close_modal()
        self.get_element("logout-btn").click()
        self.logout_modal_utils.cancel_button.click()

        # Still on dashboard, banner still visible
        assert self.check_element_exists("demo-banner")

        # Fully log out
        self.get_element("logout-btn").click()
        self.logout_modal_utils.confirm_button.click()

        self.auth_utils.wait_for_login()

    def test_regular_user_has_no_demo_banner(self, test_regular_user: FixtureUser) -> None:
        """A regular user must not see the demo banner after login."""

        self.auth_utils.set_email(test_regular_user.email)
        self.auth_utils.set_password(test_regular_user.plain_password)
        self.auth_utils.confirm()
        self.auth_utils.wait_for_dashboard()

        assert not self.check_element_exists("demo-banner", timeout=2)
