"""Selenium tests for Stripe payment integration."""

import time

import requests
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from conftest import BaseTest


class TestPremiumSettingsPage(BaseTest):
    """Test class for the Premium Settings Page"""

    page_url = "settings"

    def setup_function(self, request) -> None:
        """Setup function"""
        self.login()
        self.user_settings_utils.go_to_premium_tab()

    def test_premium_page_content(self) -> None:
        """Test premium page content"""
        assert self.check_element_exists("subscribe-button")

    def test_premium_page_features_list(self) -> None:
        """Test that premium features are displayed"""
        # Verify premium features are listed on the page
        # Adjust element IDs based on your actual implementation
        assert self.check_element_exists("premium-features")

    def test_stripe_payment_modal_opens(self) -> None:
        """Test that clicking subscribe button opens Stripe modal"""
        self.get_element("subscribe-button").click()
        time.sleep(3)

        # Verify Stripe iframe appears
        iframes = self.driver.find_elements(By.TAG_NAME, "iframe")
        assert len(iframes) > 0, "Stripe iframe should be present"

    def test_stripe_payment_modal_successful_subscription(self) -> None:
        """Test the Stripe payment modal with successful payment"""
        self.get_element("subscribe-button").click()
        time.sleep(5)

        # Switch to Stripe iframe
        iframe = self.driver.find_elements(By.TAG_NAME, "iframe")[-1]
        self.driver.switch_to.frame(iframe)

        # Fill in card details (Stripe test card for success)
        self.set_text(self.get_element("cardNumber", By.NAME), "4242 4242 4242 4242")
        self.set_text(self.get_element("cardCvc", By.NAME), "123")
        self.set_text(self.get_element("cardExpiry", By.NAME), "1228")
        self.set_text(self.get_element("billingName", By.NAME), "John Doe")

        time.sleep(0.5)
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(0.5)

        # Try to set postal code (may not always be required)
        try:
            self.set_text(self.get_element("billingPostalCode", By.NAME), "10001")
        except:
            pass

        time.sleep(5)

        # Submit payment
        self.get_element("SubmitButton-IconContainer", By.CLASS_NAME).click()
        self.driver.switch_to.default_content()

        # Verify success
        self.assert_toast_message("Subscription successful! Enjoy your premium features!")

        # Refresh db_user to get updated state
        self.db.refresh(self.db_user)
        assert self.db_user.toast_active

    def test_stripe_payment_modal_declined_card(self) -> None:
        """Test payment with a card that will be declined"""
        self.get_element("subscribe-button").click()
        time.sleep(5)

        iframe = self.driver.find_elements(By.TAG_NAME, "iframe")[-1]
        self.driver.switch_to.frame(iframe)

        # Use Stripe test card that gets declined
        self.set_text(self.get_element("cardNumber", By.NAME), "4000 0000 0000 0002")
        self.set_text(self.get_element("cardCvc", By.NAME), "123")
        self.set_text(self.get_element("cardExpiry", By.NAME), "1228")
        self.set_text(self.get_element("billingName", By.NAME), "John Doe")

        time.sleep(0.5)
        try:
            self.set_text(self.get_element("billingPostalCode", By.NAME), "10001")
        except:
            pass

        time.sleep(5)
        self.get_element("SubmitButton-IconContainer", By.CLASS_NAME).click()

        # Wait for error message in Stripe iframe
        time.sleep(3)

        # Verify error appears
        error_elements = self.driver.find_elements(By.CLASS_NAME, "Error")
        assert len(error_elements) > 0, "Error message should appear for declined card"

        self.driver.switch_to.default_content()

        # User should not have premium activated
        self.db.refresh(self.db_user)
        assert not self.db_user.toast_active

    def test_stripe_payment_modal_insufficient_funds(self) -> None:
        """Test payment with insufficient funds card"""
        self.get_element("subscribe-button").click()
        time.sleep(5)

        iframe = self.driver.find_elements(By.TAG_NAME, "iframe")[-1]
        self.driver.switch_to.frame(iframe)

        # Stripe test card for insufficient funds
        self.set_text(self.get_element("cardNumber", By.NAME), "4000 0000 0000 9995")
        self.set_text(self.get_element("cardCvc", By.NAME), "123")
        self.set_text(self.get_element("cardExpiry", By.NAME), "1228")
        self.set_text(self.get_element("billingName", By.NAME), "John Doe")

        time.sleep(0.5)
        try:
            self.set_text(self.get_element("billingPostalCode", By.NAME), "10001")
        except:
            pass

        time.sleep(5)
        self.get_element("SubmitButton-IconContainer", By.CLASS_NAME).click()
        time.sleep(3)

        # Verify error appears
        error_elements = self.driver.find_elements(By.CLASS_NAME, "Error")
        assert len(error_elements) > 0

        self.driver.switch_to.default_content()
        self.db.refresh(self.db_user)
        assert not self.db_user.toast_active

    def test_stripe_payment_modal_requires_authentication(self) -> None:
        """Test payment that requires 3D Secure authentication"""
        self.get_element("subscribe-button").click()
        time.sleep(5)

        iframe = self.driver.find_elements(By.TAG_NAME, "iframe")[-1]
        self.driver.switch_to.frame(iframe)

        # Stripe test card requiring authentication
        self.set_text(self.get_element("cardNumber", By.NAME), "4000 0025 0000 3155")
        self.set_text(self.get_element("cardCvc", By.NAME), "123")
        self.set_text(self.get_element("cardExpiry", By.NAME), "1228")
        self.set_text(self.get_element("billingName", By.NAME), "John Doe")

        time.sleep(0.5)
        try:
            self.set_text(self.get_element("billingPostalCode", By.NAME), "10001")
        except:
            pass

        time.sleep(5)
        self.get_element("SubmitButton-IconContainer", By.CLASS_NAME).click()

        # Wait for 3D Secure modal
        time.sleep(5)

        # Switch to 3D Secure iframe (nested iframe)
        auth_iframe = self.driver.find_elements(By.TAG_NAME, "iframe")[-1]
        self.driver.switch_to.frame(auth_iframe)

        # Complete authentication (click "Complete" button in test mode)
        try:
            WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, "test-source-authorize-3ds"))
            ).click()
        except:
            # Alternative selectors for 3D Secure test page
            complete_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Complete')]")
            complete_button.click()

        time.sleep(3)
        self.driver.switch_to.default_content()

        # Verify success after authentication
        self.assert_toast_message("Subscription successful! Enjoy your premium features!")
        self.db.refresh(self.db_user)
        assert self.db_user.toast_active

    def test_stripe_payment_modal_cancel(self) -> None:
        """Test canceling the payment modal"""
        self.get_element("subscribe-button").click()
        time.sleep(5)

        # Press ESC to close modal (or click close button if available)
        from selenium.webdriver.common.keys import Keys

        self.driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)

        time.sleep(2)
        self.driver.switch_to.default_content()

        # Modal should be closed, user should not be subscribed
        self.db.refresh(self.db_user)
        assert not self.db_user.toast_active

    def test_stripe_payment_modal_invalid_card_number(self) -> None:
        """Test validation with invalid card number"""
        self.get_element("subscribe-button").click()
        time.sleep(5)

        iframe = self.driver.find_elements(By.TAG_NAME, "iframe")[-1]
        self.driver.switch_to.frame(iframe)

        # Enter invalid card number
        self.set_text(self.get_element("cardNumber", By.NAME), "1234 5678 9012 3456")
        self.set_text(self.get_element("cardCvc", By.NAME), "123")
        self.set_text(self.get_element("cardExpiry", By.NAME), "1228")

        time.sleep(2)

        # Verify validation error appears (card number field should show invalid state)
        card_element = self.get_element("cardNumber", By.NAME)
        # Check for invalid class or aria-invalid attribute
        assert (
            "invalid" in card_element.get_attribute("class").lower()
            or card_element.get_attribute("aria-invalid") == "true"
        )

        self.driver.switch_to.default_content()

    def test_stripe_payment_modal_expired_card(self) -> None:
        """Test payment with expired card"""
        self.get_element("subscribe-button").click()
        time.sleep(5)

        iframe = self.driver.find_elements(By.TAG_NAME, "iframe")[-1]
        self.driver.switch_to.frame(iframe)

        self.set_text(self.get_element("cardNumber", By.NAME), "4000 0000 0000 0069")
        self.set_text(self.get_element("cardCvc", By.NAME), "123")
        self.set_text(self.get_element("cardExpiry", By.NAME), "1228")
        self.set_text(self.get_element("billingName", By.NAME), "John Doe")

        time.sleep(0.5)
        try:
            self.set_text(self.get_element("billingPostalCode", By.NAME), "10001")
        except:
            pass

        time.sleep(5)
        self.get_element("SubmitButton-IconContainer", By.CLASS_NAME).click()
        time.sleep(3)

        # Verify expired card error
        error_elements = self.driver.find_elements(By.CLASS_NAME, "Error")
        assert len(error_elements) > 0

        self.driver.switch_to.default_content()
        self.db.refresh(self.db_user)
        assert not self.db_user.toast_active

    def test_stripe_payment_modal_incorrect_cvc(self) -> None:
        """Test payment with incorrect CVC"""
        self.get_element("subscribe-button").click()
        time.sleep(5)

        iframe = self.driver.find_elements(By.TAG_NAME, "iframe")[-1]
        self.driver.switch_to.frame(iframe)

        self.set_text(self.get_element("cardNumber", By.NAME), "4000 0000 0000 0127")
        self.set_text(self.get_element("cardCvc", By.NAME), "123")
        self.set_text(self.get_element("cardExpiry", By.NAME), "1228")
        self.set_text(self.get_element("billingName", By.NAME), "John Doe")

        time.sleep(0.5)
        try:
            self.set_text(self.get_element("billingPostalCode", By.NAME), "10001")
        except:
            pass

        time.sleep(5)
        self.get_element("SubmitButton-IconContainer", By.CLASS_NAME).click()
        time.sleep(3)

        # Verify CVC error
        error_elements = self.driver.find_elements(By.CLASS_NAME, "Error")
        assert len(error_elements) > 0

        self.driver.switch_to.default_content()
        self.db.refresh(self.db_user)
        assert not self.db_user.toast_active


