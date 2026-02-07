"""GIF Generator Script for Scraping Filters Demo"""

import argparse
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as ec

from demo_recorder import DemoRecorder
from tests.utils.create_data.job_scraping import (
    create_scraped_jobs,
    create_job_alert_emails,
    create_job_scraping_service_logs,
    create_scraping_filters,
)
from tests.utils.create_data.data_tables import create_geolocations


class ScrapingFilterRecorder(DemoRecorder):
    """Records the scraping filter workflow and generates a GIF"""

    def create_demo_data(self, db, users) -> None:
        """Create full demo data with old application dates (no interviews/updates)"""

        create_geolocations(db)
        filters = create_scraping_filters(db, users)
        service_logs = create_job_scraping_service_logs(db)
        emails = create_job_alert_emails(db, users, service_logs)
        create_scraped_jobs(db, emails, users, [])
        for f in filters:
            f.is_active = False
        db.commit()

        print("  Created demo data with old application dates (no interviews/updates)")

    def record(self, email: str, password: str) -> None:
        """Record the scraping filter flow"""

        print("Recording scraping filter flow...")

        # Login silently (no frame capture)
        self.login_silently(email, password)

        # Navigate to scraped jobs page
        print("  - Navigating to scraped jobs page...")
        self.driver.get(f"{self.frontend_url}/scraped-jobs")
        time.sleep(2)
        self.inject_highlighting()

        # Capture the scraped jobs page
        print("  - Capturing scraped jobs page...")
        self.capture_frames_for_duration(1.5)

        # Move to and click the Scraping Filters button
        print("  - Opening scraping filters modal...")
        self.move_to_element("scraping-filters-button", 600)
        self.click_element("scraping-filters-button")

        # Wait for the filters modal to appear
        self.wait.until(ec.presence_of_element_located((By.ID, "scraping-filters-modal")))
        self.capture_frames_for_duration(1.5)

        # Click the Add button to create a new filter
        print("  - Clicking add filter button...")
        self.move_to_element("add-scrapingFilter-button", 500)
        self.click_element("add-scrapingFilter-button")

        # Wait for the add/edit modal to appear
        print("  - Waiting for filter form modal...")
        self.wait.until(ec.presence_of_element_located((By.ID, "modal-edit-scrapingFilter")))
        time.sleep(0.5)
        self.capture_frames_for_duration(1.0)

        # Fill in Filter Type using react-select
        print("  - Selecting filter type (Company Name)...")
        type_select = self.wait.until(ec.element_to_be_clickable((By.ID, "type")))
        self.move_to_element_obj(type_select, 400)
        type_select.click()
        time.sleep(0.3)
        self.capture_frames_for_duration(0.5)

        # Type to search and select "Company Name"
        type_input = self.driver.switch_to.active_element
        type_input.send_keys("Company")
        time.sleep(0.3)
        self.capture_frames_for_duration(0.5)
        type_input.send_keys(Keys.ENTER)
        time.sleep(0.3)
        self.capture_frames_for_duration(0.5)

        # Fill in Operator using react-select
        print("  - Selecting operator (Contains)...")
        operator_select = self.wait.until(ec.element_to_be_clickable((By.ID, "operator")))
        self.move_to_element_obj(operator_select, 400)
        operator_select.click()
        time.sleep(0.3)
        self.capture_frames_for_duration(0.5)

        operator_input = self.driver.switch_to.active_element
        operator_input.send_keys("Contains")
        time.sleep(0.3)
        self.capture_frames_for_duration(0.5)
        operator_input.send_keys(Keys.ENTER)
        time.sleep(0.3)
        self.capture_frames_for_duration(0.5)

        # Fill in Value field
        print("  - Typing filter value...")
        self.move_to_element("value", 400)
        self.type_text("value", "ABC Corp", delay=0.06)
        self.capture_frames_for_duration(0.5)

        # Click confirm/save button
        print("  - Saving filter...")
        self.move_to_element("modal-edit-scrapingFilter-confirm-button", 500)
        self.click_element("modal-edit-scrapingFilter-confirm-button")

        # Wait for the modal to close and the filter to appear in the table
        print("  - Waiting for filter to be saved...")
        time.sleep(2)
        self.capture_frames_for_duration(1.5)

        # Click the newly created filter row to view it
        print("  - Opening the created filter...")
        filter_row = self.wait.until(
            ec.element_to_be_clickable((By.CSS_SELECTOR, "#scraping-filters-modal .table-row-clickable"))
        )
        rect = self.driver.execute_script(
            """
            const rect = arguments[0].getBoundingClientRect();
            return {x: rect.left + rect.width/2, y: rect.top + rect.height/2};
        """,
            filter_row,
        )
        self.driver.execute_script(f"window.moveCursorTo({rect['x']}, {rect['y']}, 500);")
        self.capture_frames_for_duration(0.6)

        self.driver.execute_script(f"window.simulateClick({rect['x']}, {rect['y']});")
        self.capture_frames_for_duration(0.3)
        filter_row.click()

        # Wait for the view modal to appear
        print("  - Viewing filter details...")
        self.wait.until(ec.presence_of_element_located((By.ID, "modal-view-scrapingFilter")))
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
    parser.add_argument("--output", default="scraping_filter_demo.gif", help="Output GIF path")
    parser.add_argument("--fps", type=int, default=10, help="Frames per second")
    args = parser.parse_args()

    recorder = ScrapingFilterRecorder(
        output_path=args.output,
        fps=args.fps,
        headless=not args.no_headless,
    )
    recorder.run()


if __name__ == "__main__":
    main()
