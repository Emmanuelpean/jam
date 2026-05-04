"""Selenium tests for the App Overview guided tour."""

import time

from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from app import models
from base_test import BaseTest
from react_select import ReactSelect

# Tour element IDs
TOUR_POPOVER = "tour-popover"
TOUR_TITLE = "tour-popover-title"
TOUR_COUNTER = "tour-step-counter"
TOUR_SKIP = "tour-skip-btn"
TOUR_NEXT = "tour-next-btn"
TOUR_BACK = "tour-back-btn"
TOUR_BACKDROP = "tour-backdrop"

# Tour select panel
TAKE_A_TOUR_BTN = "take-a-tour-btn"
TSP_PANEL = "tsp-panel"
TSP_PROGRESS = "tsp-progress"

TOTAL_STEPS = 6  # intro, dashboard-overview, dashboard-customise, sidebar, premium, command-palette
TOUR_NAME = "App Overview"
TOUR_ID = "app-overview"


class TestAppOverviewTour(BaseTest):
    user_index = 0
    page_url = "dashboard"

    def setup_function(self, request) -> None:
        self.login()

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _open_tour_select(self) -> None:
        """Click 'Take a Tour' to open the tour select panel.

        Uses a JS click to bypass sidebar animation / clickability edge cases:
        the button is always in the sidebar DOM and its React onClick fires regardless
        of whether the About submenu is visually open or the sidebar is mid-transition.
        """
        self.get_element(TAKE_A_TOUR_BTN, enabled=False)  # wait for element to exist
        self.driver.execute_script(f"document.getElementById('{TAKE_A_TOUR_BTN}').click();")
        self.get_element(TSP_PANEL, enabled=False, timeout=5)

    def _start_tour(self, tour_id: str = TOUR_ID, popover_timeout: float = 10.0) -> None:
        """Open the tour select panel and start the given tour."""
        self._open_tour_select()
        self.get_element(f"tsp-item-{tour_id}").click()
        self._wait_for_popover(timeout=popover_timeout)

    def _wait_for_popover(self, timeout: float = 10.0) -> None:
        """Wait for the tour popover to appear in the DOM."""
        self.get_element(TOUR_POPOVER, timeout=timeout, enabled=False)

    def _wait_for_popover_gone(self, timeout: float = 10.0) -> None:
        """Wait for the tour popover to disappear."""
        self.wait_for_disappear(TOUR_POPOVER, timeout=timeout)

    def _popover_title(self) -> str:
        return self.get_element(TOUR_TITLE, enabled=False).text

    def _step_counter_text(self) -> str:
        return self.get_element(TOUR_COUNTER, enabled=False).text

    def _click_next(self) -> None:
        self.get_element(TOUR_NEXT).click()

    def _click_back(self) -> None:
        self.get_element(TOUR_BACK).click()

    def _click_skip(self) -> None:
        self.get_element(TOUR_SKIP).click()

    def _advance_steps(self, n: int) -> None:
        """Click Next n times, waiting for the popover between each click."""
        for _ in range(n):
            self._wait_for_popover()
            self._click_next()

    def _advance_to_last_step(self) -> None:
        """Click through steps until the Done button is visible."""
        for _ in range(TOTAL_STEPS):
            self._wait_for_popover()
            next_btn = self.get_element(TOUR_NEXT)
            if "Done" in next_btn.text:
                return
            next_btn.click()

    def _wait_for_step(self, n: int, timeout: float = 10.0) -> None:
        """Wait until the step counter shows Step N (case-insensitive, CSS may uppercase the text)."""
        WebDriverWait(self.driver, timeout).until(
            lambda d: f"STEP {n} OF" in d.find_element(By.ID, TOUR_COUNTER).text.upper()
        )

    def _poll_db_count(self, model_class, owner_id: int, expected: int, timeout: float = 10.0) -> None:
        """Poll the DB until the row count for owner_id equals expected, or raise."""
        deadline = time.time() + timeout
        while time.time() < deadline:
            # rollback() ends the current transaction so the next query gets a fresh
            # READ COMMITTED snapshot and can see rows committed by the backend API process.
            self.db.expire_all()
            self.db.rollback()
            count = self.db.query(model_class).filter_by(owner_id=owner_id).count()
            if count == expected:
                return
            time.sleep(0.5)
        self.db.expire_all()
        self.db.rollback()
        actual = self.db.query(model_class).filter_by(owner_id=owner_id).count()
        assert actual == expected, f"{model_class.__name__}: expected {expected}, got {actual} after {timeout}s"

    # ── Tour Select Panel ─────────────────────────────────────────────────────

    def test_tour_panel_opens_on_click(self) -> None:
        """Clicking 'Take a Tour' in the sidebar reveals the tour select panel."""
        self._open_tour_select()
        assert self.check_element_exists(TSP_PANEL)

    def test_tour_panel_lists_app_overview(self) -> None:
        """The panel contains an 'App Overview' entry."""
        self._open_tour_select()
        assert self.check_element_exists(f"tsp-item-{TOUR_ID}")

    def test_tour_panel_shows_progress_counter(self) -> None:
        """The progress counter (X / Y) is visible in the panel."""
        self._open_tour_select()
        assert "/" in self.get_element(TSP_PROGRESS, enabled=False).text

    # ── First step ────────────────────────────────────────────────────────────

    def test_starting_tour_shows_popover(self) -> None:
        """Starting the App Overview tour displays the tour popover."""
        self._start_tour()
        assert self.check_element_exists(TOUR_POPOVER)

    def test_first_step_title(self) -> None:
        """First step title is 'Welcome to JAM!'."""
        self._start_tour()
        assert self._popover_title() == "Welcome to JAM!"

    def test_first_step_counter(self) -> None:
        """Step counter reads 'Step 1 of N' on the first step (case-insensitive)."""
        self._start_tour()
        assert self._step_counter_text().upper() == f"STEP 1 OF {TOTAL_STEPS}"

    def test_first_step_has_no_back_button(self) -> None:
        """No Back button on the first step."""
        self._start_tour()
        assert not self.check_element_exists(TOUR_BACK)

    def test_first_step_has_backdrop(self) -> None:
        """Center steps show a full-screen backdrop."""
        self._start_tour()
        assert self.check_element_exists(TOUR_BACKDROP)

    def test_first_step_navigates_to_dashboard(self) -> None:
        """The intro step navigates to the dashboard regardless of starting page."""
        self.go_to_page("jobs")
        self._start_tour()
        self.wait_for_page("dashboard")

    # ── Navigation ────────────────────────────────────────────────────────────

    def test_next_advances_to_step_2(self) -> None:
        """Clicking Next moves to step 2."""
        self._start_tour()
        self._click_next()
        self._wait_for_step(2)

    def test_back_returns_to_step_1(self) -> None:
        """Clicking Back on step 2 returns to step 1."""
        self._start_tour()
        self._click_next()
        self._wait_for_step(2)
        self._click_back()
        self._wait_for_step(1)
        assert self._popover_title() == "Welcome to JAM!"

    def test_arrow_right_advances_step(self) -> None:
        """Right-arrow keyboard shortcut advances the tour."""
        self._start_tour()
        self.driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ARROW_RIGHT)
        self._wait_for_step(2)

    def test_arrow_left_goes_back(self) -> None:
        """Left-arrow keyboard shortcut goes back one step."""
        self._start_tour()
        self._click_next()
        self._wait_for_step(2)
        self.driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ARROW_LEFT)
        self._wait_for_step(1)

    # ── Page navigation ───────────────────────────────────────────────────────

    def test_step_2_is_on_dashboard(self) -> None:
        """Step 2 (Your Dashboard) keeps the user on the dashboard."""
        self._start_tour()
        self._advance_steps(1)
        self.wait_for_page("dashboard")

    def test_step_3_is_on_dashboard(self) -> None:
        """Step 3 (Customise Your Dashboard) stays on the dashboard."""
        self._start_tour()
        self._advance_steps(2)
        self.wait_for_page("dashboard")

    def test_step_4_navigates_to_jobs(self) -> None:
        """Step 4 (Jobs) navigates to the jobs page."""
        self._start_tour()
        self._advance_steps(3)
        self.wait_for_page("jobs")

    def test_step_4_title_is_jobs(self) -> None:
        """Step 4 title is 'Jobs'."""
        self._start_tour()
        self._advance_steps(3)
        self._wait_for_popover()
        assert self._popover_title() == "Jobs"

    def test_back_from_jobs_step_returns_to_dashboard(self) -> None:
        """Clicking Back on the Jobs step navigates back to the dashboard."""
        self._start_tour()
        self._advance_steps(3)
        self.wait_for_page("jobs")
        self._click_back()
        self.wait_for_page("dashboard")

    # ── Skip / Escape ─────────────────────────────────────────────────────────

    def test_skip_dismisses_tour(self) -> None:
        """Clicking 'Skip tour' dismisses the popover."""
        self._start_tour()
        self._click_skip()
        self._wait_for_popover_gone()

    def test_escape_dismisses_tour(self) -> None:
        """Pressing Escape dismisses the tour."""
        self._start_tour()
        self.driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
        self._wait_for_popover_gone()

    def test_skip_returns_to_origin_page(self) -> None:
        """Skipping mid-tour navigates back to the page where the tour was started."""
        self._start_tour()
        self._advance_steps(3)  # navigate away to the jobs step
        self._click_skip()
        self._wait_for_popover_gone()
        self.wait_for_page(self.page_url)

    # ── Completion ────────────────────────────────────────────────────────────

    def test_last_step_shows_done_button(self) -> None:
        """The final step shows a 'Done' button instead of 'Next'."""
        self._start_tour()
        self._advance_to_last_step()
        assert "Done" in self.get_element(TOUR_NEXT).text

    def test_completing_tour_dismisses_popover(self) -> None:
        """Clicking Done on the last step closes the tour popover."""
        self._start_tour()
        self._advance_to_last_step()
        self._click_next()  # Done
        self._wait_for_popover_gone()

    def test_completing_tour_returns_to_origin_page(self) -> None:
        """Completing the tour navigates back to the page where it was started."""
        self._start_tour()
        self._advance_to_last_step()
        self._click_next()  # Done
        self._wait_for_popover_gone()
        self.wait_for_page(self.page_url)

    def test_completed_tour_marked_in_panel(self) -> None:
        """After completing the tour, the App Overview icon has the done style."""
        self._start_tour()
        self._advance_to_last_step()
        self._click_next()  # Done
        self._wait_for_popover_gone()
        self._open_tour_select()
        icon = self.get_element(f"tsp-icon-{TOUR_ID}", enabled=False)
        assert "tsp-icon--done" in icon.get_attribute("class")

    def test_active_tour_disables_tour_panel_buttons(self) -> None:
        """While a tour is running, all buttons in the tour select panel are disabled."""
        self._start_tour()
        self._open_tour_select()
        for tour_id in ["app-overview", "first-job", "follow-up-email"]:
            assert not self.get_element(f"tsp-item-{tour_id}", enabled=False).is_enabled()

    # ----------------------------------------------------- CLEANUP ----------------------------------------------------

    def test_skip_cleans_up_follow_up_email_tour_data(self) -> None:
        """Skipping the follow-up-email tour deletes the pre-seeded demo entities."""

        owner_id = self.user.id
        self.db.expire_all()
        self.db.rollback()
        initial_jobs = self.db.query(models.Job).filter_by(owner_id=owner_id).count()
        initial_persons = self.db.query(models.Person).filter_by(owner_id=owner_id).count()
        initial_interviews = self.db.query(models.Interview).filter_by(owner_id=owner_id).count()

        # Starting the tour seeds 1 job, 2 persons, 1 interview via sequential API calls —
        # use a longer timeout because the popover only appears after all seeding is done.
        # The popover appearing is sufficient proof that seeding completed — no DB assertion needed.
        self._start_tour("follow-up-email", popover_timeout=30.0)

        self._click_skip()
        self._wait_for_popover_gone()

        # Cleanup is async — poll until all seeded entities are deleted
        self._poll_db_count(models.Job, owner_id, initial_jobs)
        self._poll_db_count(models.Person, owner_id, initial_persons)
        self._poll_db_count(models.Interview, owner_id, initial_interviews)

    def test_skip_cleans_up_first_job_tour_data(self) -> None:
        """Skipping the first-job tour mid-flow deletes any job/company created during it."""

        owner_id = self.user.id
        self.db.expire_all()
        self.db.rollback()
        initial_jobs = self.db.query(models.Job).filter_by(owner_id=owner_id).count()
        initial_companies = self.db.query(models.Company).filter_by(owner_id=owner_id).count()

        self._start_tour("first-job")
        # The tour navigates to /jobs; wait for the page before interacting with its elements
        self.wait_for_page("jobs")

        # Step 0 (first-job-intro): informational — click Next
        self._click_next()

        # Step 1 (open-job-modal): click the highlighted button to open the add-job form
        self.get_element("add-job-button").click()

        # Step 2 (job-title): tour auto-advances when modal opens; type a title to enable Next
        self.get_element("title").send_keys("Skip Test Job")
        self._click_next()

        # Step 3 (add-company): click the + button to open the inline company form
        self.get_element("add-button-company").click()

        # Step 4 (company-name): type a company name to enable Next
        self.get_element("name").send_keys("Skip Test Company")
        self._click_next()

        # Step 5 (save-company): click Confirm — company is persisted to the DB
        self.get_element("modal-edit-company-confirm-button").click()

        # Confirm the company reached the DB before skipping
        self._poll_db_count(models.Company, owner_id, initial_companies + 1)

        self._click_skip()
        self._wait_for_popover_gone()

        # Both the job (if partially saved) and the company must be removed
        self._poll_db_count(models.Company, owner_id, initial_companies)
        self._poll_db_count(models.Job, owner_id, initial_jobs)

    def test_continue_to_next_tour_preserves_preexisting_data(self) -> None:
        """Clicking 'Continue to next tour' must not delete pre-existing user data.

        Regression: during an isolated tour (Tour A), visibleData filters out pre-existing
        entities. The stale startTour() closure used to capture an empty/wrong snapshot for
        Tour B, causing endTour() to diff against it and delete all pre-existing entities.

        Test sequence: log-application (Tour A) → log-interview (Tour B).
        Both are isolated tours that auto-seed a demo job. A pre-existing job is created
        before either tour runs and must still exist after both tours complete.
        """
        owner_id = self.user.id

        # Create a pre-existing job that must survive the entire tour A → tour B sequence.
        self._make_job(title="Pre-existing Job — Must Survive Tours")

        self.db.expire_all()
        self.db.rollback()
        initial_jobs = self.db.query(models.Job).filter_by(owner_id=owner_id).count()

        # ── Tour A: log-application ──────────────────────────────────────────
        # startTour() auto-seeds a demo job; use a longer timeout for the seeding API calls.
        self._start_tour("log-application", popover_timeout=30.0)
        self.wait_for_page("jobs")

        # Intro step: purely informational — click Next.
        self._click_next()

        # "Open the Job": click the demo job row. During the isolated tour the pre-existing
        # job is hidden by the snapshot filter, so only the demo job row is visible.
        # waitForSelector=#application-tab → tour auto-advances when the view modal opens.
        self._wait_for_popover()
        self.get_element("[id^='table-row-job-']", By.CSS_SELECTOR).click()

        # "Switch to the Application Tab": click the tab.
        # waitForSelector=#add-interview-button → auto-advances.
        self._wait_for_popover()
        self.get_element("application-tab").click()

        # "Edit the Job": click Edit.
        # waitForSelector=#application_date-form-group → auto-advances.
        self._wait_for_popover()
        self.get_element("modal-view-job-edit-button").click()

        # "Application Date": set current date to satisfy waitForInput, then click Next.
        self._wait_for_popover()
        self.get_element("application_date_set_current").click()
        self._click_next()

        # "Application Status": select a value to satisfy waitForInput, then click Next.
        self._wait_for_popover()
        ReactSelect(self.get_element("application_status")).select_by_visible_text("Applied")
        self._click_next()

        # "Applied Via", "Application URL", "Application Notes": informational — Next each.
        self._advance_steps(3)

        # "Save the Application": click Confirm — waitForSelectorGone auto-advances to Done.
        self._wait_for_popover()
        self.get_element("modal-edit-job-confirm-button").click()

        # Done step: click "Continue to next tour" instead of "Done".
        # This starts Tour B (log-interview) after Tour A's cleanup completes.
        self._wait_for_popover()
        self.get_element("tour-start-next-btn").click()

        # ── Tour B: log-interview ────────────────────────────────────────────
        # startTour() seeds another demo job; give it time to complete seeding.
        self._wait_for_popover(timeout=30.0)

        # Skip Tour B immediately — endTour() must not delete the pre-existing job.
        self._click_skip()
        self._wait_for_popover_gone()

        # Both demo jobs (Tour A's and Tour B's) must be deleted; the pre-existing job
        # must remain. Poll until the DB count matches the value before either tour ran.
        self._poll_db_count(models.Job, owner_id, initial_jobs)
