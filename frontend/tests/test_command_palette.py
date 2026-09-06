"""Selenium tests for the command palette (keyboard shortcuts + UI)."""

from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait

from frontend_base_test import BaseTest


class TestCommandPalette(BaseTest):
    page_url = "dashboard"

    def setup_function(self, request) -> None:
        self.login()

    # --------------------------------------------------- OPEN/CLOSE ---------------------------------------------------

    def test_open_with_ctrl_k(self) -> None:
        """Ctrl+K opens the command palette."""

        self.command_palette_utils.open()
        assert self.command_palette_utils.is_open()

    def test_close_with_escape(self) -> None:
        """Escape closes the command palette."""

        self.command_palette_utils.open()
        self.command_palette_utils.input.send_keys(Keys.ESCAPE)
        self.command_palette_utils.wait_for_close()

    def test_close_by_clicking_backdrop(self) -> None:
        """Clicking outside the card on the backdrop closes the palette."""

        self.command_palette_utils.open()
        # Viewport is 1960x1080; card is max 560px wide and centered (~x700-1260).
        # Click at (100, 100) — well outside the card. body center is (980, 540),
        # so offset (-880, -440) lands at approximately (100, 100).
        body = self.driver.find_element(By.TAG_NAME, "body")
        ActionChains(self.driver).move_to_element_with_offset(body, -880, -440).click().perform()
        self.command_palette_utils.wait_for_close()

    def test_ctrl_k_toggles_palette(self) -> None:
        """Pressing Ctrl+K a second time closes the palette."""

        self.command_palette_utils.open()
        self.command_palette_utils.press_ctrl_k()
        self.command_palette_utils.wait_for_close()

    # --------------------------------------------------- CONTENT ---------------------------------------------------

    def test_input_is_focused_on_open(self) -> None:
        """Search input is auto-focused when the palette opens."""

        self.command_palette_utils.open()
        inp = self.command_palette_utils.input
        WebDriverWait(self.driver, 5).until(lambda d: d.switch_to.active_element == inp)

    def test_groups_are_shown(self) -> None:
        """Actions and Pages group headers are visible."""

        self.command_palette_utils.open()
        texts = self.command_palette_utils.group_headers()
        assert "ACTIONS" in texts
        assert "PAGES" in texts

    # --------------------------------------------------- SEARCH ---------------------------------------------------

    def test_search_filters_items(self) -> None:
        """Typing in the search box narrows the item list."""

        self.command_palette_utils.open()
        self.command_palette_utils.search("companies")
        items = self.command_palette_utils.items()
        assert len(items) == 1
        assert self.command_palette_utils.item_label(items[0]) == "Companies"

    def test_search_no_results(self) -> None:
        """Searching for a non-existent term shows the empty state."""

        self.command_palette_utils.open()
        self.command_palette_utils.search("zzznomatch")
        self.get_element("cp-empty", enabled=False)
        assert len(self.command_palette_utils.items()) == 0

    def test_search_clears_on_reopen(self) -> None:
        """Search query is cleared when the palette is reopened."""

        self.command_palette_utils.open()
        self.command_palette_utils.search("companies")
        self.command_palette_utils.input.send_keys(Keys.ESCAPE)
        self.command_palette_utils.wait_for_close()
        self.command_palette_utils.open()
        assert self.command_palette_utils.input.get_attribute("value") == ""

    # ------------------------------------------------- KEYBOARD NAV -------------------------------------------------

    def test_arrow_down_advances_active_item(self) -> None:
        """Arrow down moves the active selection to the next item."""

        self.command_palette_utils.open()
        items = self.command_palette_utils.items()
        first_label = self.command_palette_utils.item_label(items[0])
        self.command_palette_utils.input.send_keys(Keys.ARROW_DOWN)
        active = self.command_palette_utils.active_item
        assert self.command_palette_utils.item_label(active) != first_label

    def test_arrow_up_returns_to_first_item(self) -> None:
        """Arrow down then up returns focus to the first item."""

        self.command_palette_utils.open()
        first_label = self.command_palette_utils.item_label(self.command_palette_utils.items()[0])
        inp = self.command_palette_utils.input
        inp.send_keys(Keys.ARROW_DOWN)
        inp.send_keys(Keys.ARROW_UP)
        active = self.command_palette_utils.active_item
        assert self.command_palette_utils.item_label(active) == first_label

    def test_enter_navigates_to_item(self) -> None:
        """Pressing Enter on a filtered item navigates to its page."""

        self.command_palette_utils.open()
        self.command_palette_utils.search("Companies")
        self.command_palette_utils.input.send_keys(Keys.ENTER)
        self.command_palette_utils.wait_for_close()
        assert "/companies" in self.driver.current_url

    def test_click_item_navigates(self) -> None:
        """Clicking a page item navigates to its route."""

        self.command_palette_utils.open()
        self.command_palette_utils.search("Interviews")
        self.command_palette_utils.item("goto-interviews").click()
        self.command_palette_utils.wait_for_close()
        assert "/interviews" in self.driver.current_url

    # ----------------------------------------- MODAL DISMISSAL ON NAVIGATION -----------------------------------------

    def test_data_modal_closes_on_navigation(self) -> None:
        """Navigating via the command palette closes an open DataModal."""

        self.go_to_page("jobs")
        self.job_table_utils.add_entity_button.click()
        self.job_modal_utils.wait_for_edit_modal()
        self.command_palette_utils.open()
        self.command_palette_utils.search("Companies")
        self.command_palette_utils.input.send_keys(Keys.ENTER)
        self.command_palette_utils.wait_for_close()
        assert "/companies" in self.driver.current_url
        self.job_modal_utils.wait_for_edit_modal_close()

    def test_confirm_modal_closes_on_navigation(self) -> None:
        """Navigating via the command palette closes an open confirm modal."""

        job = self.user.create_job(title="Test Job")
        self.refresh()
        self.go_to_page("jobs")
        self.job_table_utils.table_row_click(job.id)
        self.job_modal_utils.edit_button("view").click()
        self.job_modal_utils.wait_for_edit_modal()
        self.job_modal_utils.delete_button("edit").click()
        self.delete_modal_utils.wait_for_modal()
        self.command_palette_utils.open()
        self.command_palette_utils.search("Companies")
        self.command_palette_utils.input.send_keys(Keys.ENTER)
        self.command_palette_utils.wait_for_close()
        assert "/companies" in self.driver.current_url
        self.job_modal_utils.wait_for_edit_modal_close()
        self.delete_modal_utils.wait_for_modal_close()