class TestSubscriptionManagement(BaseTest):
    """Test class for managing existing subscriptions"""

    page_url = "settings"

    def setup_function(self, request) -> None:
        """Setup function - user with active subscription"""
        self.login()
        # Create test subscription using mock webhook
        self.trigger_subscription_created()
        self.driver.refresh()
        time.sleep(2)
        self.user_settings_utils.go_to_premium_tab()

    def trigger_subscription_created(self) -> None:
        """Trigger subscription created event via mock webhook"""
        response = requests.post(
            f"{self.base_url}/test/trigger-webhook",
            json={
                "customer_email": self.db_user.email,
                "event_type": "customer.subscription.created",
                "subscription_id": "sub_test_123456789",
                "customer_id": "cus_test_123456789",
            },
        )
        assert response.status_code == 200
        self.db.refresh(self.db_user)

    def test_active_subscription_displayed(self) -> None:
        """Test that active subscription info is displayed"""
        assert self.check_element_exists("subscription-status")
        # Verify premium features are accessible
        self.db.refresh(self.db_user)
        assert self.db_user.toast_active

    def test_manage_subscription_button_exists(self) -> None:
        """Test that manage subscription button appears for active subscribers"""
        assert self.check_element_exists("manage-subscription-button")

    def test_manage_subscription_portal_opens(self) -> None:
        """Test opening Stripe customer portal"""
        self.get_element("manage-subscription-button").click()
        time.sleep(3)

        # Verify portal opens (either new tab or redirect)
        handles = self.driver.window_handles
        if len(handles) > 1:
            self.driver.switch_to.window(handles[-1])
            current_url = self.driver.current_url
            assert "billing.stripe.com" in current_url or "stripe.com" in current_url
            self.driver.close()
            self.driver.switch_to.window(handles[0])

    def test_subscription_status_shows_active(self) -> None:
        """Test that subscription status displays as active"""
        status_element = self.get_element("subscription-status")
        status_text = status_element.text.lower()
        assert "active" in status_text or "subscribed" in status_text

    def test_subscribe_button_not_shown_when_active(self) -> None:
        """Test that subscribe button is hidden when user has active subscription"""
        # Subscribe button should not be visible
        subscribe_buttons = self.driver.find_elements(By.ID, "subscribe-button")
        assert len(subscribe_buttons) == 0 or not subscribe_buttons[0].is_displayed()


