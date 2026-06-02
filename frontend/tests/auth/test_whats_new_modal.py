from base_test import BaseTest


class TestWhatsNewModal(BaseTest):

    def test_welcome_modal_shows_for_new_user(self, session) -> None:
        """Test that the Welcome modal appears after login when user has no app_version (new user)."""

        self.db_user.app_version = None
        session.commit()

        self.login()
        modal = self.get_element("welcome-modal")
        assert "Welcome to JAM!" in modal.text

        # Navigate through all steps and close
        for _ in range(6):
            self.get_element("welcome-modal-next-button").click()
        self.wait_for_disappear("welcome-modal")

        # Verify app_version is updated in the database
        assert self.db_user.app_version is not None

    def test_whats_new_modal_shows_for_returning_user(self, session) -> None:
        """Test that the What's New carousel appears after login when user has an older app_version."""

        self.db_user.app_version = "1.0.0"
        session.commit()

        self.login()
        modal = self.get_element("whats-new-modal")
        assert "What's New" in modal.text

        # Navigate through all slides and close (slide count varies by current version)
        for _ in range(50):
            try:
                self.get_element("whats-new-modal-next-button", timeout=1).click()
            except:
                break
        self.wait_for_disappear("whats-new-modal")

        # Verify app_version is updated in the database
        assert self.db_user.app_version != "1.1.0"
        assert self.db_user.app_version != "1.0.0"

    def test_no_modal_shown_when_up_to_date(self, session) -> None:
        """Test that no modal appears when user's app_version matches the current version."""

        # Set user's app_version to a future version (already seen everything)
        self.db_user.app_version = "10.0.0"
        session.commit()
        self.login()
        assert not self.check_element_exists("whats-new-modal", timeout=3)
        assert not self.check_element_exists("welcome-modal", timeout=1)
