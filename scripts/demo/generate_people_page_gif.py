"""GIF Generator Script for People/Contacts Page Demo"""

import argparse
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as ec

from demo_creator import DemoBuilder


class PeoplePageBuilder(DemoBuilder):
    """Records the contacts page workflow and generates a GIF"""

    def record(self, email: str, password: str) -> None:
        """Record the contacts page flow: add contact, fill details, save, re-open"""

        print("Recording people page flow...")

        # Login silently (no frame capture)
        self.login_silently(email, password)

        # Navigate to contacts page
        print("  - Navigating to contacts page...")
        self.driver.get(f"{self.frontend_url}/contacts")
        time.sleep(2)
        self.inject_highlighting()

        # Capture the contacts page
        print("  - Capturing contacts page...")
        self.capture_frames_for_duration(1.5)

        # Click the Add button
        print("  - Clicking add button...")
        self.move_to_element("add-person-button", 500)
        self.click_element("add-person-button")

        # Wait for the add modal to appear
        print("  - Waiting for add modal...")
        self.wait.until(ec.presence_of_element_located((By.ID, "modal-edit-person")))
        time.sleep(0.5)
        self.capture_frames_for_duration(1.0)

        # Fill in the first name
        print("  - Typing first name...")
        self.move_to_element("first_name", 400)
        self.type_text("first_name", "Jane", delay=0.07)
        self.capture_frames_for_duration(0.3)

        # Fill in the last name
        print("  - Typing last name...")
        self.move_to_element("last_name", 400)
        self.type_text("last_name", "Doe", delay=0.07)
        self.capture_frames_for_duration(0.3)

        # Select a company using react-select
        print("  - Selecting company...")
        company_select = self.wait.until(ec.element_to_be_clickable((By.ID, "company_id")))
        self.move_to_element_obj(company_select, 400)
        company_select.click()
        time.sleep(0.3)
        self.capture_frames_for_duration(0.5)

        company_input = self.driver.switch_to.active_element
        company_input.send_keys(Keys.ARROW_DOWN)
        time.sleep(0.2)
        self.capture_frames_for_duration(0.4)
        company_input.send_keys(Keys.ENTER)
        time.sleep(0.3)
        self.capture_frames_for_duration(0.5)

        # Fill in the role
        print("  - Typing role...")
        self.move_to_element("role", 400)
        self.type_text("role", "Team Leader", delay=0.05)
        self.capture_frames_for_duration(0.3)

        # Fill in the email
        print("  - Typing email...")
        self.move_to_element("email", 400)
        self.type_text("email", "jane.doe@company.com", delay=0.03)
        self.capture_frames_for_duration(0.3)

        # Fill in the LinkedIn URL
        print("  - Typing LinkedIn URL...")
        self.move_to_element("linkedin_url", 400)
        self.type_text("linkedin_url", "https://linkedin.com/in/janedoe", delay=0.03)
        self.capture_frames_for_duration(0.5)

        # Click confirm/save button
        print("  - Saving contact...")
        self.move_to_element("modal-edit-person-confirm-button", 500)
        self.click_element("modal-edit-person-confirm-button")

        # Wait for the modal to close and the entry to appear in the table
        print("  - Waiting for contact to be saved...")
        time.sleep(2)
        self.capture_frames_for_duration(1.5)

        # Click the newly created row to re-open it
        print("  - Re-opening the created contact...")
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
        print("  - Viewing contact details...")
        self.wait.until(ec.presence_of_element_located((By.ID, "modal-view-person")))
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


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-headless", action="store_true", help="Show browser window (default: headless)")
    args = parser.parse_args()

    recorder = PeoplePageBuilder(output_name="people_page.gif", headless=not args.no_headless)
    recorder.run()
