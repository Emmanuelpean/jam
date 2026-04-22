"""Tests for the User Settings Page"""

import os
import subprocess
import threading
import time

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select

from base_test import models, BaseTest
from tests.utils.create_data.utils import create_db_entries
from tests.utils.test_data import TOAST_USER_1_INDEX


@pytest.mark.xdist_group("stripe")
class TestPremiumSettingsPage(BaseTest):
    """Test class for the Premium Settings Page"""

    page_url = "settings/premium"
    _stripe_listener = None

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
            f"{stripe_cmd} listen --forward-to {self.backend_base_url}/payments/webhooks",
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

        # Start a thread to continuously drain stdout so the buffer doesn't fill up and block
        def drain_stdout() -> None:
            """Drain the stripe listener stdout to prevent it from filling up the buffer"""
            for l in self.stripe_listener.stdout:
                print(f"[STRIPE] {l.strip()}")

        self._stripe_drain_thread = threading.Thread(target=drain_stdout, daemon=True)
        self._stripe_drain_thread.start()

        self.login()

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

    def _add_payment_method_during_trial(self) -> None:
        """Add payment method during the trial"""

        self.premium_settings_utils.subscription_button.click()
        self.premium_settings_utils.stripe_add_payment_method_button.click()
        time.sleep(3)
        self.premium_settings_utils.set_stripe_payment_details()
        self.premium_settings_utils.stripe_return_to_business_link.click()
        self.premium_settings_utils.assert_status_title("Premium (Trial)")
        assert self.db_user.premium.is_active

    def _add_payment_method_no_subscription(self) -> None:
        """Add a payment method while the user doesn't have an active subscription"""

        self.premium_settings_utils.subscription_button.click()
        try:
            self.get_element("[data-testid='card-accordion-item']", By.CSS_SELECTOR).click()
        except:
            pass
        self.set_text(self.get_element("cardNumber"), "4242 4242 4242 4242")
        self.set_text(self.get_element("cardCvc"), "123")
        Select(self.get_element("billingCountry", By.NAME)).select_by_visible_text("United Kingdom")
        self.set_text(self.get_element("cardExpiry"), "1228")
        self.set_text(self.get_element("billingName"), "Test User")
        self.get_element("[data-testid='hosted-payment-submit-button']", By.CSS_SELECTOR).click()
        self.wait_for_page("settings/premium?success=true", 20)

    def _cancel_subscription(self) -> None:
        """Cancel the user subscription"""

        self.premium_settings_utils.subscription_button.click()
        self.premium_settings_utils.stripe_cancel_subscription_button.click()
        self.premium_settings_utils.stripe_confirm_button.click()
        self.premium_settings_utils.stripe_cancel_feedback.click()
        self.premium_settings_utils.stripe_return_to_business_link.click()
        self.wait_for_page("settings/premium?success=true")

    def test_trial_payment(self) -> None:
        """Test the Stripe payment modal interaction
        Activate the trial, add a payment method and move the clock forward by 15 days"""

        self._activate_trial()
        self._add_payment_method_during_trial()
        self.premium_settings_utils.advance_clock(15)
        self.premium_settings_utils.assert_status_title("Premium")
        assert self.premium_settings_utils.subscription_button.text == "Manage Subscription"

    def test_trial_elapses(self) -> None:
        """Test the Stripe payment modal interaction
        Activate the trial subscription, move the clock by 13 days, move the clock by 2 days, and check that the
        subscription is cancelled"""

        # 1. Activate the trial subscription and check user was updated
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

    def test_trial_subscribe_cancel_subscribe(self) -> None:
        """Test the Stripe payment modal interaction
        1. Activate the trial subscription and add payment method
        3. Cancel subscription and move the clock forward by 15 days
        4. Subscribe again"""

        # 1. Activate the trial subscription and add payment method
        self._activate_trial()
        self._add_payment_method_during_trial()

        # 2. Cancel the subscription and move clock forward by 15 days, the subscription should be cancelled
        self._cancel_subscription()
        self.premium_settings_utils.advance_clock(15)
        self.premium_settings_utils.assert_status_title("Free Plan")

        # 3. Subscribe again
        self._add_payment_method_no_subscription()
        self.premium_settings_utils.assert_status_title("Premium")

    def test_delete_user_with_subscription(self) -> None:
        """Test deleting user with active subscription"""

        self._activate_trial()
        self._add_payment_method_during_trial()
        self.user_settings_utils.go_to_account_tab()
        assert self.db_user.stripe_details.subscription_id is not None
        self.user_settings_utils.delete_account_button.click()
        self.set_text(self.user_settings_utils.delete_password, self.user.plain_password)
        self.user_settings_utils.continue_delete_button.click()
        self.user_settings_utils.final_delete_button.click()
        self.wait_for_page("login")
        self.assert_toast_message("Your account has been permanently deleted.")


