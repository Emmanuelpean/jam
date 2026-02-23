"""Tests for the scraped jobs."""

import datetime as dt

from sqlalchemy import func

from conftest import BaseTest, models


class TestJobScrapingTable(BaseTest):

    user_index = 0
    page_url = "dashboard"

    def setup_function(self, request) -> None:
        """Setup for each test function."""

        request.getfixturevalue("test_scraped_jobs")
        self.login()

    def show_job(self, scraped_job: models.ScrapedJob) -> None:
        """Show a job in the table.
        :param scraped_job: The scraped job to show."""

        self.scrapedJob_table_utils.set_search(scraped_job.title)
        self.scrapingFilter_table_utils.deadline_toggle.click()

    def test_import_scraped_job(self) -> None:
        """Test importing a scraped job and displaying a toast notification."""

        scraped_job = self.db.query(models.ScrapedJob).filter_by(owner_id=self.db_user.id).first()

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

        scraped_job = self.db.query(models.ScrapedJob).filter_by(owner_id=self.db_user.id).first()
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

        scraped_job = self.db.query(models.ScrapedJob).filter_by(owner_id=self.db_user.id).first()
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

        scraped_job = self.db.query(models.ScrapedJob).filter_by(owner_id=self.db_user.id).first()
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

        # noinspection PyComparisonWithNone
        scraped_job = (
            self.db.query(models.ScrapedJob)
            .filter(models.ScrapedJob.owner_id == self.user.id)
            .filter(models.ScrapedJob.is_imported.is_(False))
            .filter(models.ScrapedJob.is_active.is_(True))
            .filter(models.ScrapedJob.exclusion_filter_id == None)
            .filter(models.ScrapedJob.deadline.isnot(None))
            .first()
        )
        assert scraped_job.deadline < dt.datetime.now(dt.timezone.utc)
        self.scrapedJob_table_utils.set_search(scraped_job.title)
        assert not self.scrapedJob_table_utils.check_id_in_table(scraped_job.id)

        self.scrapingFilter_table_utils.deadline_toggle.click()
        assert self.scrapedJob_table_utils.check_id_in_table(scraped_job.id)

    # -------------------------------------------------- JOB SCRAPING --------------------------------------------------

    def test_scraped_job_skipped(self) -> None:
        """Test that a scraped job that was skipped is displayed correctly."""

        scraped_job = self.db.query(models.ScrapedJob).filter_by(owner_id=self.db_user.id, is_skipped=True).first()
        self.show_job(scraped_job)
        self.scrapedJob_table_utils.table_row(scraped_job.id).click()
        modal = self.scrapedJob_modal_utils.wait_for_import_modal()
        assert scraped_job.skip_reason in modal.text

    def test_scraped_job_not_processed(self) -> None:
        """Test that a scraped job that was not processed is displayed correctly."""

        scraped_job = self.db.query(models.ScrapedJob).filter_by(owner_id=self.db_user.id, is_processed=False).first()
        self.show_job(scraped_job)
        self.scrapedJob_table_utils.table_row(scraped_job.id).click()
        modal = self.scrapedJob_modal_utils.wait_for_import_modal()
        assert "This job has yet to be processed. Please come back soon." in modal.text

    def test_scraped_job_failed(self) -> None:
        """Test a scraped job that failed to be processed."""

        scraped_job = (
            self.db.query(models.ScrapedJob)
            .filter_by(owner_id=self.db_user.id, is_failed=True, is_imported=False)
            .first()
        )
        self.show_job(scraped_job)
        self.scrapedJob_table_utils.table_row(scraped_job.id).click()
        modal = self.scrapedJob_modal_utils.wait_for_import_modal()
        expected = "This job could not be scraped properly due to an unexpected error. You can report it here."
        assert expected in modal.text

    # --------------------------------------------------- JOB RATING ---------------------------------------------------

    def test_scraped_job_without_rating(self, session, test_job_ratings) -> None:
        """Test that a scraped job without a rating is displayed correctly."""

        # noinspection PyComparisonWithNone
        scraped_job = session.query(models.ScrapedJob).filter(models.ScrapedJob.job_rating == None).first()
        self.show_job(scraped_job)
        self.scrapedJob_table_utils.table_row(scraped_job.id).click()
        modal = self.scrapedJob_modal_utils.wait_for_import_modal()
        assert "This job has yet to be rated. Please come back later." in modal.text

    def test_scraped_job_with_rating(self, session, test_job_ratings) -> None:
        """Test that a scraped job with a rating is displayed correctly."""

        job_rating = session.query(models.JobRating).filter_by(owner_id=self.db_user.id, is_success=True).first()
        scraped_job = job_rating.scraped_job
        self.show_job(scraped_job)
        self.scrapedJob_table_utils.table_row(scraped_job.id).click()
        modal = self.scrapedJob_modal_utils.wait_for_import_modal()
        assert "Moderate match. The candidate has some relevant skills but lacks specific experience." in modal.text

    def test_scraped_job_with_failed_rating(self, session, test_job_ratings) -> None:
        """Test that a scraped job with a rating is displayed correctly."""

        # noinspection PyComparisonWithNone
        job_rating = (
            session.query(models.JobRating)
            .join(models.ScrapedJob)
            .filter(
                models.JobRating.owner_id == self.db_user.id,
                models.JobRating.is_success.is_(False),
                models.ScrapedJob.exclusion_filter_id == None,
            )
            .first()
        )
        scraped_job = job_rating.scraped_job
        self.show_job(scraped_job)
        self.scrapedJob_table_utils.table_row(scraped_job.id).click()
        modal = self.scrapedJob_modal_utils.wait_for_import_modal()
        assert "This job could not be rated due to an unexpected error. You can report it here." in modal.text
        assert "Job Rating" not in modal.text

    def test_scraped_job_with_skipped_rating(self, session, test_job_ratings) -> None:
        """Test that a scraped job with skipped rating is displayed correctly."""

        # noinspection PyComparisonWithNone
        job_rating = (
            session.query(models.JobRating)
            .join(models.ScrapedJob)
            .filter(
                models.JobRating.owner_id == self.db_user.id,
                models.JobRating.is_skipped.is_(True),
                models.ScrapedJob.exclusion_filter_id == None,
            )
            .first()
        )
        scraped_job = job_rating.scraped_job
        self.show_job(scraped_job)
        self.scrapedJob_table_utils.table_row(scraped_job.id).click()
        modal = self.scrapedJob_modal_utils.wait_for_import_modal()
        assert "Job description too short (minimum length is 100 characters)" in modal.text
        assert "Job Rating" not in modal.text

    def test_scraped_job_with_job_rating_with_notes(self, session, test_job_ratings) -> None:
        """Test that a scraped job with a rating with notes is displayed correctly."""

        job_rating = (
            session.query(models.JobRating)
            .filter(models.JobRating.owner_id == self.db_user.id, func.array_length(models.JobRating.notes, 1) > 0)
            .first()
        )
        self.show_job(job_rating.scraped_job)
        self.scrapedJob_table_utils.table_row(job_rating.scraped_job.id).click()
        modal = self.scrapedJob_modal_utils.wait_for_import_modal()
        expected = (
            "Please note the following, during AI rating:\nDescription was truncated as it was too long "
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
