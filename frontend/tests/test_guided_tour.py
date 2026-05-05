"""Selenium tests for the App Overview guided tour."""

from selenium.webdriver import Keys
from selenium.webdriver.common.by import By

from app import models
from base_test import BaseTest
from react_select import ReactSelect


class TestAppOverviewTour(BaseTest):
    user_index = 0
    page_url = "dashboard"

    def setup_function(self, request) -> None:
        self.login()

    def test_tour_panel_opens_on_click(self) -> None:
        """Clicking 'Take a Tour' in the sidebar reveals the tour select panel."""
        self.tour_utils.open_tour_select()
        assert self.check_element_exists(self.tour_utils.TSP_PANEL)
        assert self.check_element_exists(f"tsp-item-{self.tour_utils.TOUR_ID}")
        assert "/" in self.get_element(self.tour_utils.TSP_PROGRESS, enabled=False).text

    def test_starting_tour_shows_popover(self) -> None:
        """Starting the App Overview tour displays the tour popover."""
        self.go_to_page("jobs")
        self.tour_utils.start_tour()
        assert self.check_element_exists(self.tour_utils.TOUR_POPOVER)
        assert self.tour_utils.popover_title() == "Welcome to JAM!"
        assert self.tour_utils.step_counter_text().upper() == f"STEP 1 OF {self.tour_utils.TOTAL_STEPS}"
        assert not self.check_element_exists(self.tour_utils.TOUR_BACK)
        assert self.check_element_exists(self.tour_utils.TOUR_BACKDROP)
        self.wait_for_page("dashboard")

    def test_next_previous(self) -> None:
        """Clicking Next moves to step 2."""
        self.tour_utils.start_tour()
        self.tour_utils.click_next()
        self.tour_utils.wait_for_step(2)
        self.tour_utils.click_back()
        self.tour_utils.wait_for_step(1)
        assert self.tour_utils.popover_title() == "Welcome to JAM!"

    def test_arrow_navigation(self) -> None:
        """Right-arrow keyboard shortcut advances the tour."""

        self.tour_utils.start_tour()
        self.driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ARROW_RIGHT)
        self.tour_utils.wait_for_step(2)
        self.driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ARROW_LEFT)
        self.tour_utils.wait_for_step(1)

    def test_back_from_jobs_step_returns_to_dashboard(self) -> None:
        """Clicking Back on the Jobs step navigates back to the dashboard."""
        self.tour_utils.start_tour()
        self.tour_utils.advance_steps(3)
        self.wait_for_page("jobs")
        self.tour_utils.click_back()
        self.wait_for_page("dashboard")

    def test_dismiss_tour(self) -> None:
        """Clicking 'Skip tour' and ESC dismiss the popover."""

        self.tour_utils.start_tour()
        self.tour_utils.click_skip()
        self.tour_utils.wait_for_popover_gone()

        self.tour_utils.start_tour()
        self.tour_utils.driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
        self.tour_utils.wait_for_popover_gone()

        # Skipping mid-tour navigates back to the page where the tour was started.
        self.tour_utils.start_tour()
        self.tour_utils.advance_steps(3)  # navigate away to the jobs step
        self.tour_utils.click_skip()
        self.tour_utils.wait_for_popover_gone()
        self.wait_for_page(self.page_url)

    def test_last_step_shows_done_button(self) -> None:
        """The final step shows a 'Done' button instead of 'Next'."""
        self.tour_utils.start_tour()
        self.tour_utils.advance_to_last_step()
        assert "Done" in self.get_element(self.tour_utils.TOUR_NEXT).text

        # Clicking "Done" closes the tour popover
        self.tour_utils.click_next()  # Done
        self.tour_utils.wait_for_popover_gone()

        # Wait to return to origin page
        self.wait_for_page(self.page_url)

        # Check for completion in tour panel
        self.tour_utils.open_tour_select()
        icon = self.get_element(f"tsp-icon-{self.tour_utils.TOUR_ID}", enabled=False)
        assert "tsp-icon--done" in icon.get_attribute("class")

    def test_active_tour_disables_tour_panel_buttons(self) -> None:
        """While a tour is running, all buttons in the tour select panel are disabled."""
        self.tour_utils.start_tour()
        self.tour_utils.open_tour_select()
        for tour_id in ["app-overview", "first-job", "follow-up-email"]:
            assert not self.get_element(f"tsp-item-{tour_id}", enabled=False).is_enabled()

    def test_cleanup_after_skip(self) -> None:
        """Check the test data are properly cleaned up after each tour."""

        initial_jobs = self.db.query(models.Job).filter_by(owner_id=self.user.id).count()
        initial_persons = self.db.query(models.Person).filter_by(owner_id=self.user.id).count()
        initial_interviews = self.db.query(models.Interview).filter_by(owner_id=self.user.id).count()

        self.tour_utils.start_tour("follow-up-email")

        self.tour_utils.click_skip()
        self.tour_utils.wait_for_popover_gone()

        # Cleanup is async — poll until all seeded entities are deleted
        self.tour_utils.poll_db_count(models.Job, self.user.id, initial_jobs)
        self.tour_utils.poll_db_count(models.Person, self.user.id, initial_persons)
        self.tour_utils.poll_db_count(models.Interview, self.user.id, initial_interviews)

    def test_skip_cleans_up_first_job_tour_data(self) -> None:
        """Skipping the first-job tour mid-flow deletes any job/company created during it."""

        initial_jobs = self.db.query(models.Job).filter_by(owner_id=self.user.id).count()
        initial_companies = self.db.query(models.Company).filter_by(owner_id=self.user.id).count()

        self.tour_utils.start_tour("first-job")
        # The tour navigates to /jobs; wait for the page before interacting with its elements
        self.wait_for_page("jobs")

        # Step 0 (first-job-intro): informational — click Next
        self.tour_utils.click_next()

        # Step 1 (open-job-modal): click the highlighted button to open the add-job form
        self.get_element("add-job-button").click()

        # Step 2 (job-title): tour auto-advances when modal opens; type a title to enable Next
        self.get_element("title").send_keys("Skip Test Job")
        self.tour_utils.click_next()

        # Step 3 (add-company): click the + button to open the inline company form
        self.get_element("add-button-company").click()

        # Step 4 (company-name): type a company name to enable Next
        self.get_element("name").send_keys("Skip Test Company")
        self.tour_utils.click_next()

        # Step 5 (save-company): click Confirm — company is persisted to the DB
        self.get_element("modal-edit-company-confirm-button").click()

        # Confirm the company reached the DB before skipping
        self.tour_utils.poll_db_count(models.Company, self.user.id, initial_companies + 1)

        self.tour_utils.click_skip()
        self.tour_utils.wait_for_popover_gone()

        # Both the job (if partially saved) and the company must be removed
        self.tour_utils.poll_db_count(models.Company, self.user.id, initial_companies)
        self.tour_utils.poll_db_count(models.Job, self.user.id, initial_jobs)

    def test_tour_button_moves_to_about_when_all_premium_tours_completed(self) -> None:
        """After all premium tours are marked done (for a premium user), the 'Take a Tour'
        button disappears from the sidebar and appears inside the About page instead."""
        # Activate premium for this user.

        assert self.user.premium.is_active
        self.user.preferences.completed_tours = self.tour_utils.PREMIUM_TOUR_IDS
        self.db.commit()

        self.refresh()

        self.wait_for_disappear(self.tour_utils.TAKE_A_TOUR_BTN)

        self.go_to_page("about")
        assert self.check_element_exists(self.tour_utils.TAKE_A_TOUR_BTN)

    def test_tour_button_moves_to_about_when_all_non_premium_tours_completed(self, test_non_premium_user) -> None:
        """After all non-premium tours are marked done, the 'Take a Tour' button disappears
        from the sidebar and appears inside the About page instead."""

        self.login(test_non_premium_user)
        test_non_premium_user.preferences.completed_tours = self.tour_utils.NON_PREMIUM_TOUR_IDS
        self.db.commit()

        self.refresh()

        self.wait_for_disappear(self.tour_utils.TAKE_A_TOUR_BTN)

        self.go_to_page("about")
        assert self.check_element_exists(self.tour_utils.TAKE_A_TOUR_BTN)

    def test_continue_to_next_tour_preserves_preexisting_data(self) -> None:
        """Clicking 'Continue to next tour' must not delete pre-existing user data.

        Regression: during an isolated tour (Tour A), visibleData filters out pre-existing
        entities. The stale startTour() closure used to capture an empty/wrong snapshot for
        Tour B, causing endTour() to diff against it and delete all pre-existing entities.

        Test sequence: log-application (Tour A) → log-interview (Tour B).
        Both are isolated tours that auto-seed a demo job. A pre-existing job is created
        before either tour runs and must still exist after both tours complete."""

        # Create a pre-existing job that must survive the entire tour A → tour B sequence.
        self._make_job(title="Pre-existing Job — Must Survive Tours")
        initial_jobs = self.db.query(models.Job).filter_by(owner_id=self.user.id).count()

        # Tour A
        self.tour_utils.start_tour("log-application")
        self.wait_for_page("jobs")

        # Intro step: purely informational — click Next.
        self.tour_utils.click_next()

        # "Open the Job": click the demo job row. During the isolated tour the pre-existing
        # job is hidden by the snapshot filter, so only the demo job row is visible.
        # waitForSelector=#application-tab → tour auto-advances when the view modal opens.
        self.tour_utils.wait_for_popover()
        self.get_element("[id^='table-row-job-']", By.CSS_SELECTOR).click()

        # "Switch to the Application Tab": click the tab.
        # waitForSelector=#add-interview-button → auto-advances.
        self.tour_utils.wait_for_popover()
        self.get_element("application-tab").click()

        # "Edit the Job": click Edit.
        # waitForSelector=#application_date-form-group → auto-advances.
        self.tour_utils.wait_for_popover()
        self.get_element("modal-view-job-edit-button").click()

        # "Application Date": set current date to satisfy waitForInput, then click Next.
        self.tour_utils.wait_for_popover()
        self.get_element("application_date_set_current").click()
        self.tour_utils.click_next()

        # "Application Status": select a value to satisfy waitForInput, then click Next.
        self.tour_utils.wait_for_popover()
        ReactSelect(self.get_element("application_status")).select_by_visible_text("Applied")
        self.tour_utils.click_next()

        # "Applied Via", "Application URL", "Application Notes": informational — Next each.
        self.tour_utils.advance_steps(3)

        # "Save the Application": click Confirm — waitForSelectorGone auto-advances to Done.
        self.tour_utils.wait_for_popover()
        self.get_element("modal-edit-job-confirm-button").click()

        # Done step: click "Continue to next tour" instead of "Done".
        # This starts Tour B (log-interview) after Tour A's cleanup completes.
        self.tour_utils.wait_for_popover()
        self.get_element("tour-start-next-btn").click()

        # ── Tour B: log-interview ────────────────────────────────────────────
        # startTour() seeds another demo job; give it time to complete seeding.
        self.tour_utils.wait_for_popover(timeout=30.0)

        # Skip Tour B immediately — endTour() must not delete the pre-existing job.
        self.tour_utils.click_skip()
        self.tour_utils.wait_for_popover_gone()

        # Both demo jobs (Tour A's and Tour B's) must be deleted; the pre-existing job
        # must remain. Poll until the DB count matches the value before either tour ran.
        self.tour_utils.poll_db_count(models.Job, self.user.id, initial_jobs)
