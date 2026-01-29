"""Tests for the User Settings Page"""

import datetime as dt
import os
import subprocess
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from app.config import settings
from app.utils import verify_password
from conftest import models, BaseTest, BaseUtilsClass
from tests.utils.test_data import TOAST_USER_1_INDEX


class TestAccountSettingsPage(BaseTest):
    """Test class for the User Settings Page"""

    page_url = "settings/account"

    def setup_function(self, request) -> None:
        """Setup function"""

        self.login()

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
        self.assert_toast_message("Email change verification email sent successfully.")
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
        self.assert_toast_message("Email change verification email sent successfully.")
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
        self.assert_toast_message("Email change verification email sent successfully.")
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

    page_url = "settings/preferences"

    def setup_function(self, request) -> None:
        """Setup function"""

        self.login()

    def test_dashboard_settings(self) -> None:
        """Test changing the dashboard settings"""

        assert self.user_settings_utils.chase_threshold.get_attribute("value") == str(
            self.db_user.preferences.chase_threshold
        )
        assert self.user_settings_utils.deadline_threshold.get_attribute("value") == str(
            self.db_user.preferences.deadline_threshold
        )
        assert self.user_settings_utils.update_limit.get_attribute("value") == str(
            self.db_user.preferences.update_limit
        )

        self.set_text(self.user_settings_utils.chase_threshold, "100")
        self.set_text(self.user_settings_utils.deadline_threshold, "101")
        self.set_text(self.user_settings_utils.update_limit, "102")
        self.user_settings_utils.confirm()
        self.assert_toast_message("Preferences updated successfully.")

        assert self.db_user.preferences.chase_threshold == 100
        assert self.db_user.preferences.deadline_threshold == 101
        assert self.db_user.preferences.update_limit == 102

    def test_currency_settings(self) -> None:
        """Test changing the currency settings"""

        self.user_settings_utils.currency.select_by_visible_text("US Dollar")
        self.user_settings_utils.confirm()
        self.assert_toast_message("Preferences updated successfully.")
        assert self.db_user.preferences.default_currency == "USD"

    def test_theme_settings(self) -> None:
        """Test changing the theme settings"""

        self.user_settings_utils.get_theme("raspberry").click()
        time.sleep(0.1)
        assert self.db_user.preferences.theme == "raspberry"

    def test_toggle_dark_model(self) -> None:
        """Toggle Dark Model"""

        self.user_settings_utils.dark_mode_toggle.click()
        time.sleep(0.1)
        assert self.db_user.preferences.dark_mode


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


class PremiumSettingsUtils(BaseUtilsClass):

    def delete_stripe_data(self) -> None:
        """Delete Stripe customer data for the user"""

        response = self.client.delete("/test/delete-all-customers")
        assert response.status_code == 200

    def advance_clock(self, days: int = 15) -> None:
        """Advance the Stripe clock"""

        response = self.client.post("/test/advance-test-clock", json={"days": days})
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
        self.get_element("card-tab").click()
        self.set_text(self.get_element("payment-numberInput"), "4242 4242 4242 4242")
        self.set_text(self.get_element("payment-cvcInput"), "123")
        self.get_element("payment-countryInput", timeout=2).send_keys("United States")
        self.set_text(self.get_element("payment-expiryInput"), "1228")
        self.set_text(self.get_element("payment-postalCodeInput"), "10001")
        self.driver.switch_to.default_content()
        self.confirm_button.click()
        time.sleep(3)

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

    @property
    def confirm_button(self) -> WebElement:
        """Confirm button element"""

        return self.get_element("[data-test='confirm']", By.CSS_SELECTOR)

    @property
    def cancel_feedback(self) -> WebElement:
        """Confirm button element"""

        return self.get_element("[data-testid='cancellation_reason_cancel']", By.CSS_SELECTOR)


