"""Tests for the User Settings Page"""

import datetime as dt
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from app.utils import verify_password
from conftest import models, BaseTest, BaseUtilsClass
from tests.utils.test_data import TOAST_USER_1_INDEX


class TestAccountSettingsPage(BaseTest):
    """Test class for the User Settings Page"""

    page_url = "settings"

    def setup_function(self, request) -> None:
        """Setup function"""

        self.login()
        self.user_settings_utils.go_to_account_tab()

    # ------------------------------------------------- UPDATING EMAIL -------------------------------------------------

    def test_update_email_no_password(self) -> None:
        """Test updating email without current password"""

        self.set_text(self.user_settings_utils.current_password, "")
        self.set_text(self.user_settings_utils.email, "test@test.com")
        time.sleep(1)
        self.user_settings_utils.confirm()
        self.user_settings_utils.assert_password_error_message(
            "Current password is required to update email or password"
        )

    def test_update_email_incorrect_password(self) -> None:
        """Test updating email without current password"""

        self.set_text(self.user_settings_utils.current_password, "wrong")
        self.set_text(self.user_settings_utils.email, "test@test.com")
        self.user_settings_utils.confirm()
        self.assert_toast_message("Current password is incorrect. Please try again.")

    def test_change_email_success(self) -> None:
        """Test changing the email address"""

        new_email = "newemail@email.com"
        self.clear_test_emails()
        self.set_text(self.user_settings_utils.current_password, self.user.plain_password)
        self.set_text(self.user_settings_utils.email, new_email)
        self.user_settings_utils.confirm()
        self.assert_toast_message("Verification email sent successfully.")
        verification_url = self.get_verification_link_from_email(new_email)
        self.driver.get(verification_url)
        self.assert_toast_message("Email address changed successfully. You can now log in with your new email.")
        self.db_user.email = new_email

    def test_verification_with_invalid_token_shows_error(self, session) -> None:
        """Test visiting email verification URL with an invalid or expired token shows an error message."""

        new_email = "newuser@test.com"
        self.clear_test_emails()
        self.set_text(self.user_settings_utils.current_password, self.user.plain_password)
        self.set_text(self.user_settings_utils.email, new_email)
        self.user_settings_utils.confirm()
        self.assert_toast_message("Verification email sent successfully.")
        invalid_verification_url = self.get_verification_link_from_email(new_email)[:-4]
        self.driver.get(invalid_verification_url)
        self.assert_toast_message(
            "Invalid or expired token. Please request a new one by logging in and changing your email address."
        )

    def test_expired_verification_token(self, session) -> None:
        """Test email verification with an expired token."""

        new_email = "newuser@test.com"
        self.clear_test_emails()
        self.set_text(self.user_settings_utils.current_password, self.user.plain_password)
        self.set_text(self.user_settings_utils.email, new_email)
        self.user_settings_utils.confirm()
        self.assert_toast_message("Verification email sent successfully.")
        user = session.query(models.User).filter(models.User.email == self.user.email).first()
        user.verification_token_created_at = dt.datetime.now(dt.timezone.utc) - dt.timedelta(minutes=20)
        invalid_verification_url = self.get_verification_link_from_email(new_email)[:-4]
        self.driver.get(invalid_verification_url)
        self.assert_toast_message(
            "Invalid or expired token. Please request a new one by logging in and changing your email address."
        )

    def test_change_email_already_exist(self, test_users) -> None:
        """Test changing the email address"""

        self.set_text(self.user_settings_utils.current_password, self.user.plain_password)
        self.set_text(self.user_settings_utils.email, test_users[2].email)
        self.user_settings_utils.confirm()
        self.assert_toast_message("Email is already in use. Please try a different email.")
        assert self.db_user.email == self.user.email

    def test_change_email_incorrect_format(self, test_users) -> None:
        """Test changing the email address"""

        self.set_text(self.user_settings_utils.current_password, self.user.plain_password)
        self.set_text(self.user_settings_utils.email, "f")
        self.user_settings_utils.confirm()
        self.user_settings_utils.assert_email_error_message("Email format is invalid")
        assert self.db_user.email == self.user.email

    # ------------------------------------------------ UPDATING PASSWORD -----------------------------------------------

    def test_change_password_success(self) -> None:
        """Test changing the password"""

        new_password = "newpassword"
        self.user_settings_utils.current_password.send_keys(self.user.plain_password)
        self.set_text(self.user_settings_utils.new_password, new_password)
        self.set_text(self.user_settings_utils.confirm_password, new_password)
        self.user_settings_utils.confirm()
        self.wait_for_page("login")
        self.assert_toast_message("Password updated successfully. Please log in again.")
        assert verify_password(new_password, self.db_user.password)

    def test_change_password_invalid(self) -> None:
        """Test changing the password"""

        self.user_settings_utils.current_password.send_keys(self.user.plain_password)
        self.set_text(self.user_settings_utils.new_password, "n")
        self.set_text(self.user_settings_utils.confirm_password, "n")
        self.user_settings_utils.confirm()
        self.user_settings_utils.assert_new_password_error_message("New password must be at least 8 characters long")
        assert verify_password(self.user.plain_password, self.db_user.password)

    def test_change_password_nonmatching(self) -> None:
        """Test changing the password"""

        self.user_settings_utils.current_password.send_keys(self.user.plain_password)
        self.set_text(self.user_settings_utils.new_password, "testpassword")
        self.set_text(self.user_settings_utils.confirm_password, "n")
        self.user_settings_utils.confirm()
        self.user_settings_utils.assert_confirm_password_error_message("Passwords do not match")
        assert verify_password(self.user.plain_password, self.db_user.password)


