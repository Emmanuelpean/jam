"""Selenium tests for the Scraping Filters guided tour.

Tour step order (scraping-filters):
  0   sf-intro      informational — centre popover; route: /job-alerts/jobs
  1   sf-open       Scraping Filters button (hideNextButton); auto-advances when #scraping-filters-modal appears
  2   sf-overview   filter panel overview; Next
  3   sf-tabs       active-tab; Next
  4   sf-add        Add button (hideNextButton); auto-advances when #modal-edit-scrapingExclusionFilter appears
  5   sf-type       type-form-group; waitForInput (ReactSelect); Next enabled when type selected
  6   sf-operator   operator-form-group; waitForInput (ReactSelect); Next enabled when operator selected
  7   sf-value      value-form-group; waitForInput (text input); Next enabled when value typed
  8   sf-test       scraping-filter-test-btn; Next
  9   sf-save       confirm button (hideNextButton); auto-advances when modal closes
  10  sf-manage     [demo-scraping-filter-row]; blockLeftClick; allowedContextMenuActions: []
  11  sf-done       Done step — keep/delete toggle appears (hasUserCreatedData=true after filter created)

Cleanup on Done/Skip:
  - keepData=True (toggle on, default): created ScrapingExclusionFilter persists
  - keepData=False (toggle off): created filter is deleted
  - Skip before sf-add: no filter created
"""

from selenium.webdriver import ActionChains

from app import models
from base_test import BaseTest
from select_utils import Select

TOUR_ID = "scraping-filters"


