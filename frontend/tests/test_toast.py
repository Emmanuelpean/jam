"""Tests for the scraped jobs."""

from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from conftest import BaseTest, models
from frontend.tests.test_table_page import DataTableUtils, DataModalUtils
from react_select import ReactSelect


class TestToast(BaseTest):

    user_index = 0
    page_url = "dashboard"
    entity_type = "scrapedJobs"
    entry_name = "scraped job"

    def setup_function(self, request) -> None:
        """Setup for each test function."""

        request.getfixturevalue("test_scraped_jobs")
        self.table_utils = DataTableUtils(self.driver, self.entity_type, self.frontend_base_url, self.db)
        self.modal_utils = DataModalUtils(self.driver, self.entry_name, self.frontend_base_url, self.db)
        self.login()

    def test_import_scraped_job(self) -> None:
        """Test importing a scraped job and displaying a toast notification."""

        job_count = self.db.query(models.Job).count()
        self.table_utils.get_element("table-row-scrapedJobs-2").click()
        self.table_utils.get_element("modal-import-scraped job-import-button").click()
        self.modal_utils.wait_for_import_modal_modal_close()
        self.table_utils.assert_toast_message("Job imported successfully.")
        assert self.db.query(models.Job).count() == job_count + 1
        self.table_utils.go_to_page("jobs")
        self.table_utils.get_element("table-row-jobs-{}".format(job_count + 1))
        self.db.expire_all()
        scraped_job = self.db.query(models.ScrapedJob).filter_by(id=2).first()
        assert scraped_job.is_imported

    def test_right_click_import_scraped_job(self) -> None:
        """Test importing a scraped job via right-click and displaying a toast notification."""

        job_count = self.db.query(models.Job).count()
        self.table_utils.context_menu(2, "import")
        self.table_utils.get_element("modal-import-scraped job-import-button").click()
        self.modal_utils.wait_for_import_modal_modal_close()
        self.table_utils.assert_toast_message("Job imported successfully.")
        assert self.db.query(models.Job).count() == job_count + 1
        self.table_utils.go_to_page("jobs")
        self.table_utils.get_element("table-row-jobs-{}".format(job_count + 1))
        self.db.expire_all()
        scraped_job = self.db.query(models.ScrapedJob).filter_by(id=2).first()
        assert scraped_job.is_imported

    def test_delete_scraped_job(self) -> None:
        """Test deleting a scraped job and displaying a toast notification."""

        self.get_element("table-row-scrapedJobs-2").click()
        self.get_element("modal-import-scraped job-delete-button").click()
        self.get_element("delete-alert-modal-confirm-button").click()
        self.wait_for_import_modal_modal_close()
        self.assert_toast_message("Scraped Job deleted successfully.")
        self.db.expire_all()
        scraped_job = self.db.query(models.ScrapedJob).filter_by(id=2).first()
        assert not scraped_job.is_active

    def test_context_menu_delete_scraped_job(self) -> None:
        """Test deleting a scraped job via right-click and displaying a toast notification."""

        self.context_menu(2, "delete")
        self.get_element("delete-alert-modal-confirm-button").click()
        self.wait_for_import_modal_modal_close()
        self.assert_toast_message("Scraped Job deleted successfully.")
        self.db.expire_all()
        scraped_job = self.db.query(models.ScrapedJob).filter_by(id=2).first()
        assert not scraped_job.is_active


class TestScrapingFilters(BaseTest):

    user_index = 0
    page_url = "dashboard"
    entry_type = "scrapingFilters"
    entry_name = "Scraping Filters"
    test_fixture = ["test_scraping_filters", "test_scraped_jobs"]
    test_data = dict(type="Attendance Type", operator="Contains", value="In Person")

    def setup_function(self, request) -> None:
        """Setup for each test function."""

        self.login()

    def open_modal(self) -> None:
        """Open the scraping filters modal."""

        self.get_element("scraping-filters-button").click()
        self.get_element("scraping-filters-modal")

    def test_add_scraping_filter(self) -> None:
        """Test adding a scraping filter and displaying a toast notification."""

        filter_count = self.db.query(models.ScrapingFilter).count()
        self.open_modal()
        self.get_element(f"add-{self.entry_type}-button").click()
        self._fill_modal()
        self.select_option("type", "Attendance Type")
        self.select_option("operator", "Contains")
        self.set_text(self.get_element("value"), "In Person")
        self.get_element("modal-edit-scraping filter-confirm-button").click()
        assert self.db.query(models.ScrapingFilter).count() == filter_count + 1

    def context_menu(self, entity_id: int, choice: str) -> None:
        """Row context menu"""

        actions = ActionChains(self.driver)
        actions.context_click(self.table_row(entity_id)).perform()
        self.get_element(f"context-menu-{choice}").click()

    def deactivate_scraping_filter(self) -> None:
        """Test deactivating a scraping filter and displaying a toast notification."""

        self.open_modal()
        self.get_element("table-row-scrapingFilters-2").click()
        self.get_element("modal-edit-scraping filter-deactivate-button").click()
        self.get_element("delete-alert-modal-confirm-button").click()
        self.wait_for_modal_close("modal-edit-scraping filter")
        self.assert_toast_message("Scraping Filter deactivated successfully.")
        self.db.expire_all()
        scraping_filter = self.db.query(models.ScrapingFilter).filter_by(id=1).first()
        assert not scraping_filter.is_active
