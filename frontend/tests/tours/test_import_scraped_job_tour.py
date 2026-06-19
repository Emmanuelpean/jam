"""Selenium tests for the Import Scraped Job guided tour.

Tour step order (import-scraped-job):
  0   scraped-intro              informational — centre popover
  1   scraped-nav                sidebar nav-scraped-jobs highlighted
  2   scraped-table              table overview; blockLeftClick; allowedContextMenuActions: []
  3   scraped-ai-score           AI score column header highlighted
  4   scraped-filters            Scraping Filters button; auto-advances to hint if filters opened
  4b  scraped-filters-tour-hint  conditional — shown when filter panel opens; Next closes panel
  5   scraped-emails-tab         click Job Emails tab (hideNextButton); auto-advances when active
  6   scraped-open-email         click demo email row (hideNextButton); auto-advances when modal opens
  7   scraped-email-modal-content  view email modal content; Next/Back closes modal
  8   scraped-back-to-alerts     click Job Alerts tab (hideNextButton); auto-advances when active
  9   scraped-open-row           click demo scraped job row (hideNextButton); auto-advances when modal opens
  10  scraped-review-form        review import form
  11  scraped-company-location   review company & location field
  12  scraped-import-btn         click Import (hideNextButton); auto-advances when modal closes
  13  scraped-done               Done step — no keep/delete toggle (noKeepData: true)

JAM entities seeded at tour start (all is_tour=True):
  ScrapedJob: demo scraped job with AI rating (overall_score=8)
  JobEmail:   demo job email linked to the scraped job

Cleanup on Done/Skip:
  - Demo ScrapedJob is deleted via deleteTourDemo
  - Imported Job (created on scraped-import-btn) is KEPT (noKeepData=true → always keepData=false for demo,
    but the actual imported Job is user data that persists after Done)
"""

import time

from app import models
from base_test import BaseTest

TOUR_ID = "import-scraped-job"


