"""Tests for the scraped jobs."""

import datetime as dt
import uuid

from selenium.webdriver.common.by import By

from conftest import BaseTest, models


class TestJobScrapingTable(BaseTest):

    user_index = 0
    page_url = "dashboard"

    def setup_function(self, request) -> None:
        """Setup for each test function."""

        request.getfixturevalue("test_job_scraping_service_logs")
        request.getfixturevalue("test_user_qualifications")
        self.login()

    def _make_scraped_job(self, **kwargs) -> models.ScrapedJob:
        """Create and persist a ScrapedJob for this test."""

        service_log = self.db.query(models.JobEmailScrapingServiceLog).first()
        defaults = {
            "external_job_id": str(uuid.uuid4()),
            "platform": "linkedin",
            "owner_id": self.db_user.id,
            "is_processed": True,
            "title": "Test Job",
            "url": "test.com",
            "service_log_id": service_log.id,
        }
        defaults.update(kwargs)
        job = models.ScrapedJob(**defaults)
        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)
        return job

    def _make_job_rating(self, scraped_job: models.ScrapedJob, **kwargs) -> models.JobRating:
        """Create and persist a JobRating linked to the given scraped job."""

        qualification = self.db.query(models.UserQualification).filter_by(owner_id=self.db_user.id).first()
        defaults = {
            "scraped_job_id": scraped_job.id,
            "owner_id": self.db_user.id,
            "user_qualification_id": qualification.id,
        }
        defaults.update(kwargs)
        rating = models.JobRating(**defaults)
        self.db.add(rating)
        self.db.commit()
        self.db.refresh(rating)
        return rating

    def show_job(self, scraped_job: models.ScrapedJob) -> None:
        """Show a job in the table.
        :param scraped_job: The scraped job to show."""

        self.scrapedJob_table_utils.set_search(scraped_job.title)
        self.scrapingFilter_table_utils.deadline_toggle.click()

    def test_import_scraped_job(self) -> None:
        """Test importing a scraped job and displaying a toast notification."""

        scraped_job = self._make_scraped_job(
            title="Import Test Job",
            is_scraped=True,
            description="A job to import for testing purposes.",
        )
        self.driver.refresh()

        # Import the scraped job
        job_count = self.db.query(models.Job).count()
        self.show_job(scraped_job)
        self.scrapedJob_table_utils.table_row(scraped_job.id).click()
        modal = self.scrapedJob_modal_utils.wait_for_import_modal()
        assert "job rating" not in modal.text.lower()
        self.scrapedJob_modal_utils.import_button().click()
        self.scrapedJob_modal_utils.wait_for_import_modal_close()
        self.scrapedJob_table_utils.assert_toast_message("Job imported successfully.")

        # Verify that the job count has increased by 1
        assert self.db.query(models.Job).count() == job_count + 1
        self.scrapedJob_table_utils.go_to_page("jobs")
        self.job_table_utils.wait_for_table_load()
        assert len(self.job_table_utils.table_rows) == job_count + 1
        self.db.expire_all()

        # Verify that the scraped job is marked as imported
        scraped_job = self.db.query(models.ScrapedJob).filter_by(id=scraped_job.id).first()
        assert scraped_job.is_imported

    def test_right_click_import_scraped_job(self) -> None:
        """Test importing a scraped job via right-click and displaying a toast notification."""

        scraped_job = self._make_scraped_job(title="Right Click Import Test Job", is_scraped=True)
        self.driver.refresh()
        self.show_job(scraped_job)

        job_count = self.db.query(models.Job).count()
        self.scrapedJob_table_utils.table_context_menu(scraped_job.id, "import")
        self.scrapedJob_modal_utils.import_button().click()
        self.scrapedJob_modal_utils.wait_for_import_modal_close()
        self.scrapedJob_table_utils.assert_toast_message("Job imported successfully.")

        # Verify that the job count has increased by 1
        assert self.db.query(models.Job).count() == job_count + 1
        self.scrapedJob_table_utils.go_to_page("jobs")
        self.job_table_utils.wait_for_table_load()
        assert len(self.job_table_utils.table_rows) == job_count + 1
        self.db.expire_all()

        # Verify that the scraped job is marked as imported
        scraped_job = self.db.query(models.ScrapedJob).filter_by(id=scraped_job.id).first()
        assert scraped_job.is_imported

    def test_delete_scraped_job(self) -> None:
        """Test deleting a scraped job and displaying a toast notification."""

        scraped_job = self._make_scraped_job(title="Delete Test Job", is_scraped=True)
        self.driver.refresh()
        self.show_job(scraped_job)

        self.scrapedJob_table_utils.table_row(scraped_job.id).click()
        self.scrapedJob_modal_utils.delete_button("import").click()
        self.delete_modal.confirm_button.click()
        self.scrapedJob_modal_utils.wait_for_import_modal_close()
        self.assert_toast_message("Scraped Job deleted successfully.")
        self.db.expire_all()
        scraped_job = self.db.query(models.ScrapedJob).filter_by(id=scraped_job.id).first()
        assert not scraped_job.is_active

    def test_context_menu_delete_scraped_job(self) -> None:
        """Test deleting a scraped job via right-click and displaying a toast notification."""

        scraped_job = self._make_scraped_job(title="Context Menu Delete Test Job", is_scraped=True)
        self.driver.refresh()
        self.show_job(scraped_job)

        self.scrapedJob_table_utils.table_context_menu(scraped_job.id, "delete")
        self.delete_modal.confirm_button.click()
        self.scrapedJob_modal_utils.wait_for_import_modal_close()
        self.assert_toast_message("Scraped Job deleted successfully.")
        self.db.expire_all()
        scraped_job = self.db.query(models.ScrapedJob).filter_by(id=scraped_job.id).first()
        assert not scraped_job.is_active

    def test_deadline_toggle(self) -> None:
        """Test the deadline toggle"""

        scraped_job = self._make_scraped_job(
            title="Past Deadline Test Job",
            is_scraped=True,
            is_imported=False,
            deadline=dt.datetime(2024, 1, 1, tzinfo=dt.timezone.utc),
        )
        self.driver.refresh()
        assert scraped_job.deadline < dt.datetime.now(dt.timezone.utc)
        self.scrapedJob_table_utils.set_search(scraped_job.title)
        assert self.scrapedJob_table_utils.check_id_not_in_table(scraped_job.id)

        self.scrapingFilter_table_utils.deadline_toggle.click()
        assert self.scrapedJob_table_utils.check_id_in_table(scraped_job.id)

    # -------------------------------------------------- JOB SCRAPING --------------------------------------------------

    def test_scraped_job_skipped(self) -> None:
        """Test that a scraped job that was skipped is displayed correctly."""

        scraped_job = self._make_scraped_job(
            title="Skipped Test Job",
            is_skipped=True,
            skip_reason="You reached your month quota for job scraping.",
        )
        self.driver.refresh()
        self.show_job(scraped_job)
        self.scrapedJob_table_utils.table_row(scraped_job.id).click()
        modal = self.scrapedJob_modal_utils.wait_for_import_modal()
        assert scraped_job.skip_reason in modal.text

    def test_scraped_job_not_processed(self) -> None:
        """Test that a scraped job that was not processed is displayed correctly."""

        scraped_job = self._make_scraped_job(title="Not Processed Test Job", is_processed=False)
        self.driver.refresh()
        self.show_job(scraped_job)
        self.scrapedJob_table_utils.table_row(scraped_job.id).click()
        modal = self.scrapedJob_modal_utils.wait_for_import_modal()
        assert "This job has yet to be processed. Please come back soon." in modal.text

    def test_scraped_job_failed(self) -> None:
        """Test a scraped job that failed to be processed."""

        scraped_job = self._make_scraped_job(title="Failed Test Job", is_failed=True)
        self.driver.refresh()
        self.show_job(scraped_job)
        self.scrapedJob_table_utils.table_row(scraped_job.id).click()
        modal = self.scrapedJob_modal_utils.wait_for_import_modal()
        expected = "This job could not be scraped properly due to an unexpected error. You can report it here."
        assert expected in modal.text

    def test_scraped_job_retry_pending_badge(self) -> None:
        """Test that a job pending retry shows the correct badge in the table."""

        scraped_job = self._make_scraped_job(
            title="Retry Pending Test Job",
            is_processed=False,
            retry_count=1,
            scrape_error=[{"datetime": "2025-01-01T00:00:00+00:00", "error": "Simulated scraping failure"}],
        )
        self.driver.refresh()
        self.show_job(scraped_job)

        row = self.scrapedJob_table_utils.table_row(scraped_job.id)
        badge = row.find_element(By.CSS_SELECTOR, ".badge")
        assert badge.text == "Retrying (1/3)"

    def test_scraped_job_retry_pending_modal_warning(self) -> None:
        """Test that a job pending retry shows the correct warning in the modal."""

        scraped_job = self._make_scraped_job(
            title="Retry Warning Test Job",
            is_processed=False,
            retry_count=2,
            scrape_error=[
                {"datetime": "2025-01-01T00:00:00+00:00", "error": "First failure"},
                {"datetime": "2025-01-02T00:00:00+00:00", "error": "Second failure"},
            ],
        )
        self.driver.refresh()
        self.show_job(scraped_job)
        self.scrapedJob_table_utils.table_row(scraped_job.id).click()
        modal = self.scrapedJob_modal_utils.wait_for_import_modal()
        assert "Scraping failed (attempt 2/3). It will be reattempted soon." in modal.text

    def test_scraped_job_closed(self) -> None:
        """Test a scraped job that failed to be processed."""

        scraped_job = self._make_scraped_job(title="Closed Test Job", is_closed=True)
        self.driver.refresh()
        self.show_job(scraped_job)
        self.scrapedJob_table_utils.table_row(scraped_job.id).click()
        modal = self.scrapedJob_modal_utils.wait_for_import_modal()
        expected = "This job is now closed and you may not be able to apply to it."
        assert expected in modal.text

    # --------------------------------------------------- JOB RATING ---------------------------------------------------

    def test_scraped_job_without_rating(self) -> None:
        """Test that a scraped job without a rating is displayed correctly."""

        scraped_job = self._make_scraped_job(title="No Rating Test Job", is_scraped=True)
        self.driver.refresh()
        self.show_job(scraped_job)
        self.scrapedJob_table_utils.table_row(scraped_job.id).click()
        modal = self.scrapedJob_modal_utils.wait_for_import_modal()
        assert "This job has yet to be rated. Please come back later." in modal.text

    def test_scraped_job_with_rating(self) -> None:
        """Test that a scraped job with a rating is displayed correctly."""

        scraped_job = self._make_scraped_job(title="Rated Test Job", is_scraped=True)
        self._make_job_rating(
            scraped_job,
            overall_score=4,
            technical_score=5,
            experience_score=3,
            educational_score=6,
            interest_score=4,
            is_success=True,
            feedback="Moderate match. The candidate has some relevant skills but lacks specific experience.",
            llm_model="chatgpt",
        )
        self.driver.refresh()
        self.show_job(scraped_job)
        self.scrapedJob_table_utils.table_row(scraped_job.id).click()
        modal = self.scrapedJob_modal_utils.wait_for_import_modal()
        assert "Moderate match. The candidate has some relevant skills but lacks specific experience." in modal.text

    def test_scraped_job_with_failed_rating(self) -> None:
        """Test that a scraped job with a failed rating is displayed correctly."""

        scraped_job = self._make_scraped_job(title="Failed Rating Test Job", is_scraped=True)
        self._make_job_rating(
            scraped_job, is_success=False, error="Failed to scrape job details: Page not found", llm_model="chatgpt"
        )
        self.driver.refresh()
        self.show_job(scraped_job)
        self.scrapedJob_table_utils.table_row(scraped_job.id).click()
        modal = self.scrapedJob_modal_utils.wait_for_import_modal()
        assert "This job could not be rated due to an unexpected error. You can report it here." in modal.text
        assert "Job Rating" not in modal.text

    def test_scraped_job_with_skipped_rating(self) -> None:
        """Test that a scraped job with a skipped rating is displayed correctly."""

        scraped_job = self._make_scraped_job(title="Skipped Rating Test Job", is_scraped=True)
        self._make_job_rating(
            scraped_job,
            is_success=False,
            is_skipped=True,
            skip_reason="Job description too short (minimum length is 100 characters)",
            llm_model="chatgpt",
        )
        self.driver.refresh()
        self.show_job(scraped_job)
        self.scrapedJob_table_utils.table_row(scraped_job.id).click()
        modal = self.scrapedJob_modal_utils.wait_for_import_modal()
        assert "Job description too short (minimum length is 100 characters)" in modal.text
        assert "Job Rating" not in modal.text

    def test_scraped_job_with_job_rating_with_notes(self) -> None:
        """Test that a scraped job with a rating with notes is displayed correctly."""

        scraped_job = self._make_scraped_job(title="Rating With Notes Test Job", is_scraped=True)
        self._make_job_rating(
            scraped_job,
            overall_score=6,
            technical_score=7,
            experience_score=6,
            educational_score=5,
            interest_score=7,
            is_success=True,
            feedback="Moderate match with potential for growth.",
            llm_model="chatgpt",
            notes=[
                "Description was truncated as it was too long (5234 characters. Limit is 5000 characters)",
                "Title was truncated as it was too long (5234 characters. Limit is 5000 characters)",
            ],
        )
        self.driver.refresh()
        self.show_job(scraped_job)
        self.scrapedJob_table_utils.table_row(scraped_job.id).click()
        modal = self.scrapedJob_modal_utils.wait_for_import_modal()
        expected = (
            "Notes:\nDescription was truncated as it was too long "
            "(5234 characters. Limit is 5000 characters)\nTitle was truncated as it was too long "
            "(5234 characters. Limit is 5000 characters)"
        )
        assert expected in modal.text


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

        filter_count = self.db.query(models.ScrapingExclusionFilter).count()
        self.scrapingFilter_table_utils.add_entity_button.click()
        self.scrapingFilter_modal_utils.add_entry(**self.test_data)
        assert self.db.query(models.ScrapingExclusionFilter).count() == filter_count + 1

    def test_deactivate_scraping_filter(self) -> None:
        """Test deactivating a scraping filter and displaying a toast notification."""

        self.scrapingFilter_table_utils.table_row(self.no_filtered_index).click()
        self.scrapingFilter_modal_utils.deactivate_button().click()
        self.scrapingFilter_modal_utils.wait_for_view_modal_close()
        self.assert_toast_message("Scraping Filter deactivated successfully.")
        self.db.expire_all()
        scraping_filter = self.db.query(models.ScrapingExclusionFilter).filter_by(id=self.no_filtered_index).first()
        assert not scraping_filter.is_active
        self.get_element("inactive-tab").click()
        assert self.scrapingFilter_table_utils.table_row(self.no_filtered_index).is_displayed()

    def test_edit_scraping_filter(self) -> None:
        """Test deactivating a scraping filter when it has filtered jobs."""

        assert (
            not self.db.query(models.ScrapingExclusionFilter).filter_by(id=self.no_filtered_index).first().filtered_jobs
        )
        self.scrapingFilter_table_utils.table_row(self.no_filtered_index).click()
        assert self.scrapingFilter_modal_utils.deactivate_button().is_enabled()
        assert not self.scrapingFilter_modal_utils.edit_button("view", enabled=False).click()
        self.scrapingFilter_modal_utils._fill_modal(value="Virtual")
        self.scrapingFilter_modal_utils.confirm_button("edit").click()
        self.scrapingFilter_modal_utils.wait_for_view_modal_close()

    def test_edit_scraping_filter_failure(self) -> None:
        """Test deactivating a scraping filter when it has filtered jobs."""

        assert self.db.query(models.ScrapingExclusionFilter).filter_by(id=self.filtered_index).first().filtered_jobs
        self.scrapingFilter_table_utils.table_row(self.filtered_index).click()
        assert self.scrapingFilter_modal_utils.deactivate_button().is_enabled()
        assert not self.scrapingFilter_modal_utils.edit_button("view", enabled=False).is_enabled()
