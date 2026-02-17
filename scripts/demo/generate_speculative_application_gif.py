"""GIF Generator Script for Speculative Applications Demo"""

import argparse
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as ec

from demo_creator import DemoBuilder


class SpeculativeApplicationBuilder(DemoBuilder):
    """Records the speculative application workflow and generates a GIF"""

    def record(self, email: str, password: str) -> None:
        """Record the speculative application flow"""

        print("Recording speculative application flow...")

        # Login silently (no frame capture)
        self.login_silently(email, password)

        # Navigate to speculative applications page
        print("  - Navigating to speculative applications page...")
        self.driver.get(f"{self.frontend_url}/speculative-applications")
        time.sleep(2)
        self.inject_highlighting()

        # Capture the page
        print("  - Capturing speculative applications page...")
        self.capture_frames_for_duration(1.5)

        # Click the Add button
        print("  - Clicking add button...")
        self.move_to_element("add-speculativeApplication-button", 500)
        self.click_element("add-speculativeApplication-button")

        # Wait for the add modal to appear
        print("  - Waiting for form modal...")
        self.wait.until(ec.presence_of_element_located((By.ID, "modal-edit-speculativeApplication")))
        time.sleep(0.5)
        self.capture_frames_for_duration(1.0)

        print("  - Setting time...")
        clock_icon = self.wait.until(ec.presence_of_element_located((By.ID, "date_set_current")))
        self.move_to_element_obj(clock_icon, 400)
        clock_icon.click()
        time.sleep(0.3)
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

        # Fill in contact email
        print("  - Typing contact email...")
        self.move_to_element("contact_email", 400)
        self.type_text("contact_email", "careers@example.com", delay=0.04)
        self.capture_frames_for_duration(0.5)

        # Fill in note
        print("  - Typing note...")
        self.move_to_element("note", 400)
        self.type_text("note", "Interested in software engineering roles.", delay=0.04)
        self.capture_frames_for_duration(0.5)

        # Click confirm/save button
        print("  - Saving speculative application...")
        self.move_to_element("modal-edit-speculativeApplication-confirm-button", 500)
        self.click_element("modal-edit-speculativeApplication-confirm-button")

        # Wait for the modal to close and the entry to appear in the table
        print("  - Waiting for application to be saved...")
        time.sleep(2)
        self.capture_frames_for_duration(1.5)

        # Click the newly created row to re-open it
        print("  - Re-opening the created application...")
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
        print("  - Viewing application details...")
        self.wait.until(ec.presence_of_element_located((By.ID, "modal-view-speculativeApplication")))
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

    recorder = SpeculativeApplicationBuilder(output_name="speculative_application.gif", headless=not args.no_headless)
    recorder.run()


if __name__ == "__main__":
    main()
