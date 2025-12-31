"""Tests for the scraped jobs."""

from conftest import BaseTest, models


class TestToast(BaseTest):

    user_index = 0
    page_url = "dashboard"

    def setup_function(self, request) -> None:
        """Setup for each test function."""

        request.getfixturevalue("test_scraped_jobs")
        self.login()

    def test_import_scraped_job(self) -> None:
        """Test importing a scraped job and displaying a toast notification."""

        # Import the scraped job with ID 2
        job_count = self.db.query(models.Job).count()
        self.scraped_job_table_utils.table_row(2).click()
        self.scraped_job_modal_utils.import_button().click()
        self.scraped_job_modal_utils.wait_for_import_modal_modal_close()
        self.scraped_job_table_utils.assert_toast_message("Job imported successfully.")

        # Verify that the job count has increased by 1
        assert self.db.query(models.Job).count() == job_count + 1
        self.scraped_job_table_utils.go_to_page("jobs")
        self.job_table_utils.wait_for_table_load()
        assert len(self.job_table_utils.table_rows) == job_count + 1
        self.db.expire_all()

        # Verify that the scraped job is marked as imported
        scraped_job = self.db.query(models.ScrapedJob).filter_by(id=2).first()
        assert scraped_job.is_imported

    def test_right_click_import_scraped_job(self) -> None:
        """Test importing a scraped job via right-click and displaying a toast notification."""

        job_count = self.db.query(models.Job).count()
        self.scraped_job_table_utils.table_context_menu(2, "import")
        self.scraped_job_modal_utils.import_button().click()
        self.scraped_job_modal_utils.wait_for_import_modal_modal_close()
        self.scraped_job_table_utils.assert_toast_message("Job imported successfully.")

        # Verify that the job count has increased by 1
        assert self.db.query(models.Job).count() == job_count + 1
        self.scraped_job_table_utils.go_to_page("jobs")
        self.job_table_utils.wait_for_table_load()
        assert len(self.job_table_utils.table_rows) == job_count + 1
        self.db.expire_all()

        # Verify that the scraped job is marked as imported
        scraped_job = self.db.query(models.ScrapedJob).filter_by(id=2).first()
        assert scraped_job.is_imported

    def test_delete_scraped_job(self) -> None:
        """Test deleting a scraped job and displaying a toast notification."""

        self.scraped_job_table_utils.table_row(2).click()
        self.scraped_job_modal_utils.delete_button("import").click()
        self.delete_confirm_button.click()
        self.scraped_job_modal_utils.wait_for_import_modal_modal_close()
        self.assert_toast_message("Scraped Job deleted successfully.")
        self.db.expire_all()
        scraped_job = self.db.query(models.ScrapedJob).filter_by(id=2).first()
        assert not scraped_job.is_active

    def test_context_menu_delete_scraped_job(self) -> None:
        """Test deleting a scraped job via right-click and displaying a toast notification."""

        self.scraped_job_table_utils.table_context_menu(2, "delete")
        self.delete_confirm_button.click()
        self.scraped_job_modal_utils.wait_for_import_modal_modal_close()
        self.assert_toast_message("Scraped Job deleted successfully.")
        self.db.expire_all()
        scraped_job = self.db.query(models.ScrapedJob).filter_by(id=2).first()
        assert not scraped_job.is_active


class TestScrapingFilters(BaseTest):

    user_index = 0
    page_url = "dashboard"
    test_data = dict(type="Attendance Type", operator="Contains", value="In Person")
    filtered_index = 1
    no_filtered_index = 3

    def setup_function(self, request) -> None:
        """Setup for each test function."""

        request.getfixturevalue("test_scraped_jobs")
        request.getfixturevalue("test_scraping_filters")
        self.login()
        self.open_modal()

    def open_modal(self) -> None:
        """Open the scraping filters modal."""

        self.get_element("scraping-filters-button").click()
        self.get_element("scraping-filters-modal")

    def test_add_scraping_filter(self) -> None:
        """Test adding a scraping filter and displaying a toast notification."""

        filter_count = self.db.query(models.ScrapingFilter).count()
        self.scraping_filter_table_utils.add_entity_button.click()
        self.scraping_filter_modal_utils.add_entry(**self.test_data)
        assert self.db.query(models.ScrapingFilter).count() == filter_count + 1

    def test_deactivate_scraping_filter(self) -> None:
        """Test deactivating a scraping filter and displaying a toast notification."""

        self.scraping_filter_table_utils.table_row(self.no_filtered_index).click()
        self.scraping_filter_modal_utils.deactivate_button().click()
        self.scraping_filter_modal_utils.wait_for_view_modal_close()
        self.assert_toast_message("Scraping Filter deactivated successfully.")
        self.db.expire_all()
        scraping_filter = self.db.query(models.ScrapingFilter).filter_by(id=self.no_filtered_index).first()
        assert not scraping_filter.is_active
        self.get_element("inactive-tab").click()
        assert self.scraping_filter_table_utils.table_row(self.no_filtered_index).is_displayed()

    def test_edit_scraping_filter(self) -> None:
        """Test deactivating a scraping filter when it has filtered jobs."""

        assert not self.db.query(models.ScrapingFilter).filter_by(id=self.no_filtered_index).first().filtered_jobs
        self.scraping_filter_table_utils.table_row(self.no_filtered_index).click()
        assert self.scraping_filter_modal_utils.deactivate_button().is_enabled()
        assert not self.scraping_filter_modal_utils.edit_button("view", enabled=False).click()
        self.scraping_filter_modal_utils._fill_modal(value="Virtual")
        self.scraping_filter_modal_utils.confirm_button("edit").click()
        self.scraping_filter_modal_utils.wait_for_view_modal_close()

    def test_edit_scraping_filter_failure(self) -> None:
        """Test deactivating a scraping filter when it has filtered jobs."""

        assert self.db.query(models.ScrapingFilter).filter_by(id=self.filtered_index).first().filtered_jobs
        self.scraping_filter_table_utils.table_row(self.filtered_index).click()
        assert self.scraping_filter_modal_utils.deactivate_button().is_enabled()
        assert not self.scraping_filter_modal_utils.edit_button("view", enabled=False).is_enabled()
