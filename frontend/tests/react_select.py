import time

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait


class ReactSelect(object):

    @staticmethod
    def add_prefix(value, prefix):
        return prefix + value

    def __init__(self, web_element, prefix=""):
        self.driver = web_element.parent
        self.select_menu = web_element
        self.wait = WebDriverWait(self.driver, 1)

        self.select_menu_locator = ReactSelect.add_prefix("react-select__menu", prefix)
        self.select_value = ReactSelect.add_prefix("react-select__multi-value", prefix)
        self.select_single_value = ReactSelect.add_prefix("react-select__single-value", prefix)
        self.select_control = ReactSelect.add_prefix("react-select__control", prefix)
        self.select_value_container = ReactSelect.add_prefix("react-select__value-container", prefix)
        self.options_locator = "//div[@role='option']"
        self.select_clear = ReactSelect.add_prefix("react-select__clear-indicator", prefix)
        self.select_value_icon = ReactSelect.add_prefix("react-select__multi-value__remove", prefix)
        self.select_value_label = ReactSelect.add_prefix("react-select__multi-value__label", prefix)

        self.is_multiple = "select__value-container--is-multi" in self.select_menu.find_element(
            By.CLASS_NAME, self.select_value_container
        ).get_attribute("class")

    @property
    def menu(self):
        input_el = self.select_menu.find_element(By.CSS_SELECTOR, "input")
        input_id = input_el.get_attribute("id")  # e.g. 'react-select-3-input'
        menu_id = input_id.replace("input", "listbox")
        return self.driver.find_element(By.ID, menu_id)

    @property
    def selected_options_on_line(self):
        if not self.is_multiple:
            return self.select_menu.find_elements(By.CLASS_NAME, self.select_single_value)

        return self.select_menu.find_elements(By.CLASS_NAME, self.select_value)

    @property
    def options(self):
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
    def first_selected_option(self) -> None:
        """The first selected option in this select tag (or the currently selected option in a
        normal select)"""
        for opt in self.options:
            if opt.is_selected():
                return opt
        raise NoSuchElementException("No options are selected")

    def select_by_index(self, index) -> None:
        match = str(index)
        for opt in self.options:
            if self._get_option_index(opt) == match:
                self._setSelected(opt)
                self._close_menu()
                return

        raise NoSuchElementException("Could not locate element with index %d" % index)

    def deselect_all(self) -> None:

        if not self.is_multiple and len(self.select_menu.find_elements(By.CLASS_NAME, self.select_clear)) == 0:
            raise Exception("There is no deselect all button")

        self.select_menu.find_element(By.CLASS_NAME, self.select_clear).click()

    def select_by_visible_text(self, text) -> None:
        wanted_elements_indexes = [self._get_option_index(i) for i in self.options if i.text.strip() == text.strip()]

        if len(wanted_elements_indexes) == 0:
            raise NoSuchElementException("Could not locate element with text {0}".format(text))

        for element_index in wanted_elements_indexes:
            self.select_by_index(element_index)

            if not self.is_multiple:
                return

    def deselect_by_index(self, index) -> None:
        if not self.is_multiple:
            raise NotImplementedError("You may only deselect options of a multi-select")

        index = int(index)
        if len(self.selected_options_on_line) < index:
            raise NoSuchElementException("Could not locate element with index %d %index")

        self._unsetSelected(self.selected_options_on_line[index])

    def deselect_by_visible_text(self, text) -> None:
        if not self.is_multiple:
            raise NotImplementedError("You may only deselect options of a multi-select")

        selected = False

        for opt in self.selected_options_on_line:
            if opt.find_element(By.CLASS_NAME, self.select_value_label).text.strip() == text.strip():
                self._unsetSelected(opt)
                selected = True

        if not selected:
            raise NoSuchElementException("Could not locate element with text {0}".format(text))

    def open_menu(self) -> None:
        if self._is_menu_open():
            return

        self._click_select_arrow_button()

    @staticmethod
    def _get_option_index(option) -> list[str]:
        return option.get_attribute("id").split("option-")[1]

    @staticmethod
    def _setSelected(option) -> None:
        if not option.is_selected():
            option.click()

    def _is_menu_open(self) -> bool:
        children = self.select_menu.find_elements(By.CSS_SELECTOR, "*")
        for child in children:
            child_classy = child.get_attribute("class")
            child_classy = "" if child_classy is None else child_classy
            if self.select_menu_locator in child_classy:
                return True

        return False

    def _close_menu(self) -> None:
        if self._is_menu_open():
            self._click_select_arrow_button()

    def _unsetSelected(self, selected_option) -> None:
        selected_option.find_element(By.CLASS_NAME, self.select_value_icon).click()

    def _click_select_arrow_button(self) -> None:
        time.sleep(0.2)
        self.select_menu.find_element(By.CLASS_NAME, self.select_control).click()
        time.sleep(0.2)
