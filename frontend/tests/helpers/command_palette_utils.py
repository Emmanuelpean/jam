"""Utilities for the command palette (Ctrl+K)."""

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement

from helpers.jam_test_utils import JamTestUtils


class CommandPaletteUtils(JamTestUtils):
    """Test class for the command palette opened via Ctrl+K."""

    def __init__(self, **kwargs):
        self._init(**kwargs)

    # ------------------------------------------------- ELEMENTS -------------------------------------------------

    @property
    def input(self) -> WebElement:
        """The search input in the command palette."""

        return self.get_element("cp-input")

    @property
    def active_item(self) -> WebElement:
        """The currently highlighted item."""

        return self.get_element("[id^='cp-item-'].active", selector=By.CSS_SELECTOR)

    def item(self, item_id: str) -> WebElement:
        """A specific palette item by its id suffix (e.g. 'goto-interviews', 'company-42')."""

        return self.get_element(f"cp-item-{item_id}")

    def item_matching(self, id_prefix: str) -> WebElement:
        """The single item whose id starts with the given prefix, waiting for it to appear."""

        return self.get_element(f"[id^='cp-item-{id_prefix}']", selector=By.CSS_SELECTOR)

    def items(self, id_prefix: str = "") -> list[WebElement]:
        """All currently listed items, optionally filtered to those with the given id prefix."""

        return self.driver.find_elements(By.CSS_SELECTOR, f"[id^='cp-item-{id_prefix}']")

    def group_headers(self) -> list[str]:
        """Text of all visible group headers (e.g. ACTIONS, PAGES, COMPANIES)."""

        return [h.text for h in self.driver.find_elements(By.CSS_SELECTOR, "[id^='cp-group-']")]

    @staticmethod
    def item_label(item: WebElement) -> str:
        """The visible label text of a palette item."""

        return item.find_element(By.CSS_SELECTOR, ".cp-item-label").text

    # -------------------------------------------------- HELPERS --------------------------------------------------

    def open(self) -> None:
        """Open the command palette with Ctrl+K."""

        self.driver.find_element(By.TAG_NAME, "body").send_keys(Keys.CONTROL + "k")
        self.get_element("cp-input", timeout=5)

    def press_ctrl_k(self) -> None:
        """Press Ctrl+K without waiting for the palette to open (used to toggle it closed)."""

        self.driver.find_element(By.TAG_NAME, "body").send_keys(Keys.CONTROL + "k")

    def is_open(self) -> bool:
        """Whether the palette backdrop is present."""

        return self.check_element_exists("cp-backdrop")

    def wait_for_close(self) -> None:
        """Wait for the palette to close."""

        self.wait_for_disappear("cp-backdrop")

    def search(self, query: str) -> None:
        """Type into the search input."""

        self.input.send_keys(query)
