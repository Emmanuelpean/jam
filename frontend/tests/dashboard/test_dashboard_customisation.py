"""Tests for the customisable dashboard: edit mode, adding/removing widgets, save, cancel, reset."""

from selenium.webdriver.common.by import By

from dashboard_base import DashboardTestBase

# Toolbar button IDs
EDIT_BTN = "dashboard-edit-btn"
SAVE_BTN = "dashboard-save-btn"
ADD_WIDGET_BTN = "dashboard-add-widget-btn"
RESET_BTN = "dashboard-reset-btn"

# Widget picker modal card ID patterns
PICKER_TYPE = "widget-picker-type-{type}"
PICKER_VARIANT = "widget-picker-variant-{key}"

# Confirm dialog IDs (remove widget uses showDelete, reset uses showConfirm)
DELETE_CONFIRM_BTN = "delete-alert-modal-confirm-button"
DELETE_CANCEL_BTN = "delete-alert-modal-cancel-button"
RESET_CONFIRM_BTN = "confirm-alert-modal-confirm-button"


class TestDashboardCustomisation(DashboardTestBase):
    """Tests for the customisable dashboard."""

    user_index = 0

    def setup_function(self, request) -> None:
        # Start with a simple, known layout: one metric widget
        self._set_dashboard_widgets({"type": "metric", "metric": "total_jobs"})
        self.login()

    # ------------------------------------------------- HELPERS -------------------------------------------------

    def _enter_edit_mode(self) -> None:
        """Click the pencil button to enter edit mode."""
        self.get_element(EDIT_BTN).click()
        self.get_elements(SAVE_BTN)

    def _exit_edit_mode_cancel(self) -> None:
        """Click the edit/cancel toggle button to cancel (exit without saving)."""
        self.get_element(EDIT_BTN).click()
        self.wait_for_disappear(SAVE_BTN)

    def _save(self) -> None:
        """Click save and wait for save button to disappear (edit mode exits)."""
        self.get_element(SAVE_BTN).click()
        self.wait_for_disappear(SAVE_BTN)

    def _add_widget(self, widget_type: str, variant_key: str) -> None:
        """Open widget picker, select type then variant."""
        self.get_element(ADD_WIDGET_BTN).click()
        type_id = PICKER_TYPE.format(type=widget_type)
        self.get_element(type_id).click()
        variant_id = PICKER_VARIANT.format(key=variant_key)
        self.get_element(variant_id).click()
        self.wait_for_disappear(variant_id)

    def _remove_widget(self, widget_id: str, confirm: bool = True) -> None:
        """Click the remove button for a widget and confirm (or cancel) the dialog."""
        self.get_element(f"widget-remove-btn-{widget_id}").click()
        btn_id = DELETE_CONFIRM_BTN if confirm else DELETE_CANCEL_BTN
        self.get_element(btn_id).click()

    def _grid_item_count(self) -> int:
        return len(self.driver.find_elements(By.CSS_SELECTOR, ".dashboard-grid-item"))

    # ------------------------------------------- EDIT MODE TOGGLE ------------------------------------------

    def test_edit_mode_shows_toolbar_and_widget_buttons(self) -> None:
        """Entering edit mode reveals save, add-widget and reset buttons."""
        self._enter_edit_mode()
        assert self.get_element(SAVE_BTN).is_displayed()
        assert self.get_element(ADD_WIDGET_BTN).is_displayed()
        assert self.get_element(RESET_BTN).is_displayed()
        assert self.get_element("widget-remove-btn-w-test-0").is_displayed()

    def test_cancel_hides_toolbar_buttons(self) -> None:
        """Cancelling edit mode hides the save/add/reset buttons."""
        self._enter_edit_mode()
        self._exit_edit_mode_cancel()
        # Save button should no longer be in the DOM / visible
        assert not self.check_element_exists(SAVE_BTN)
        assert not self.get_element("widget-remove-btn-w-test-0", enabled=False).is_displayed()

    # ----------------------------------------------- ADD WIDGET -------------------------------------------

    def test_add_metric_widget_appears_on_dashboard(self) -> None:
        """Adding a metric widget via the picker increases the widget count by 1."""
        initial_count = self._grid_item_count()
        self._enter_edit_mode()
        self._add_widget("metric", "applications")
        assert self._grid_item_count() == initial_count + 1

    def test_add_table_widget_appears_on_dashboard(self) -> None:
        """Adding a table widget via the picker increases the widget count by 1."""
        initial_count = self._grid_item_count()
        self._enter_edit_mode()
        self._add_widget("table", "follow_up")
        assert self._grid_item_count() == initial_count + 1

    def test_add_timeline_widget_appears_on_dashboard(self) -> None:
        """Adding a timeline widget via the picker increases the widget count by 1."""
        initial_count = self._grid_item_count()
        self._enter_edit_mode()
        self._add_widget("timeline", "recent_activity")
        assert self._grid_item_count() == initial_count + 1

    # --------------------------------------------- REMOVE WIDGET ------------------------------------------

    def test_remove_widget_decreases_count(self) -> None:
        """Confirming widget removal decreases the widget count by 1."""
        self._enter_edit_mode()
        initial_count = self._grid_item_count()
        # The widget added in setup has id w-test-0
        self._remove_widget("w-test-0", confirm=True)
        assert self._grid_item_count() == initial_count - 1

    def test_cancel_remove_keeps_widget(self) -> None:
        """Cancelling the remove confirmation dialog leaves the widget count unchanged."""
        self._enter_edit_mode()
        initial_count = self._grid_item_count()
        self._remove_widget("w-test-0", confirm=False)
        assert self._grid_item_count() == initial_count

    # ----------------------------------------------- SAVE / CANCEL ----------------------------------------

    def test_save_persists_added_widget_across_reload(self) -> None:
        """After adding a widget and saving, the widget is still present after a page reload."""
        self._enter_edit_mode()
        self._add_widget("metric", "applications")
        count_before_save = self._grid_item_count()
        self._save()
        self._reload()
        assert self._grid_item_count() == count_before_save

    def test_save_persists_removed_widget_across_reload(self) -> None:
        """After removing a widget and saving, the widget is absent after reload."""
        self._enter_edit_mode()
        self._remove_widget("w-test-0", confirm=True)
        count_after_remove = self._grid_item_count()
        self._save()
        self._reload()
        assert self._grid_item_count() == count_after_remove

    def test_cancel_discards_added_widget(self) -> None:
        """Adding a widget then cancelling leaves the layout unchanged from before edit mode."""
        initial_count = self._grid_item_count()
        self._enter_edit_mode()
        self._add_widget("metric", "applications")
        assert self._grid_item_count() == initial_count + 1
        self._exit_edit_mode_cancel()
        assert self._grid_item_count() == initial_count

    def test_cancel_discards_removed_widget(self) -> None:
        """Removing a widget then cancelling restores the widget."""
        initial_count = self._grid_item_count()
        self._enter_edit_mode()
        self._remove_widget("w-test-0", confirm=True)
        assert self._grid_item_count() == initial_count - 1
        self._exit_edit_mode_cancel()
        assert self._grid_item_count() == initial_count

    # ----------------------------------------------- RESET ------------------------------------------------

    def test_reset_restores_default_layout(self) -> None:
        """Resetting restores more widgets than the single-widget test layout."""
        initial_count = self._grid_item_count()
        self._enter_edit_mode()
        self.get_element(RESET_BTN).click()
        self.get_element(RESET_CONFIRM_BTN).click()
        self._save()
        assert self._grid_item_count() > initial_count

    def test_reset_persists_across_reload(self) -> None:
        """After reset and save, reloading shows the same widget count as right after reset."""
        self._enter_edit_mode()
        self.get_element(RESET_BTN).click()
        self.get_element(RESET_CONFIRM_BTN).click()
        self._save()
        count_after_reset = self._grid_item_count()
        self._reload()
        assert self._grid_item_count() == count_after_reset
