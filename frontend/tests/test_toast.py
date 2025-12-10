"""Tests for the scraped jobs."""

from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from conftest import BaseTest, models, eis_models


class TestToast(BaseTest):

    user_index = 0
    page_url = "dashboard"
    entity_type = "scrapedJobs"

    def setup_function(self, request) -> None:
        """Setup for each test function."""

        request.getfixturevalue("test_scraped_jobs")
        self.login()
        # request.getfixturevalue("test_jobs")

    def test_import_scraped_job(self) -> None:
        """Test importing a scraped job and displaying a toast notification."""

        job_count = self.db.query(models.Job).count()
        self.get_element("table-row-scrapedJobs-2").click()
        self.get_element("modal-import-scraped job-import-button").click()
        self.wait_for_import_modal_modal_close()
        self.assert_toast_message("Job imported successfully.")
        assert self.db.query(models.Job).count() == job_count + 1
        self.go_to("jobs")
        self.get_element("table-row-jobs-{}".format(job_count + 1))
        self.db.expire_all()
        scraped_job = self.db.query(eis_models.ScrapedJob).filter(eis_models.ScrapedJob.id == 2).first()
        assert scraped_job.is_imported

    def test_right_click_import_scraped_job(self) -> None:
        """Test importing a scraped job via right-click and displaying a toast notification."""

        job_count = self.db.query(models.Job).count()
        self.context_menu(2, "import")
        self.get_element("modal-import-scraped job-import-button").click()
        self.wait_for_import_modal_modal_close()
        self.assert_toast_message("Job imported successfully.")
        assert self.db.query(models.Job).count() == job_count + 1
        self.go_to("jobs")
        self.get_element("table-row-jobs-{}".format(job_count + 1))
        self.db.expire_all()
        scraped_job = self.db.query(eis_models.ScrapedJob).filter(eis_models.ScrapedJob.id == 2).first()
        assert scraped_job.is_imported

    def test_delete_scraped_job(self) -> None:
        """Test deleting a scraped job and displaying a toast notification."""

        self.get_element("table-row-scrapedJobs-2").click()
        self.get_element("modal-import-scraped job-delete-button").click()
        self.get_element("delete-alert-modal-confirm-button").click()
        self.wait_for_import_modal_modal_close()
        self.assert_toast_message("Scraped Job deleted successfully.")
        self.db.expire_all()
        scraped_job = self.db.query(eis_models.ScrapedJob).filter(eis_models.ScrapedJob.id == 2).first()
        assert not scraped_job.is_active

    def test_context_menu_delete_scraped_job(self) -> None:
        """Test deleting a scraped job via right-click and displaying a toast notification."""

        self.context_menu(2, "delete")
        self.get_element("delete-alert-modal-confirm-button").click()
        self.wait_for_import_modal_modal_close()
        self.assert_toast_message("Scraped Job deleted successfully.")
        self.db.expire_all()
        scraped_job = self.db.query(eis_models.ScrapedJob).filter(eis_models.ScrapedJob.id == 2).first()
        assert not scraped_job.is_active

    def wait_for_import_modal_modal_close(self) -> None:
        """Wait for the import modal to close."""

        self._wait_for_modal_close("modal-import-scraped job")

    @property
    def table_rows(self) -> list[WebElement]:
        """Get all table rows on the page"""

        self.get_element("table-row-clickable", By.CLASS_NAME)
        return self.driver.find_elements(By.CSS_SELECTOR, f"[id^='table-row-{self.entity_type}-']")

    def table_row(self, item_id: int, *args, **kwargs) -> WebElement:
        """Get a specific table row by its ID"""

        return self.get_element(f"table-row-{self.entity_type}-{item_id}", *args, **kwargs)

    def context_menu(self, entity_id: int, choice: str) -> None:
        """Row context menu"""

        actions = ActionChains(self.driver)
        actions.context_click(self.table_row(entity_id)).perform()
        self.get_element(f"context-menu-{choice}").click()
