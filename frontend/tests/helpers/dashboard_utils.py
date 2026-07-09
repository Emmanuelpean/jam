"""Shared base class for dashboard Selenium tests."""

import json

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from frontend_base_test import BaseTest

# Default grid dimensions per widget type (mirrors widgetRegistry.ts defaults)
_LAYOUT_DEFAULTS: dict[str, dict] = {
    "metric": {"w": 3, "h": 4, "minW": 2, "minH": 4},
    "table": {"w": 8, "h": 12, "minW": 4, "minH": 8},
    "timeline": {"w": 4, "h": 12, "minW": 3, "minH": 8},
    "graph": {"w": 6, "h": 8, "minW": 4, "minH": 6},
    "map": {"w": 8, "h": 14, "minW": 4, "minH": 10},
}


class DashboardUtils(BaseTest):
    """Extends BaseTest with helpers for dashboard page reload and layout setup.
    Data-creation helpers live on BaseTest. Subclasses must still set `user_fixture`
    and call `self.login()` in `setup_function`."""

    page_url = "dashboard"

    # Widgets created by `_set_dashboard_widgets` get ids TEST_WIDGET_ID_PREFIX + "0", "1", ...
    TEST_WIDGET_ID_PREFIX = "w-test-"
    TEST_WIDGET_ID = f"{TEST_WIDGET_ID_PREFIX}0"

    # Default-layout table widget ids
    FOLLOW_UP_TABLE = "table-card-follow_up"
    UPCOMING_DEADLINES_TABLE = "table-card-upcoming_deadlines"
    JOB_ALERTS_TABLE = "table-card-job_alerts"
    FAVOURITES_TABLE = "table-card-favourites"
    FAVOURITE_JOBS_TABLE = "table-card-favourite_jobs"
    FAILED_JOBS_TABLE = "table-card-error_jobs"

    # Default-layout metric card ids (set in StatCard.tsx / DashboardPage.tsx)
    TOTAL_JOBS = "stat-card-total_jobs"
    APPLICATIONS = "stat-card-applications"
    PENDING = "stat-card-pending"
    FOLLOW_UP = "stat-card-follow_up"
    ACTIVE_APPLICATIONS = "stat-card-active_applications"
    INTERVIEW_RATE = "stat-card-interview_rate"
    AVG_RESPONSE_TIME = "stat-card-avg_response_time"

    # Default-layout activity feed ids (set in ActivityFeed.tsx / DashboardCard.tsx)
    RECENT_ACTIVITY = "activity-card-recent_activity"
    UPCOMING_INTERVIEWS = "activity-card-upcoming_interviews"

    # Map widget: side panel CSS class and location marker CSS selector
    MAP_PANEL = "map-jobs-panel"
    MARKER = "path.leaflet-interactive"

    def _reload(self) -> None:
        """Reload the dashboard page and wait for data to finish loading."""
        self.driver.refresh()
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "[data-loaded='true']")))

    # ----------------------------------------------- WIDGET HELPERS -----------------------------------------------

    def _card(self, card_id: str) -> WebElement:
        """Return the widget card element with the given id."""
        return self.get_element(card_id)

    def _badge_count(self, card_id: str) -> int:
        """Return the integer badge count shown on a card."""
        return int(self.get_element(f"{card_id}-badge").text)

    def _empty_state_visible(self, card_id: str) -> bool:
        """Whether the empty state is shown for the given widget card."""
        return self.check_element_exists(f"{card_id}-empty")

    def _rows(self, table_id: str, row_entity: str = "job") -> list[WebElement]:
        """Return the data rows of a table widget."""
        return self._card(table_id).find_elements(By.CSS_SELECTOR, f"[id^='table-row-{row_entity}-']")

    def _assert_row_count(self, table_id: str, count: int, row_entity: str = "job") -> None:
        """Assert a table widget shows `count` rows and its badge reports the same count."""
        assert len(self._rows(table_id, row_entity)) == count
        assert self._badge_count(table_id) == count

    def _activity_items(self, card_id: str) -> list[WebElement]:
        """Return the activity items of a timeline widget."""
        return self._card(card_id).find_elements(By.CSS_SELECTOR, ".activity-item")

    def _value(self, card_id: str) -> int:
        """Return the integer value displayed on a stat card."""
        return int(self.get_element(f"{card_id}-value").text)

    def _pct_value(self, card_id: str) -> int:
        """Return the integer percentage value (strips trailing '%')."""
        return int(self.get_element(f"{card_id}-value").text.rstrip("%"))

    def _days_value(self, card_id: str) -> int:
        """Return the integer days value (strips trailing 'd')."""
        return int(self.get_element(f"{card_id}-value").text.rstrip("d"))

    def _markers(self) -> list[WebElement]:
        """Return the map widget's location marker elements."""
        return self.driver.find_elements(By.CSS_SELECTOR, self.MARKER)

    def _remove_widget(self, widget_id: str, confirm: bool = True) -> None:
        """Click the remove button for a widget and confirm (or cancel) the dialog."""
        self.dashboard_edit_utils.click_remove(widget_id)
        if confirm:
            self.delete_modal_utils.confirm_button.click()
        else:
            self.delete_modal_utils.cancel_button.click()

    # ----------------------------------------------- LAYOUT HELPERS -----------------------------------------------

    def _set_dashboard_widgets(self, *configs: dict) -> None:
        """Replace the user's dashboard layout with a layout containing only the given widgets.

        Each element in *configs is a WidgetConfig dict, for example:
            {"type": "metric",   "metric": "active_applications"}
            {"type": "timeline", "feed":   "recent_activity"}
            {"type": "table",    "source": "follow_up"}

        Widgets are placed left-to-right in a 12-column grid; a new row starts when the
        next widget would overflow. Call before ``self.login()`` so the page loads with
        the correct layout, or call ``self._reload()`` afterwards to apply the change."""

        col = 0
        row = 0
        widgets = []
        layout = []

        for i, config in enumerate(configs):
            widget_id = f"{self.TEST_WIDGET_ID_PREFIX}{i}"
            dims = _LAYOUT_DEFAULTS.get(config.get("type", "metric"), _LAYOUT_DEFAULTS["metric"])

            if col + dims["w"] > 12:
                col = 0
                row += dims["h"]

            widgets.append({"id": widget_id, "config": config})
            layout.append({"i": widget_id, "x": col, "y": row, **dims})
            col += dims["w"]

        self.user.preferences.dashboard_layout = json.dumps({"widgets": widgets, "layout": layout})
        self.db.commit()
