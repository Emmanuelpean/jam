"""Shared Selenium utility functions used across react_select and base_test."""

import platform
import time

from selenium.common import TimeoutException
from selenium.webdriver import ActionChains, Keys
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait


class SeleniumUtils(object):
    """Mixin providing Selenium utilities. Consumers must set self.driver and self.wait directly."""

    driver: WebDriver = None
    wait: WebDriverWait = None

    def get_webdriver_wait(
        self,
        timeout: float | int | None = None,
        parent: WebElement | WebDriver | None = None,
    ) -> WebDriverWait:
        """Get a WebDriverWait instance with the given timeout"""

        if not parent:
            parent = self.driver
        if timeout:
            return WebDriverWait(parent, timeout)
        else:
            return self.wait

    def go_to_url(self, url: str) -> None:
        """Helper method to go to a specific page"""

        self.driver.execute_script(f"window.history.pushState({{}}, '', '{url}');")
        self.driver.execute_script("window.dispatchEvent(new Event('popstate'));")
        self.wait_for_url(url)

    def wait_for_url(self, url: str, timeout=None) -> None:
        """Wait for the url"""

        try:
            self.get_webdriver_wait(timeout).until(ec.url_to_be(url))
        except:
            raise AssertionError(f"Failed to wait for URL {url}. Current URL: {self.driver.current_url}")

    def advance_browser_clock_days(self, days: int) -> None:
        """Advance the browser clock by the given number of days
        :param days: Number of days to advance the clock by"""

        self.driver.execute_script(
            """
            const RealDate = window.Date;
    
            const offsetMs = Number(arguments[0]) || 0;
            const baseTime = RealDate.now() + offsetMs;
    
            function MockDate(...args) {
                if (this instanceof MockDate) {
                    return args.length
                        ? new RealDate(...args)
                        : new RealDate(baseTime);
                }
                return RealDate();
            }
    
            MockDate.prototype = RealDate.prototype;
    
            // Preserve static methods
            MockDate.now = () => baseTime;
            MockDate.parse = RealDate.parse;
            MockDate.UTC = RealDate.UTC;
    
            window.Date = MockDate;
        """,
            days * 24 * 60 * 60 * 1000,
        )

    def get_all_element_ids(self) -> list[str]:
        """Get all element IDs present on the current page"""

        # Find all elements that have an ID attribute
        elements_with_id = self.driver.find_elements(By.XPATH, "//*[@id]")

        # Extract the ID values
        element_ids = []
        for element in elements_with_id:
            element_id = element.get_attribute("id")
            if element_id:
                element_ids.append(element_id)

        return sorted(element_ids)

    def get_element(
        self,
        element_id: str,
        selector: str = By.ID,
        timeout: float = 10.0,
        enabled: bool = True,
        parent: WebElement | None = None,
    ) -> WebElement:
        """Get an element by its ID, with retry on stale element references.
        :param element_id: ID of the element to get
        :param selector: Selector to use for finding the element
        :param timeout: How long to wait before raising an error
        :param enabled: Whether to wait for the element to be enabled
        :param parent: Parent element to search within"""

        time.sleep(0.1)
        try:
            wait = self.get_webdriver_wait(timeout, parent)
            if parent:
                element = wait.until(lambda p: p.find_element(selector, element_id))
            else:
                if enabled:
                    element = wait.until(ec.element_to_be_clickable((selector, element_id)))
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'})", element)
                else:
                    element = wait.until(ec.presence_of_element_located((selector, element_id)))

            return element

        except Exception:
            context = "parent element" if parent else "page"
            raise AssertionError(
                f"Could not find element {element_id} in {context}\nPossible IDs: {self.get_all_element_ids()}"
            )

    def get_elements(
        self,
        element_id: str,
        selector: str = By.ID,
        timeout: float = 10.0,
        parent: WebElement | None = None,
    ) -> list[WebElement]:
        """Get all matching elements, waiting until at least one is present.
        :param element_id: ID/selector value of the elements to get
        :param selector: Selector to use for finding the elements
        :param timeout: How long to wait before raising an error
        :param parent: Parent element to search within"""

        try:
            wait = self.get_webdriver_wait(timeout, parent)
            if parent:
                wait.until(lambda p: len(p.find_elements(selector, element_id)) > 0)
                return parent.find_elements(selector, element_id)
            else:
                wait.until(ec.presence_of_all_elements_located((selector, element_id)))
                return self.driver.find_elements(selector, element_id)

        except Exception:
            context = "parent element" if parent else "page"
            raise AssertionError(
                f"Could not find elements {element_id} in {context}\nPossible IDs: {self.get_all_element_ids()}"
            )

    def check_element_exists(
        self,
        element_id: str,
        selector: str = By.ID,
        timeout: float = 0.1,
    ) -> bool:
        """Check if an element exists by its ID.
        :param element_id: ID of the element to check
        :param selector: Selector to use for finding the element
        :param timeout: How long to wait before raising an error"""

        try:
            wait = self.get_webdriver_wait(timeout)
            wait.until(ec.presence_of_element_located((selector, element_id)))
            return True
        except TimeoutException:
            return False

    def _get_element_diagnostics(self, element: WebElement) -> str:
        """Get diagnostic information about why an element isn't clickable"""

        diagnostics = []

        # Check visibility
        try:
            is_displayed = element.is_displayed()
            diagnostics.append(f"  - is_displayed(): {is_displayed}")
        except Exception as e:
            diagnostics.append(f"  - is_displayed(): Error - {e}")

        # Check enabled state
        try:
            is_enabled = element.is_enabled()
            diagnostics.append(f"  - is_enabled(): {is_enabled}")
        except Exception as e:
            diagnostics.append(f"  - is_enabled(): Error - {e}")

        # Check CSS properties
        try:
            display = element.value_of_css_property("display")
            visibility = element.value_of_css_property("visibility")
            opacity = element.value_of_css_property("opacity")
            diagnostics.append(f"  - CSS display: {display}")
            diagnostics.append(f"  - CSS visibility: {visibility}")
            diagnostics.append(f"  - CSS opacity: {opacity}")
        except Exception as e:
            diagnostics.append(f"  - CSS properties: Error - {e}")

        # Check position/size
        try:
            size = element.size
            location = element.location
            diagnostics.append(f"  - Size: {size}")
            diagnostics.append(f"  - Location: {location}")
        except Exception as e:
            diagnostics.append(f"  - Size/Location: Error - {e}")

        # Check for overlapping elements
        try:
            overlapping = self._check_overlapping_elements(element)
            if overlapping:
                diagnostics.append(f"  - Overlapping elements detected: {overlapping}")
            else:
                diagnostics.append(f"  - No overlapping elements detected")
        except Exception as e:
            diagnostics.append(f"  - Overlap check: Error - {e}")

        # Check page load state
        try:
            ready_state = self.driver.execute_script("return document.readyState;")
            diagnostics.append(f"  - Page readyState: {ready_state}")
        except Exception as e:
            diagnostics.append(f"  - Page state: Error - {e}")

        return "\n".join(diagnostics)

    def _check_overlapping_elements(self, element: WebElement) -> str:
        """Check if another element is overlaying the target element"""

        try:
            # Get element center point
            location = element.location
            size = element.size
            center_x = location["x"] + size["width"] / 2
            center_y = location["y"] + size["height"] / 2

            # Find element at that point using JavaScript
            script = """
                var element = arguments[0];
                var x = arguments[1];
                var y = arguments[2];
                var topElement = document.elementFromPoint(x, y);
                
                if (topElement === element) {
                    return null;
                }
                
                // Return info about the overlapping element
                return {
                    tag: topElement.tagName,
                    id: topElement.id || 'no-id',
                    class: topElement.className || 'no-class',
                    zIndex: window.getComputedStyle(topElement).zIndex
                };
                """

            result = self.driver.execute_script(script, element, center_x, center_y)

            if result:
                return f"<{result['tag']} id='{result['id']}' class='{result['class']}' z-index='{result['zIndex']}'>"
            return ""

        except Exception as e:
            return f"Error checking overlap: {e}"

    def wait_for_element_text(
        self,
        element_id: str,
        expected_text: str,
        selector: str = By.ID,
        timeout: float | int | None = None,
    ) -> bool:
        """Wait for an element's text to become the expected value.
        :param element_id: ID of the element to check
        :param expected_text: The text value to wait for
        :param selector: Selector to use for finding the element
        :param timeout: How long to wait before raising an error
        :return: The element once its text matches"""

        def text_matches(driver) -> bool:
            """Check if the element's text matches the expected value
            :param driver: WebDriver instance
            :return True if the text matches, False otherwise"""

            try:
                el = driver.find_element(selector, element_id)
                return el if el.text == expected_text else False
            except:
                return False

        try:
            wait = self.get_webdriver_wait(timeout)
            return wait.until(text_matches)
        except TimeoutException:
            # Get actual text for error message
            try:
                element = self.driver.find_element(selector, element_id)
                actual_text = element.text
            except:
                actual_text = "<element not found>"
            raise AssertionError(
                f"Element '{element_id}' text did not become '{expected_text}' within {timeout}s. "
                f"Actual text: '{actual_text}'"
            )

    def wait_for_disappear(
        self,
        element_id: str,
        selector: str = By.ID,
        timeout: float | int | None = None,
    ) -> None:
        """Wait for an element to disappear from the DOM
        :param element_id: ID of the element to get
        :param selector: Selector to use for finding the element
        :param timeout: How long to wait before raising an error"""

        try:
            wait = self.get_webdriver_wait(timeout)
            wait.until(ec.invisibility_of_element_located((selector, element_id)))
        except TimeoutException:
            raise AssertionError(f"Element {element_id} did not disappear")

    def assert_not_visible(self, element_id: str) -> None:
        """Assert that an element is not visible"""

        assert not self.driver.find_elements(By.ID, element_id)

    def context_menu(self, element: WebElement, choice: str) -> None:
        """Row context menu"""

        actions = ActionChains(self.driver)
        actions.context_click(element).perform()
        context_menu = self.get_element(f"context-menu-{choice}")
        assert context_menu, "Context menu not found"
        context_menu.click()

    @staticmethod
    def set_text(
        element: WebElement,
        text: str = "",
    ) -> None:
        """Clears the input element"""

        modifier_key = Keys.COMMAND if platform.system() == "Darwin" else Keys.CONTROL
        element.send_keys(modifier_key, "a")
        element.send_keys(Keys.DELETE)
        element.send_keys(text)

    def _wait_for_modal_close(
        self,
        name: str,
        timeout: float | int | None = None,
    ) -> None:
        """Wait for the modal to close"""

        try:
            self.get_webdriver_wait(timeout).until(ec.invisibility_of_element_located((By.ID, name)))
        except:
            raise AssertionError(f"{name} is present in: {self.get_all_element_ids()}")

    @staticmethod
    def get_attribute(element: WebElement, attribute: str) -> str:
        """Get the value of an element's attribute"""

        attribute_value = element.get_attribute(attribute)
        if not attribute_value:
            raise AssertionError(f"Attribute '{attribute}' not found on element: {element}")
        return attribute_value
