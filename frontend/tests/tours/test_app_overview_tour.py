"""Selenium tests for the App Overview guided tour.

Tour step order (app-overview):
  0  intro               centre popover — "Welcome to JAM!" (route: dashboard)
  1  dashboard-overview  dashboard-main highlighted (route: dashboard)
  2  dashboard-customise dashboard-edit-btn highlighted (route: dashboard)
  3  sidebar             nav-jobs highlighted (route: jobs)
  4  premium             premium-tab highlighted (route: settings/premium)
  5  command-palette     centre popover — Done button (no route)
"""

from selenium.webdriver import Keys
from selenium.webdriver.common.by import By

from base_test import BaseTest


TOUR_ID = "app-overview"
TOTAL_STEPS = 6


class TestAppOverviewTour(BaseTest):
    user_index = 0
    page_url = "dashboard"

    def setup_function(self, request) -> None:
        self.login()

    # ------------------------------------------------------------------ helpers

    def _start_tour(self) -> None:
        """Start the App Overview tour and wait for the intro popover on the dashboard."""
        self.tour_utils.start_tour(TOUR_ID)
        self.wait_for_page("dashboard")
        self.tour_utils.wait_for_popover()

    # ------------------------------------------------------------------ tests

    def test_complete_tour(self) -> None:
        """Walk through all 6 steps, click Done, and verify the tour is marked complete.

        Checks step titles, page navigation at each step, and that the tour select
        panel shows the completion icon after Done.
        """
        self._start_tour()

        # Step 0 (intro): centre popover on the dashboard
        assert self.tour_utils.popover_title() == "Welcome to JAM!"
        assert f"STEP 1 OF {TOTAL_STEPS}" in self.tour_utils.step_counter_text().upper()
        self.tour_utils.click_next()

        # Step 1 (dashboard-overview): still on the dashboard
        self.tour_utils.wait_for_popover()
        self.wait_for_page("dashboard")
        self.tour_utils.click_next()

        # Step 2 (dashboard-customise): still on the dashboard
        self.tour_utils.wait_for_popover()
        self.wait_for_page("dashboard")
        self.tour_utils.click_next()

        # Step 3 (sidebar): navigates to the jobs page
        self.tour_utils.wait_for_popover()
        self.wait_for_page("jobs")
        self.tour_utils.click_next()

        # Step 4 (premium): navigates to the premium settings page
        self.tour_utils.wait_for_popover()
        self.wait_for_page("settings/premium")
        self.tour_utils.click_next()

        # Step 5 (command-palette): Done button visible
        self.tour_utils.wait_for_popover()
        assert f"STEP {TOTAL_STEPS} OF {TOTAL_STEPS}" in self.tour_utils.step_counter_text().upper()
        assert "Done" in self.get_element(self.tour_utils.TOUR_NEXT).text
        self.tour_utils.click_next()

        self.tour_utils.wait_for_popover_gone()
        self.wait_for_page(self.page_url)

        # Tour is marked complete in the tour select panel
        self.tour_utils.open_tour_select()
        icon = self.get_element(f"tsp-icon-{TOUR_ID}", enabled=False)
        assert "tsp-icon--done" in icon.get_attribute("class")

    def test_skip_from_intro(self) -> None:
        """Clicking Skip Tour at the intro step immediately closes the tour."""
        self._start_tour()
        self.tour_utils.click_skip()
        self.tour_utils.wait_for_popover_gone()
        self.wait_for_page(self.page_url)

    def test_skip_mid_tour_returns_to_origin(self) -> None:
        """Skipping mid-tour from the jobs page (step 3) returns to the dashboard."""
        self._start_tour()
        # Advance to step 3 (sidebar) — the tour navigates to jobs
        self.tour_utils.advance_steps(3)
        self.wait_for_page("jobs")

        self.tour_utils.click_skip()
        self.tour_utils.wait_for_popover_gone()
        self.wait_for_page(self.page_url)

    def test_back_navigation(self) -> None:
        """Clicking Back on step 2 returns to step 1."""
        self._start_tour()
        self.tour_utils.click_next()  # intro → dashboard-overview
        self.tour_utils.wait_for_step(2)

        self.tour_utils.click_back()
        self.tour_utils.wait_for_step(1)
        assert self.tour_utils.popover_title() == "Welcome to JAM!"

    def test_arrow_key_navigation(self) -> None:
        """Right-arrow advances the tour; left-arrow goes back."""
        self._start_tour()
        body = self.driver.find_element(By.TAG_NAME, "body")
        body.send_keys(Keys.ARROW_RIGHT)
        self.tour_utils.wait_for_step(2)
        body.send_keys(Keys.ARROW_LEFT)
        self.tour_utils.wait_for_step(1)

    def test_esc_closes_tour(self) -> None:
        """Pressing Escape closes the tour popover."""
        self._start_tour()
        self.driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
        self.tour_utils.wait_for_popover_gone()
