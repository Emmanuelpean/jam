"""Tests for the scraped jobs."""

import datetime as dt

from selenium.webdriver.common.by import By

from base_test import BaseTest, models


class TestJobScrapingTable(BaseTest):

    user_index = 0
    page_url = "scraped-jobs"

    def setup_function(self, request) -> None:
        """Setup for each test function."""

        request.getfixturevalue("test_job_scraping_service_logs")
        request.getfixturevalue("test_user_qualifications")
        self.login()

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

    def test_new_alert_last_login(self) -> None:
        """Test that alerts created after previous_login are highlighted with a NEW indicator,
        and alerts created before previous_login are not."""

        previous_login = dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=12)

        # Create an old job (before previous_login) and backdate its created_at
        old_job = self._make_scraped_job(title="Old Alert - No Dot", is_scraped=True)
        old_job.created_at = previous_login - dt.timedelta(hours=1)
        self.db.commit()
        self.db.refresh(old_job)

        # Set previous_login on the user
        user = self.db_user
        user.previous_login = previous_login
        self.db.commit()
        self.db.expire_all()

        # Create a new job (after previous_login — created_at will be now)
        new_job = self._make_scraped_job(title="New Alert - Has Dot", is_scraped=True)

        self.driver.refresh()

        # Old job: first data cell should NOT have the table-cell--new class
        self.scrapedJob_table_utils.set_search(old_job.title)
        old_row = self.scrapedJob_table_utils.table_row(old_job.id)
        assert not old_row.find_elements(By.CSS_SELECTOR, "td.table-cell--new")

        # New job: first data cell SHOULD have the table-cell--new class
        self.scrapedJob_table_utils.set_search(new_job.title)
        new_row = self.scrapedJob_table_utils.table_row(new_job.id)
        assert new_row.find_elements(By.CSS_SELECTOR, "td.table-cell--new")

    def test_read_dot_visibility(self) -> None:
        """Test that the read dot shows for unread jobs and hides for already-read jobs."""

        unread_job = self._make_scraped_job(title="Unread Job - Has Read Dot", is_scraped=True)
        read_job = self._make_scraped_job(title="Read Job - No Read Dot", is_scraped=True)
        read_job.read_at = dt.datetime.now(dt.timezone.utc)
        self.db.commit()
        self.db.refresh(read_job)
        self.driver.refresh()

        self.show_job(unread_job)
        assert self.scrapedJob_table_utils.table_row(unread_job.id).find_elements(
            By.CSS_SELECTOR, "span.read-dot"
        ), "Expected read-dot for unread job"

        self.show_job(read_job)
        assert not self.scrapedJob_table_utils.table_row(read_job.id).find_elements(
            By.CSS_SELECTOR, "span.read-dot"
        ), "Expected no read-dot for already-read job"

    def test_read_dot_shown_when_scraped_after_read(self) -> None:
        """Test that a job scraped after being read shows the read dot again."""

        past = dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=2)
        job = self._make_scraped_job(title="Re-scraped Job - Has Read Dot", is_scraped=True)
        job.read_at = past  # read before last scrape
        job.scrape_datetime = past + dt.timedelta(hours=1)  # scraped after read
        self.db.commit()
        self.db.refresh(job)
        self.driver.refresh()
        self.show_job(job)

        row = self.scrapedJob_table_utils.table_row(job.id)
        assert row.find_elements(By.CSS_SELECTOR, "span.read-dot"), "Expected read-dot when scraped after last read"

    def test_opening_row_marks_as_read(self) -> None:
        """Test that opening an unread job sets read_at in the database and removes the read dot."""

        job = self._make_scraped_job(title="Mark Read On Open Test Job", is_scraped=True)
        assert job.read_at is None
        self.driver.refresh()
        self.show_job(job)

        row = self.scrapedJob_table_utils.table_row(job.id)
        assert row.find_elements(By.CSS_SELECTOR, "span.read-dot"), "Expected read-dot before opening"

        row.click()
        self.scrapedJob_modal_utils.wait_for_import_modal()
        self.close_modal()

        row = self.scrapedJob_table_utils.table_row(job.id)
        assert not row.find_elements(By.CSS_SELECTOR, "span.read-dot"), "Expected read-dot to disappear after opening"

        self.db.expire_all()
        updated = self.db.query(models.ScrapedJob).filter_by(id=job.id).first()
        assert updated.read_at is not None, "Expected read_at to be set in the database"

    def test_already_read_job_does_not_update_read_at(self) -> None:
        """Test that opening an already-read job does not update read_at."""

        past = dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=2)
        job = self._make_scraped_job(title="Already Read Test Job", is_scraped=True)
        # Backdate created_at and scrape_datetime so read_at is after both
        job.created_at = past - dt.timedelta(hours=1)
        job.scrape_datetime = past - dt.timedelta(hours=1)
        read_time = past
        job.read_at = read_time
        self.db.commit()
        self.db.refresh(job)
        self.driver.refresh()
        self.show_job(job)

        self.scrapedJob_table_utils.table_row(job.id).click()
        self.scrapedJob_modal_utils.wait_for_import_modal()

        self.db.expire_all()
        updated = self.db.query(models.ScrapedJob).filter_by(id=job.id).first()
        assert updated.read_at.astimezone(dt.timezone.utc) == read_time, "Expected read_at to remain unchanged"

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
        assert badge.text == "RETRYING (1/3)"

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
        self._create_job_rating(
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
        self._create_job_rating(
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
        self._create_job_rating(
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
        self._create_job_rating(
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
    page_url = "scraped-jobs"
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


class TestDismissExpiredBulkAction(BaseTest):

    user_index = 0
    page_url = "scraped-jobs"

    def setup_function(self, request) -> None:
        """Setup for each test function."""

        request.getfixturevalue("test_job_scraping_service_logs")
        self.login()

    def _open_bulk_actions(self) -> None:
        """Open the bulk actions dropdown."""

        self.get_element("bulk-actions-dropdown").click()

    def _click_delete_expired(self) -> None:
        """Open bulk actions and click Delete Expired."""

        self._open_bulk_actions()
        self.get_element("bulk-action-delete-expired").click()

    def test_delete_expired_no_expired_jobs_shows_toast(self) -> None:
        """When there are no expired jobs, clicking Delete Expired shows a success toast without opening a modal."""

        self._make_scraped_job(title="Active Job", is_closed=False)
        self.driver.refresh()
        self.scrapedJob_table_utils.wait_for_table_load()

        self._click_delete_expired()
        self.scrapedJob_table_utils.assert_toast_message("No expired job alerts found.")

    def test_delete_expired_opens_modal_with_expired_jobs(self) -> None:
        """When there are expired jobs, clicking Delete Expired opens the confirmation modal with the jobs listed."""

        self._make_scraped_job(title="Expired Closed Job", is_closed=True)
        self._make_scraped_job(
            title="Past Deadline Job",
            deadline=dt.datetime(2024, 1, 1, tzinfo=dt.timezone.utc),
        )
        self._make_scraped_job(title="Active Job", is_closed=False)
        self.driver.refresh()
        self.scrapedJob_table_utils.wait_for_table_load()

        self._click_delete_expired()
        modal = self.get_element("dismiss-expired-modal")
        assert modal.is_displayed()
        assert "Delete 2 Expired Job Alerts" in modal.text

    def test_delete_expired_confirm_dismisses_jobs(self) -> None:
        """Confirming dismissal deactivates the expired jobs and shows a toast."""

        expired_job = self._make_scraped_job(title="Job To Dismiss", is_closed=True)
        self.driver.refresh()
        self.scrapedJob_table_utils.wait_for_table_load()

        self._click_delete_expired()
        self.get_element("dismiss-expired-modal")
        self.get_element("dismiss-expired-confirm-btn").click()

        self.scrapedJob_table_utils.assert_toast_message("1 expired job alert dismissed.")

        self.db.expire_all()
        updated = self.db.query(models.ScrapedJob).filter_by(id=expired_job.id).first()
        assert not updated.is_active

    def test_delete_expired_cancel_does_not_dismiss(self) -> None:
        """Cancelling the confirmation modal leaves jobs active."""

        expired_job = self._make_scraped_job(title="Job Not To Dismiss", is_closed=True)
        self.driver.refresh()
        self.scrapedJob_table_utils.wait_for_table_load()

        self._click_delete_expired()
        self.get_element("dismiss-expired-modal")
        self.get_element("dismiss-expired-cancel-btn").click()

        self.db.expire_all()
        updated = self.db.query(models.ScrapedJob).filter_by(id=expired_job.id).first()
        assert updated.is_active
