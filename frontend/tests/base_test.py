"""Re-exports from conftest for IDE import resolution.

conftest.py is treated as a special pytest file by IDEs and excluded from
their module index. Import from this module instead in test subfolders.
"""

import json
import os
import uuid
import re
import time
from datetime import datetime, timezone, timedelta
from typing import Generator

import pytest
import requests
from selenium import webdriver
from selenium.common import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait

from app import models
from app.config import settings
from app.core.oauth2 import create_access_token
from select_utils import Select
from selenium_utils import SeleniumUtils


class BaseUtils(SeleniumUtils):
    """Base class for selenium utilities"""

    driver: WebDriver = None
    wait: WebDriverWait = None
    frontend_base_url: str = ""
    backend_base_url: str = ""
    db = None
    client = None

    def _init(self, driver: WebDriver, frontend_base_url: str, backend_base_url: str, db, client) -> None:
        self.driver = driver
        self.wait = WebDriverWait(self.driver, 10)
        self.frontend_base_url = frontend_base_url
        self.backend_base_url = backend_base_url
        self.db = db
        self.client = client

    def go_to_page(self, page: str) -> None:
        """Helper method to go to a specific page"""

        self.go_to_url(f"{self.frontend_base_url}/{page}")

    def wait_for_page(self, page: str, timeout=None) -> None:
        """Wait for the dashboard to load"""

        self.wait_for_url(f"{self.frontend_base_url}/{page}", timeout=timeout)

    # ----------------------------------------------------- EMAILS -----------------------------------------------------

    def get_verification_token_from_db(self, email: str) -> str:
        """Helper method to get verification token from database
        :param email: Email of the user to get the token for"""

        user = self.db.query(models.User).filter(models.User.email == email).first()
        token = user.verification_token
        assert token is not None, "Verification token not found in database"
        return token

    def get_verification_link_from_email(self, email: str) -> str:
        """Helper method to get verification link from test email endpoint"""

        response = requests.get(f"{self.backend_base_url}/test/emails/verification-link/{email}")
        assert response.status_code == 200, f"Failed to get verification link: {response.text}"
        return response.json()["verification_url"]

    def get_reset_link_from_email(self, email: str) -> str:
        """Helper method to get password reset link from test email endpoint"""

        response = requests.get(f"{self.backend_base_url}/test/emails/reset-link/{email}")
        assert response.status_code == 200, f"Failed to get reset link: {response.text}"
        return response.json()["reset_url"]

    def clear_test_emails(self) -> None:
        """Helper method to clear all test emails"""

        response = requests.delete(f"{self.backend_base_url}/test/emails/emails")
        assert response.status_code == 200, "Failed to clear test emails"

    # ---------------------------------------------------- ELEMENTS ----------------------------------------------------

    def wait_for_delete_modal(self) -> WebElement:
        """Wait for the delete modal to appear"""

        return self.get_element("delete-alert-modal")

    @property
    def toast(self) -> WebElement:
        """Get the toast modal on the modal"""

        return self.get_element("toast")

    def assert_toast_message(self, error_message: str) -> None:
        """Assert that the given error message is displayed on the page"""

        element = self.toast
        assert error_message in element.text, f"Message not found: {error_message}"
        element.click()  # Dismiss toast

    def wait_for_windows(self, n: int) -> None:
        """Wait for the given number of browser windows to be present"""

        self.wait.until(ec.number_of_windows_to_be(n))

    def switch_to_window(self, index: int) -> None:
        """Switch to the browser window with the given index"""

        self.driver.switch_to.window(self.driver.window_handles[index])

    def close_modal(self):
        """Close the modal"""

        self.get_element("modal-close-btn").click()


