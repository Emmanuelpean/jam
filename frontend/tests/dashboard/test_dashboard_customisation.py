"""Tests for the customisable dashboard: edit mode, adding/removing widgets, save, cancel, reset."""

from helpers.dashboard_utils import DashboardUtils


class TestDashboardCustomisation(DashboardUtils):
    """Tests for the customisable dashboard."""

    user_fixture = "test_regular_user"

    def setup_function(self, request) -> None:
        # Start with a simple, known layout: one metric widget
        self._set_dashboard_widgets({"type": "metric", "metric": "total_jobs"})
        self.login()

    # ------------------------------------------- EDIT MODE TOGGLE ------------------------------------------

    def test_edit_mode_shows_toolbar_and_widget_buttons(self) -> None:
        """Entering edit mode reveals save, add-widget and reset buttons."""
        self.dashboard_edit_utils.enter_edit_mode()
        assert self.dashboard_edit_utils.save_button.is_displayed()
        assert self.dashboard_edit_utils.add_widget_button.is_displayed()
        assert self.dashboard_edit_utils.reset_button.is_displayed()
        assert self.dashboard_edit_utils.remove_button(self.TEST_WIDGET_ID).is_displayed()

    def test_cancel_hides_toolbar_buttons(self) -> None:
        """Cancelling edit mode hides the save/add/reset buttons."""
        self.dashboard_edit_utils.enter_edit_mode()
        self.dashboard_edit_utils.exit_edit_mode_cancel()
        # Save button should no longer be in the DOM / visible
        assert not self.check_element_exists("dashboard-save-btn")
        assert not self.dashboard_edit_utils.remove_button(self.TEST_WIDGET_ID, enabled=False).is_displayed()

    # ----------------------------------------------- ADD WIDGET -------------------------------------------

    def test_add_metric_widget_appears_on_dashboard(self) -> None:
        """Adding a metric widget via the picker increases the widget count by 1."""
        initial_count = len(self.dashboard_edit_utils.grid_items())
        self.dashboard_edit_utils.enter_edit_mode()
        self.dashboard_edit_utils.add_widget("metric", "applications")
        assert len(self.dashboard_edit_utils.grid_items()) == initial_count + 1

    def test_add_table_widget_appears_on_dashboard(self) -> None:
        """Adding a table widget via the picker increases the widget count by 1."""
        initial_count = len(self.dashboard_edit_utils.grid_items())
        self.dashboard_edit_utils.enter_edit_mode()
        self.dashboard_edit_utils.add_widget("table", "follow_up")
        assert len(self.dashboard_edit_utils.grid_items()) == initial_count + 1

    def test_add_timeline_widget_appears_on_dashboard(self) -> None:
        """Adding a timeline widget via the picker increases the widget count by 1."""
        initial_count = len(self.dashboard_edit_utils.grid_items())
        self.dashboard_edit_utils.enter_edit_mode()
        self.dashboard_edit_utils.add_widget("timeline", "recent_activity")
        assert len(self.dashboard_edit_utils.grid_items()) == initial_count + 1

    # --------------------------------------------- REMOVE WIDGET ------------------------------------------

    def test_remove_widget_decreases_count(self) -> None:
        """Confirming widget removal decreases the widget count by 1."""
        self.dashboard_edit_utils.enter_edit_mode()
        initial_count = len(self.dashboard_edit_utils.grid_items())
        self._remove_widget(self.TEST_WIDGET_ID, confirm=True)
        assert len(self.dashboard_edit_utils.grid_items()) == initial_count - 1

    def test_cancel_remove_keeps_widget(self) -> None:
        """Cancelling the remove confirmation dialog leaves the widget count unchanged."""
        self.dashboard_edit_utils.enter_edit_mode()
        initial_count = len(self.dashboard_edit_utils.grid_items())
        self._remove_widget(self.TEST_WIDGET_ID, confirm=False)
        assert len(self.dashboard_edit_utils.grid_items()) == initial_count

    # ----------------------------------------------- SAVE / CANCEL ----------------------------------------

    def test_save_persists_added_widget_across_reload(self) -> None:
        """After adding a widget and saving, the widget is still present after a page reload."""
        self.dashboard_edit_utils.enter_edit_mode()
        self.dashboard_edit_utils.add_widget("metric", "applications")
        count_before_save = len(self.dashboard_edit_utils.grid_items())
        self.dashboard_edit_utils.save()
        self._reload()
        assert len(self.dashboard_edit_utils.grid_items()) == count_before_save

    def test_save_persists_removed_widget_across_reload(self) -> None:
        """After removing a widget and saving, the widget is absent after reload."""
        self.dashboard_edit_utils.enter_edit_mode()
        self._remove_widget(self.TEST_WIDGET_ID, confirm=True)
        count_after_remove = len(self.dashboard_edit_utils.grid_items())
        self.dashboard_edit_utils.save()
        self._reload()
        assert len(self.dashboard_edit_utils.grid_items()) == count_after_remove

    def test_cancel_discards_added_widget(self) -> None:
        """Adding a widget then cancelling leaves the layout unchanged from before edit mode."""
        initial_count = len(self.dashboard_edit_utils.grid_items())
        self.dashboard_edit_utils.enter_edit_mode()
        self.dashboard_edit_utils.add_widget("metric", "applications")
        assert len(self.dashboard_edit_utils.grid_items()) == initial_count + 1
        self.dashboard_edit_utils.exit_edit_mode_cancel()
        assert len(self.dashboard_edit_utils.grid_items()) == initial_count

    def test_cancel_discards_removed_widget(self) -> None:
        """Removing a widget then cancelling restores the widget."""
        initial_count = len(self.dashboard_edit_utils.grid_items())
        self.dashboard_edit_utils.enter_edit_mode()
        self._remove_widget(self.TEST_WIDGET_ID, confirm=True)
        assert len(self.dashboard_edit_utils.grid_items()) == initial_count - 1
        self.dashboard_edit_utils.exit_edit_mode_cancel()
        assert len(self.dashboard_edit_utils.grid_items()) == initial_count

    # ----------------------------------------------- RESET ------------------------------------------------

    def test_reset_restores_default_layout(self) -> None:
        """Resetting restores more widgets than the single-widget test layout."""
        initial_count = len(self.dashboard_edit_utils.grid_items())
        self.dashboard_edit_utils.enter_edit_mode()
        self.dashboard_edit_utils.reset_button.click()
        self.confirm_modal_utils.confirm_button.click()
        self.dashboard_edit_utils.save()
        assert len(self.dashboard_edit_utils.grid_items()) > initial_count

    def test_reset_persists_across_reload(self) -> None:
        """After reset and save, reloading shows the same widget count as right after reset."""
        self.dashboard_edit_utils.enter_edit_mode()
        self.dashboard_edit_utils.reset_button.click()
        self.confirm_modal_utils.confirm_button.click()
        self.dashboard_edit_utils.save()
        count_after_reset = len(self.dashboard_edit_utils.grid_items())
        self._reload()
        assert len(self.dashboard_edit_utils.grid_items()) == count_after_reset