class TestPreferenceSettingsPage(BaseTest):
    """Test class for the Preference Settings Page"""

    page_url = "settings"

    def setup_function(self, request) -> None:
        """Setup function"""

        self.login()
        self.user_settings_utils.go_to_preferences_tab()

    def test_theme_hint(self) -> None:
        """Test theme hint"""

        assert self.user_settings_utils.theme_hint.text == (
            "Mixed Berry is not your favourite flavour of JAM?! You can easily pick "
            "another theme by clicking on the JAM logo in the sidebar."
        )

    def test_dashboard_settings(self) -> None:
        """Test changing the dashboard settings"""

        assert self.db_user.chase_threshold == 14
        assert self.db_user.deadline_threshold == 7
        assert self.db_user.update_limit == 10

        self.set_text(self.user_settings_utils.chase_threshold, "100")
        self.set_text(self.user_settings_utils.deadline_threshold, "101")
        self.set_text(self.user_settings_utils.update_limit, "102")
        self.user_settings_utils.confirm()
        time.sleep(0.1)

        assert self.db_user.chase_threshold == 100
        assert self.db_user.deadline_threshold == 101
        assert self.db_user.update_limit == 102


class TestQualificationSettingsPage(BaseTest):
    """Test class for the Qualification Settings Page"""

    page_url = "settings"
    user_index = TOAST_USER_1_INDEX

    def setup_function(self, request) -> None:
        """Setup function"""

        self.login()
        self.user_settings_utils.go_to_qualifications_tab()

    def test_qualification_settings(self) -> None:
        """Test changing the qualification settings"""

        self.set_text(self.user_settings_utils.qualities_input, "New Quality")
        self.set_text(self.user_settings_utils.experience_input, "New Experience")
        self.user_settings_utils.confirm()
        self.assert_toast_message("Qualifications saved successfully.")
        assert self.db.query(models.UserQualification).filter_by(owner_id=self.user.id).count() == 1
        self.set_text(self.user_settings_utils.experience_input, "Different Experience")
        self.user_settings_utils.confirm()
        self.assert_toast_message("Qualifications saved successfully.")
        assert self.db.query(models.UserQualification).filter_by(owner_id=self.user.id).count() == 1
        qualification = self.db.query(models.UserQualification).filter_by(owner_id=self.user.id).first()
        assert qualification.qualities == "New Quality"
        assert qualification.experience == "Different Experience"


