"""Tests for the dashboard Map widget."""

from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

from dashboard_base import DashboardTestBase

MAP_PANEL = "map-jobs-panel"  # CSS class of the side panel that lists a location's jobs
MARKER = "path.leaflet-interactive"  # CircleMarker rendered for each location


class TestMapWidget(DashboardTestBase):
    """Tests for the Map widget (Jobs by Location).

    Regression cover for the side panel: clicking a location marker must open the
    panel listing that location's jobs. The panel previously rendered but was hidden
    behind the (fixed-width, overflowing) map, so it must also be the top-most element
    at its own location, not covered by the map.
    """

    user_fixture = "test_regular_user"

    def setup_function(self, request) -> None:
        self._set_dashboard_widgets({"type": "map", "metric": "job_count"})
        self.login()

    # --------------------------------------------------- HELPERS ---------------------------------------------------

    def _markers(self):
        return self.driver.find_elements(By.CSS_SELECTOR, MARKER)

    # ---------------------------------------------------- TESTS ----------------------------------------------------

    def test_clicking_marker_opens_visible_job_panel(self) -> None:
        """Clicking a location marker opens the side panel listing that location's jobs,
        and the panel is visible on top of the map (not hidden behind it)."""
        self.user.create_geolocated_job("London Engineer", "London", "United Kingdom", 51.5074, -0.1278)
        self._reload()

        # Wait for the marker to be drawn, then click it.
        WebDriverWait(self.driver, 10).until(lambda d: len(self._markers()) >= 1)
        marker = self._markers()[0]
        ActionChains(self.driver).move_to_element(marker).click().perform()

        # The side panel must appear and list the job.
        panel = WebDriverWait(self.driver, 10).until(ec.visibility_of_element_located((By.CLASS_NAME, MAP_PANEL)))
        assert "London Engineer" in panel.text

        # Regression guard: the panel must be the top-most element at its own centre,
        # i.e. not covered by the overflowing map.
        topmost_is_panel = self.driver.execute_script(
            """
            const panel = arguments[0];
            const r = panel.getBoundingClientRect();
            const top = document.elementFromPoint(r.left + r.width / 2, r.top + r.height / 2);
            return panel.contains(top);
            """,
            panel,
        )
        assert topmost_is_panel, "Map jobs panel is covered by another element (regression)"
