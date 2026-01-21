"""Module to interact with react-select components using Selenium"""

import time
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait
from typing import Any


def get_all_element_ids(driver) -> list[str]:
    """Get all element IDs present on the current page
    :param driver: Selenium WebDriver instance"""

    # Find all elements that have an ID attribute
    elements_with_id = driver.find_elements(By.XPATH, "//*[@id]")

    # Extract the ID values
    element_ids = []
    for element in elements_with_id:
        element_id = element.get_attribute("id")
        if element_id:
            element_ids.append(element_id)

    return sorted(element_ids)


def get_element(
    driver: WebDriver,
    element_id: str,
    selector: str = By.ID,
    timeout: float = 10.0,
    parent: WebElement = None,
    multiple: bool = False,
) -> None | list[WebElement] | WebElement | Any:
    """Get an element or multiple elements by selector.
    :param driver: Selenium WebDriver instance
    :param element_id: ID/value of the element to get
    :param selector: Selector to use for finding the element
    :param timeout: How long to wait before raising an error
    :param parent: Optional parent WebElement to search within
    :param multiple: If True, return list of all matching elements using find_elements
    :return: Single WebElement or list of WebElements if multiple=True"""

    try:
        if parent:
            # When searching within a parent element
            wait = WebDriverWait(parent, timeout)

            if multiple:
                # Wait for at least one element, then return all matching elements
                wait.until(lambda p: len(p.find_elements(selector, element_id)) > 0)
                elements = parent.find_elements(selector, element_id)
                return elements
            else:
                element = wait.until(lambda p: p.find_element(selector, element_id))
        else:
            wait = WebDriverWait(driver, timeout)

            if multiple:
                # Wait for at least one element, then return all matching elements
                wait.until(ec.presence_of_all_elements_located((selector, element_id)))
                elements = driver.find_elements(selector, element_id)
                return elements
            else:
                element = wait.until(ec.element_to_be_clickable((selector, element_id)))

        if not multiple:
            ActionChains(driver).move_to_element(element).perform()
            return element

    except Exception:
        context = f"parent element" if parent else "page"
        element_type = "elements" if multiple else "element"
        raise AssertionError(
            f"Could not find {element_type} {element_id} in {context}\nPossible IDs: {get_all_element_ids(driver)}"
        )


class ReactSelect(object):
    """Class to interact with a react-select component"""

    def __init__(self, web_element) -> None:
        """Initialize the ReactSelect with a WebElement representing the select component"""

        self.driver = web_element.parent
        self.select_menu = web_element
        self.wait = WebDriverWait(self.driver, 1)

        self.select_menu_locator = "react-select__menu"
        self.select_value = "react-select__multi-value"
        self.select_single_value = "react-select__single-value"
        self.select_control = "react-select__control"
        self.select_value_container = "react-select__value-container"
        self.options_locator = "//div[@role='option']"
        self.select_clear = "react-select__clear-indicator"
        self.select_value_icon = "react-select__multi-value__remove"
        self.select_value_label = "react-select__multi-value__label"

        self.value_container_element = get_element(
            self.driver, self.select_value_container, By.CLASS_NAME, parent=self.select_menu
        )
        self.is_multiple = "select__value-container--is-multi" in self.value_container_element.get_attribute("class")

    @property
    def menu(self) -> WebElement:
        """Returns the menu WebElement"""

        input_el = get_element(self.driver, "input", By.CSS_SELECTOR, parent=self.select_menu)
        input_id = input_el.get_attribute("id")  # e.g. 'react-select-3-input'
        menu_id = input_id.replace("input", "listbox")
        return self.driver.find_element(By.ID, menu_id)

    @property
    def selected_options_on_line(self) -> list[WebElement]:
        """Returns a list of all selected options currently visible in the select line"""

        if not self.is_multiple:
            return get_element(self.driver, self.select_single_value, By.CLASS_NAME, parent=self.select_menu)
        else:
            return get_element(self.driver, self.select_value, By.CLASS_NAME, parent=self.select_menu, multiple=True)

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
        """The first selected option in this select tag (or the currently selected option in a
        normal select)"""

        for opt in self.options:
            if opt.is_selected():
                return opt
        raise NoSuchElementException("No options are selected")

    def select_by_index(self, index) -> None:
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

        wanted_elements_indexes = [self._get_option_index(i) for i in self.options if i.text.strip() == text.strip()]

        if len(wanted_elements_indexes) == 0:
            raise NoSuchElementException("Could not locate element with text {0}".format(text))

        for element_index in wanted_elements_indexes:
            self.select_by_index(element_index)

            if not self.is_multiple:
                return

    def deselect_by_index(self, index) -> None:
        """Deselect the option at the given index (0-based) (only for multi-selects)"""

        if not self.is_multiple:
            raise NotImplementedError("You may only deselect options of a multi-select")

        index = int(index)
        if len(self.selected_options_on_line) < index:
            raise NoSuchElementException("Could not locate element with index %d %index")

        self._unset_selected(self.selected_options_on_line[index])

    def deselect_by_visible_text(self, text) -> None:
        """Deselect all options that display text matching the argument (only for multi-selects)"""

        if not self.is_multiple:
            raise NotImplementedError("You may only deselect options of a multi-select")

        selected = False

        for opt in self.selected_options_on_line:
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

    @staticmethod
    def _get_option_index(option) -> list[str]:
        """Get the index of the given option element"""

        return option.get_attribute("id").split("option-")[1]

    @staticmethod
    def _set_selected(option) -> None:
        """Select the given option element"""

        if not option.is_selected():
            option.click()

    def _is_menu_open(self) -> bool:
        """Check if the select menu is currently open"""

        max_attempts = 3
        for attempt in range(max_attempts):
            try:
                children = get_element(self.driver, "*", By.CSS_SELECTOR, parent=self.select_menu, multiple=True)
                for child in children:
                    child_classy = child.get_attribute("class")
                    child_classy = "" if child_classy is None else child_classy
                    if self.select_menu_locator in child_classy:
                        return True
                return False

            except StaleElementReferenceException:
                if attempt == max_attempts - 1:
                    raise
                time.sleep(0.1)
                continue

        return False

    def _close_menu(self) -> None:
        """Close the select menu if it is open"""

        if self._is_menu_open():
            self._click_select_arrow_button()

    def _unset_selected(self, selected_option) -> None:
        """Deselect the given selected option element"""

        get_element(self.driver, self.select_value_icon, By.CLASS_NAME, parent=selected_option).click()

    def _click_select_arrow_button(self) -> None:
        """Click the select arrow button to open/close the menu"""

        time.sleep(0.2)
        get_element(self.driver, self.select_control, By.CLASS_NAME, parent=self.select_menu).click()
        time.sleep(0.2)