class DataModalUtils(BaseUtils):
    """Base class for testing data modals"""

    def __init__(self, entry_type: str, **kwargs):
        self._init(**kwargs)
        self.entry_type = entry_type

    # -------------------------------------------- INLINE ADD BUTTONS --------------------------------------------

    @property
    def add_company_button(self) -> WebElement:
        """+ button that opens the inline company form inside this modal."""
        return self.get_element("add-button-company")

    @property
    def add_contact_button(self) -> WebElement:
        """+ button that opens the inline person/contact form inside this modal."""
        return self.get_element("add-button-contact")

    @property
    def add_keyword_button(self) -> WebElement:
        """+ button that opens the inline keyword form inside this modal."""
        return self.get_element("add-button-keyword")

    # ------------------------------------------------ HELPER FUNCTIONS ------------------------------------------------

    def wait_for_view_modal_close(self) -> None:
        """Wait for the view modal to close"""

        self._wait_for_modal_close(f"modal-view-{self.entry_type}")

    def wait_for_edit_modal_close(self) -> None:
        """Wait for the view modal to close"""

        self._wait_for_modal_close(f"modal-edit-{self.entry_type}")

    def wait_for_view_modal(self) -> WebElement:
        """Wait for the view modal to appear"""

        return self.get_element(f"modal-view-{self.entry_type}")

    def wait_for_edit_modal(self) -> WebElement:
        """Wait for the edit modal to appear"""

        return self.get_element(f"modal-edit-{self.entry_type}")

    def wait_for_import_modal(self) -> WebElement:
        """Wait for the import modal to close"""

        return self.get_element(f"modal-import-{self.entry_type}")

    def wait_for_import_modal_close(self) -> None:
        """Wait for the import modal to close"""

        self._wait_for_modal_close(f"modal-import-{self.entry_type}")

    def confirm_button(self, mode: str) -> WebElement:
        """Get the confirm button on the modal"""

        return self.get_element(f"modal-{mode}-{self.entry_type}-confirm-button")

    def assert_confirm_button_disabled(self, mode: str) -> None:
        """Wait until the confirm button becomes disabled."""

        WebDriverWait(self.driver, 5).until(
            lambda d: not d.find_element(By.ID, f"modal-{mode}-{self.entry_type}-confirm-button").is_enabled(),
            "Confirm button did not become disabled",
        )

    def cancel_button(self, mode: str) -> WebElement:
        """Get the cancel button on the modal"""

        return self.get_element(f"modal-{mode}-{self.entry_type}-cancel-button")

    def edit_button(self, mode: str, **kwargs) -> WebElement:
        """Get the edit button on the modal"""

        return self.get_element(f"modal-{mode}-{self.entry_type}-edit-button", **kwargs)

    def import_button(self) -> WebElement:
        """Get the import button on the modal"""

        return self.get_element(f"modal-import-{self.entry_type}-import-button")

    def delete_button(self, mode: str) -> WebElement:
        """Get the delete button on the modal"""

        return self.get_element(f"modal-{mode}-{self.entry_type}-delete-button")

    def deactivate_button(self) -> WebElement:
        """Get the deactivate button on the modal"""

        return self.get_element(f"modal-view-{self.entry_type}-deactivate-button")

    def activate_button(self) -> WebElement:
        """Get the activate button on the modal"""

        return self.get_element(f"modal-view-{self.entry_type}-activate-button")

    def _fill_modal(self, duplicate_fields=None, **values) -> None:
        """Fill the modal with the given values (key: key of the input elements, value: value to set)."""

        if any(isinstance(v, dict) for v in values.values()):
            for tab_key in values:
                self.get_element(f"{tab_key}-tab").click()
                self._fill_modal(**values[tab_key])
        else:
            self.wait_for_edit_modal()
            for key, value in values.items():
                if duplicate_fields and key not in duplicate_fields:
                    continue
                if key in (
                    "operator",
                    "country",
                    "company_id",
                    "job_id",
                    "aggregator_id",
                    "job_application_id",
                    "type",
                    "source",
                    "attendance_type",
                    "applied_via",
                    "application_status",
                ):
                    select = Select(self.get_element(key))
                    select.select_by_visible_text(value)
                elif key in ["date", "application_date"]:
                    self.get_element(key + "_set_current").click()
                else:
                    self.set_text(self.get_element(key), value)

    def check_edit_modal(self, **values) -> None:
        """Check that the modal in edit mode contains the expected data
        :param values: values to check"""

        if any(isinstance(v, dict) for v in values.values()):
            for tab_key in values:
                self.get_element(f"{tab_key}-tab").click()
                self.check_edit_modal(**values[tab_key])
        else:
            for key in values:
                if "date" in key:
                    continue
                element = self.get_element(key)
                if element.tag_name == "input":
                    value = element.get_attribute("value")
                else:
                    value = element.text
                assert str(value) == str(values[key])

    # -------------------------------------------------- VIEW MODALS --------------------------------------------------

    def test_view_modal(self, entry=None) -> None:
        """Helper method to test the view modal for an entry"""

        if self.entry_type == "keyword":
            self.check_keyword_view_modal(entry)
        elif self.entry_type == "aggregator":
            self.check_aggregator_view_modal(entry)
        elif self.entry_type == "company":
            self.check_company_view_modal(entry)
        elif self.entry_type == "person":
            self.check_person_view_modal(entry)
        elif self.entry_type == "jobApplicationUpdate":
            self.check_update_view_modal(entry)
        elif self.entry_type == "interview":
            self.check_interview_view_modal(entry)
        elif self.entry_type == "job":
            self.check_job_view_modal(entry)
        elif self.entry_type == "speculativeApplication":
            self.check_speculative_application_view_modal(entry)
        elif self.entry_type == "setting":
            self.check_setting_view_modal(entry)
        else:
            raise AssertionError("Not implemented")

    def check_keyword_view_modal(self, entry: models.Keyword) -> None:
        """Helper method to test the view modal for a keyword entry"""

        modal = self.wait_for_view_modal()

        # Verify modal contains the entry information
        expected = f"Tag Details\n{entry.name}\n"
        if entry.jobs:
            expected += f"Jobs\n({len(entry.jobs)})\n"
        expected += "Close\nEdit"
        assert modal.text == expected

        # Close modal
        self.cancel_button("view").click()
        self.wait_for_view_modal_close()

    def check_aggregator_view_modal(self, entry: models.Aggregator) -> None:
        """Helper method to test the view modal for an aggregator entry"""

        modal = self.wait_for_view_modal()

        # Verify modal contains the entry information
        expected = f"Aggregator Details\n{entry.name}\nWebsite\n{entry.url.replace('https://', '')}\n"
        if entry.jobs:
            expected += f"Jobs\n({len(entry.jobs)})\n"
        if entry.job_applications:
            expected += f"Job Applications\n({len(entry.job_applications)})\n"
        expected += "Close\nEdit"
        assert modal.text == expected

        # Close modal
        self.cancel_button("view").click()
        self.wait_for_view_modal_close()

    def check_company_view_modal(self, entry: models.Company) -> None:
        """Helper method to test the view modal for a company entry"""

        modal = self.wait_for_view_modal()

        # Verify modal contains the entry information
        expected = (
            f"Company Details\n{entry.name}\nWebsite\n{entry.url.replace("https://", "")}"
            f"\nDescription\n{entry.description}\n"
        )
        if entry.jobs:
            expected += f"Jobs\n({len(entry.jobs)})\n"
        if entry.persons:
            expected += f"Contacts\n({len(entry.persons)})\n"
        expected += "Close\nEdit"
        assert modal.text == expected

        # Close modal
        self.cancel_button("view").click()
        self.wait_for_view_modal_close()

    def check_person_view_modal(self, entry: models.Person) -> None:
        """Helper method to test the view modal for a person entry"""

        modal = self.wait_for_view_modal()
        expected = (
            f"Contact Details\n{entry.name}\n"
            f"Company\n{entry.company.name.upper()}\nRole\n{entry.role}\n"
            f"Email\n{entry.email}\nPhone\n{entry.phone}\nLinkedIn Profile\nProfile\nRecruiter\n"
        )
        if entry.interviews:
            expected += f"Interviews\n({len(entry.interviews)})\n"
        if entry.jobs:
            expected += f"Jobs\n({len(entry.jobs)})\n"
        if entry.recruited_jobs:
            expected += f"Submitted Jobs\n({len(entry.recruited_jobs)})\n"
        expected += "Close\nEdit"
        assert modal.text == expected

        # Close modal
        self.cancel_button("view").click()
        self.wait_for_view_modal_close()

    def check_interview_view_modal(self, entry: models.Interview, standalone: bool = True) -> None:
        """Helper method to test the view modal for an interview entry
        :param entry: Interview entry
        :param standalone: Whether the interview is viewed standalone or as part of a job application"""

        modal = self.wait_for_view_modal()
        display_time = entry.date.astimezone()
        entry_type = {"HR": "HR", "Technical": "Technical"}[entry.type]
        if standalone:
            expected = "Interview Details\n" "Job\n" f"{entry.job.title.upper()} ({entry.job.company.name.upper()})\n"
        else:
            expected = "Interview Details\n"
        expected += "Date & Time\n" f"{display_time.strftime("%d/%m/%Y %H:%M")}\n" "Type\n" f"{entry_type}\n"

        if entry.attendance_type and not entry.location:
            expected += f"Location\n{entry.attendance_type.upper()}\n"
        elif entry.location:
            expected += "Location\n" f"{entry.location.upper()} ({entry.attendance_type.upper()})\n"
        else:
            expected += format_field("Location", None)

        interviewers = (
            ", ".join([interviewer.name.upper() for interviewer in entry.interviewers]) if entry.interviewers else None
        )
        expected += format_field("Interviewers", interviewers)

        expected += format_field("Notes", entry.note)

        expected += "Close\nEdit"

        assert modal.text == expected

        # Close modal
        self.cancel_button("view").click()
        self.wait_for_view_modal_close()

    def check_update_view_modal(self, entry: models.JobApplicationUpdate, standalone: bool = True) -> None:
        """Helper method to test the view modal for a job application update entry"""

        modal = self.wait_for_view_modal()
        display_time = entry.date.astimezone()
        if standalone:
            expected = (
                "Job Application Update Details\n"
                "Job\n"
                f"{entry.job.title.upper()} ({entry.job.company.name.upper()})\n"
                "Date & Time\n"
                f"{display_time.strftime("%d/%m/%Y %H:%M")}\n"
                "Type\n"
                f"{entry.type[0].upper() + entry.type[1:]}\n"
            )
        else:
            expected = (
                "Job Application Update Details\n"
                "Date & Time\n"
                f"{display_time.strftime("%d/%m/%Y %H:%M")}\n"
                "Type\n"
                f"{entry.type[0].upper() + entry.type[1:]}\n"
            )
        expected += format_field("Notes", entry.note)
        expected += "Close\nEdit"
        assert modal.text == expected

        # Close modal
        self.cancel_button("view").click()
        self.wait_for_view_modal_close()

    def check_job_view_modal(self, entry: models.Job) -> None:
        """Helper method to test the view modal for a job application update entry"""

        modal = self.wait_for_view_modal()

        # Job tab
        expected = "Job Details\nJob Details\nJob Application\n"
        if entry.application_status:
            expected += f"{entry.application_status.upper()}\n"
        expected += "Overview\n"
        expected += f"{entry.title}\n"

        company = entry.company.name.upper() if entry.company else None
        expected += format_field("Company", company)

        if entry.attendance_type and not entry.location:
            expected += f"Location\n{entry.attendance_type.upper()}\n"
        elif entry.attendance_type and entry.location:
            expected += f"Location\n{entry.location.upper()} ({entry.attendance_type.upper()})\n"
        elif not entry.attendance_type and entry.location:
            expected += f"Location\n{entry.location.upper()}\n"
        else:
            expected += format_field("Location", None)

        expected += "Details\n"
        expected += format_field("Description", entry.description)
        expected += format_field("Notes", entry.note)

        expected += "Compensation & Priority\n"
        expected += format_field("Salary Range", self.salary_range(entry))

        deadline = entry.deadline.strftime("%d/%m/%Y") if entry.deadline else None
        expected += format_field("Application Deadline", deadline)

        expected += "Personal Rating\n"
        if not entry.personal_rating:
            expected += "Not Provided\n"

        expected += "Favourite\n"

        expected += "Source & Links\n"
        if entry.source_type in ["aggregator", "aggregator_email"]:
            expected += format_field(
                "Source Aggregator", entry.source_aggregator.name.upper() if entry.source_aggregator else None
            )
        elif entry.source_type == "recruiter":
            expected += format_field("Source Recruiter", entry.recruiter.name.upper() if entry.recruiter else None)
        elif entry.source_type == "recruitment_company":
            expected += format_field(
                "Source Recruitment Company",
                entry.recruitment_company.name.upper() if entry.recruitment_company else None,
            )
        else:
            expected += format_field("Source", entry.source_type.capitalize() if entry.source_type else None)

        url = entry.url.replace("https://", "") if entry.url else None
        expected += format_field("Job URL", url)

        expected += "Tags & Contacts\n"
        if entry.keywords:
            tags = "\n".join([tag.name.upper() for tag in entry.keywords])
            expected += format_field("Tags", tags)

        if entry.contacts:
            contacts = "\n".join([person.name.upper() for person in entry.contacts])
            expected += format_field("Contacts", contacts)

        expected += "Close\nEdit"
        assert modal.text == expected

        # Job Application
        self.get_element("application-tab").click()
        expected = "Job Details\nJob Details\nJob Application\n"
        if entry.application_status:
            expected += f"{entry.application_status.upper()}\n"
        expected += "Application Details\n"
        app_date = entry.application_date.astimezone().strftime("%d/%m/%Y") if entry.application_date else None
        expected += format_field("Application Date" if entry.application_date else "Date", app_date)

        app_status = entry.application_status.upper() if entry.application_status else None
        expected += format_field("Status", app_status)

        if entry.applied_via == "aggregator" and entry.application_aggregator:
            applied_via = entry.application_aggregator.name.upper()
        elif entry.applied_via:
            applied_via = entry.applied_via.upper()
        else:
            applied_via = None
        expected += format_field("Applied Via", applied_via)

        app_url = entry.application_url.replace("https://", "") if entry.application_url else None
        expected += format_field("Application URL", app_url)

        expected += "Documents\n"
        if entry.cv_id or entry.cover_letter_id:
            if entry.cv_id:
                cv = entry.application_cv
                expected += f"CV\n{cv.filename.upper()}\n"
            else:
                expected += "CV\n"
            if entry.cover_letter_id:
                cl = entry.application_cover_letter
                expected += f"Cover Letter\n{cl.filename.upper()}\n"
            else:
                expected += "Cover Letter\n"

        expected += "Notes\n"
        expected += format_field(None, entry.application_note if entry.note else None)
        expected += (
            "Add Interview\n"
            "Date\n"
            "Type\n"
            "Location\n"
            "Notes\n"
            "No Interviews found\n"
            "Add Job Application Update\n"
            "Date\n"
            "Type\n"
            "Notes\n"
            "No Job Application Updates found\n"
        )
        if entry.has_application:
            expected += "Follow-up Email\n"
        expected += "Edit\nClose"
        assert modal.text == expected

        # Close modal
        self.cancel_button("view").click()
        self.wait_for_view_modal_close()

    def check_speculative_application_view_modal(self, entry: models.SpeculativeApplication) -> None:
        """Helper method to test the view modal for a speculative application entry"""

        modal = self.wait_for_view_modal()
        expected = "Speculative Application Details\n" "Company\n" f"{entry.company.name.upper()}\n"

        date_time = entry.date.astimezone().strftime("%d/%m/%Y %H:%M") if entry.date else None
        expected += format_field("Date & Time", date_time)

        expected += format_field("Contact Email", entry.contact_email)

        if entry.contacts:
            contacts = "\n".join([person.name.upper() for person in entry.contacts])
            expected += format_field("Contacts", contacts)
        else:
            expected += format_field("Contacts", None)

        expected += format_field("Notes", entry.note)
        expected += "Close\nEdit"
        assert modal.text == expected

        # Close modal
        self.cancel_button("view").click()
        self.wait_for_view_modal_close()

    def check_setting_view_modal(self, entry: models.Setting):
        """Helper method to test the view modal for a settings entry"""

        modal = self.wait_for_view_modal()
        expected = f"Setting Details\n" f"Name\n{entry.name}\n" f"Value\n{entry.value}\n"
        expected += format_field("Description", entry.description)
        expected += f"Active\n" f"Close\nEdit"
        assert modal.text == expected

        # Close modal
        self.cancel_button("view").click()
        self.wait_for_view_modal_close()

    @staticmethod
    def salary_range(item: models.Job) -> str | None:
        """
        Returns a formatted salary range string based on minimum and maximum salary values.

        Parameters
        ----------
        item : dict | None
            A dictionary that may contain 'salary_min' and 'salary_max' keys.

        Returns
        -------
        str | None
            A formatted salary string such as:
            - "£30,000"
            - "£30,000 - £40,000"
            - "From £30,000"
            - "Up to £40,000"
            or None if no salary values are provided.
        """
        if not item:
            return None

        salary_min = item.salary_min
        salary_max = item.salary_max

        if not salary_min and not salary_max:
            return None

        if salary_min == salary_max and salary_min:
            return f"£{salary_min:,.0f}"

        if salary_min and salary_max:
            return f"£{salary_min:,.0f} - £{salary_max:,.0f}"

        if salary_min:
            return f"From £{salary_min:,.0f}"

        if salary_max:
            return f"Up to £{salary_max:,.0f}"

        return None

    def add_entry(self, **data) -> None:
        """Add a new entry"""

        self.wait_for_edit_modal()
        self._fill_modal(**data)
        self.confirm_button("edit").click()
        self.wait_for_edit_modal_close()


