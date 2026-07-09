"""Utilities for the premium settings page."""

import time

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from helpers.jam_test_utils import JamTestUtils


class PremiumSettingsUtils(JamTestUtils):

    def __init__(self, **kwargs):
        self._init(**kwargs)

    @property
    def incomplete_qualifications_alert(self) -> WebElement:
        """Get the incomplete qualifications warning alert element."""

        return self.get_element("incomplete-qualifications-alert")

    @property
    def confirmation_link_alert(self) -> WebElement:
        """Get the confirmation link alert element."""

        return self.get_element("confirmation-link-alert")

    @property
    def confirmation_link_heading(self) -> WebElement:
        """Get the confirmation link heading element."""

        return self.get_element("confirmation-link-heading")

    @property
    def confirmation_link_prompt(self) -> WebElement:
        """Get the confirmation link prompt element."""

        return self.get_element("confirmation-link-prompt")

    @property
    def confirmation_link_confirm_button(self) -> WebElement:
        """Get the confirmation link confirm button element."""

        return self.get_element("confirmation-link-prompt-confirm-button")

    @property
    def confirmation_link_cancel_button(self) -> WebElement:
        """Get the confirmation link cancel button element."""

        return self.get_element("confirmation-link-prompt-cancel-button")

    def dismiss_confirmation_link_alert(self) -> None:
        """Dismiss the warning alert to trigger the showConfirm prompt."""

        self.confirmation_link_alert.find_element(By.CSS_SELECTOR, ".btn-close").click()
        time.sleep(0.5)

    def delete_stripe_data(self) -> None:
        """Delete Stripe customer data for the user"""

        response = self.client.delete("/test/payments/delete-all-customers")
        assert response.status_code == 200

    def advance_clock(self, days: int = 15) -> None:
        """Advance the Stripe clock"""

        response = self.client.post("/test/payments/advance-test-clock", json={"days": days})
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