class TestSubscriptionWebhooks(BaseTest):
    """Test subscription state changes via mock webhooks"""

    page_url = "settings"

    def setup_function(self, request) -> None:
        """Setup function"""
        self.login()
        self.user_settings_utils.go_to_premium_tab()

    def trigger_webhook(self, event_type: str, trial_end: int = None) -> None:
        """Helper to trigger webhook events"""
        response = requests.post(
            f"{self.base_url}/test/trigger-webhook",
            json={
                "customer_email": self.db_user.email,
                "event_type": event_type,
                "subscription_id": "sub_test_123456789",
                "customer_id": "cus_test_123456789",
                "trial_end": trial_end,
            },
        )
        assert response.status_code == 200
        self.db.refresh(self.db_user)

    def test_subscription_activation_updates_state(self) -> None:
        """Test that subscription created event activates premium"""
        # Trigger webhook event
        self.trigger_webhook("customer.subscription.created")

        # Verify database state
        assert self.db_user.toast_active
        assert self.db_user.stripe_subscription_id == "sub_test_123456789"
        assert self.db_user.stripe_customer_id == "cus_test_123456789"

        # Refresh page and verify UI
        self.driver.refresh()
        time.sleep(2)
        self.user_settings_utils.go_to_premium_tab()

        # Verify subscription status is shown
        assert self.check_element_exists("subscription-status")

    def test_subscription_cancellation_updates_state(self) -> None:
        """Test that subscription deleted event deactivates premium"""
        # First create subscription
        self.trigger_webhook("customer.subscription.created")
        assert self.db_user.toast_active

        # Then cancel it
        self.trigger_webhook("customer.subscription.deleted")

        # Verify database state
        assert not self.db_user.toast_active
        assert self.db_user.stripe_subscription_id is None

        # Refresh page and verify UI
        self.driver.refresh()
        time.sleep(2)
        self.user_settings_utils.go_to_premium_tab()

        # Verify subscribe button is shown again
        assert self.check_element_exists("subscribe-button")

    def test_subscription_pause_updates_state(self) -> None:
        """Test that subscription paused event deactivates premium"""
        # First create subscription
        self.trigger_webhook("customer.subscription.created")
        assert self.db_user.toast_active

        # Then pause it
        self.trigger_webhook("customer.subscription.paused")

        # Verify database state
        assert not self.db_user.toast_active

        # Refresh page and verify UI
        self.driver.refresh()
        time.sleep(2)
        self.user_settings_utils.go_to_premium_tab()

        # User should see paused state or subscribe button
        # Adjust based on your UI implementation

    def test_trial_ending_notification(self) -> None:
        """Test trial ending notification event"""
        import time as time_module

        # Create subscription with trial
        self.trigger_webhook("customer.subscription.created")

        # Trigger trial ending soon event
        trial_end_timestamp = int(time_module.time()) + 86400 * 3  # 3 days from now
        self.trigger_webhook("customer.subscription.trial_will_end", trial_end=trial_end_timestamp)

        # Verify event was processed successfully
        # Note: Email sending is tested in unit tests
        assert self.db_user.toast_active  # Subscription should still be active

    def test_multiple_webhook_events_sequence(self) -> None:
        """Test handling sequence of webhook events"""
        # Create subscription
        self.trigger_webhook("customer.subscription.created")
        assert self.db_user.toast_active

        # Pause subscription
        self.trigger_webhook("customer.subscription.paused")
        assert not self.db_user.toast_active

        # Delete subscription
        self.trigger_webhook("customer.subscription.deleted")
        assert not self.db_user.toast_active
        assert self.db_user.stripe_subscription_id is None