class DataTableUtils(BaseUtils):
    """Base class for testing data tables"""

    def __init__(self, entry_type: str, **kwargs):
        self._init(**kwargs)
        self.entry_type = entry_type

    # ----------------------------------------------------- TABLES -----------------------------------------------------

    @property
    def table_rows(self) -> list[WebElement]:
        """Get all table rows on the page"""

        time.sleep(0.5)
        try:
            self.get_element(f"[id^='table-row-{self.entry_type}-']", By.CSS_SELECTOR, 1)
        except AssertionError:
            return []
        return self.driver.find_elements(By.CSS_SELECTOR, f"[id^='table-row-{self.entry_type}-']")

    def table_row(self, item_id: int, *args, **kwargs) -> WebElement:
        """Get a specific table row by its ID"""

        return self.get_element(f"table-row-{self.entry_type}-{item_id}", *args, **kwargs)

    def table_context_menu(self, entity_id: int, choice: str) -> None:
        """Row context menu"""

        self.context_menu(self.table_row(entity_id), choice)

    def check_row_exist(self, column: str, name: str, expected_count: int = 1) -> None:
        """Check that a specific row with a specific name exists in the table
        :param column: Name of the column to check
        :param name: Name of the column
        :param expected_count: Expected number of rows with that name"""

        assert (
            self.get_column_values(column).count(name) == expected_count
        ), f"Expected {expected_count} rows with name '{name}'"

    def get_column_values(self, column_key: str | None = None) -> list[str] | list[dict[str, str]]:
        """Get values from a specific table column via the column key
        (matched using id attributes starting with 'table-header-').
        :param column_key: The key of the column. If None, returns all rows as list of dicts.
        :return: List of values from that column, or list of row dicts if no key provided.
        """
        # Find all elements where id starts with 'table-header-'
        header_elements = self.driver.find_elements(By.XPATH, "//*[@id[starts-with(., 'table-header-')]]")
        header_keys = []
        for header in header_elements:
            th_id = header.get_attribute("id")
            # Ensure only ids with "table-header-" are considered
            if th_id and th_id.startswith("table-header-"):
                header_keys.append(th_id[len("table-header-") :])

        # If no column_key provided, return all rows as list of dicts
        if column_key is None:
            rows_data = []
            for row in self.table_rows:
                row_dict = {}
                cells = row.find_elements(By.TAG_NAME, "td")
                for i, key in enumerate(header_keys):
                    if i < len(cells):
                        row_dict[key] = cells[i].text
                rows_data.append(row_dict)
            return rows_data

        if column_key not in header_keys:
            raise ValueError(f"Column key '{column_key}' not found. Available keys: {header_keys}")

        column_index = header_keys.index(column_key)
        return [row.find_elements(By.TAG_NAME, "td")[column_index].text for row in self.table_rows]

    def wait_for_table_load(self, timeout: int | float = 0.1) -> None:
        """Wait for loading spinner to disappear"""

        try:
            WebDriverWait(self.driver, timeout).until(
                ec.invisibility_of_element_located((By.CSS_SELECTOR, "spinner-border"))
            )
        except TimeoutException:
            pass

    def get_row_id(self, index: int) -> int:
        """Get the entry ID of a table row by its index (0-based)
        :param index: Index of the table row"""

        pattern = rf"table-row-{self.entry_type}-(\d+)"
        row_id = self.get_attribute(self.table_rows[index], "id")
        match = re.search(pattern, row_id)
        if not match:
            raise ValueError(f"Could not find ID for table row at index {index}")
        return int(match.group(1))

    def check_id_in_table(self, entry_id: int, **kwargs) -> bool:
        """Check if an ID is in the table"""

        try:
            self.get_element(f"[id^='table-row-{self.entry_type}-']", By.CSS_SELECTOR, **kwargs)
        except AssertionError:
            return False
        rows = self.driver.find_elements(By.CSS_SELECTOR, f"[id^='table-row-{self.entry_type}-']")
        return any(row.get_attribute("id") == f"table-row-{self.entry_type}-{entry_id}" for row in rows)

    def check_id_not_in_table(self, entry_id: int) -> bool:
        """Check if an ID is not in the table"""

        return not self.check_id_in_table(entry_id, timeout=2)

    def set_search(self, search_text: str) -> None:
        """Set the search input to the given text"""

        self.set_text(self.get_element("search-input"), search_text)
        time.sleep(0.2)

    # ----------------------------------------------------- BUTTONS ----------------------------------------------------

    @property
    def add_entity_button(self) -> WebElement:
        """Get the Add Entity button"""

        return self.get_element(f"add-{self.entry_type}-button")

    @property
    def deadline_toggle(self) -> WebElement:
        """Get the Deadline Toggle button"""

        return self.get_element("show-past-deadline-toggle")

    def set_page_item_select(self, value: str) -> None:
        """Set the number of items to display per page
        :param value: Value to select (e.g. "20", "40")"""

        if len(self.table_rows) >= 20:
            Select(self.get_element("page-items-select")).select_by_visible_text(f"Show {value} Entries")

    def table_row_click(self, row_index: int) -> None:
        """Click on a table row by its index (0-based)"""

        element = self.table_row(row_index)
        self.driver.execute_script("arguments[0].click();", element)

    # --------------------------------------------------- FILTERS -----------------------------------------------------

    def get_row_count(self) -> int:
        """Return the number of currently visible table rows"""

        return len(self.table_rows)

    def is_filter_sidebar_open(self) -> bool:
        """Return True if the filter sidebar has the 'open' CSS class"""

        sidebar = self.get_element("filter-sidebar", enabled=False)
        section_classes = sidebar.get_attribute("class")
        if section_classes:
            return "open" in section_classes
        else:
            return False

    def open_filter_sidebar(self) -> None:
        """Click the filter toggle button and wait for the sidebar to render"""

        self.get_element("filter-toggle-btn").click()
        self.get_element("filter-clear-btn", enabled=False)

    def is_section_active(self, column_key: str) -> bool:
        """Return True if the filter section for the given column key is highlighted as active"""

        section = self.get_element(f"filter-section-{column_key}", enabled=False)
        section_classes = section.get_attribute("class")
        if section_classes:
            return "filter-section--active" in section_classes
        else:
            return False

    def get_filter_pills(self) -> list:
        """Return all visible filter pill span elements"""

        return self.driver.find_elements(By.CLASS_NAME, "header-filter-pill")

    def get_active_count_from_sidebar(self) -> int:
        """Return the count shown in the sidebar header badge (0 if the badge is absent)"""

        badges = self.driver.find_elements(By.CLASS_NAME, "filter-sidebar-count")
        if not badges:
            return 0
        try:
            return int(badges[0].text)
        except (ValueError, IndexError):
            return 0

    def select_from_react_select_filter(self, column_key: str, visible_text: str) -> None:
        """Select an option from a react-select filter by its visible label"""

        section = self.get_element(f"filter-section-{column_key}", enabled=False)
        select_container = section.find_element(By.CLASS_NAME, "jam-select")
        rs = Select(select_container)
        rs.select_by_visible_text(visible_text)
        time.sleep(0.5)


