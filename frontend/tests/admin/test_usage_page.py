"""Tests for the External Service Monitoring (Usage) page.

The Usage page is opened as a modal from the admin dashboard (/admin):
- Clicking the "External Service Monitoring" card opens the modal.
- The body shows per-service spend summary cards, daily charts, a time filter and
  a log viewer; the modal header holds the monitoring service control.

Daily usage/income rows are seeded into the DB so the summary totals are deterministic.
"""

import datetime as dt

from selenium.webdriver.common.by import By

from base_test import BaseTest


class TestUsagePage(BaseTest):
    """Tests for the admin Usage / ESM dashboard modal."""

    user_index = 1  # admin user required for the admin dashboard
    page_url = "admin"

    # Seeded daily values, all within the default 1-month window.
    ANTHROPIC_USD = 10.0
    APIFY_USD = 5.0
    BRIGHTDATA_USD = 3.0
    STRIPE_NET_GBP = 80.0
    USD_TO_GBP = 0.79  # must match UsagePage

    def setup_function(self, request) -> None:
        # A couple of days back keeps the rows safely inside the window regardless
        # of any browser/server timezone boundary on "today".
        day = dt.date.today() - dt.timedelta(days=2)
        self._make_anthropic_usage(date=day, usage_usd=self.ANTHROPIC_USD)
        self._make_apify_usage(date=day, usage_usd=self.APIFY_USD)
        self._make_brightdata_usage(date=day, usage_usd=self.BRIGHTDATA_USD)
        self._make_stripe_income(date=day, gross_gbp=100.0, net_gbp=self.STRIPE_NET_GBP)
        self.login()

    def _open_usage(self) -> None:
        """Open the External Service Monitoring modal from the admin dashboard."""

        # Click the title (top of the card) to avoid the sparkline hover overlay.
        card = self.get_element("admin-card-usage", enabled=False)
        card.find_element(By.CLASS_NAME, "card-title").click()
        self.get_element("admin-page-modal", enabled=False)

    def test_page_renders(self) -> None:
        """The Usage modal renders its summary cards, charts, filter and log viewer."""

        self._open_usage()

        # Time filter + log viewer
        assert self.get_element("history-filters", enabled=False).is_displayed()
        assert self.get_element("usage-log-viewer", enabled=False).is_displayed()
        assert self.check_element_exists("log-toggle", selector=By.CLASS_NAME)

        # Five summary cards: Anthropic / Apify / Bright Data / Stripe / Net balance
        assert len(self.get_elements("usage-summary-card", selector=By.CLASS_NAME)) == 5

        # The four per-service charts
        modal_text = self.get_element("admin-page-modal", enabled=False).text
        for label in ("Anthropic (Claude)", "Apify", "Bright Data", "Stripe Income"):
            assert label in modal_text, f"Missing service chart: {label}"

    def test_summary_values(self) -> None:
        """Summary totals reflect the seeded daily usage/income."""

        self._open_usage()

        net = self.STRIPE_NET_GBP - (self.ANTHROPIC_USD + self.APIFY_USD + self.BRIGHTDATA_USD) * self.USD_TO_GBP
        values = {
            "Anthropic spend": f"${self.ANTHROPIC_USD:.2f}",
            "Apify spend": f"${self.APIFY_USD:.2f}",
            "Bright Data spend": f"${self.BRIGHTDATA_USD:.2f}",
            "Stripe income": f"£{self.STRIPE_NET_GBP:.2f}",
            "Net balance": f"£{net:.2f}",
        }

        # The history is fetched asynchronously once the filter emits its default range.
        modal = self.get_element("admin-page-modal", enabled=False)
        self.wait.until(lambda d: values["Anthropic spend"] in modal.text)

        text = modal.text
        # Summary card labels are upper-cased via CSS, so compare case-insensitively.
        text_upper = text.upper()
        for label, value in values.items():
            assert label.upper() in text_upper, f"Missing summary card: {label}"
            assert value in text, f"Missing value {value} for {label}"

    def test_status_control(self) -> None:
        """The monitoring service control opens from the modal header (no config fields)."""

        self._open_usage()

        self.get_element("service-status-icons", selector=By.CLASS_NAME).click()
        self.get_element("confirm-start-button")
        # Unlike the scraping/rating runners, ESM has no configurable period.
        assert not self.check_element_exists("period_hours", selector=By.NAME)

    def test_balance_captions(self) -> None:
        """The Apify and Bright Data summary cards show their balance captions."""

        # Latest balance snapshot per service, fetched when the modal opens.
        self._make_apify_balance(limit_usd=100.0)
        self._make_brightdata_balance(balance_usd=50.0, pending_costs_usd=2.0)

        self._open_usage()

        modal = self.get_element("admin-page-modal", enabled=False)
        self.wait.until(lambda d: "Cycle limit: $100.00" in modal.text)

        text = modal.text
        assert "Cycle limit: $100.00" in text  # Apify cycle limit
        assert "Balance: $50.00" in text  # Bright Data balance
        assert "Pending: $2.00" in text  # Bright Data pending costs
