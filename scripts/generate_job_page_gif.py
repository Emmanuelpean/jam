"""GIF Generator Script for Job Page Demo"""

import argparse
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as ec

from demo_creator import DemoBuilder


class JobPageBuilder(DemoBuilder):
    """Records the job page workflow and generates a GIF"""

    def record(self, email: str, password: str) -> None:
        """Record the job page flow: add job, fill details, save, re-open"""

        print("Recording job page flow...")

        # Login silently (no frame capture)
        self.login_silently(email, password)

        # Navigate to jobs page
        print("  - Navigating to jobs page...")
        self.driver.get(f"{self.frontend_url}/jobs")
        time.sleep(2)
        self.inject_highlighting()

        # Capture the jobs page
        print("  - Capturing jobs page...")
        self.capture_frames_for_duration(1.5)

        # Click the Add button
        print("  - Clicking add button...")
        self.move_to_element("add-job-button", 500)
        self.click_element("add-job-button")

        # Wait for the add modal to appear
        print("  - Waiting for add modal...")
        self.wait.until(ec.presence_of_element_located((By.ID, "modal-edit-job")))
        time.sleep(0.5)
        self.capture_frames_for_duration(1.0)

        # Fill in the job title
        print("  - Typing job title...")
        self.move_to_element("title", 400)
        self.type_text("title", "Python Software Engineer", delay=0.04)
        self.capture_frames_for_duration(0.5)

        # Select a company using react-select
        print("  - Selecting company...")
        company_select = self.wait.until(ec.element_to_be_clickable((By.ID, "company_id")))
        self.move_to_element_obj(company_select, 400)
        company_select.click()
        time.sleep(0.3)
        self.capture_frames_for_duration(0.5)

        company_input = self.driver.switch_to.active_element
        company_input.send_keys(Keys.ENTER)
        time.sleep(0.3)
        self.capture_frames_for_duration(0.5)

        # Fill in the job URL
        print("  - Typing job URL...")
        self.move_to_element("url", 400)
        self.type_text("url", "https://linkedin.com/jobs/123456", delay=0.03)
        self.capture_frames_for_duration(0.5)

        # Set deadline
        print("  - Setting deadline...")
        self.move_to_element("deadline", 400)
        deadline_field = self.wait.until(ec.presence_of_element_located((By.ID, "deadline")))
        deadline_field.send_keys("2026-03-15")
        time.sleep(0.3)
        self.capture_frames_for_duration(0.5)

        # Select contacts using react-select
        print("  - Selecting contacts...")
        contacts_select = self.wait.until(ec.element_to_be_clickable((By.ID, "contacts")))
        self.move_to_element_obj(contacts_select, 400)
        contacts_select.click()
        time.sleep(0.3)
        self.capture_frames_for_duration(0.5)

        contacts_input = self.driver.switch_to.active_element
        contacts_input.send_keys(Keys.ENTER)
        time.sleep(0.3)
        self.capture_frames_for_duration(0.5)

        # Close the contacts dropdown
        contacts_input.send_keys(Keys.ESCAPE)
        time.sleep(0.2)

        # Click confirm/save button
        print("  - Saving job...")
        self.move_to_element("modal-edit-job-confirm-button", 500)
        self.click_element("modal-edit-job-confirm-button")

        # Wait for the modal to close and the entry to appear in the table
        print("  - Waiting for job to be saved...")
        time.sleep(2)
        self.capture_frames_for_duration(1.5)

        # Click the newly created row to re-open it
        print("  - Re-opening the created job...")
        row = self.wait.until(ec.element_to_be_clickable((By.CSS_SELECTOR, ".table-row-clickable")))
        rect = self.driver.execute_script(
            """
            const rect = arguments[0].getBoundingClientRect();
            return {x: rect.left + rect.width/2, y: rect.top + rect.height/2};
        """,
            row,
        )
        self.driver.execute_script(f"window.moveCursorTo({rect['x']}, {rect['y']}, 500);")
        self.capture_frames_for_duration(0.6)

        self.driver.execute_script(f"window.simulateClick({rect['x']}, {rect['y']});")
        self.capture_frames_for_duration(0.3)
        row.click()

        # Wait for the view modal to appear
        print("  - Viewing job details...")
        self.wait.until(ec.presence_of_element_located((By.ID, "modal-view-job")))
        time.sleep(1)
        self.capture_frames_for_duration(4.0)

        print(f"Captured {len(self.frames)} frames")

    def move_to_element_obj(self, element, duration_ms: int = 500) -> None:
        """Move cursor to a WebElement object with animation"""

        rect = self.driver.execute_script(
            """
            const rect = arguments[0].getBoundingClientRect();
            return {x: rect.left + rect.width/2, y: rect.top + rect.height/2};
        """,
            element,
        )

        self.driver.execute_script(f"window.moveCursorTo({rect['x']}, {rect['y']}, {duration_ms});")
        self.capture_frames_for_duration(duration_ms / 1000 + 0.1)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-headless", action="store_true", help="Show browser window (default: headless)")
    args = parser.parse_args()

    recorder = JobPageBuilder(output_name="job_page.gif", headless=not args.no_headless)
    recorder.run()


if __name__ == "__main__":
    main()
