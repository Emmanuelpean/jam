"""Module to interact with react-select components using Selenium"""

import time

from selenium.common.exceptions import (
    NoSuchElementException,
    StaleElementReferenceException,
    TimeoutException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait

from helpers.selenium_utils import SeleniumUtils


class Select(SeleniumUtils):
    """Class to interact with a react-select component"""

    def __init__(self, web_element: WebElement) -> None:
        """Initialise the ReactSelect with a WebElement representing the select component"""

        self.driver = web_element.parent
        self.wait = WebDriverWait(web_element.parent, 1)

        self.select_menu = web_element
        self.select_menu_locator = "jam-select__menu"
        self.select_value = "jam-select__tag"
        self.select_single_value = "jam-select__single-value"
        self.select_control = "jam-select__control"
        self.select_value_container = "jam-select__values"
        self.options_locator = "//div[@role='option']"
        self.select_clear = "jam-select__clear"
        self.select_value_icon = "jam-select__tag-remove"
        self.select_value_label = "jam-select__tag-label"

        self.value_container_element = self.get_element(
            self.select_value_container, By.CLASS_NAME, parent=self.select_menu
        )
        self.value_container_class = self.value_container_element.get_attribute("class")
        assert self.value_container_class
        self.is_multiple = "jam-select--multi" in self.value_container_class

    @property
    def menu(self) -> WebElement:
        """Returns the menu WebElement"""

        container_id = self.get_attribute(self.select_menu, "id")
        menu_id = container_id + "-listbox"
        return WebDriverWait(self.driver, 5).until(ec.presence_of_element_located((By.ID, menu_id)))

    @property
    def selected_options_on_line(self) -> list[WebElement] | WebElement:
        """Returns a list of all selected options currently visible in the select line"""

        if not self.is_multiple:
            return self.get_element(self.select_single_value, By.CLASS_NAME, parent=self.select_menu)
        else:
            return self.get_elements(self.select_value, By.CLASS_NAME, parent=self.select_menu)

    @property
    def options(self) -> list[WebElement]:
        """Returns a list of all options belonging to this select tag"""

        return self.menu.find_elements(By.XPATH, self.options_locator)

    @property
    def all_selected_options(self) -> list[str]:
        """Returns a list of all selected options belonging to this select tag"""

        ret = []
        for opt in self.options:
            if opt.is_selected():
                ret.append(opt)
        return ret

    @property
    def first_selected_option(self) -> None | WebElement:
        """The first selected option in this select tag (or the currently selected option in a normal select)"""

        for opt in self.options:
            if opt.is_selected():
                return opt
        raise NoSuchElementException("No options are selected")

    def select_by_index(self, index: int | str) -> None:
        """Select the option at the given index (0-based)"""

        match = str(index)
        for opt in self.options:
            if self._get_option_index(opt) == match:
                self._set_selected(opt)
                self._close_menu()
                return

        raise NoSuchElementException("Could not locate element with index %d" % index)

    def deselect_all(self) -> None:
        """Deselect all selected options (only for multi-selects)"""

        if not self.is_multiple and len(self.select_menu.find_elements(By.CLASS_NAME, self.select_clear)) == 0:
            raise Exception("There is no deselect all button")

        self.select_menu.find_element(By.CLASS_NAME, self.select_clear).click()

    def select_by_visible_text(self, text) -> None:
        """Select all options that display text matching the argument"""

        self.open_menu()

        def _matching_indexes(_driver) -> list[str]:
            """Return option indexes whose text matches, tolerating options that are
            present but not yet populated/rendered (react-select renders the option
            elements before their text is available)."""

            try:
                return [
                    self._get_option_index(opt) for opt in self.options if opt.text.strip() == text.strip()
                ]
            except StaleElementReferenceException:
                return []

        try:
            wanted_elements_indexes = WebDriverWait(self.driver, 5).until(lambda d: _matching_indexes(d) or False)
        except TimeoutException:
            raise NoSuchElementException("Could not locate element with text {0}".format(text))

        for element_index in wanted_elements_indexes:
            self.select_by_index(element_index)

            if not self.is_multiple:
                return

    def deselect_by_index(self, index: int | str) -> None:
        """Deselect the option at the given index (0-based) (only for multi-selects)"""

        selected_options_on_line = self.selected_options_on_line
        if not self.is_multiple or not isinstance(selected_options_on_line, list):
            raise NotImplementedError("You may only deselect options of a multi-select")

        index = int(index)
        if len(selected_options_on_line) < index:
            raise NoSuchElementException("Could not locate element with index %d %index")

        self._unset_selected(selected_options_on_line[index])

    def deselect_by_visible_text(self, text: str) -> None:
        """Deselect all options that display text matching the argument (only for multi-selects)"""

        selected_options_on_line = self.selected_options_on_line
        if not self.is_multiple or not isinstance(selected_options_on_line, list):
            raise NotImplementedError("You may only deselect options of a multi-select")

        selected = False

        for opt in selected_options_on_line:
            if opt.find_element(By.CLASS_NAME, self.select_value_label).text.strip() == text.strip():
                self._unset_selected(opt)
                selected = True

        if not selected:
            raise NoSuchElementException("Could not locate element with text {0}".format(text))

    def open_menu(self) -> None:
        """Open the select menu"""

        if self._is_menu_open():
            return

        self._click_select_arrow_button()

    def _get_option_index(self, option: WebElement) -> str:
        """Get the index of the given option element"""

        id_attribute = self.get_attribute(option, "id")
        return id_attribute.split("option-")[1]

    @staticmethod
    def _set_selected(option: WebElement) -> None:
        """Select the given option element"""

        if not option.is_selected():
            option.click()

    def _is_menu_open(self) -> bool:
        """Check if the select menu is currently open"""

        max_attempts = 3
        for attempt in range(max_attempts):
            try:
                input_el = self.select_menu.find_element(By.CSS_SELECTOR, "input[role='combobox']")
                return input_el.get_attribute("aria-expanded") == "true"
            except StaleElementReferenceException:
                if attempt == max_attempts - 1:
                    raise
                time.sleep(0.1)
                continue

        return False

    def _close_menu(self) -> None:
        """Close the select menu if it is open.

        Uses JavaScript dispatch instead of a Selenium click because the backdrop overlay
        (z-index 9998) covers the control element, causing ElementClickInterceptedException
        when the select menu is open."""

        if self._is_menu_open():
            control = self.select_menu.find_element(By.CLASS_NAME, self.select_control)
            self.driver.execute_script(
                "arguments[0].dispatchEvent(new MouseEvent('mousedown', {bubbles: true, cancelable: true, view: window, buttons: 1}))",
                control,
            )
            time.sleep(0.2)

    def _unset_selected(self, selected_option: WebElement) -> None:
        """Deselect the given selected option element"""

        self.get_element(self.select_value_icon, By.CLASS_NAME, parent=selected_option).click()

    def _click_select_arrow_button(self) -> None:
        """Click the select arrow button to open/close the menu"""

        time.sleep(0.2)
        self.get_element(self.select_control, By.CLASS_NAME, parent=self.select_menu).click()
        time.sleep(0.2)
