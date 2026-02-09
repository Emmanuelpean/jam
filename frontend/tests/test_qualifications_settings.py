"""Tests for the User Settings Page"""

from conftest import models, BaseTest
from tests.utils.test_data import TOAST_USER_1_INDEX


class TestQualificationSettingsPage(BaseTest):
    """Test class for the Qualification Settings Page"""

    page_url = "settings/qualifications"
    user_index = TOAST_USER_1_INDEX

    def setup_function(self, request) -> None:
        """Setup function"""

        self.login()

    def test_qualification_settings(self) -> None:
        """Test changing the qualification settings"""

        self.set_text(self.user_settings_utils.qualities_input, "New Quality")
        self.set_text(self.user_settings_utils.experience_input, "New Experience")
        self.user_settings_utils.confirm()
        self.assert_toast_message("Qualifications saved successfully.")
        assert self.db.query(models.UserQualification).filter_by(owner_id=self.user.id).count() == 1

        # Modify qualifications
        self.set_text(self.user_settings_utils.experience_input, "Different Experience")
        self.user_settings_utils.confirm()
        self.assert_toast_message("Qualifications saved successfully.")
        assert self.db.query(models.UserQualification).filter_by(owner_id=self.user.id).count() == 1
        qualification = self.db.query(models.UserQualification).filter_by(owner_id=self.user.id).first()
        assert qualification.qualities == "New Quality"
        assert qualification.experience == "Different Experience"

        # Refresh page and modify qualifications
        self.driver.refresh()
        self.set_text(self.user_settings_utils.experience_input, "Different Experience1")
        self.user_settings_utils.confirm()
        self.assert_toast_message("Qualifications saved successfully.")
        assert self.db.query(models.UserQualification).filter_by(owner_id=self.user.id).count() == 1
        self.db.expire_all()
        qualification = self.db.query(models.UserQualification).filter_by(owner_id=self.user.id).first()
        assert qualification.qualities == "New Quality"
        assert qualification.experience == "Different Experience1"
