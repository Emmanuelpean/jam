"""Tests for the User Settings Page"""

from frontend_base_test import models, BaseTest


class TestQualificationSettingsPage(BaseTest):
    """Test class for the Qualification Settings Page"""

    page_url = "settings/qualifications"

    EXPERIENCE_CHAR_LIMIT = 10000
    OTHER_CHAR_LIMIT = 3500

    def setup_function(self, request) -> None:
        """Setup function"""

        self.login()

    @property
    def qualifications(self) -> list[models.UserQualification]:
        """The qualifications owned by the test user, refreshed from the database."""

        return self.db.query(models.UserQualification).filter_by(owner_id=self.user.id).all()

    def test_qualification_settings(self) -> None:
        """Test changing the qualification settings"""

        self.set_text(self.user_settings_utils.qualities_input, "New Quality")
        self.set_text(self.user_settings_utils.experience_input, "New Experience")
        self.user_settings_utils.confirm()
        self.toast_utils.assert_toast_message("Qualifications saved successfully.")
        assert len(self.qualifications) == 1

        # Modify qualifications
        self.set_text(self.user_settings_utils.experience_input, "Different Experience")
        self.user_settings_utils.confirm()
        self.toast_utils.assert_toast_message("Qualifications saved successfully.")
        assert len(self.qualifications) == 1
        assert self.qualifications[0].qualities == "New Quality"
        assert self.qualifications[0].experience == "Different Experience"

        # Refresh page and modify qualifications
        self.driver.refresh()
        self.set_text(self.user_settings_utils.experience_input, "Different Experience1")
        self.user_settings_utils.confirm()
        self.toast_utils.assert_toast_message("Qualifications saved successfully.")
        assert len(self.qualifications) == 1
        assert self.qualifications[0].qualities == "New Quality"
        assert self.qualifications[0].experience == "Different Experience1"

    def test_experience_char_limit_disables_save(self) -> None:
        """Test that exceeding the experience character limit disables the save button."""

        over_limit_text = "a" * (self.EXPERIENCE_CHAR_LIMIT + 1)
        self.set_text(self.user_settings_utils.experience_input, over_limit_text)
        confirm_button = self.get_element("confirm-button", enabled=False)
        assert not confirm_button.is_enabled()

    def test_skills_char_limit_disables_save(self) -> None:
        """Test that exceeding the skills character limit disables the save button."""

        over_limit_text = "a" * (self.OTHER_CHAR_LIMIT + 1)
        self.set_text(self.user_settings_utils.skills_input, over_limit_text)
        confirm_button = self.get_element("confirm-button", enabled=False)
        assert not confirm_button.is_enabled()
