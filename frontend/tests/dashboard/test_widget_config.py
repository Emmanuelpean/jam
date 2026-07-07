"""Tests for per-widget dashboard configuration (the edit-mode settings sidebar).

These replace the old user-level Dashboard Settings: the chase/deadline thresholds
and update limit are now configured per widget via a gear button in edit mode.
"""

import datetime as dt
import json
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from dashboard_base import DashboardTestBase

FOLLOW_UP_TABLE = "table-card-follow_up"
EDIT_BTN = "dashboard-edit-btn"
SAVE_BTN = "dashboard-save-btn"
# Widgets created by _set_dashboard_widgets get ids w-test-0, w-test-1, ...
CONFIG_BTN = "widget-config-btn-w-test-0"

NOW = dt.datetime.now(dt.timezone.utc)
TEN_DAYS_AGO = NOW - dt.timedelta(days=10)


class TestFollowUpWidgetConfig(DashboardTestBase):
    """The Follow-up table honours its own per-widget chase threshold."""

    user_fixture = "test_regular_user"

    def _rows(self):
        card = self.get_element(FOLLOW_UP_TABLE)
        return card.find_elements(By.CSS_SELECTOR, "[id^='table-row-job-']")

    def _enter_edit_mode(self) -> None:
        self.get_element(EDIT_BTN).click()
        WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.ID, SAVE_BTN)))

    # ---------------------------------------------------- TESTS ----------------------------------------------------

    def test_low_per_widget_threshold_includes_application(self) -> None:
        """A 10-day-old application appears when the widget's chase threshold is below 10."""
        self._set_dashboard_widgets({"type": "table", "source": "follow_up", "chaseThreshold": 5})
        self.login()
        self.user.create_job(title="Chase Me", application_date=TEN_DAYS_AGO, application_status="applied")
        self._reload()
        assert len(self._rows()) == 1

    def test_high_per_widget_threshold_excludes_application(self) -> None:
        """The same application is hidden when the widget's chase threshold is above 10."""
        self._set_dashboard_widgets({"type": "table", "source": "follow_up", "chaseThreshold": 30})
        self.login()
        self.user.create_job(title="Not Yet", application_date=TEN_DAYS_AGO, application_status="applied")
        self._reload()
        assert len(self._rows()) == 0

    def test_config_toggle_only_visible_in_edit_mode(self) -> None:
        """The gear toggle is shown only while the dashboard is in edit mode.

        The button stays mounted (so it can animate in/out), so we assert on visibility
        rather than presence in the DOM.
        """
        self._set_dashboard_widgets({"type": "table", "source": "follow_up"})
        self.login()
        # enabled=False: presence-only lookup, since the hidden button is not clickable yet.
        assert not self.get_element(CONFIG_BTN, enabled=False).is_displayed()
        self._enter_edit_mode()
        assert self.get_element(CONFIG_BTN).is_displayed()

    def test_sidebar_change_persists_across_reload(self) -> None:
        """Changing the threshold in the sidebar and saving persists it and updates the table."""
        self._set_dashboard_widgets({"type": "table", "source": "follow_up"})
        self.login()
        # 10 days old: hidden by the default 14-day threshold.
        self.user.create_job(title="Chase Me", application_date=TEN_DAYS_AGO, application_status="applied")
        self._reload()
        assert len(self._rows()) == 0

        self._enter_edit_mode()
        self.get_element(CONFIG_BTN).click()
        time.sleep(0.3)  # allow the sidebar slide transition
        self.set_text(self.get_element(f"{FOLLOW_UP_TABLE}-chaseThreshold"), "5")

        # Lowering the threshold to 5 surfaces the 10-day-old application live.
        WebDriverWait(self.driver, 5).until(lambda _: len(self._rows()) == 1)

        self.get_element(SAVE_BTN).click()
        WebDriverWait(self.driver, 5).until(EC.invisibility_of_element_located((By.ID, SAVE_BTN)))

        layout = json.loads(self.db_user.preferences.dashboard_layout)
        assert layout["widgets"][0]["config"]["chaseThreshold"] == 5

        self._reload()
        assert len(self._rows()) == 1
