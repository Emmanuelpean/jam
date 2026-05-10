"""Selenium tests for the command palette (keyboard shortcuts + UI)."""

from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait

from base_test import BaseTest

CP_ITEM_ACTIVE = "[id^='cp-item-'].active"
CP_ITEM_LABEL = ".cp-item-label"


class TestCommandPalette(BaseTest):
    user_index = 0
    page_url = "dashboard"

    def setup_function(self, request) -> None:
        self.login()

    # -------------------------------------------------- HELPERS --------------------------------------------------

    def open_palette(self) -> None:
        """Open the command palette."""

        self.driver.find_element(By.TAG_NAME, "body").send_keys(Keys.CONTROL + "k")
        self.get_element("cp-input", timeout=5)

    @property
    def palette_input(self) -> WebElement:
        """Get the search input in the command palette."""

        return self.get_element("cp-input")

    def _get_items(self) -> list[WebElement]:
        """Get all items in the command palette."""

        return self.driver.find_elements(By.CSS_SELECTOR, "[id^='cp-item-']")

    def is_open(self) -> bool:
        """Check if the command palette is open."""

        return self.check_element_exists("cp-backdrop", By.ID)

    def wait_for_close(self) -> None:
        """Wait for the command palette to close."""

        self.wait_for_disappear("cp-backdrop")
        # WebDriverWait(self.driver, 5).until(EC.invisibility_of_element_located((By.ID, "cp-backdrop")))

    # --------------------------------------------------- OPEN/CLOSE ---------------------------------------------------

    def test_open_with_ctrl_k(self) -> None:
        """Ctrl+K opens the command palette."""

        self.open_palette()
        assert self.is_open()

    def test_close_with_escape(self) -> None:
        """Escape closes the command palette."""

        self.open_palette()
        self.palette_input.send_keys(Keys.ESCAPE)
        self.wait_for_close()

    def test_close_by_clicking_backdrop(self) -> None:
        """Clicking outside the card on the backdrop closes the palette."""

        self.open_palette()
        # Viewport is 1960x1080; card is max 560px wide and centered (~x700-1260).
        # Click at (100, 100) — well outside the card. body center is (980, 540),
        # so offset (-880, -440) lands at approximately (100, 100).
        body = self.driver.find_element(By.TAG_NAME, "body")
        ActionChains(self.driver).move_to_element_with_offset(body, -880, -440).click().perform()
        self.wait_for_close()

    def test_ctrl_k_toggles_palette(self) -> None:
        """Pressing Ctrl+K a second time closes the palette."""

        self.open_palette()
        self.driver.find_element(By.TAG_NAME, "body").send_keys(Keys.CONTROL + "k")
        self.wait_for_close()

    # --------------------------------------------------- CONTENT ---------------------------------------------------

    def test_input_is_focused_on_open(self) -> None:
        """Search input is auto-focused when the palette opens."""

        self.open_palette()
        inp = self.get_element("cp-input")
        WebDriverWait(self.driver, 5).until(lambda d: d.switch_to.active_element == inp)

    def test_groups_are_shown(self) -> None:
        """Actions and Pages group headers are visible."""

        self.open_palette()
        headers = self.driver.find_elements(By.CSS_SELECTOR, "[id^='cp-group-']")
        texts = [h.text for h in headers]
        assert "ACTIONS" in texts
        assert "PAGES" in texts

    # --------------------------------------------------- SEARCH ---------------------------------------------------

    def test_search_filters_items(self) -> None:
        """Typing in the search box narrows the item list."""

        self.open_palette()
        self.palette_input.send_keys("companies")
        items = self._get_items()
        assert len(items) == 1
        assert items[0].find_element(By.CSS_SELECTOR, CP_ITEM_LABEL).text == "Companies"

    def test_search_no_results(self) -> None:
        """Searching for a non-existent term shows the empty state."""

        self.open_palette()
        self.palette_input.send_keys("zzznomatch")
        self.get_element("cp-empty", enabled=False)
        assert len(self._get_items()) == 0

    def test_search_clears_on_reopen(self) -> None:
        """Search query is cleared when the palette is reopened."""

        self.open_palette()
        self.palette_input.send_keys("companies")
        self.palette_input.send_keys(Keys.ESCAPE)
        self.wait_for_close()
        self.open_palette()
        assert self.palette_input.get_attribute("value") == ""

    # ------------------------------------------------- KEYBOARD NAV -------------------------------------------------

    def test_arrow_down_advances_active_item(self) -> None:
        """Arrow down moves the active selection to the next item."""

        self.open_palette()
        items = self._get_items()
        first_label = items[0].find_element(By.CSS_SELECTOR, CP_ITEM_LABEL).text
        self.palette_input.send_keys(Keys.ARROW_DOWN)
        active = self.get_element(CP_ITEM_ACTIVE, By.CSS_SELECTOR)
        assert active.find_element(By.CSS_SELECTOR, CP_ITEM_LABEL).text != first_label

    def test_arrow_up_returns_to_first_item(self) -> None:
        """Arrow down then up returns focus to the first item."""

        self.open_palette()
        first_label = self._get_items()[0].find_element(By.CSS_SELECTOR, CP_ITEM_LABEL).text
        inp = self.palette_input
        inp.send_keys(Keys.ARROW_DOWN)
        inp.send_keys(Keys.ARROW_UP)
        active = self.get_element(CP_ITEM_ACTIVE, By.CSS_SELECTOR)
        assert active.find_element(By.CSS_SELECTOR, CP_ITEM_LABEL).text == first_label

    def test_enter_navigates_to_item(self) -> None:
        """Pressing Enter on a filtered item navigates to its page."""

        self.open_palette()
        self.palette_input.send_keys("Companies")
        self.palette_input.send_keys(Keys.ENTER)
        self.wait_for_close()
        assert "/companies" in self.driver.current_url

    def test_click_item_navigates(self) -> None:
        """Clicking a page item navigates to its route."""

        self.open_palette()
        self.palette_input.send_keys("Interviews")
        self.get_element("cp-item-goto-interviews").click()
        self.wait_for_close()
        assert "/interviews" in self.driver.current_url

    # ----------------------------------------- MODAL DISMISSAL ON NAVIGATION -----------------------------------------

    def test_data_modal_closes_on_navigation(self) -> None:
        """Navigating via the command palette closes an open DataModal."""

        self.go_to_page("jobs")
        self.job_table_utils.add_entity_button.click()
        self.job_modal_utils.wait_for_edit_modal()
        self.open_palette()
        self.palette_input.send_keys("Companies")
        self.palette_input.send_keys(Keys.ENTER)
        self.wait_for_close()
        assert "/companies" in self.driver.current_url
        self.job_modal_utils.wait_for_edit_modal_close()

    def test_confirm_modal_closes_on_navigation(self, test_jobs) -> None:
        """Navigating via the command palette closes an open confirm modal."""

        job = self._make_job(title="Test Job")
        self.refresh()
        self.go_to_page("jobs")
        self.job_table_utils.table_row_click(job.id)
        self.job_modal_utils.edit_button("view").click()
        self.job_modal_utils.wait_for_edit_modal()
        self.job_modal_utils.delete_button("edit").click()
        self.delete_modal.wait_for_modal()
        self.open_palette()
        self.palette_input.send_keys("Companies")
        self.palette_input.send_keys(Keys.ENTER)
        self.wait_for_close()
        assert "/companies" in self.driver.current_url
        self.job_modal_utils.wait_for_edit_modal_close()
        self.delete_modal.wait_for_modal_close()


class TestCommandPaletteUnauthenticated(BaseTest):

    def setup_function(self, request) -> None:
        self.auth_utils.go_to_login()

    def test_ctrl_k_disabled_when_not_logged_in(self) -> None:
        """Ctrl+K does not open the command palette when unauthenticated."""

        self.driver.find_element(By.TAG_NAME, "body").send_keys(Keys.CONTROL + "k")
        assert not self.check_element_exists("cp-backdrop", By.ID)