class AuthentificationUtils(BaseUtils):
    """Test class for Authentication functionality including:
    - Login with valid credentials
    - Login with invalid credentials
    - Signup with valid data
    - Signup with invalid data
    - Form validation"""

    def __init__(self, **kwargs):
        self._init(**kwargs)

    # ----------------------------------------------------- INPUTS -----------------------------------------------------

    def go_to_login(self) -> None:
        """Go to the login page"""

        self.go_to_page(f"login")

    def go_to_register(self) -> None:
        """Go to the register page"""

        self.go_to_page(f"register")
        time.sleep(0.5)  # animation

    def go_to_forgot_password(self) -> None:
        """Go to the forgot password page"""

        self.go_to_page(f"forgot-password")
        time.sleep(0.5)  # animation

    @property
    def try_button(self) -> WebElement:
        """Get the Try button"""

        return self.get_element("try-app-btn")

    def set_email(self, email: str) -> None:
        """Set the email field to the given value"""

        self.set_text(self.get_element("email"), email)

    def set_password(self, password: str) -> None:
        """Set the password field to the given value"""

        self.set_text(self.get_element("password"), password)

    def set_confirm_password(self, password: str) -> None:
        """Set the confirm password field to the given value"""

        self.set_text(self.get_element("confirmPassword"), password)

    def confirm(self) -> None:
        """Confirm the form submission"""

        self.get_element("confirm-button").click()

    def set_terms(self) -> None:
        """Set the accept terms checkbox to True"""

        self.get_element("terms").click()

    def set_remember_me(self) -> None:
        """Check the remember me checkbox"""

        self.get_element("remember-me").click()

    def set_first_name(self, value: str) -> None:
        """Get the first name field"""

        self.get_element("firstName").send_keys(value)

    def set_last_name(self, value: str) -> None:
        """Get the last name field"""

        self.get_element("lastName").send_keys(value)

    def register_user(
        self,
        email: str,
        password: str,
        first_name: str = "First Name",
        last_name: str = "Last Name",
    ) -> None:
        """Register a new user"""

        self.go_to_register()
        self.set_email(email)
        self.set_password(password)
        self.set_confirm_password(password)
        self.set_terms()
        self.confirm()
        self.set_first_name(first_name)
        self.set_last_name(last_name)
        self.confirm()

    def login_user(self, email: str, password: str) -> None:
        """Login with given credentials"""

        self.go_to_login()
        self.set_email(email)
        self.set_password(password)
        self.confirm()

    # ----------------------------------------------------- ERRORS -----------------------------------------------------

    def _assert_message(self, key: str, message: str) -> None:
        """Assert that the given message is displayed on the page
        :param key: Key to use for finding the error message element
        :param message: Message to check for"""

        assert message in self.get_element(key + "error-message").text, f"Message not found: {message}"

    def assert_email_error_message(self, error_message: str) -> None:
        """Assert that the given error message is displayed on the page"""

        self._assert_message("email-", error_message)

    def assert_password_error_message(self, error_message: str) -> None:
        """Assert that the given error message is displayed on the page"""

        self._assert_message("password-", error_message)

    def assert_confirm_password_error_message(self, error_message: str) -> None:
        """Assert that the given error message is displayed on the page"""

        self._assert_message("confirmPassword-", error_message)

    def assert_accept_terms_error_message(self, error_message: str) -> None:
        """Assert that the given error message is displayed on the page"""

        self._assert_message("terms-", error_message)

    def assert_no_email_error_message(self) -> None:
        """Assert that the email error message is not displayed on the page"""

        self.wait_for_disappear("email-error-message")

    def assert_no_password_error_message(self) -> None:
        """Assert that the password error message is not displayed on the page"""

        self.wait_for_disappear("password-error-message")

    def assert_no_confirm_password_error_message(self) -> None:
        """Assert that the confirm password error message is not displayed on the page"""

        self.wait_for_disappear("confirmPassword-error-message")

    # ------------------------------------------------------ PAGES -----------------------------------------------------

    def wait_for_dashboard(self) -> None:
        """Wait for the dashboard to load"""

        self.wait_for_page("dashboard")

    def wait_for_login(self) -> None:
        """Wait for the login page to load"""

        self.wait_for_page("login")

    def wait_for_register(self) -> None:
        """Wait for the register page to load"""

        self.wait_for_page("register")

    def switch_mode(self) -> None:
        """Switch between login and register modes"""

        self.get_element("switch-mode-button").click()
        time.sleep(0.5)

    def go_to_verification_url(self, token: str) -> None:
        """Navigate to login page with verification token"""

        self.driver.get(f"{self.frontend_base_url}/verify-email/?token={token}")

    def switch_to_forgot_password(self) -> None:
        """Navigate to forgot password page"""

        self.get_element("forgot-password-link").click()
        time.sleep(0.5)

    def assert_confirm_button_disabled(self) -> None:
        """Wait until the confirm button becomes disabled."""

        WebDriverWait(self.driver, 5).until(
            lambda d: not d.find_element(By.ID, "confirm-button").is_enabled(),
            "Confirm button did not become disabled",
        )

    def assert_confirm_button_enabled(self) -> None:
        """Wait until the confirm button becomes enabled (clickable)."""

        self.get_element("confirm-button")