class TestCommandPaletteRecordSearch(BaseTest):
    """The palette search also matches the user's records (jobs, companies, contacts, tags, aggregators)."""

    user_fixture = "test_regular_user"
    page_url = "dashboard"

    def setup_function(self, request) -> None:
        self.login()

    # --------------------------------------------------- TESTS ---------------------------------------------------

    def test_search_matches_job_title(self) -> None:
        """Typing a job title surfaces that job as a result."""

        self.user.create_job(title="Zynapse Backend Engineer")
        self.refresh()
        self.command_palette_utils.open()
        self.command_palette_utils.search("Zynapse")
        item = self.command_palette_utils.item_matching("job-")
        assert self.command_palette_utils.item_label(item) == "Zynapse Backend Engineer"

    def test_enter_opens_job_view_modal(self) -> None:
        """Selecting a job result navigates to /jobs and opens its view modal."""

        job = self.user.create_job(title="Zynapse Platform Lead")
        self.refresh()
        self.command_palette_utils.open()
        self.command_palette_utils.search("Zynapse Platform Lead")
        self.command_palette_utils.input.send_keys(Keys.ENTER)
        self.command_palette_utils.wait_for_close()
        assert "/jobs" in self.driver.current_url
        modal = self.job_modal_utils.wait_for_view_modal()
        assert job.title in modal.text

    def test_click_company_result_opens_view_modal(self) -> None:
        """Clicking a company result navigates to /companies and opens its view modal."""

        company = self.user.create_company(name="Zentech Solutions")
        self.refresh()
        self.command_palette_utils.open()
        self.command_palette_utils.search("Zentech")
        self.command_palette_utils.item(f"company-{company.id}").click()
        self.command_palette_utils.wait_for_close()
        assert "/companies" in self.driver.current_url
        modal = self.company_modal_utils.wait_for_view_modal()
        assert company.name in modal.text

    def test_search_matches_contact_name(self) -> None:
        """Selecting a contact result navigates to /contacts and opens its view modal."""

        person = self.user.create_person(first_name="Zaphod", last_name="Beeblebrox")
        self.refresh()
        self.command_palette_utils.open()
        self.command_palette_utils.search("Zaphod")
        self.command_palette_utils.item(f"person-{person.id}").click()
        self.command_palette_utils.wait_for_close()
        assert "/contacts" in self.driver.current_url
        self.person_modal_utils.wait_for_view_modal()

    def test_search_matches_tag_name(self) -> None:
        """Selecting a tag result navigates to /keywords and opens its view modal."""

        keyword = self.user.create_keyword(name="Zigzag")
        self.refresh()
        self.command_palette_utils.open()
        self.command_palette_utils.search("Zigzag")
        self.command_palette_utils.item(f"keyword-{keyword.id}").click()
        self.command_palette_utils.wait_for_close()
        assert "/keywords" in self.driver.current_url
        self.keyword_modal_utils.wait_for_view_modal()

    def test_search_matches_aggregator_name(self) -> None:
        """Selecting an aggregator result navigates to /aggregators and opens its view modal."""

        aggregator = self.user.create_aggregator(name="Zephyr Jobs")
        self.refresh()
        self.command_palette_utils.open()
        self.command_palette_utils.search("Zephyr")
        self.command_palette_utils.item(f"aggregator-{aggregator.id}").click()
        self.command_palette_utils.wait_for_close()
        assert "/aggregators" in self.driver.current_url
        self.aggregator_modal_utils.wait_for_view_modal()

    def test_results_capped_per_group(self) -> None:
        """No more than five matching records are shown per entity group."""

        for i in range(7):
            self.user.create_job(title=f"Zcapped Role {i}")
        self.refresh()
        self.command_palette_utils.open()
        self.command_palette_utils.search("Zcapped")
        job_items = self.command_palette_utils.items("job-")
        assert len(job_items) == 5

    def test_record_results_grouped_by_entity(self) -> None:
        """Matching records appear under their entity group header."""

        self.user.create_company(name="Zgroup Industries")
        self.refresh()
        self.command_palette_utils.open()
        self.command_palette_utils.search("Zgroup")
        assert "COMPANIES" in self.command_palette_utils.group_headers()

    def test_no_record_match_shows_empty_state(self) -> None:
        """A query that matches no page, action or record shows the empty state."""

        self.command_palette_utils.open()
        self.command_palette_utils.search("Zznorecordmatch")
        self.get_element("cp-empty", enabled=False)
        assert len(self.command_palette_utils.items()) == 0


class TestCommandPaletteUnauthenticated(BaseTest):

    def setup_function(self, request) -> None:
        self.auth_utils.go_to_login()

    def test_ctrl_k_disabled_when_not_logged_in(self) -> None:
        """Ctrl+K does not open the command palette when unauthenticated."""

        self.driver.find_element(By.TAG_NAME, "body").send_keys(Keys.CONTROL + "k")
        assert not self.command_palette_utils.is_open()
