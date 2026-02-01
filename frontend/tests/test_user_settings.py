"""Tests for the User Settings Page"""

import datetime as dt
import os
import subprocess
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.select import Select

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
        self.assert_toast_message("The current password is incorrect.")

    def test_change_email_success(self) -> None:
        """Test changing the email address"""

        new_email = "newemail@email.com"
        self.clear_test_emails()
        self.set_text(self.user_settings_utils.current_password, self.user.plain_password)
        self.set_text(self.user_settings_utils.email, new_email)
        self.user_settings_utils.confirm()
        self.assert_toast_message("Email change verification email sent successfully.")
        assert new_email in self.get_element("pending-email-info").text
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
        self.assert_toast_message("Email already registered")
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

    # -------------------------------------------------- DATA EXPORT ---------------------------------------------------

    def test_download_data_export(self) -> None:
        """Test downloading user data export"""

        # Find and click the download data button
        self.user_settings_utils.download_data_button.click()

        # Wait for the download to complete (toast notification)
        self.assert_toast_message("Data downloaded")

    # ------------------------------------------------ ACCOUNT DELETION ------------------------------------------------

    def test_delete_account_cancel_first_modal(self) -> None:
        """Test cancelling account deletion from the first modal"""

        self.user_settings_utils.delete_account_button.click()
        self.user_settings_utils.cancel_delete_button.click()
        assert self.db_user is not None
        assert self.db_user.email == self.user.email

    def test_delete_account_cancel_confirmation_modal(self) -> None:
        """Test cancelling account deletion from the confirmation modal"""

        self.user_settings_utils.delete_account_button.click()
        self.set_text(self.user_settings_utils.delete_password, self.user.plain_password)
        self.user_settings_utils.continue_delete_button.click()
        self.user_settings_utils.cancel_confirm_delete_button.click()
        assert self.db_user is not None
        assert self.db_user.email == self.user.email

    def test_delete_account_success(self, session) -> None:
        """Test successful account deletion"""

        user_id = self.user.id
        self.user_settings_utils.delete_account_button.click()
        self.set_text(self.user_settings_utils.delete_password, self.user.plain_password)
        self.user_settings_utils.continue_delete_button.click()
        self.user_settings_utils.final_delete_button.click()
        self.wait_for_page("login")
        self.assert_toast_message("Your account has been permanently deleted.")
        deleted_user = session.query(models.User).filter(models.User.id == user_id).first()
        assert deleted_user is None

    def test_delete_account_wrong_password(self) -> None:
        """Test account deletion with wrong password"""

        self.user_settings_utils.delete_account_button.click()
        self.set_text(self.user_settings_utils.delete_password, self.user.plain_password + "something")
        self.user_settings_utils.continue_delete_button.click()
        self.user_settings_utils.final_delete_button.click()
        self.assert_toast_message("Failed to delete account. Password is incorrect.")
        assert self.db_user is not None
        assert self.db_user.email == self.user.email

    def test_download_data_before_deletion(self, session) -> None:
        """Test downloading data from the confirmation modal before deletion"""

        self.user_settings_utils.delete_account_button.click()
        self.set_text(self.user_settings_utils.delete_password, self.user.plain_password)
        self.user_settings_utils.continue_delete_button.click()
        self.user_settings_utils.download_data_modal_button.click()
        self.assert_toast_message("Data downloaded")


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
        self.advance_browser_clock_days(days)

    @property
    def subscription_button(self) -> WebElement:
        """Subscribe button element"""

        return self.get_element("subscription-button")

    def assert_status_title(self, expected_title: str) -> None:
        """Assert status title"""

        assert self.wait_for_element_text("status-title", expected_title)

    def assert_status_message(self, expected_message: str) -> None:
        """Assert status message"""

        assert self.wait_for_element_text("status-message", expected_message)

    @property
    def stripe_add_payment_method_button(self) -> WebElement:
        """Add payment method button element"""

        return self.get_element("[data-test='add-payment-method']", By.CSS_SELECTOR)

    @property
    def stripe_cancel_subscription_button(self) -> WebElement:
        """Cancel subscription button element"""

        return self.get_element("[data-test='cancel-subscription']", By.CSS_SELECTOR)

    @property
    def stripe_return_to_business_link(self) -> WebElement:
        """Return to business link element"""

        return self.get_element("[data-testid='return-to-business-link']", By.CSS_SELECTOR)

    @property
    def stripe_start_trial_button(self) -> WebElement:
        """Start trial button element"""

        return self.get_element("[data-testid='hosted-payment-submit-button']", By.CSS_SELECTOR)

    @property
    def stripe_confirm_button(self) -> WebElement:
        """Confirm button element"""

        return self.get_element("[data-test='confirm']", By.CSS_SELECTOR)

    @property
    def stripe_cancel_feedback(self) -> WebElement:
        """Confirm button element"""

        return self.get_element("[data-testid='cancellation_reason_cancel']", By.CSS_SELECTOR)

    def set_stripe_payment_details(self) -> None:
        """Set payment details in the Stripe iframe"""

        self.driver.switch_to.frame(0)
        self.get_element("card-tab").click()
        self.set_text(self.get_element("payment-numberInput"), "4242 4242 4242 4242")
        self.set_text(self.get_element("payment-cvcInput"), "123")
        self.get_element("payment-countryInput", timeout=2).send_keys("United States")
        self.set_text(self.get_element("payment-expiryInput"), "1228")
        self.set_text(self.get_element("payment-postalCodeInput"), "10001")
        self.driver.switch_to.default_content()
        self.stripe_confirm_button.click()
        time.sleep(3)


