"""Selenium tests for the command palette (keyboard shortcuts + UI)."""

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from base_test import BaseTest

CP_ITEM_ACTIVE = "[id^='cp-item-'].active"
CP_ITEM_LABEL = ".cp-item-label"


class TestCommandPalette(BaseTest):
    user_index = 0
    page_url = "dashboard"

    def setup_function(self, request) -> None:
        self.login()

    # -------------------------------------------------- HELPERS --------------------------------------------------

    def _open_with_ctrl_k(self) -> None:
        self.driver.find_element(By.TAG_NAME, "body").send_keys(Keys.CONTROL + "k")
        self.get_element("cp-backdrop", enabled=False, timeout=5)

    def _open_with_double_shift(self) -> None:
        ActionChains(self.driver).key_down(Keys.SHIFT).key_up(Keys.SHIFT).key_down(Keys.SHIFT).key_up(
            Keys.SHIFT
        ).perform()
        self.get_element("cp-backdrop", enabled=False, timeout=5)

    def _get_input(self):
        return self.get_element("cp-input")

    def _get_items(self):
        return self.driver.find_elements(By.CSS_SELECTOR, "[id^='cp-item-']")

    def _is_open(self) -> bool:
        return self.check_element_exists("cp-backdrop", By.ID)

    def _wait_for_closed(self) -> None:
        WebDriverWait(self.driver, 5).until(EC.invisibility_of_element_located((By.ID, "cp-backdrop")))

    # --------------------------------------------------- OPEN/CLOSE ---------------------------------------------------

    def test_open_with_ctrl_k(self) -> None:
        """Ctrl+K opens the command palette."""
        self._open_with_ctrl_k()
        assert self._is_open()

    def test_open_with_double_shift(self) -> None:
        """Double-shift opens the command palette."""
        self._open_with_double_shift()
        assert self._is_open()

    def test_close_with_escape(self) -> None:
        """Escape closes the command palette."""
        self._open_with_ctrl_k()
        self._get_input().send_keys(Keys.ESCAPE)
        self._wait_for_closed()
        assert not self._is_open()

    def test_close_by_clicking_backdrop(self) -> None:
        """Clicking outside the card on the backdrop closes the palette."""
        self._open_with_ctrl_k()
        # Viewport is 1960x1080; card is max 560px wide and centered (~x700-1260).
        # Click at (100, 100) — well outside the card. body center is (980, 540),
        # so offset (-880, -440) lands at approximately (100, 100).
        body = self.driver.find_element(By.TAG_NAME, "body")
        ActionChains(self.driver).move_to_element_with_offset(body, -880, -440).click().perform()
        self._wait_for_closed()
        assert not self._is_open()

    def test_ctrl_k_toggles_palette(self) -> None:
        """Pressing Ctrl+K a second time closes the palette."""
        self._open_with_ctrl_k()
        self.driver.find_element(By.TAG_NAME, "body").send_keys(Keys.CONTROL + "k")
        self._wait_for_closed()
        assert not self._is_open()

    # --------------------------------------------------- CONTENT ---------------------------------------------------

    def test_input_is_focused_on_open(self) -> None:
        """Search input is auto-focused when the palette opens."""
        self._open_with_ctrl_k()
        inp = self.get_element("cp-input")
        WebDriverWait(self.driver, 5).until(lambda d: d.switch_to.active_element == inp)

    def test_groups_are_shown(self) -> None:
        """Actions and Pages group headers are visible."""
        self._open_with_ctrl_k()
        headers = self.driver.find_elements(By.CSS_SELECTOR, "[id^='cp-group-']")
        texts = [h.text for h in headers]
        assert "ACTIONS" in texts
        assert "PAGES" in texts

    def test_all_pages_listed(self) -> None:
        """All expected page items appear in the list."""
        self._open_with_ctrl_k()
        labels = [el.text for el in self.driver.find_elements(By.CSS_SELECTOR, CP_ITEM_LABEL)]
        for expected in ("Dashboard", "Jobs", "People", "Companies", "Interviews", "Settings"):
            assert expected in labels, f"'{expected}' not found in palette items"

    # --------------------------------------------------- SEARCH ---------------------------------------------------

    def test_search_filters_items(self) -> None:
        """Typing in the search box narrows the item list."""
        self._open_with_ctrl_k()
        total = len(self._get_items())
        self._get_input().send_keys("companies")
        WebDriverWait(self.driver, 5).until(lambda d: len(d.find_elements(By.CSS_SELECTOR, "[id^='cp-item-']")) < total)
        items = self._get_items()
        assert len(items) == 1
        assert items[0].find_element(By.CSS_SELECTOR, CP_ITEM_LABEL).text == "Companies"

    def test_search_no_results(self) -> None:
        """Searching for a non-existent term shows the empty state."""
        self._open_with_ctrl_k()
        self._get_input().send_keys("zzznomatch")
        self.get_element("cp-empty", enabled=False)
        assert len(self._get_items()) == 0

    def test_search_clears_on_reopen(self) -> None:
        """Search query is cleared when the palette is reopened."""
        self._open_with_ctrl_k()
        self._get_input().send_keys("companies")
        self._get_input().send_keys(Keys.ESCAPE)
        self._wait_for_closed()
        self._open_with_ctrl_k()
        assert self._get_input().get_attribute("value") == ""

    # ------------------------------------------------- KEYBOARD NAV -------------------------------------------------

    def test_arrow_down_advances_active_item(self) -> None:
        """Arrow down moves the active selection to the next item."""
        self._open_with_ctrl_k()
        items = self._get_items()
        first_label = items[0].find_element(By.CSS_SELECTOR, CP_ITEM_LABEL).text
        self._get_input().send_keys(Keys.ARROW_DOWN)
        active = self.get_element(CP_ITEM_ACTIVE, By.CSS_SELECTOR)
        assert active.find_element(By.CSS_SELECTOR, CP_ITEM_LABEL).text != first_label

    def test_arrow_up_returns_to_first_item(self) -> None:
        """Arrow down then up returns focus to the first item."""
        self._open_with_ctrl_k()
        first_label = self._get_items()[0].find_element(By.CSS_SELECTOR, CP_ITEM_LABEL).text
        inp = self._get_input()
        inp.send_keys(Keys.ARROW_DOWN)
        inp.send_keys(Keys.ARROW_UP)
        active = self.get_element(CP_ITEM_ACTIVE, By.CSS_SELECTOR)
        assert active.find_element(By.CSS_SELECTOR, CP_ITEM_LABEL).text == first_label

    def test_enter_navigates_to_item(self) -> None:
        """Pressing Enter on a filtered item navigates to its page."""
        self._open_with_ctrl_k()
        self._get_input().send_keys("Companies")
        WebDriverWait(self.driver, 5).until(lambda d: len(d.find_elements(By.CSS_SELECTOR, "[id^='cp-item-']")) == 1)
        self._get_input().send_keys(Keys.ENTER)
        self._wait_for_closed()
        assert "/companies" in self.driver.current_url

    def test_click_item_navigates(self) -> None:
        """Clicking a page item navigates to its route."""
        self._open_with_ctrl_k()
        self._get_input().send_keys("Interviews")
        WebDriverWait(self.driver, 5).until(lambda d: len(d.find_elements(By.CSS_SELECTOR, "[id^='cp-item-']")) == 1)
        self.get_element("cp-item-goto-interviews").click()
        self._wait_for_closed()
        assert "/interviews" in self.driver.current_url

    # ----------------------------------------------- J SHORTCUTS ---------------------------------------------------

    def test_j_d_navigates_to_dashboard(self) -> None:
        """J+D shortcut navigates to the dashboard."""
        self.go_to_page("jobs")
        body = self.driver.find_element(By.TAG_NAME, "body")
        body.send_keys("j")
        body.send_keys("d")
        WebDriverWait(self.driver, 5).until(lambda d: "/dashboard" in d.current_url)

    def test_j_c_navigates_to_companies(self) -> None:
        """J+C shortcut navigates to companies."""
        body = self.driver.find_element(By.TAG_NAME, "body")
        body.send_keys("j")
        body.send_keys("c")
        WebDriverWait(self.driver, 5).until(lambda d: "/companies" in d.current_url)

    def test_j_p_navigates_to_persons(self) -> None:
        """J+P shortcut navigates to people."""
        body = self.driver.find_element(By.TAG_NAME, "body")
        body.send_keys("j")
        body.send_keys("p")
        WebDriverWait(self.driver, 5).until(lambda d: "/persons" in d.current_url)

    def test_j_n_opens_add_job_modal(self) -> None:
        """J+N shortcut navigates to jobs and opens the add job modal."""
        body = self.driver.find_element(By.TAG_NAME, "body")
        body.send_keys("j")
        body.send_keys("n")
        WebDriverWait(self.driver, 5).until(lambda d: "/jobs" in d.current_url)
        self.get_element(".modal.show", By.CSS_SELECTOR, enabled=False)

    def test_j_shortcut_ignored_while_typing(self) -> None:
        """J+D does not navigate while an input is focused."""
        self.go_to_page("jobs")
        search = self.get_element("search-input")
        search.click()
        search.send_keys("jd")
        assert "/jobs" in self.driver.current_url
        assert not self._is_open()