class UserSettingsUtils(BaseUtils):
    """Test class for the User Settings Page"""

    def __init__(self, **kwargs):
        self._init(**kwargs)

    def go_to_account_tab(self) -> None:
        """Get the account tab button"""

        self.get_element("account-tab").click()

    def go_to_preferences_tab(self) -> None:
        """Get the preferences tab button"""

        self.get_element("preferences-tab").click()

    def go_to_qualifications_tab(self) -> None:
        """Get the qualifications tab button"""

        self.get_element("qualifications-tab").click()

    def go_to_premium_tab(self) -> None:
        """Get the premium tab button"""

        self.get_element("premium-tab").click()

    @property
    def current_password(self) -> WebElement:
        """Get the current password field"""
        return self.get_element("current_password")

    @property
    def email(self) -> WebElement:
        """Get the email field"""

        return self.get_element("email")

    @property
    def new_password(self) -> WebElement:
        """Get the new password field"""

        return self.get_element("new_password")

    @property
    def confirm_password(self) -> WebElement:
        """Get the confirmation password field"""

        return self.get_element("confirm_password")

    @property
    def chase_threshold(self) -> WebElement:
        """Get the chase threshold input"""

        return self.get_element("chase_threshold")

    @property
    def deadline_threshold(self) -> WebElement:
        """Get the deadline threshold input"""

        return self.get_element("deadline_threshold")

    @property
    def update_limit(self) -> WebElement:
        """Get the update limit input"""

        return self.get_element("update_limit")

    @property
    def currency(self) -> Select:
        """Get the currency field"""

        return Select(self.get_element("default_currency"))

    def get_theme(self, theme_key: str) -> WebElement:
        """Get the theme field"""

        return self.get_element(theme_key + "-theme")

    @property
    def dark_mode_btn(self) -> WebElement:
        """Get the dark mode toggle button"""

        return self.get_element("theme-dark-btn")

    @property
    def light_mode_btn(self) -> WebElement:
        """Get the light mode toggle button"""

        return self.get_element("theme-light-btn")

    @property
    def system_theme_btn(self) -> WebElement:
        """Get the system theme toggle button"""

        return self.get_element("theme-system-btn")

    def confirm(self) -> None:
        """Confirm the form submission"""

        self.get_element("confirm-button").click()

    def _assert_message(self, key: str, message: str) -> None:
        """Assert that the given message is displayed on the page
        :param key: Key to use for finding the error message element
        :param message: Message to check for"""

        assert message in self.get_element(key + "error-message").text, f"Message not found: {message}"

    def assert_email_error_message(self, error_message: str) -> None:
        """Assert that the given error message is displayed on the page"""

        self._assert_message("email-", error_message)

    def assert_password_error_message(self, error_message: str) -> None:
        """Assert that the given error message is displayed on the page"""

        self._assert_message("current_password-", error_message)

    def assert_new_password_error_message(self, error_message: str) -> None:
        """Assert that the given error message is displayed on the page"""

        self._assert_message("new_password-", error_message)

    def assert_confirm_password_error_message(self, error_message: str) -> None:
        """Assert that the given error message is displayed on the page"""

        self._assert_message("confirm_password-", error_message)

    def assert_no_email_error_message(self) -> None:
        """Assert that the email error message is not displayed on the page"""

        self.wait_for_disappear("email-error-message")

    def assert_no_new_password_error_message(self) -> None:
        """Assert that the new password error message is not displayed on the page"""

        self.wait_for_disappear("new_password-error-message")

    def assert_no_confirm_password_error_message(self) -> None:
        """Assert that the confirm password error message is not displayed on the page"""

        self.wait_for_disappear("confirm_password-error-message")

    def assert_confirm_button_enabled(self) -> None:
        """Wait until the confirm button becomes enabled (clickable)."""

        self.get_element("confirm-button")

    @property
    def download_data_button(self) -> WebElement:
        """Get the download data button"""

        return self.get_element("download-data-button")

    @property
    def delete_account_button(self) -> WebElement:
        """Get the delete account button"""

        return self.get_element("delete-account-button")

    @property
    def delete_password(self) -> WebElement:
        """Get the delete password field"""

        return self.get_element("delete_password")

    @property
    def delete_account_modal(self) -> WebElement:
        """Get the delete account modal"""

        return self.get_element("delete-account-modal")

    @property
    def cancel_delete_button(self) -> WebElement:
        """Get the cancel delete button in first modal"""

        return self.get_element("cancel-delete-button")

    @property
    def continue_delete_button(self) -> WebElement:
        """Get the continue button in first modal"""

        return self.get_element("continue-delete-button")

    @property
    def confirm_delete_modal(self) -> WebElement:
        """Get the confirmation delete modal"""

        return self.get_element("confirm-delete-modal")

    @property
    def download_data_modal_button(self) -> WebElement:
        """Get the download data button in confirmation modal"""

        return self.get_element("download-data-modal-button")

    @property
    def cancel_confirm_delete_button(self) -> WebElement:
        """Get the cancel button in confirmation modal"""

        return self.get_element("cancel-confirm-delete-button")

    @property
    def final_delete_button(self) -> WebElement:
        """Get the final delete button"""

        return self.get_element("final-delete-button")

    @property
    def experience_input(self) -> WebElement:
        """Get the experience input field"""

        return self.get_element("experience")

    @property
    def skills_input(self) -> WebElement:
        """Get the skills input field"""

        return self.get_element("skills")

    @property
    def qualities_input(self) -> WebElement:
        """Get the qualities input field"""

        return self.get_element("qualities")

    @property
    def education_input(self) -> WebElement:
        """Get the education input field"""

        return self.get_element("education")

    @property
    def interests_input(self) -> WebElement:
        """Get the interests input field"""

        return self.get_element("interests")


class FollowUpEmailModalUtils(BaseUtils):
    """Utilities for the Follow-Up Email Modal."""

    def __init__(self, **kwargs):
        self._init(**kwargs)

    def wait_for_modal(self) -> WebElement:
        """Get the follow-up email modal element."""

        return self.get_element("follow-up-modal")

    def wait_for_modal_close(self) -> None:
        """Wait for the follow-up email modal to close."""

        self._wait_for_modal_close("follow-up-modal")

    @property
    def contact(self) -> Select:
        """Get the contact element in the modal."""

        return Select(self.get_element("contactId"))

    @property
    def contact_text(self) -> str:
        """Get the contact text element in the modal."""

        return self.get_element("contactId").text

    @property
    def subject(self) -> WebElement:
        """Get the subject element in the modal."""

        return self.get_element("subject")

    @property
    def body(self) -> WebElement:
        """Get the body element in the modal."""

        return self.get_element("body")

    @property
    def cancel_button(self) -> WebElement:
        """Get the cancel button in the modal."""

        return self.get_element("cancel-btn")

    @property
    def send_button(self) -> WebElement:
        """Get the send button in the modal."""

        return self.get_element("send-btn")

    @property
    def send_menu_button(self) -> WebElement:
        """Get the send button in the modal."""

        return self.get_element("dropdown-split-email")

    @property
    def gmail_option(self) -> WebElement:
        """Get the Gmail option in the send menu."""

        return self.get_element("gmail-btn")

    @property
    def outlook_option(self) -> WebElement:
        """Get the Outlook option in the send menu."""

        return self.get_element("outlook-btn")

    @property
    def default_option(self) -> WebElement:
        """Get the Yahoo option in the send menu."""

        return self.get_element("default-email-btn")


