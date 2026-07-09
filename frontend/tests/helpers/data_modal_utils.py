"""Utilities for interacting with data entry/view modals."""

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.wait import WebDriverWait

from app import models
from helpers.jam_test_utils import JamTestUtils
from helpers.formatting import format_field
from helpers.select_utils import Select


class DataModalUtils(JamTestUtils):
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
        elif self.entry_type == "user":
            self.check_user_view_modal(entry)
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
            expected += format_field("Source", entry.source_type.upper() if entry.source_type else None)

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
        expected += format_field(None, entry.application_note if entry.application_note else None)
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

    def check_user_view_modal(self, entry: models.User) -> None:
        """Helper method to test the view modal for a user entry.

        The user view shows email, name and several toggle fields rendered as
        icons (no text), so this checks the key identifying fields rather than an
        exact full-text match."""

        modal = self.wait_for_view_modal()
        assert "User Details" in modal.text
        assert entry.email in modal.text

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
