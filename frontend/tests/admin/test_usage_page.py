"""Tests for the Provider Monitoring (Usage) page.

The Usage page is opened as a modal from the admin dashboard (/admin):
- Clicking the "Provider Monitoring" card opens the modal.
- The body shows per-service spend summary cards, daily charts, a time filter and
  a log viewer; the modal header holds the monitoring service control.

Daily usage/income rows are seeded into the DB so the summary totals are deterministic.
"""

import datetime as dt

from frontend_base_test import BaseTest


class TestUsagePage(BaseTest):
    """Tests for the admin Usage / ESM dashboard modal."""

    user_fixture = "test_admin_user"
    page_url = "admin"

    # Seeded daily values, all within the default 1-month window.
    ANTHROPIC_USD = 10.0
    APIFY_USD = 5.0
    BRIGHTDATA_USD = 3.0
    STRIPE_NET_GBP = 80.0
    USD_TO_GBP = 0.79

    def setup_function(self, request) -> None:
        # The Service config row is normally seeded at backend startup, but the per-test DB
        # truncation wipes it, so the status control needs it created explicitly.
        self.create_service(self.db, name="provider_monitoring_service", display_name="Provider Monitoring")

        day = dt.date.today() - dt.timedelta(days=2)
        self.create_anthropic_usage(self.db, date=day, usage_usd=self.ANTHROPIC_USD)
        self.create_apify_usage(self.db, date=day, usage_usd=self.APIFY_USD)
        self.create_brightdata_usage(self.db, date=day, usage_usd=self.BRIGHTDATA_USD)
        self.create_stripe_income(self.db, date=day, gross_gbp=100.0, net_gbp=self.STRIPE_NET_GBP)
        self.login()

    def test_page_renders(self) -> None:
        """The Usage modal renders its summary cards, charts, filter and log viewer."""

        self.usage_page_utils.open()

        # Time filter + log viewer
        assert self.usage_page_utils.history_filters.is_displayed()
        assert self.usage_page_utils.usage_log_viewer.is_displayed()
        assert self.usage_page_utils.log_toggle

        # Five summary cards: Anthropic / Apify / Bright Data / Stripe / Net balance
        assert len(self.usage_page_utils.summary_cards) == 5

        # The four per-service charts
        modal_text = self.usage_page_utils.admin_page_modal.text
        for label in ("Anthropic (Claude)", "Apify", "Bright Data", "Stripe Income"):
            assert label in modal_text, f"Missing service chart: {label}"

    def test_summary_values(self) -> None:
        """Summary totals reflect the seeded daily usage/income."""

        self.usage_page_utils.open()

        net = self.STRIPE_NET_GBP - (self.ANTHROPIC_USD + self.APIFY_USD + self.BRIGHTDATA_USD) * self.USD_TO_GBP
        values = {
            "Anthropic spend": f"${self.ANTHROPIC_USD:.2f}",
            "Apify spend": f"${self.APIFY_USD:.2f}",
            "Bright Data spend": f"${self.BRIGHTDATA_USD:.2f}",
            "Stripe income": f"£{self.STRIPE_NET_GBP:.2f}",
            "Net balance": f"£{net:.2f}",
        }

        # The history is fetched asynchronously once the filter emits its default range.
        text = self.usage_page_utils.wait_for_modal_text_containing(values["Anthropic spend"])

        # Summary card labels are upper-cased via CSS, so compare case-insensitively.
        text_upper = text.upper()
        for label, value in values.items():
            assert label.upper() in text_upper, f"Missing summary card: {label}"
            assert value in text, f"Missing value {value} for {label}"

    def test_status_control(self) -> None:
        """The monitoring service control opens from the modal header (no config fields)."""

        self.usage_page_utils.open()

        self.usage_page_utils.open_status_control()
        assert self.usage_page_utils.run_now_button
        # Unlike the scraping/rating runners, ESM has no configurable period.
        assert not self.check_element_exists("period_hours")

    def test_balance_captions(self) -> None:
        """The Apify and Bright Data summary cards show their balance captions."""

        # Latest balance snapshot per service, fetched when the modal opens.
        self.create_apify_balance(self.db, limit_usd=100.0)
        self.create_brightdata_balance(self.db, balance_usd=50.0, pending_costs_usd=2.0)

        self.usage_page_utils.open()

        text = self.usage_page_utils.wait_for_modal_text_containing("Cycle limit: $100.00")
        assert "Cycle limit: $100.00" in text  # Apify cycle limit
        assert "Balance: $50.00" in text  # Bright Data balance
        assert "Pending: $2.00" in text  # Bright Data pending costs