class TestForwardingConfirmationLinks(BaseTest):
    """Test suite for forwarding confirmation link UI on the Premium tab."""

    user_index = TOAST_USER_1_INDEX
    page_url = "settings/premium"
    _link: models.ForwardingConfirmationLink = None

    def _create_confirmation_link(self, is_used: bool = False, **kwargs) -> models.ForwardingConfirmationLink:
        """Helper to create a forwarding confirmation link in the database."""

        return create_db_entries(
            self.db,
            models.ForwardingConfirmationLink,
            {
                "email_external_id": "ext_test_123",
                "url": "https://mail.google.com/confirm/abc123",
                "platform": "gmail",
                "is_used": is_used,
                "owner_id": self.user.id,
                **kwargs,
            },
        )[0]

    def setup_function(self, request) -> None:
        """Setup for each test function."""

        self._link = self._create_confirmation_link()
        self.login()

    def test_confirmation_alert_displayed(self) -> None:
        """Test that the confirmation alert is displayed when a pending link exists."""

        heading = self.premium_settings_utils.confirmation_link_heading
        assert "gmail forwarding confirmation required" in heading.text.lower()

    def test_dismiss_alert_shows_confirm_prompt(self) -> None:
        """Test dismissing the alert shows the showConfirm modal."""

        self.premium_settings_utils.dismiss_confirmation_link_alert()
        prompt = self.premium_settings_utils.confirmation_link_prompt
        assert prompt.is_displayed()

    def test_mark_as_used_success(self) -> None:
        """Test confirming marks the link as used and removes the alert."""

        self.premium_settings_utils.dismiss_confirmation_link_alert()
        self.premium_settings_utils.confirmation_link_confirm_button.click()

        self.assert_toast_message("Confirmation link marked as used")

        # Verify in database
        self.db.expire_all()
        link = self.db.query(models.ForwardingConfirmationLink).filter_by(id=self._link.id).first()
        assert link.is_used

    def test_keep_link(self) -> None:
        """Test clicking cancel keeps the alert visible."""

        self.premium_settings_utils.dismiss_confirmation_link_alert()
        self.premium_settings_utils.confirmation_link_cancel_button.click()

        # Alert should still be visible
        alert = self.premium_settings_utils.confirmation_link_alert
        assert alert.is_displayed()
        heading = self.premium_settings_utils.confirmation_link_heading
        assert "gmail forwarding confirmation required" in heading.text.lower()

    def test_no_alert_when_link_is_used(self) -> None:
        """Test that no confirmation alert is shown when the link is already used."""

        # Mark the existing link as used
        link = self.db.query(models.ForwardingConfirmationLink).filter_by(id=self._link.id).first()
        link.is_used = True
        self.db.commit()

        # Refresh page
        self.driver.refresh()
        time.sleep(1)

        # Verify no alert exists
        assert not self.check_element_exists("confirmation-link-alert")
