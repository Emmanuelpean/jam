"""GIF Generator Script for Scraped Jobs (Job Alerts) Page Demo"""

import argparse
import time

from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec

from demo_creator import DemoBuilder


class ScrapedJobsBuilder(DemoBuilder):
    """Records the scraped jobs page workflow and generates a GIF"""

    def record(self, email: str, password: str) -> None:
        """Record the job alerts flow: view page, open a job, import via right-click"""

        print("Recording scraped jobs flow...")

        self.login_silently(email, password)

        print("  - Navigating to job alerts page...")
        self.driver.get(f"{self.frontend_url}/job-alerts/jobs")
        time.sleep(2)
        self.inject_highlighting()

        print("  - Capturing job alerts page...")
        self.capture_frames_for_duration(2.0)

        # Wait for real data rows (not skeleton rows) then click the first one
        print("  - Opening first job alert...")
        rows = self.wait.until(
            ec.presence_of_all_elements_located((By.CSS_SELECTOR, "[id^='table-row-scrapedJob-']"))
        )
        first_row = rows[0]
        self._move_to_element_obj(first_row, 500)
        self._click_element_obj(first_row)

        # Clicking a row opens the import modal (which also shows the AI rating)
        print("  - Viewing AI-rated job alert...")
        self.wait.until(ec.presence_of_element_located((By.ID, "modal-import-scrapedJob")))
        time.sleep(0.5)
        self.capture_frames_for_duration(3.5)

        # Close this modal and right-click a different row to show the context menu
        print("  - Closing modal...")
        self.move_to_element("modal-import-scrapedJob-cancel-button", 400)
        self.wait.until(ec.element_to_be_clickable((By.ID, "modal-import-scrapedJob-cancel-button"))).click()
        time.sleep(0.5)
        self.capture_frames_for_duration(0.8)

        # Right-click the second row to show context menu
        print("  - Right-clicking second job alert...")
        rows = self.driver.find_elements(By.CSS_SELECTOR, "[id^='table-row-scrapedJob-']")
        second_row = rows[1]
        self._move_to_element_obj(second_row, 500)
        self.capture_frames_for_duration(0.3)
        self._right_click_element_obj(second_row)
        time.sleep(0.3)
        self.capture_frames_for_duration(0.8)

        # Click Import from the context menu
        print("  - Selecting Import from context menu...")
        self.move_to_element("context-menu-import", 300)
        self.click_element("context-menu-import")
        time.sleep(0.5)
        self.wait.until(ec.presence_of_element_located((By.ID, "modal-import-scrapedJob")))
        time.sleep(0.5)
        self.capture_frames_for_duration(1.5)

        # Click the Import button to import the job
        print("  - Importing job...")
        self.move_to_element("modal-import-scrapedJob-import-button", 400)
        self.click_element("modal-import-scrapedJob-import-button")
        time.sleep(1.5)
        self.capture_frames_for_duration(2.0)

        print(f"Captured {len(self.frames)} frames")

    def _move_to_element_obj(self, element, duration_ms: int = 500) -> None:
        """Animate the demo cursor to a WebElement"""

        rect = self.driver.execute_script(
            "const r = arguments[0].getBoundingClientRect();"
            "return {x: r.left + r.width/2, y: r.top + r.height/2};",
            element,
        )
        self.driver.execute_script(f"window.moveCursorTo({rect['x']}, {rect['y']}, {duration_ms});")
        self.capture_frames_for_duration(duration_ms / 1000 + 0.1)

    def _click_element_obj(self, element) -> None:
        """Click a WebElement with visual cursor effect"""

        rect = self.driver.execute_script(
            "const r = arguments[0].getBoundingClientRect();"
            "return {x: r.left + r.width/2, y: r.top + r.height/2};",
            element,
        )
        self.driver.execute_script(f"window.simulateClick({rect['x']}, {rect['y']});")
        self.capture_frames_for_duration(0.3)
        element.click()
        time.sleep(0.2)
        self.capture_frames_for_duration(0.3)

    def _right_click_element_obj(self, element) -> None:
        """Right-click a WebElement with visual cursor effect"""

        rect = self.driver.execute_script(
            "const r = arguments[0].getBoundingClientRect();"
            "return {x: r.left + r.width/2, y: r.top + r.height/2};",
            element,
        )
        self.driver.execute_script(f"window.simulateClick({rect['x']}, {rect['y']});")
        self.capture_frames_for_duration(0.2)
        ActionChains(self.driver).context_click(element).perform()
        time.sleep(0.2)
        self.capture_frames_for_duration(0.3)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-headless", action="store_true", help="Show browser window (default: headless)")
    args = parser.parse_args()

    recorder = ScrapedJobsBuilder(output_name="scraped_jobs.gif", headless=not args.no_headless)
    recorder.run()
