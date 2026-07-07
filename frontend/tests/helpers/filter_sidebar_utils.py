"""Utilities for the Filter Sidebar on data tables."""

import time

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from helpers.base_utils import BaseUtils


class FilterSidebarUtils(BaseUtils):
    """Helpers for applying filters via the filter sidebar and reading its date presets."""

    def __init__(self, **kwargs):
        self._init(**kwargs)

    def apply_text_filter(self, key: str, value: str) -> None:
        """Type into a text filter input and wait for the debounced results."""

        self.get_element(f"filter-input-{key}").send_keys(value)
        time.sleep(0.5)

    def apply_number_min(self, key: str, value: str) -> None:
        """Set a number filter's minimum and wait for the debounced results."""

        self.set_text(self.get_element(f"filter-num-min-{key}"), value)
        time.sleep(0.5)

    def date_preset_button(self, key: str, label_fragment: str) -> WebElement:
        """Return the date-preset button in a section whose label contains the fragment."""

        section = self.get_element(f"filter-section-{key}")
        buttons = section.find_elements(By.CLASS_NAME, "filter-date-preset-btn")
        return next(b for b in buttons if label_fragment in b.text)