class TestScrapingFilterTour(BaseTest):
    user_index = 0
    page_url = "job-alerts/jobs"

    def setup_function(self, request) -> None:
        self.login()

    # ------------------------------------------------------------------ helpers

    def _advance_through_intro(self) -> None:
        """Start the tour and click through the sf-intro step.

        Returns with the popover on sf-open (step 1).
        """
        self.tour_utils.start_tour(TOUR_ID)
        self.wait_for_page("job-alerts/jobs")
        # Step 0 (sf-intro): informational — click Next
        self.tour_utils.click_next()

    def _open_filter_panel(self) -> None:
        """From sf-open, click the Scraping Filters button to open the panel.

        The tour auto-advances to sf-overview when #scraping-filters-modal appears.
        Returns with the popover on sf-overview (step 2).
        """
        self.tour_utils.wait_for_popover()
        self.get_element("scraping-filters-button").click()
        # Auto-advances to sf-overview
        self.tour_utils.wait_for_popover()

    def _advance_to_filter_form(self) -> None:
        """From sf-overview, advance through tabs step and open the add form.

        Returns with the popover on sf-type (step 5) and #modal-edit-scrapingExclusionFilter open.
        """
        # Step 2 (sf-overview): click Next
        self.tour_utils.click_next()

        # Step 3 (sf-tabs): click Next
        self.tour_utils.wait_for_popover()
        self.tour_utils.click_next()

        # Step 4 (sf-add): click the Add button; auto-advances to sf-type when modal appears
        self.tour_utils.wait_for_popover()
        self.get_element("add-scrapingExclusionFilter-button").click()
        self.tour_utils.wait_for_popover()

    def _fill_filter_form(
        self, filter_type: str = "Job Title", operator: str = "Contains", value: str = "Senior"
    ) -> None:
        """Fill the filter form on steps sf-type, sf-operator, sf-value.

        Each step's Next button is disabled until the field is filled.
        Returns with the popover on sf-test (step 8).
        """
        # Step 5 (sf-type): select type from ReactSelect; Next becomes enabled
        self.tour_utils.wait_for_popover()
        Select(self.get_element("type")).select_by_visible_text(filter_type)
        self.tour_utils.click_next()

        # Step 6 (sf-operator): select operator from ReactSelect
        self.tour_utils.wait_for_popover()
        Select(self.get_element("operator")).select_by_visible_text(operator)
        self.tour_utils.click_next()

        # Step 7 (sf-value): type the filter value
        self.tour_utils.wait_for_popover()
        self.set_text(self.get_element("value"), value)
        self.tour_utils.click_next()

    def _save_filter(self) -> None:
        """From sf-test (step 8), click Next then click Save.

        The tour auto-advances to sf-manage when the modal closes.
        Returns with the popover on sf-manage (step 10).
        """
        # Step 8 (sf-test): no action required — click Next
        self.tour_utils.wait_for_popover()
        self.tour_utils.click_next()

        # Step 9 (sf-save): click Save; auto-advances when #modal-edit-scrapingExclusionFilter closes
        self.tour_utils.wait_for_popover()
        self.scrapingExclusionFilter_modal_utils.confirm_button("edit").click()
        # Wait for sf-manage popover
        self.tour_utils.wait_for_popover()

    def _get_demo_filter(self) -> models.ScrapingExclusionFilter:
        """Return the most recently created ScrapingExclusionFilter for this user."""
        self.db.expire_all()
        return (
            self.db.query(models.ScrapingExclusionFilter)
            .filter_by(owner_id=self.user.id)
            .order_by(models.ScrapingExclusionFilter.id.desc())
            .first()
        )

    # ------------------------------------------------------------------ tests

    def test_full_flow(self) -> None:
        """Complete the entire tour end-to-end with keep data (default toggle on).

        The created ScrapingExclusionFilter should persist after Done.
        """
        initial_count = self.db.query(models.ScrapingExclusionFilter).filter_by(owner_id=self.user.id).count()

        self._advance_through_intro()
        self._open_filter_panel()
        self._advance_to_filter_form()
        self._fill_filter_form()
        self._save_filter()

        # Step 10 (sf-manage): click Next
        self.tour_utils.wait_for_popover()
        self.tour_utils.click_next()

        # Step 11 (sf-done): keep/delete toggle must appear; leave as Keep (default)
        self.tour_utils.wait_for_popover()
        assert "Done" in self.get_element(self.tour_utils.TOUR_NEXT).text
        assert self.check_element_exists("tour-keep-data"), "Keep my data toggle must appear on sf-done"
        self.tour_utils.click_next()

        self.tour_utils.wait_for_popover_gone()
        self.wait_for_page(self.page_url)

        # Filter was kept
        self.tour_utils.poll_db_count(models.ScrapingExclusionFilter, self.user.id, initial_count + 1)

    def test_keep_data_delete(self) -> None:
        """Complete the tour with the keep data toggle turned OFF.

        The created ScrapingExclusionFilter should be deleted after Done.
        """
        initial_count = self.db.query(models.ScrapingExclusionFilter).filter_by(owner_id=self.user.id).count()

        self._advance_through_intro()
        self._open_filter_panel()
        self._advance_to_filter_form()
        self._fill_filter_form()
        self._save_filter()

        # Step 10 (sf-manage): click Next
        self.tour_utils.wait_for_popover()
        self.tour_utils.click_next()

        # Step 11 (sf-done): uncheck keep data → filter will be deleted
        self.tour_utils.wait_for_popover()
        assert self.check_element_exists("tour-keep-data"), "Keep my data toggle must appear"
        self.tour_utils.keep_data_toggle.click()
        self.tour_utils.click_next()

        self.tour_utils.wait_for_popover_gone()
        self.wait_for_page(self.page_url)

        # Filter was deleted (returns to initial count)
        self.tour_utils.poll_db_count(models.ScrapingExclusionFilter, self.user.id, initial_count)

    def test_skip_tour(self) -> None:
        """Skip the tour before the filter is created (during sf-overview).

        No ScrapingExclusionFilter should be created.
        """
        initial_count = self.db.query(models.ScrapingExclusionFilter).filter_by(owner_id=self.user.id).count()

        self._advance_through_intro()
        self._open_filter_panel()

        # Skip at sf-overview (step 2) — filter form never opened
        self.tour_utils.click_skip()

        self.tour_utils.wait_for_popover_gone()
        self.wait_for_page(self.page_url)

        # No filter created
        self.tour_utils.poll_db_count(models.ScrapingExclusionFilter, self.user.id, initial_count)

    def test_left_click_blocked(self) -> None:
        """On sf-manage (step 10), a left-click on the filter row must not open the edit modal."""
        self._advance_through_intro()
        self._open_filter_panel()
        self._advance_to_filter_form()
        self._fill_filter_form()
        self._save_filter()

        # Step 10 (sf-manage): blockLeftClick is active
        self.tour_utils.wait_for_popover()
        demo_filter = self._get_demo_filter()
        self.scrapingExclusionFilter_table_utils.table_row_click(demo_filter.id)
        assert not self.check_element_exists(
            "modal-edit-scrapingExclusionFilter", timeout=2
        ), "Edit modal must not open when blockLeftClick is active on sf-manage step"

        # Clean up
        self.tour_utils.click_skip()
        self.tour_utils.wait_for_popover_gone()

    def test_context_menu_blocked(self) -> None:
        """On sf-manage (step 10), right-clicking the filter row must not show context menu items.

        allowedContextMenuActions: [] means no context menu actions are permitted.
        """
        self._advance_through_intro()
        self._open_filter_panel()
        self._advance_to_filter_form()
        self._fill_filter_form()
        self._save_filter()

        # Step 10 (sf-manage): allowedContextMenuActions: []
        self.tour_utils.wait_for_popover()
        demo_filter = self._get_demo_filter()
        filter_row = self.scrapingExclusionFilter_table_utils.table_row(demo_filter.id)
        ActionChains(self.driver).context_click(filter_row).perform()

        assert not self.check_element_exists(
            "context-menu-edit", timeout=2
        ), "Context menu edit option must not appear on sf-manage step"
        assert not self.check_element_exists(
            "context-menu-delete", timeout=2
        ), "Context menu delete option must not appear on sf-manage step"

        # Clean up
        self.tour_utils.click_skip()
        self.tour_utils.wait_for_popover_gone()