class TestPremiumSettingsPage(BaseTest):
    """Test class for the Premium Settings Page"""

    page_url = "settings/premium"

    def clear_stripe_customer_data(self) -> None:
        """Clear Stripe customer data for the user"""

        self.client.post("/test/delete_stripe_customer")

    def setup_function(self, request) -> None:
        """Setup function"""

        # Check if we're in CI (GitHub Actions) - if so, skip starting listener
        is_ci = os.getenv("CI") == "true"

        if not is_ci:
            # Kill any leftover stripe processes from previous runs
            if os.name == "nt":
                subprocess.run("taskkill /F /IM stripe.exe", shell=True, capture_output=True)
            else:
                subprocess.run("pkill -f 'stripe listen'", shell=True, capture_output=True)

            stripe_cmd = r'"C:\Program Files\Stripe\stripe.exe"' if os.name == "nt" else "stripe"
            stripe_api_key = settings.stripe_api_key
            self.stripe_listener = subprocess.Popen(
                f"{stripe_cmd} listen --api-key {stripe_api_key} --forward-to {settings.backend_url}/payments/webhooks",
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
        else:
            # In CI, the listener is already running, so just set to None
            self.stripe_listener = None

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

    def _activate_trial(self) -> None:
        """Activate the user trial"""

        self.premium_settings_utils.delete_stripe_data()
        assert self.premium_settings_utils.subscription_button.text == "Start Free Trial"
        self.premium_settings_utils.subscription_button.click()
        self.premium_settings_utils.stripe_start_trial_button.click()
        self.wait_for_page("settings/premium?success=true")
        self.premium_settings_utils.assert_status_title("Premium (Trial)")
        self.premium_settings_utils.assert_status_message("14 days remaining in your free trial")
        assert self.db_user.premium.is_active

    def _add_payment_method(self) -> None:
        """Add payment method"""

        self.premium_settings_utils.subscription_button.click()
        self.premium_settings_utils.stripe_add_payment_method_button.click()
        time.sleep(3)
        self.premium_settings_utils.set_stripe_payment_details()
        self.premium_settings_utils.stripe_return_to_business_link.click()
        self.premium_settings_utils.assert_status_title("Premium (Trial)")
        assert self.db_user.premium.is_active

    def test_trial_payment(self) -> None:
        """Test the Stripe payment modal interaction"""

        self._activate_trial()
        self._add_payment_method()
        self.premium_settings_utils.advance_clock(15)
        self.premium_settings_utils.assert_status_title("Premium")
        assert self.premium_settings_utils.subscription_button.text == "Manage Subscription"

    def test_trial_elapses(self) -> None:
        """Test the Stripe payment modal interaction"""

        # 1. Activate trial subscription and check user updated
        self._activate_trial()

        # 2. Move clock forward by 13 days and check that 1 day is left on trial
        self.premium_settings_utils.advance_clock(13)
        self.premium_settings_utils.assert_status_title("Premium (Trial)")
        self.premium_settings_utils.assert_status_message("1 day remaining in your free trial")
        assert self.premium_settings_utils.subscription_button.text == "Manage Subscription"
        assert self.db_user.premium.is_active

        # 3. Move the clock further by 2 days and ensure that the user is not premium any more
        self.premium_settings_utils.advance_clock(2)
        self.premium_settings_utils.assert_status_title("Free Plan")
        assert self.premium_settings_utils.subscription_button.text == "Subscribe"
        assert not self.db_user.premium.is_active

    def test_trial_card_15days_card(self) -> None:
        """Test the Stripe payment modal interaction
        1. Activate trial subscription
        2. Add payment method
        3. Cancel subscription and move the clock forward by 15 days
        4. Subscribe again"""

        # 1. Activate trial subscription and check user updated
        self._activate_trial()

        # 2. Manage subscription and add payment method
        self._add_payment_method()

        # 3. Cancel subscription and move clock forward by 15 days, the subscription should be cancelled
        self.premium_settings_utils.subscription_button.click()
        self.premium_settings_utils.stripe_cancel_subscription_button.click()
        self.premium_settings_utils.stripe_confirm_button.click()
        self.premium_settings_utils.stripe_cancel_feedback.click()
        self.premium_settings_utils.advance_clock(15)
        self.premium_settings_utils.stripe_return_to_business_link.click()
        self.wait_for_page("settings/premium?success=true")
        self.premium_settings_utils.assert_status_title("Free Plan")

        # Try to subscribe again
        self.premium_settings_utils.subscription_button.click()
        self.get_element("[data-testid='card-accordion-item']", By.CSS_SELECTOR).click()
        self.set_text(self.get_element("cardNumber"), "4242 4242 4242 4242")
        self.set_text(self.get_element("cardCvc"), "123")
        Select(self.get_element("billingCountry", By.NAME)).select_by_visible_text("United Kingdom")
        self.set_text(self.get_element("cardExpiry"), "1228")
        self.set_text(self.get_element("billingName"), "Test User")
        self.get_element("[data-testid='hosted-payment-submit-button']", By.CSS_SELECTOR).click()
        self.wait_for_page("settings/premium?success=true")
        self.premium_settings_utils.assert_status_title("Premium")

    def test_delete_user_with_subscription(self) -> None:
        """Test deleting user with active subscription"""

        self._activate_trial()
        self._add_payment_method()
        self.user_settings_utils.go_to_account_tab()
        assert self.db_user.stripe_details.subscription_id is not None
        self.user_settings_utils.delete_account_button.click()
        self.set_text(self.user_settings_utils.delete_password, self.user.plain_password)
        self.user_settings_utils.continue_delete_button.click()
        self.user_settings_utils.final_delete_button.click()
        self.wait_for_page("login")
        self.assert_toast_message("Your account has been permanently deleted.")
