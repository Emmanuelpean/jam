"""
GIF Generator Script for Follow-Up Email Demo

This script generates an animated GIF demonstrating the follow-up email workflow.
It reuses the DemoRecorder infrastructure from demo_recorder.py and follows
the test_send_email test pattern from frontend/tests/test_followup_email.py.

Usage:
    python scripts/generate_followup_email_gif.py [--output OUTPUT_PATH] [--fps FPS] [--no-headless]

Requirements:
    pip install -r scripts/requirements.txt
"""

import argparse
import copy
import datetime as dt
import time

from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as ec

from demo_recorder import DemoRecorder
from tests.utils.create_data.data_tables import (
    create_geolocations,
    create_keywords,
    create_aggregators,
    create_locations,
    create_companies,
    create_people,
    create_files,
    create_jobs,
)
from tests.utils.test_data import data_tables


class FollowUpEmailRecorder(DemoRecorder):
    """Records the follow-up email workflow and generates a GIF"""

    def create_demo_data(self, db, users) -> None:
        """Create full demo data with old application dates (no interviews/updates)"""

        create_geolocations(db)
        keywords = create_keywords(db, users)
        aggregators = create_aggregators(db, users)
        locations = create_locations(db, users)
        companies = create_companies(db, users)
        people = create_people(db, users, companies)
        files = create_files(db, users)

        # Deep-copy job data and set all application dates to 2+ months ago
        job_data = copy.deepcopy(data_tables.JOB_DATA)
        old_date = dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=75)
        for job in job_data:
            if job.get("application_date"):
                job["application_date"] = old_date.strftime("%Y-%m-%dT%H:%M:%S%z")

        # Create jobs with old dates - NO interviews or updates
        create_jobs(db, keywords, people, users, companies, locations, aggregators, files, job_data=job_data)

        print("  Created demo data with old application dates (no interviews/updates)")

    def get_chrome_prefs(self) -> dict:
        """Add mailto handler exclusion to base prefs"""

        prefs = super().get_chrome_prefs()
        prefs["protocol_handler"] = {"excluded_schemes": {"mailto": True}}
        return prefs

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

    recorder = FollowUpEmailRecorder(headless=not args.no_headless)
    recorder.run()


if __name__ == "__main__":
    main()
