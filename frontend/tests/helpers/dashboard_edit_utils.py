"""Utilities for the customisable dashboard's edit-mode toolbar, widget picker and per-widget config."""

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from helpers.jam_test_utils import JamTestUtils


class DashboardEditUtils(JamTestUtils):
    """Test class for the dashboard edit-mode toolbar: enter/save/cancel, add/remove widgets,
    reset to the default layout, and the per-widget config sidebar's gear button."""

    def __init__(self, **kwargs):
        self._init(**kwargs)

    # ------------------------------------------------- ELEMENTS -------------------------------------------------

    @property
    def edit_button(self) -> WebElement:
        """The pencil button that toggles edit mode."""

        return self.get_element("dashboard-edit-btn")

    @property
    def save_button(self) -> WebElement:
        """The save button, visible only in edit mode."""

        return self.get_element("dashboard-save-btn")

    @property
    def add_widget_button(self) -> WebElement:
        """The button that opens the widget picker."""

        return self.get_element("dashboard-add-widget-btn")

    @property
    def reset_button(self) -> WebElement:
        """The 'reset to default layout' button."""

        return self.get_element("dashboard-reset-btn")

    def config_button(self, widget_id: str, enabled: bool = True) -> WebElement:
        """The gear button that opens a widget's per-widget config sidebar."""

        return self.get_element(f"widget-config-btn-{widget_id}", enabled=enabled)

    def remove_button(self, widget_id: str, enabled: bool = True) -> WebElement:
        """The remove ('x') button for a widget, visible only in edit mode."""

        return self.get_element(f"widget-remove-btn-{widget_id}", enabled=enabled)

    def picker_type_card(self, widget_type: str) -> WebElement:
        """The widget-type card in the widget picker modal."""

        return self.get_element(f"widget-picker-type-{widget_type}")

    def picker_variant_card(self, variant_key: str) -> WebElement:
        """The variant card in the widget picker modal, shown after picking a type."""

        return self.get_element(f"widget-picker-variant-{variant_key}")

    def widget_config_field(self, card_id: str, field: str) -> WebElement:
        """A field inside a widget's per-widget config sidebar (e.g. 'chaseThreshold')."""

        return self.get_element(f"{card_id}-{field}")

    def grid_items(self) -> list[WebElement]:
        """All widget cards currently on the dashboard grid."""

        return self.driver.find_elements(By.CSS_SELECTOR, ".dashboard-grid-item")

    # -------------------------------------------------- HELPERS --------------------------------------------------

    def enter_edit_mode(self) -> None:
        """Click the pencil button to enter edit mode."""

        self.edit_button.click()
        self.get_elements("dashboard-save-btn")

    def exit_edit_mode_cancel(self) -> None:
        """Click the edit/cancel toggle button to cancel (exit without saving)."""

        self.edit_button.click()
        self.wait_for_disappear("dashboard-save-btn")

    def save(self) -> None:
        """Click save and wait for the save button to disappear (edit mode exits)."""

        self.save_button.click()
        self.wait_for_disappear("dashboard-save-btn")

    def add_widget(self, widget_type: str, variant_key: str) -> None:
        """Open the widget picker, select a type then a variant."""

        self.add_widget_button.click()
        self.picker_type_card(widget_type).click()
        self.picker_variant_card(variant_key).click()
        self.wait_for_disappear(f"widget-picker-variant-{variant_key}")

    def click_remove(self, widget_id: str) -> None:
        """Click a widget's remove button (opens the delete confirmation dialog)."""

        self.remove_button(widget_id).click()
