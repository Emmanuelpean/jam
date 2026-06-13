"""Utilities for the guided tour."""

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.wait import WebDriverWait

from utilities.base_utils import BaseUtils


class TourUtils(BaseUtils):

    def __init__(self, **kwargs):
        self._init(**kwargs)

    NON_PREMIUM_TOUR_IDS = [
        "app-overview",
        "first-job",
        "log-application",
        "log-interview",
        "log-update",
        "follow-up-email",
        "add-contact",
        "speculative-applications",
    ]
    PREMIUM_TOUR_IDS = NON_PREMIUM_TOUR_IDS + ["import-scraped-job", "scraping-filters"]

    # Tour element IDs
    TOUR_POPOVER = "tour-popover"
    TOUR_TITLE = "tour-popover-title"
    TOUR_COUNTER = "tour-step-counter"
    TOUR_SKIP = "tour-skip-btn"
    TOUR_NEXT = "tour-next-btn"
    TOUR_BACK = "tour-back-btn"
    TOUR_BACKDROP = "tour-backdrop"

    # Tour select panel
    TAKE_A_TOUR_BTN = "take-a-tour-btn"
    TSP_PANEL = "tsp-panel"
    TSP_PROGRESS = "tsp-progress"

    TOTAL_STEPS = 6  # intro, dashboard-overview, dashboard-customise, sidebar, premium, command-palette
    TOUR_NAME = "App Overview"
    TOUR_ID = "app-overview"

    def open_tour_select(self) -> None:
        """Click 'Take a Tour' to open the tour select panel.

        Uses a JS click to bypass sidebar animation / clickability edge cases:
        the button is always in the sidebar DOM and its React onClick fires regardless
        of whether the About submenu is visually open or the sidebar is mid-transition.
        """
        self.get_element(self.TAKE_A_TOUR_BTN, enabled=False)  # wait for element to exist
        self.driver.execute_script(f"document.getElementById('{self.TAKE_A_TOUR_BTN}').click();")
        self.get_element(self.TSP_PANEL, enabled=False, timeout=5)

    def start_tour(self, tour_id: str = TOUR_ID, popover_timeout: float = 10.0) -> None:
        """Open the tour select panel and start the given tour."""
        self.open_tour_select()
        self.get_element(f"tsp-item-{tour_id}").click()
        self.wait_for_popover(timeout=popover_timeout)

    def wait_for_popover(self, timeout: float = 10.0) -> None:
        """Wait for the tour popover to appear in the DOM."""
        self.get_element(self.TOUR_POPOVER, timeout=timeout, enabled=False)

    def wait_for_popover_gone(self, timeout: float = 10.0) -> None:
        """Wait for the tour popover to disappear."""
        self.wait_for_disappear(self.TOUR_POPOVER, timeout=timeout)

    def popover_title(self) -> str:
        """Tour popover title"""
        return self.get_element(self.TOUR_TITLE, enabled=False).text

    def step_counter_text(self) -> str:
        """Tour step counter text"""
        return self.get_element(self.TOUR_COUNTER, enabled=False).text

    def click_next(self) -> None:
        """Click the next tour step button."""
        self.get_element(self.TOUR_NEXT).click()

    def click_back(self) -> None:
        """Click the back tour step button."""
        self.get_element(self.TOUR_BACK).click()

    def click_skip(self) -> None:
        """Click the skip tour button."""
        self.get_element(self.TOUR_SKIP).click()

    def advance_steps(self, n: int) -> None:
        """Click Next n times, waiting for the popover between each click."""
        for _ in range(n):
            self.wait_for_popover()
            self.click_next()

    def advance_to_last_step(self) -> None:
        """Click through steps until the Done button is visible."""
        for _ in range(self.TOTAL_STEPS):
            self.wait_for_popover()
            next_btn = self.get_element(self.TOUR_NEXT)
            if "Done" in next_btn.text:
                return
            next_btn.click()

    def wait_for_step(self, n: int, timeout: float = 10.0) -> None:
        """Wait until the step counter shows Step N (case-insensitive, CSS may uppercase the text)."""
        WebDriverWait(self.driver, timeout).until(
            lambda d: f"STEP {n} OF" in d.find_element(By.ID, self.TOUR_COUNTER).text.upper()
        )

    @property
    def keep_data_toggle(self) -> WebElement:
        """Keep my data toggle on the done step."""
        return self.get_element("tour-keep-data")

    def poll_db_count(self, model_class, owner_id: int, expected: int, timeout: float = 10.0) -> None:
        """Poll the DB until the row count for owner_id equals expected, or raise."""
        self.poll_db_value(
            lambda: self.db.query(model_class).filter_by(owner_id=owner_id).count(),
            expected,
            timeout=timeout,
        )