class TestPremiumSettingsPage(BaseTest):
    """Test class for the Premium Settings Page"""

    page_url = "settings/premium"

    def clear_stripe_customer_data(self) -> None:
        """Clear Stripe customer data for the user"""

        self.client.post("/test/delete_stripe_customer")

    def setup_function(self, request) -> None:
        """Setup function"""

        # Kill any leftover stripe processes from previous runs
        if os.name == "nt":
            subprocess.run("taskkill /F /IM stripe.exe", shell=True, capture_output=True)
        else:
            subprocess.run("pkill -f 'stripe listen'", shell=True, capture_output=True)

        stripe_cmd = r'"C:\Program Files\Stripe\stripe.exe"' if os.name == "nt" else "stripe"
        self.stripe_listener = subprocess.Popen(
            f"{stripe_cmd} listen --forward-to {settings.backend_url}/payments/webhooks",
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            shell=True,
            text=True,
        )

        # Wait for stripe listener to be ready (it outputs "Ready!" when connected)
        timeout = 30
        start_time = time.time()
        while time.time() - start_time < timeout:
            line = self.stripe_listener.stdout.readline()
            if line:
                print(f"[STRIPE] {line.strip()}")
                if "Ready!" in line:
                    break
        else:
            raise RuntimeError("Stripe listener failed to start within timeout")

        self.login()
        self.premium_settings_utils = PremiumSettingsUtils(
            self.driver,
            self.frontend_base_url,
            self.backend_base_url,
            self.db,
            self.client,
        )

    def teardown_function(self, _request) -> None:
        """Teardown function"""

        if self.stripe_listener:
            self.stripe_listener.terminate()
            self.stripe_listener.wait()

    def test_trial_card_15days(self) -> None:
        """Test the Stripe payment modal interaction"""

        # 1. Activate trial subscription and check user updated
        self.premium_settings_utils.delete_stripe_data()
        self.premium_settings_utils.subscribe_button.click()
        self.premium_settings_utils.start_trial_button.click()
        assert self.premium_settings_utils.status_title.text == "Premium (Trial)"
        assert self.db_user.premium.is_active

        # 2. Manage subscription and add payment method
        self.premium_settings_utils.manage_subscription_button.click()
        self.premium_settings_utils.add_payment_method_button.click()
        time.sleep(3)
        self.premium_settings_utils.set_payment_details()
        self.premium_settings_utils.return_to_business_link.click()
        assert self.premium_settings_utils.status_title.text == "Premium (Trial)"
        assert self.db_user.premium.is_active

        # Cancel subscription and move clock forward by 15 days
        self.premium_settings_utils.manage_subscription_button.click()
        self.premium_settings_utils.cancel_subscription_button.click()
        self.premium_settings_utils.confirm_button.click()
        self.premium_settings_utils.cancel_feedback.click()
        self.premium_settings_utils.advance_clock(15)
        self.premium_settings_utils.return_to_business_link.click()
        assert self.premium_settings_utils.status_title.text == "Free Plan"

    def test_stripe_payment_paying(self) -> None:
        """Test the Stripe payment modal interaction"""

        # 1. Activate trial subscription and check user updated
        self.premium_settings_utils.delete_stripe_data()
        self.premium_settings_utils.subscribe_button.click()
        self.premium_settings_utils.start_trial_button.click()
        assert self.premium_settings_utils.status_title.text == "Premium (Trial)"
        assert self.db_user.premium.is_active

        # 2. Manage subscription and add payment method
        self.premium_settings_utils.manage_subscription_button.click()
        self.premium_settings_utils.add_payment_method_button.click()
        time.sleep(3)
        self.premium_settings_utils.set_payment_details()
        self.premium_settings_utils.return_to_business_link.click()
        assert self.premium_settings_utils.status_title.text == "Premium (Trial)"
        assert self.db_user.premium.is_active

        # Move clock forward by 15 days
        self.premium_settings_utils.advance_clock(15)
        self.driver.refresh()
        assert self.premium_settings_utils.status_title.text == "Free Plan"