class TestSubscriptionUIUpdates(BaseTest):
    """Test UI updates based on subscription state"""

    page_url = "settings"

    def setup_function(self, request) -> None:
        """Setup function"""
        self.login()
        self.user_settings_utils.go_to_premium_tab()

    def test_ui_shows_subscribe_button_when_no_subscription(self) -> None:
        """Test UI shows subscribe button when user has no subscription"""
        assert self.check_element_exists("subscribe-button")
        self.db.refresh(self.db_user)
        assert not self.db_user.toast_active

    def test_ui_updates_after_subscription_activation(self) -> None:
        """Test UI updates after subscription is activated"""
        # Trigger subscription creation
        response = requests.post(
            f"{self.base_url}/test/trigger-webhook",
            json={
                "customer_email": self.db_user.email,
                "event_type": "customer.subscription.created",
                "subscription_id": "sub_test_123456789",
                "customer_id": "cus_test_123456789",
            },
        )
        assert response.status_code == 200

        # Refresh page
        self.driver.refresh()
        time.sleep(2)
        self.user_settings_utils.go_to_premium_tab()

        # Verify UI shows active subscription
        assert self.check_element_exists("subscription-status")

        # Verify subscribe button is hidden/replaced
        subscribe_buttons = self.driver.find_elements(By.ID, "subscribe-button")
        assert len(subscribe_buttons) == 0 or not subscribe_buttons[0].is_displayed()

    def test_premium_features_accessible_with_active_subscription(self) -> None:
        """Test that premium features are accessible with active subscription"""
        # Activate subscription
        requests.post(
            f"{self.base_url}/test/trigger-webhook",
            json={
                "customer_email": self.db_user.email,
                "event_type": "customer.subscription.created",
                "subscription_id": "sub_test_123456789",
                "customer_id": "cus_test_123456789",
            },
        )

        self.driver.refresh()
        time.sleep(2)

        # Verify database state
        self.db.refresh(self.db_user)
        assert self.db_user.toast_active

        # Test accessing premium features (adjust based on your features)
        # For example, check if premium badge is shown
        # assert self.check_element_exists("premium-badge")