class AlertModalUtils(BaseUtils):
    """Utilities for the Confirm Modal."""

    key = ""

    def __init__(self, **kwargs):
        self._init(**kwargs)

    def wait_for_modal(self) -> WebElement:
        """Get the confirm modal element."""

        return self.get_element(f"{self.key}-alert-modal")

    def wait_for_modal_close(self) -> None:
        """Wait for the confirm modal to close."""

        self._wait_for_modal_close(f"{self.key}-alert-modal")

    @property
    def confirm_button(self) -> WebElement:
        """Get the confirm button in the modal."""

        return self.get_element(f"{self.key}-alert-modal-confirm-button")

    @property
    def cancel_button(self) -> WebElement:
        """Get the cancel button in the modal."""

        return self.get_element(f"{self.key}-alert-modal-cancel-button")


class ConfirmModalUtils(AlertModalUtils):
    """Utilities for the Confirm Modal."""

    key = "confirm"


class DeleteModalUtils(AlertModalUtils):
    """Utilities for the Delete Modal."""

    key = "delete"


class LogoutModalUtils(AlertModalUtils):
    """Utilities for the Logout Confirm Modal."""

    key = "logout"


class PremiumSettingsUtils(BaseUtils):

    def __init__(self, **kwargs):
        self._init(**kwargs)

    @property
    def incomplete_qualifications_alert(self) -> WebElement:
        """Get the incomplete qualifications warning alert element."""

        return self.get_element("incomplete-qualifications-alert")

    @property
    def confirmation_link_alert(self) -> WebElement:
        """Get the confirmation link alert element."""

        return self.get_element("confirmation-link-alert")

    @property
    def confirmation_link_heading(self) -> WebElement:
        """Get the confirmation link heading element."""

        return self.get_element("confirmation-link-heading")

    @property
    def confirmation_link_prompt(self) -> WebElement:
        """Get the confirmation link prompt element."""

        return self.get_element("confirmation-link-prompt")

    @property
    def confirmation_link_confirm_button(self) -> WebElement:
        """Get the confirmation link confirm button element."""

        return self.get_element("confirmation-link-prompt-confirm-button")

    @property
    def confirmation_link_cancel_button(self) -> WebElement:
        """Get the confirmation link cancel button element."""

        return self.get_element("confirmation-link-prompt-cancel-button")

    def dismiss_confirmation_link_alert(self) -> None:
        """Dismiss the warning alert to trigger the showConfirm prompt."""

        self.confirmation_link_alert.find_element(By.CSS_SELECTOR, ".btn-close").click()
        time.sleep(0.5)

    def delete_stripe_data(self) -> None:
        """Delete Stripe customer data for the user"""

        response = self.client.delete("/test/payments/delete-all-customers")
        assert response.status_code == 200

    def advance_clock(self, days: int = 15) -> None:
        """Advance the Stripe clock"""

        response = self.client.post("/test/payments/advance-test-clock", json={"days": days})
        assert response.status_code == 200
        self.advance_browser_clock_days(days)

    @property
    def subscription_button(self) -> WebElement:
        """Subscribe button element"""

        return self.get_element("subscription-button")

    def assert_status_title(self, expected_title: str) -> None:
        """Assert status title"""

        assert self.wait_for_element_text("status-title", expected_title)

    def assert_status_message(self, expected_message: str) -> None:
        """Assert status message"""

        assert self.wait_for_element_text("status-message", expected_message)

    @property
    def stripe_add_payment_method_button(self) -> WebElement:
        """Add payment method button element"""

        return self.get_element("[data-test='add-payment-method']", By.CSS_SELECTOR)

    @property
    def stripe_cancel_subscription_button(self) -> WebElement:
        """Cancel subscription button element"""

        return self.get_element("[data-test='cancel-subscription']", By.CSS_SELECTOR)

    @property
    def stripe_return_to_business_link(self) -> WebElement:
        """Return to business link element"""

        return self.get_element("[data-testid='return-to-business-link']", By.CSS_SELECTOR)

    @property
    def stripe_start_trial_button(self) -> WebElement:
        """Start trial button element"""

        return self.get_element("[data-testid='hosted-payment-submit-button']", By.CSS_SELECTOR)

    @property
    def stripe_confirm_button(self) -> WebElement:
        """Confirm button element"""

        return self.get_element("[data-test='confirm']", By.CSS_SELECTOR)

    @property
    def stripe_cancel_feedback(self) -> WebElement:
        """Confirm button element"""

        return self.get_element("[data-testid='cancellation_reason_cancel']", By.CSS_SELECTOR)

    def set_stripe_payment_details(self) -> None:
        """Set payment details in the Stripe iframe"""

        self.driver.switch_to.frame(0)
        self.get_element("card-tab").click()
        self.set_text(self.get_element("payment-numberInput"), "4242 4242 4242 4242")
        self.set_text(self.get_element("payment-cvcInput"), "123")
        self.get_element("payment-countryInput", timeout=2).send_keys("United States")
        self.set_text(self.get_element("payment-expiryInput"), "1228")
        self.set_text(self.get_element("payment-postalCodeInput"), "10001")
        self.driver.switch_to.default_content()
        self.stripe_confirm_button.click()
        time.sleep(3)


class TourUtils(BaseUtils):

    def __init__(self, **kwargs):
        self._init(**kwargs)

    NON_PREMIUM_TOUR_IDS = [
        "app-overview",
        "first-job",
        "log-application",
        "log-interview",
        "log-update",
        "follow-up-email",
        "add-contact",
        "speculative-applications",
    ]
    PREMIUM_TOUR_IDS = NON_PREMIUM_TOUR_IDS + ["import-scraped-job", "scraping-filters"]

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

    def open_tour_select(self) -> None:
        """Click 'Take a Tour' to open the tour select panel.

        Uses a JS click to bypass sidebar animation / clickability edge cases:
        the button is always in the sidebar DOM and its React onClick fires regardless
        of whether the About submenu is visually open or the sidebar is mid-transition.
        """
        self.get_element(self.TAKE_A_TOUR_BTN, enabled=False)  # wait for element to exist
        self.driver.execute_script(f"document.getElementById('{self.TAKE_A_TOUR_BTN}').click();")
        self.get_element(self.TSP_PANEL, enabled=False, timeout=5)

    def start_tour(self, tour_id: str = TOUR_ID, popover_timeout: float = 10.0) -> None:
        """Open the tour select panel and start the given tour."""
        self.open_tour_select()
        self.get_element(f"tsp-item-{tour_id}").click()
        self.wait_for_popover(timeout=popover_timeout)

    def wait_for_popover(self, timeout: float = 10.0) -> None:
        """Wait for the tour popover to appear in the DOM."""
        self.get_element(self.TOUR_POPOVER, timeout=timeout, enabled=False)

    def wait_for_popover_gone(self, timeout: float = 10.0) -> None:
        """Wait for the tour popover to disappear."""
        self.wait_for_disappear(self.TOUR_POPOVER, timeout=timeout)

    def popover_title(self) -> str:
        """Tour popover title"""
        return self.get_element(self.TOUR_TITLE, enabled=False).text

    def step_counter_text(self) -> str:
        """Tour step counter text"""
        return self.get_element(self.TOUR_COUNTER, enabled=False).text

    def click_next(self) -> None:
        """Click the next tour step button."""
        self.get_element(self.TOUR_NEXT).click()

    def click_back(self) -> None:
        """Click the back tour step button."""
        self.get_element(self.TOUR_BACK).click()

    def click_skip(self) -> None:
        """Click the skip tour button."""
        self.get_element(self.TOUR_SKIP).click()

    def advance_steps(self, n: int) -> None:
        """Click Next n times, waiting for the popover between each click."""
        for _ in range(n):
            self.wait_for_popover()
            self.click_next()

    def advance_to_last_step(self) -> None:
        """Click through steps until the Done button is visible."""
        for _ in range(self.TOTAL_STEPS):
            self.wait_for_popover()
            next_btn = self.get_element(self.TOUR_NEXT)
            if "Done" in next_btn.text:
                return
            next_btn.click()

    def wait_for_step(self, n: int, timeout: float = 10.0) -> None:
        """Wait until the step counter shows Step N (case-insensitive, CSS may uppercase the text)."""
        WebDriverWait(self.driver, timeout).until(
            lambda d: f"STEP {n} OF" in d.find_element(By.ID, self.TOUR_COUNTER).text.upper()
        )

    @property
    def keep_data_toggle(self) -> WebElement:
        """Keep my data toggle on the done step."""
        return self.get_element("tour-keep-data")

    def poll_db_count(self, model_class, owner_id: int, expected: int, timeout: float = 10.0) -> None:
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