class TestImportScrapedJobTour(BaseTest):
    user_index = 0
    page_url = "job-alerts/jobs"

    def setup_function(self, request) -> None:
        self.login()

    # ------------------------------------------------------------------ helpers

    def _start_and_advance_to_emails_tab(self) -> None:
        """Start the tour, click through intro/nav/table/ai-score/filters, then switch to Emails tab.

        Returns with the tour popover on step 6 (scraped-open-email) and the
        page on job-alerts/emails.
        """
        self.tour_utils.start_tour(TOUR_ID)
        self.wait_for_page("job-alerts/jobs")

        # Step 1 (scraped-nav): informational — click Next
        self.tour_utils.click_next()

        # Step 2 (scraped-table): table overview; left-click is blocked — click Next
        self.tour_utils.wait_for_popover()
        self.tour_utils.click_next()

        # Step 3 (scraped-ai-score): AI score column — click Next
        self.tour_utils.wait_for_popover()
        self.tour_utils.click_next()

        # Step 4 (scraped-filters): skip without opening filters — click Next
        # nextStepId points directly to scraped-emails-tab
        self.tour_utils.wait_for_popover()
        self.tour_utils.click_next()

        # Step 5 (scraped-emails-tab): click the Job Emails tab;
        # tour auto-advances to step 6 when #job-emails-header.page-header-active appears.
        self.tour_utils.wait_for_popover()
        self.get_element("job-emails-header").click()

        # Step 6 (scraped-open-email): popover appears on the demo email row
        self.tour_utils.wait_for_popover()

    def _open_email_modal_and_close(self) -> None:
        """From step 6 (scraped-open-email), click the demo email row and close the modal.

        Returns with the tour popover on step 8 (scraped-back-to-alerts).
        """
        # Step 6 (scraped-open-email): click demo email row;
        # tour auto-advances to step 7 when #modal-view-jobEmail appears.
        demo_email = self.db.query(models.JobEmail).filter_by(owner_id=self.user.id, is_tour=True).first()
        time.sleep(0.5)  # wait for animation to finish
        self.jobEmail_table_utils.table_row_click(demo_email.id)

        # Step 7 (scraped-email-modal-content): email modal shown; click Next which closes modal
        # via nextActionSelector (#modal-view-jobEmail-cancel-button)
        self.tour_utils.wait_for_popover()
        self.tour_utils.click_next()

        # Step 8 (scraped-back-to-alerts): click Job Alerts tab;
        # tour auto-advances when #scraped-jobs-header.page-header-active appears.
        self.tour_utils.wait_for_popover()

    def _back_to_alerts_and_open_import_form(self) -> None:
        """From step 8 (scraped-back-to-alerts), switch back to alerts and open the import modal.

        Returns with the tour popover on step 10 (scraped-review-form).
        """
        # Click Job Alerts tab — auto-advances to step 9
        self.get_element("scraped-jobs-header").click()

        # Step 9 (scraped-open-row): click demo scraped job row;
        # tour auto-advances to step 10 when #modal-import-scrapedJob appears.
        self.tour_utils.wait_for_popover()
        demo_job = self.db.query(models.ScrapedJob).filter_by(owner_id=self.user.id, is_tour=True).first()
        self.scrapedJob_table_utils.table_row_click(demo_job.id)

        # Step 10 (scraped-review-form): import form shown — popover appears
        self.tour_utils.wait_for_popover()

    # ------------------------------------------------------------------ tests

    def test_full_flow(self) -> None:
        """Complete the entire tour end-to-end and verify the imported job is kept.

        noKeepData=True means no keep/delete toggle. The demo ScrapedJob is cleaned
        up on Done; the imported Job record persists.
        """
        initial_scraped = self.db.query(models.ScrapedJob).filter_by(owner_id=self.user.id).count()
        initial_jobs = self.db.query(models.Job).filter_by(owner_id=self.user.id).count()

        self._start_and_advance_to_emails_tab()
        self._open_email_modal_and_close()
        self._back_to_alerts_and_open_import_form()

        # Step 10 (scraped-review-form): click Next
        self.tour_utils.click_next()

        # Step 11 (scraped-company-location): click Next
        self.tour_utils.wait_for_popover()
        self.tour_utils.click_next()

        # Step 12 (scraped-import-btn): click Import button;
        # tour auto-advances to step 13 when #modal-import-scrapedJob closes.
        self.tour_utils.wait_for_popover()
        self.scrapedJob_modal_utils.import_button().click()

        # Step 13 (scraped-done): no keep/delete toggle — click Done
        self.tour_utils.wait_for_popover()
        assert "Done" in self.get_element(self.tour_utils.TOUR_NEXT).text
        assert not self.check_element_exists("tour-keep-data"), "Keep my data toggle must not appear"
        self.tour_utils.click_next()

        self.tour_utils.wait_for_popover_gone()
        self.wait_for_page(self.page_url)

        # Demo ScrapedJob cleaned up (returns to initial count); imported Job persists
        self.tour_utils.poll_db_count(models.ScrapedJob, self.user.id, initial_scraped)
        self.tour_utils.poll_db_count(models.Job, self.user.id, initial_jobs + 1)

    def test_filters_hint_step(self) -> None:
        """Opening the filter panel during the filters step triggers the hint step.

        The hint step should show a popover with 'There's a Tour for This!' content.
        Clicking Next closes the panel and moves on to the emails tab step.
        """
        self.tour_utils.start_tour(TOUR_ID)
        self.wait_for_page("job-alerts/jobs")

        # Steps 0-2: intro → nav → table → ai-score
        self.tour_utils.click_next()
        self.tour_utils.wait_for_popover()
        self.tour_utils.click_next()
        self.tour_utils.wait_for_popover()
        self.tour_utils.click_next()

        # Step 4 (scraped-filters): click the Scraping Filters button to open the panel;
        # tour auto-advances to hint step when #scraping-filters-modal appears.
        self.tour_utils.wait_for_popover()
        self.get_element("scraping-filters-button").click()

        # Step 4b (scraped-filters-tour-hint): hint popover should appear
        self.tour_utils.wait_for_popover()
        assert "Tour" in self.tour_utils.popover_title()

        # Click Next — nextActionSelector closes the filter panel, then moves to emails-tab step
        self.tour_utils.click_next()

        # Step 5 (scraped-emails-tab): click Job Emails tab
        self.tour_utils.wait_for_popover()
        self.get_element("job-emails-header").click()

        # Clean up by skipping
        self.tour_utils.wait_for_popover()
        self.tour_utils.click_skip()
        self.tour_utils.wait_for_popover_gone()

    def test_table_left_click_blocked(self) -> None:
        """On step 2 (scraped-table), a left-click on the table must not open the import modal."""
        self.tour_utils.start_tour(TOUR_ID)
        self.wait_for_page("job-alerts/jobs")

        # Step 1 (scraped-intro): click Next
        self.tour_utils.click_next()

        # Step 2 (scraped-table): blockLeftClick is active
        self.tour_utils.wait_for_popover()
        demo_job = self.db.query(models.ScrapedJob).filter_by(owner_id=self.user.id, is_tour=True).first()
        # Attempt a left-click on the demo row — modal must NOT open
        self.scrapedJob_table_utils.table_row_click(demo_job.id)
        assert not self.check_element_exists(
            "modal-import-scrapedJob", timeout=2
        ), "Import modal must not open when blockLeftClick is active on scraped-table step"

        # Clean up by skipping
        self.tour_utils.click_skip()
        self.tour_utils.wait_for_popover_gone()

    def test_no_keep_data_toggle(self) -> None:
        """The done step must never show the keep/delete toggle (noKeepData=true)."""
        initial_scraped = self.db.query(models.ScrapedJob).filter_by(owner_id=self.user.id).count()
        initial_jobs = self.db.query(models.Job).filter_by(owner_id=self.user.id).count()

        self._start_and_advance_to_emails_tab()
        self._open_email_modal_and_close()
        self._back_to_alerts_and_open_import_form()

        # Advance through review → company → import
        self.tour_utils.click_next()
        self.tour_utils.wait_for_popover()
        self.tour_utils.click_next()
        self.tour_utils.wait_for_popover()
        self.scrapedJob_modal_utils.import_button().click()

        # Done step — assert no toggle at all
        self.tour_utils.wait_for_popover()
        assert "Done" in self.get_element(self.tour_utils.TOUR_NEXT).text
        assert not self.check_element_exists("tour-keep-data"), "Keep my data toggle must not appear (noKeepData=true)"
        self.tour_utils.click_next()

        self.tour_utils.wait_for_popover_gone()
        self.wait_for_page(self.page_url)

        # Verify cleanup: demo scraped job gone (returns to initial count), imported job kept
        self.tour_utils.poll_db_count(models.ScrapedJob, self.user.id, initial_scraped)
        self.tour_utils.poll_db_count(models.Job, self.user.id, initial_jobs + 1)

    def test_skip_tour(self) -> None:
        """Skip the tour after the table step — no job is imported.

        Demo ScrapedJob must be cleaned up on skip.
        """
        initial_scraped = self.db.query(models.ScrapedJob).filter_by(owner_id=self.user.id).count()
        initial_jobs = self.db.query(models.Job).filter_by(owner_id=self.user.id).count()

        self.tour_utils.start_tour(TOUR_ID)
        self.wait_for_page("job-alerts/jobs")

        # Steps 0-2: intro → nav → table
        self.tour_utils.click_next()
        self.tour_utils.wait_for_popover()
        self.tour_utils.click_next()
        self.tour_utils.wait_for_popover()

        # Skip during step 2 (scraped-table)
        self.tour_utils.click_skip()

        self.tour_utils.wait_for_popover_gone()
        self.wait_for_page(self.page_url)

        # Demo ScrapedJob cleaned up (returns to initial count); no new Job created
        self.tour_utils.poll_db_count(models.ScrapedJob, self.user.id, initial_scraped)
        self.tour_utils.poll_db_count(models.Job, self.user.id, initial_jobs)

    def test_email_modal_back_closes_and_returns(self) -> None:
        """Clicking Back on the email modal content step closes the modal
        and returns to the open-email step.
        """
        self._start_and_advance_to_emails_tab()

        # Step 6 (scraped-open-email): click demo email row
        demo_email = self.db.query(models.JobEmail).filter_by(owner_id=self.user.id, is_tour=True).first()
        self.jobEmail_table_utils.table_row_click(demo_email.id)

        # Step 7 (scraped-email-modal-content): modal is open
        self.tour_utils.wait_for_popover()
        self.jobEmail_modal_utils.wait_for_view_modal()

        # Click Back — backActionSelector closes the modal, returns to scraped-open-email
        self.tour_utils.click_back()

        # Wait for the modal to close (confirms backActionSelector fired), then check popover title
        self.wait_for_disappear("modal-view-jobEmail")
        self.wait_for_element_text(self.tour_utils.TOUR_TITLE, "Open the Demo Email")
        assert not self.check_element_exists(
            "modal-view-jobEmail", timeout=2
        ), "Email modal must be closed after clicking Back on scraped-email-modal-content"

        # Clean up by skipping
        self.tour_utils.click_skip()
        self.tour_utils.wait_for_popover_gone()
