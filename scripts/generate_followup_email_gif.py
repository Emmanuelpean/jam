"""GIF Generator Script for Follow-Up Email Demo"""

import argparse
import time

from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as ec

from demo_creator import DemoBuilder


class FollowUpEmailBuilder(DemoBuilder):
    """Records the follow-up email workflow and generates a GIF"""

    def record(self, email: str, password: str) -> None:
        """Record the follow-up email flow"""

        print("Recording follow-up email flow...")

        # Login silently (no frame capture)
        self.login_silently(email, password)

        # Navigate to dashboard
        print("  - Navigating to dashboard...")
        self.driver.get(f"{self.frontend_url}/dashboard")
        time.sleep(2)
        self.inject_highlighting()

        # Start recording - capture dashboard
        print("  - Capturing dashboard...")
        self.capture_frames_for_duration(1)

        # Move cursor to first job in Needs Chase table and right-click
        print("  - Right-clicking job row 1 in Needs Chase table...")
        self.move_to_element("table-row-job-13", 600)
        self.right_click_element("table-row-job-13")

        # Move to "Follow-up Email" context menu item and click
        print("  - Clicking Follow-up Email menu item...")
        self.move_to_element("context-menu-followup", 400)
        self.click_element("context-menu-followup")

        # Wait for follow-up modal and pause to show content
        print("  - Waiting for follow-up modal...")
        self.wait.until(ec.presence_of_element_located((By.ID, "follow-up-modal")))
        time.sleep(1)
        self.capture_frames_for_duration(1.0)

        # Open contact dropdown to show options
        print("  - Opening contact dropdown...")
        self.move_to_element("contactId", 400)
        self.click_element("contactId")
        time.sleep(0.5)
        self.capture_frames_for_duration(1.0)

        # Close dropdown by pressing Escape
        print("  - Closing contact dropdown...")
        ActionChains(self.driver).send_keys(Keys.ESCAPE).perform()
        time.sleep(0.3)
        self.capture_frames_for_duration(0.5)

        # Move to Send Email button and click
        print("  - Clicking Send Email button...")
        self.move_to_element("send-btn", 500)
        self.click_element("send-btn")

        # Wait for confirmation modal
        print("  - Waiting for confirmation modal...")
        self.wait.until(ec.presence_of_element_located((By.ID, "confirm-alert-modal")))
        time.sleep(0.5)
        self.capture_frames_for_duration(1.0)

        # Move to Yes/Confirm button and click
        print("  - Clicking confirm button...")
        self.move_to_element("confirm-alert-modal-confirm-button", 400)
        self.click_element("confirm-alert-modal-confirm-button")

        # Wait for toast notification and capture
        print("  - Waiting for toast notification...")
        time.sleep(1)
        self.capture_frames_for_duration(2.0)

        print(f"Captured {len(self.frames)} frames")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-headless", action="store_true", help="Show browser window (default: headless)")
    args = parser.parse_args()

    recorder = FollowUpEmailBuilder(headless=not args.no_headless)
    recorder.run()


if __name__ == "__main__":
    main()