class BaseTest(BaseUtils):
    """Base class for selenium tests"""

    _shared_backend_url = None
    _shared_frontend_url = None
    _shared_driver = None
    user: models.User  # user to use
    client = None  # authorised client
    base_utils = None  # base utils

    # Parameters needed
    page_url = "dashboard"  # url of the page to test (not including the base url)
    user_index = 1  # index of the user to use for the test

    _test_name = ""

    # Company
    company_modal_utils: DataModalUtils
    company_table_utils: DataTableUtils

    # Aggregator
    aggregator_modal_utils: DataModalUtils
    aggregator_table_utils: DataTableUtils

    # Keyword
    keyword_modal_utils: DataModalUtils
    keyword_table_utils: DataTableUtils

    # Person
    person_modal_utils: DataModalUtils
    person_table_utils: DataTableUtils

    # Job
    job_modal_utils: DataModalUtils
    job_table_utils: DataTableUtils

    # Interview
    interview_modal_utils: DataModalUtils
    interview_table_utils: DataTableUtils

    # Job Application Update
    jobApplicationUpdate_modal_utils: DataModalUtils
    jobApplicationUpdate_table_utils: DataTableUtils

    # Speculative Application
    speculativeApplication_modal_utils: DataModalUtils
    speculativeApplication_table_utils: DataTableUtils

    # Scraped Job
    scrapedJob_modal_utils: DataModalUtils
    scrapedJob_table_utils: DataTableUtils

    # Job Email
    jobEmail_modal_utils: DataModalUtils
    jobEmail_table_utils: DataTableUtils

    # Scraping Filter
    scrapingExclusionFilter_modal_utils: DataModalUtils
    scrapingExclusionFilter_table_utils: DataTableUtils

    # Settings
    setting_modal_utils: DataModalUtils
    setting_table_utils: DataTableUtils

    # Others
    auth_utils: AuthentificationUtils
    user_settings_utils: UserSettingsUtils
    followup_modal: FollowUpEmailModalUtils
    confirm_modal: ConfirmModalUtils
    delete_modal: DeleteModalUtils
    logout_modal: LogoutModalUtils
    premium_settings_utils: PremiumSettingsUtils
    tour_utils: TourUtils

    @pytest.fixture(autouse=True)
    def setup_method(
        self,
        test_frontend_server,
        test_backend_server,
        request,
        test_users,
        authorised_clients,
        session,
    ) -> Generator[None, None, None]:
        """Set up the test environment before each test with test data"""

        self._test_name = request.node.name
        try:

            # Configure Chrome options to disable password prompts
            chrome_options = Options()
            prefs = {
                "profile.password_manager_leak_detection": False,
                "credentials_enable_service": False,
                "password_manager_enabled": False,
                "profile.password_manager_enabled": False,
                "protocol_handler": {"excluded_schemes": {"mailto": True}},
                "intl.accept_languages": "en-GB",
            }
            chrome_options.add_experimental_option("prefs", prefs)
            chrome_options.add_argument("--headless=new")
            chrome_options.add_argument("--window-size=1960,1080")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--ignore-certificate-errors")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--lang=en-GB")

            # Enable verbose logging
            chrome_options.add_argument("--enable-logging")
            chrome_options.add_argument("--v=1")
            chrome_options.set_capability("goog:loggingPrefs", {"browser": "ALL", "performance": "ALL"})

            self.driver = webdriver.Chrome(options=chrome_options)
            self.wait = WebDriverWait(self.driver, 10)

            # Set timezone using CDP
            self.driver.execute_cdp_cmd("Emulation.setTimezoneOverride", {"timezoneId": "Europe/London"})
            # Set locale using CDP
            self.driver.execute_cdp_cmd("Emulation.setLocaleOverride", {"locale": "en-GB"})

            # Frontend/Backend
            self.frontend_base_url = test_frontend_server
            self.backend_base_url = test_backend_server

            # Client/User
            self.user = test_users[self.user_index]
            self.client = authorised_clients[self.user_index]
            self.db = session

            modal_entities = [
                "company",
                "aggregator",
                "keyword",
                "person",
                "job",
                "interview",
                "jobApplicationUpdate",
                "speculativeApplication",
                "scrapedJob",
                "jobEmail",
                "scrapingExclusionFilter",
                "scrapingFavouriteFilter",
                "setting",
            ]

            shared_kwargs = {
                "driver": self.driver,
                "frontend_base_url": self.frontend_base_url,
                "backend_base_url": self.backend_base_url,
                "db": self.db,
                "client": self.client,
            }
            for name in modal_entities:
                setattr(self, f"{name}_modal_utils", DataModalUtils(entry_type=name, **shared_kwargs))
            for name in modal_entities:
                setattr(self, f"{name}_table_utils", DataTableUtils(entry_type=name, **shared_kwargs))

            self.auth_utils = AuthentificationUtils(**shared_kwargs)
            self.user_settings_utils = UserSettingsUtils(**shared_kwargs)
            self.followup_modal = FollowUpEmailModalUtils(**shared_kwargs)
            self.confirm_modal = ConfirmModalUtils(**shared_kwargs)
            self.delete_modal = DeleteModalUtils(**shared_kwargs)
            self.logout_modal = LogoutModalUtils(**shared_kwargs)
            self.premium_settings_utils = PremiumSettingsUtils(**shared_kwargs)
            self.tour_utils = TourUtils(**shared_kwargs)

            self.driver.get(self.frontend_base_url)
            self.setup_function(request)

        except Exception:
            if hasattr(self, "driver"):
                try:
                    self._save_browser_logs(failed=True)
                    self.driver.quit()
                except:
                    pass
            raise
        yield  # This allows the test to run

        # Teardown
        try:
            if hasattr(self, "driver"):
                # Check if test failed
                test_failed = request.node.rep_call.failed if hasattr(request.node, "rep_call") else False

                # Save logs on failure or in CI (always in CI for debugging)
                if test_failed or os.getenv("CI"):
                    self._save_browser_logs(failed=test_failed)
                    self._save_page_screenshot(failed=test_failed)
                self.driver.quit()
        except Exception as e:
            print(f"Error during teardown: {e}")

    def setup_function(self, request) -> None:
        """Function to run before each test - can be overridden in subclasses"""
        pass

    def _save_browser_logs(self, failed: bool = False) -> None:
        """Save browser console logs to file"""
        try:
            # Get browser logs
            browser_logs = self.driver.get_log("browser")
            performance_logs = self.driver.get_log("performance")

            # Create filename with test name and timestamp
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            status_string = "FAILED" if failed else "PASSED"
            safe_test_name = self._test_name.replace("/", "_").replace(":", "_")

            # Save browser console logs
            browser_log_file = settings.log_directory + f"/{safe_test_name}_{status_string}_{timestamp}_browser.log"
            with open(browser_log_file, "w") as f:
                f.write(f"Test: {self._test_name}\n")
                f.write(f"Status: {status_string}\n")
                f.write(f"Timestamp: {timestamp}\n")
                f.write(f"URL: {self.driver.current_url}\n")
                f.write("=" * 80 + "\n\n")

                for entry in browser_logs:
                    f.write(f"[{entry['level']}] {entry['timestamp']}: {entry['message']}\n")

            # Save performance logs (network requests)
            perf_log_file = settings.log_directory + f"/{safe_test_name}_{status_string}_{timestamp}_network.log"
            with open(perf_log_file, "w") as f:
                f.write(f"Test: {self._test_name}\n")
                f.write(f"Network Performance Logs\n")
                f.write("=" * 80 + "\n\n")

                for entry in performance_logs:
                    try:
                        log_entry = json.loads(entry["message"])
                        # Filter for network events
                        if "Network" in log_entry.get("message", {}).get("method", ""):
                            f.write(json.dumps(log_entry, indent=2) + "\n")
                    except:
                        pass

            print(f"✅ Saved browser logs to {browser_log_file}")

        except Exception as e:
            print(f"⚠️ Could not save browser logs: {e}")

    def _save_page_screenshot(self, failed: bool = False) -> None:
        """Save screenshot and page HTML of current page"""
        try:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            status_string = "FAILED" if failed else "PASSED"
            safe_test_name = self._test_name.replace("/", "_").replace(":", "_")

            screenshot_file = settings.log_directory + f"/{safe_test_name}_{status_string}_{timestamp}.png"
            self.driver.save_screenshot(str(screenshot_file))
            print(f"✅ Saved screenshot to {screenshot_file}")

            html_file = settings.log_directory + f"/{safe_test_name}_{status_string}_{timestamp}.html"
            with open(html_file, "w", encoding="utf-8") as f:
                f.write(self.driver.page_source)
            print(f"✅ Saved page source to {html_file}")

        except Exception as e:
            print(f"⚠️ Could not save screenshot/page source: {e}")

    def login(self, user: models.User | None = None) -> None:
        """Log in by generating a JWT token directly and injecting it into localStorage."""

        if not user:
            user = self.user
        if not user:
            raise AssertionError("No user provided")

        # Generate JWT directly — no HTTP call, no bcrypt verification
        token = create_access_token(
            data={"user_id": user.id},
            token_version=user.token_version,
        )

        # Inject token into localStorage — browser is already on the same origin from setup_method
        self.driver.execute_script(f'window.localStorage.setItem("token", "{token}");')

        self.driver.get(f"{self.frontend_base_url}/{self.page_url}")
        self.wait_for_page(self.page_url)
        self.wait_for_disappear("loading-spinner")

    def refresh(self) -> None:
        """Refresh the page"""

        self.driver.refresh()
        self.wait_for_disappear("loading-spinner")

    # ---------------------------------------------------- DATABASE ----------------------------------------------------

    @property
    def db_user(self) -> models.User:
        """Get the user from the database"""

        self.db.expire_all()
        user = self.db.query(models.User).filter(models.User.id == self.user.id).first()
        assert user
        return user

    def verify_user_in_database(self, email: str) -> list[models.User]:
        """Helper method to verify user exists in database"""

        return self.db.query(models.User).filter(models.User.email == email).all()

    def _make_company(self, **kwargs) -> models.Company:
        """Create and persist a Company owned by the current test user."""

        defaults = {
            "name": "Test Company",
            "owner_id": self.user.id,
        }
        defaults.update(kwargs)
        company = models.Company(**defaults)
        self.db.add(company)
        self.db.commit()
        self.db.refresh(company)
        return company

    def _make_person(self, **kwargs) -> models.Person:
        """Create and persist a Person owned by the current test user."""

        defaults = {
            "first_name": "Test",
            "last_name": "Person",
            "owner_id": self.user.id,
        }
        defaults.update(kwargs)
        person = models.Person(**defaults)
        self.db.add(person)
        self.db.commit()
        self.db.refresh(person)
        return person

    def _make_job(self, **kwargs) -> models.Job:
        """Create and persist a Job owned by the current test user."""

        defaults = {
            "title": "Test Job",
            "owner_id": self.user.id,
        }
        defaults.update(kwargs)
        job = models.Job(**defaults)
        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)
        return job

    def _make_speculative_application(self, company: models.Company, **kwargs) -> models.SpeculativeApplication:
        """Create and persist a SpeculativeApplication owned by the current test user."""

        defaults = {
            "company_id": company.id,
            "owner_id": self.user.id,
        }
        defaults.update(kwargs)
        application = models.SpeculativeApplication(**defaults)
        self.db.add(application)
        self.db.commit()
        self.db.refresh(application)
        return application

    def _make_aggregator(self, **kwargs) -> models.Aggregator:
        """Create and persist an Aggregator owned by the current test user."""

        defaults = {
            "name": "Test Aggregator",
            "url": "https://www.test-aggregator.com",
            "owner_id": self.user.id,
        }
        defaults.update(kwargs)
        aggregator = models.Aggregator(**defaults)
        self.db.add(aggregator)
        self.db.commit()
        self.db.refresh(aggregator)
        return aggregator

    def _make_service_log(self, **kwargs) -> models.JobEmailScrapingServiceLog:
        """Create and persist a JobEmailScrapingServiceLog."""

        defaults = {
            "run_datetime": datetime.now(timezone.utc),
        }
        defaults.update(kwargs)
        service_log = models.JobEmailScrapingServiceLog(**defaults)
        self.db.add(service_log)
        self.db.commit()
        self.db.refresh(service_log)
        return service_log

    def _make_scraped_job(
        self, service_log: models.JobEmailScrapingServiceLog | None = None, **kwargs
    ) -> models.ScrapedJob:
        """Create and persist a ScrapedJob owned by the current test user."""

        if service_log is None:
            service_log = self._make_service_log()
        defaults = {
            "external_job_id": str(uuid.uuid4()),
            "platform": "linkedin",
            "owner_id": self.user.id,
            "is_processed": True,
            "is_scraped": True,
            "title": "Test Job",
            "url": "test.com",
            "service_log_id": service_log.id,
        }
        defaults.update(kwargs)
        job = models.ScrapedJob(**defaults)
        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)
        return job

    def _make_qualifications(self, **kwargs) -> models.UserQualification:
        """Create and persist a UserQualification owned by the current test user."""

        defaults = {
            "owner_id": self.user.id,
            "experience": "Test experience",
        }
        defaults.update(kwargs)
        qualification = models.UserQualification(**defaults)
        self.db.add(qualification)
        self.db.commit()
        self.db.refresh(qualification)
        return qualification

    def _create_job_rating(self, scraped_job: models.ScrapedJob, **kwargs) -> models.JobRating:
        """Create and persist a JobRating linked to the given scraped job."""

        qualification = self._make_qualifications()
        defaults = {
            "owner_id": self.user.id,
            "scraped_job_id": scraped_job.id,
            "user_qualification_id": qualification.id,
        }
        defaults.update(kwargs)
        rating = models.JobRating(**defaults)
        self.db.add(rating)
        self.db.commit()
        self.db.refresh(rating)
        return rating

    def _create_setting(self, **kwargs) -> models.Setting:
        """Create a new setting entry"""

        setting = models.Setting(**kwargs)
        self.db.add(setting)
        self.db.commit()
        self.db.refresh(setting)
        return setting