class PremiumSettingsUtils(BaseUtilsClass):

    def delete_stripe_data(self) -> None:
        """Delete Stripe customer data for the user"""

        response = self.client.delete("/test/delete-all-customers")
        assert response.status_code == 200

    def call_stripe_create_webhook(self, user) -> None:
        """Call Stripe webhook to simulate an event"""

        response = self.client.post(
            "/test/webhook",
            json={"type": "customer.subscription.created", "customer_id": user.stripe_details.customer_id},
        )
        assert response.status_code == 200

    @property
    def subscribe_button(self) -> WebElement:
        """Subscribe button element"""

        return self.get_element("subscribe-button")

    @property
    def manage_subscription_button(self) -> WebElement:
        """Manage subscription button element"""

        return self.get_element("manage-subscription-button")

    def set_payment_details(self) -> None:
        """Set payment details in the Stripe iframe"""

        self.driver.switch_to.frame(0)
        self.set_text(self.get_element("Field-numberInput"), "4242 4242 4242 4242")
        self.set_text(self.get_element("Field-cvcInput"), "123")
        self.get_element("Field-countryInput").send_keys("United States")
        self.set_text(self.get_element("Field-expiryInput"), "1228")
        self.set_text(self.get_element("Field-postalCodeInput"), "10001")
        self.driver.switch_to.default_content()
        self.get_element("[data-test='confirm']", By.CSS_SELECTOR).click()

    @property
    def status_title(self) -> WebElement:
        """Status title element"""

        return self.get_element("status-title")

    @property
    def add_payment_method_button(self) -> WebElement:
        """Add payment method button element"""

        return self.get_element("[data-test='add-payment-method']", By.CSS_SELECTOR)

    @property
    def cancel_subscription_button(self) -> WebElement:
        """Cancel subscription button element"""

        return self.get_element("[data-test='cancel-subscription']", By.CSS_SELECTOR)

    @property
    def return_to_business_link(self) -> WebElement:
        """Return to business link element"""

        return self.get_element("[data-testid='return-to-business-link']", By.CSS_SELECTOR)

    @property
    def start_trial_button(self) -> WebElement:
        """Start trial button element"""

        return self.get_element("[data-testid='hosted-payment-submit-button']", By.CSS_SELECTOR)


class TestPremiumSettingsPage(BaseTest):
    """Test class for the Premium Settings Page"""

    page_url = "settings/premium"

    def clear_stripe_customer_data(self) -> None:
        """Clear Stripe customer data for the user"""

        self.client.post("/test/delete_stripe_customer")

    def setup_function(self, request) -> None:
        """Setup function"""

        self.login()
        self.user_settings_utils.go_to_premium_tab()
        self.premium_settings_utils = PremiumSettingsUtils(
            self.driver,
            self.frontend_base_url,
            self.backend_base_url,
            self.db,
            self.client,
        )

    def test_premium_page_content(self) -> None:
        """Test premium page content"""

        assert self.check_element_exists("subscribe-button")

    def test_stripe_payment(self) -> None:
        """Test the Stripe payment modal interaction"""

        # Activate trial subscription
        self.premium_settings_utils.delete_stripe_data()
        self.premium_settings_utils.subscribe_button.click()
        self.premium_settings_utils.start_trial_button.click()
        time.sleep(1)
        self.premium_settings_utils.call_stripe_create_webhook(self.db_user)
        time.sleep(3)
        assert self.premium_settings_utils.status_title.text == "Premium (Trial)"
        assert self.db_user.premium.is_active

        # Manage subscription and add payment method
        self.premium_settings_utils.manage_subscription_button.click()
        self.premium_settings_utils.add_payment_method_button.click()
        self.premium_settings_utils.set_payment_details()
        self.premium_settings_utils.return_to_business_link.click()