def format_file_size(size: int | None) -> str:
    """Python equivalent of the frontend formatFileSize utility."""
    if not size:
        return ""
    if size < 1024:
        return f"{size} B"
    if size < 1024 * 1024:
        return f"{size / 1024:.1f} KB"
    return f"{size / (1024 * 1024):.1f} MB"


def contiguous_subdicts(dictionary: dict) -> list[dict]:
    """Return a list of all contiguous sub-dictionaries in the given dictionary.
    :param dictionary: The dictionary to search."""

    keys = list(dictionary.keys())
    n = len(keys)
    results = []
    for size in range(1, n):
        for start in range(n):
            # Generate indices with wrap-around using modulo
            subkeys = [keys[(start + i) % n] for i in range(size)]
            subdict = {k: dictionary[k] for k in subkeys}
            results.append(subdict)
    return [dict()] + results


def format_field(label: str | None, value: str | None) -> str:
    """Format a field for display in a view modal, showing 'Not Provided' for None values.
    :param label: The field label to display
    :param value: The value to display, or None
    :return: Formatted string with label and value or 'Not Provided'"""

    if label:
        return f"{label}\n{value if value else 'Not Provided'}\n"
    else:
        return f"{value if value else 'Not Provided'}\n"


class MaintenanceTestBase(BaseTest):
    """Shared helpers for maintenance tests."""

    _setting_id = None

    def _set_maintenance_scheduled_at(self, iso_timestamp: str) -> None:
        """Create or update the maintenance_scheduled_at setting via the API."""

        if self._setting_id is None:
            response = self.client.post("/settings/", json={"name": "maintenance_scheduled_at", "value": iso_timestamp})
            assert response.status_code == 201
            self._setting_id = response.json()["id"]
        else:
            response = self.client.put(f"/settings/{self._setting_id}", json={"value": iso_timestamp})
            assert response.status_code == 200

    def _clear_maintenance_scheduled_at(self) -> None:
        """Delete the maintenance_scheduled_at setting if it exists."""

        if self._setting_id is not None:
            self.client.delete(f"/settings/{self._setting_id}")
            self._setting_id = None

    @staticmethod
    def _get_future_timestamp(minutes: int | float = 30) -> str:
        """Get an ISO 8601 timestamp for a time in the future."""

        future_time = datetime.now(timezone.utc) + timedelta(minutes=minutes)
        return future_time.isoformat()

    @staticmethod
    def _get_past_timestamp(minutes: int | float = 5) -> str:
        """Get an ISO 8601 timestamp for a time in the past."""

        past_time = datetime.now(timezone.utc) - timedelta(minutes=minutes)
        return past_time.isoformat()
