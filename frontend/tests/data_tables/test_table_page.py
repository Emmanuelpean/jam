"""Test the main pages of JAM"""

import datetime as dt

from base_test import models
from helpers.table_page import BaseTablePage


class TestKeywordsPage(BaseTablePage):
    """Test class for the keywords Page functionality including:
    - Displaying entries
    - Adding entries
    - Viewing entries
    - Editing entries
    - Deleting entries"""

    endpoint = "keywords"
    page_url = "keywords"
    entry_type = "keyword"
    test_data = {"name": "Test_Name"}
    required_fields = ["name"]
    duplicate_fields = ["name"]
    columns = ["name", "created_at"]
    model = models.Keyword

    def create_entries(self, count: int = 1) -> list[models.Keyword]:
        """Create keyword entries owned by the logged-in user"""

        return [self.user.create_keyword(name=f"Keyword {i}") for i in range(count)]


class TestAggregatorsPage(BaseTablePage):
    """Test class for Aggregators Page functionality including:
    - Displaying entries
    - Adding new entries
    - Viewing entries
    - Editing entries
    - Deleting entries"""

    endpoint = "aggregators"
    page_url = "aggregators"
    entry_type = "aggregator"
    test_data = {"name": "Test_Name", "url": "https://www.google.com"}
    required_fields = ["name", "url"]
    duplicate_fields = ["name"]
    columns = ["name", "url", "created_at"]
    model = models.Aggregator

    def create_entries(self, count: int = 1) -> list[models.Aggregator]:
        """Create aggregator entries owned by the logged-in user"""

        return [
            self.user.create_aggregator(
                name=f"Aggregator {i}", url=f"https://aggregator{i}.com"
            )
            for i in range(count)
        ]


class TestCompaniesPage(BaseTablePage):
    """Test class for Aggregators Page functionality including:
    - Displaying entries
    - Adding new entries
    - Viewing entries
    - Editing entries
    - Deleting entries"""

    endpoint = "companies"
    page_url = "companies"
    entry_type = "company"
    test_data = {
        "name": "Test_Name",
        "url": "https://www.google.com",
        "description": "This is a test description",
    }
    required_fields = ["name"]
    duplicate_fields = ["name"]
    columns = ["name", "url", "description", "created_at"]
    model = models.Company

    def create_entries(self, count: int = 1) -> list[models.Company]:
        """Create company entries owned by the logged-in user"""

        return [
            self.user.create_company(
                name=f"Company {i}",
                url=f"https://company{i}.com",
                description=f"Description {i}",
            )
            for i in range(count)
        ]

    def test_delete_company_with_linked_speculative_applications_shows_warning(
        self,
    ) -> None:
        """Warning appears when the company has linked speculative applications."""

        company = self.user.create_company(name="Acme Corp")
        self.user.create_speculative_application(company)
        self.user.create_speculative_application(company)
        self.refresh()
        self.company_table_utils.wait_for_table_load()

        self.company_table_utils.table_context_menu(company.id, "delete")
        modal = self.delete_modal.wait_for_modal()
        assert (
            "This will also permanently delete 2 speculative applications linked to this company."
            in modal.text
        )

    def test_delete_company_without_speculative_applications_no_warning(self) -> None:
        """No warning appears when the company has no linked speculative applications."""

        company = self.user.create_company(name="Empty Corp")
        self.refresh()
        self.company_table_utils.wait_for_table_load()

        self.company_table_utils.table_context_menu(company.id, "delete")
        modal = self.delete_modal.wait_for_modal()
        assert "speculative application" not in modal.text.lower()


class TestPersonsPage(BaseTablePage):
    """Test class for Aggregators Page functionality including:
    - Displaying entries
    - Adding new entries
    - Viewing entries
    - Editing entries
    - Deleting entries"""

    endpoint = "persons"
    page_url = "contacts"
    entry_type = "person"
    test_data = {
        "first_name": "Test_firstname",
        "last_name": "Test_lastname",
        "email": "test_email@test.com",
        "company_id": "Tech Corp",
        "phone": "000000000",
        "linkedin_url": "https://www.linkedin.com/company/websolutions-ltd/",
        "role": "Test_role",
    }
    required_fields = ["last_name", "first_name"]
    duplicate_fields = ["last_name", "first_name", "company_id"]
    columns = ["name", "email", "companyBadge", "phone", "role", "created_at"]
    sorting_columns = ["name", "companyBadge", "role", "email", "created_at"]
    model = models.Person

    def create_entries(self, count: int = 1) -> list[models.Person]:
        """Create person entries (linked to a shared company) owned by the logged-in user.

        The company is named "Tech Corp" so it can be selected from the modal via ``test_data``.
        """

        company = self.user.create_company(
            name="Tech Corp", url="https://techcorp.com", description="Tech company"
        )
        return [
            self.user.create_person(
                first_name=f"First{i}",
                last_name=f"Last{i}",
                email=f"person{i}@test.com",
                phone="1234567890",
                role="Engineer",
                linkedin_url="https://linkedin.com/in/test",
                company_id=company.id,
            )
            for i in range(count)
        ]

    def test_table_company_badge(self) -> None:
        """Test that the company badge is displayed correctly"""

        person = self.load_entries()[0]
        self.get_element("table-row-1-companyBadge").click()
        self.company_modal_utils.check_company_view_modal(person.company)

    def test_add_company(self) -> None:
        """Test adding a new person with a new company"""

        self.table_utils.add_entity_button.click()
        self.modal_utils._fill_modal(first_name="John", last_name="Doe")
        self.get_element("add-button-company").click()
        self.company_modal_utils.add_entry(name="Company")
        assert self.get_element("first_name").get_attribute("value") == "John"
        assert self.get_element("last_name").get_attribute("value") == "Doe"
        assert self.get_element("company_id").text == "Company"

    def test_modify_company(self) -> None:
        """Test modifying the company of an existing person"""

        person = self.load_entries()[0]
        self.table_utils.table_row_click(person.id)
        self.get_element("modal-view-person-CompanyBadge").click()
        self.company_modal_utils.edit_button("view").click()
        self.company_modal_utils.wait_for_edit_modal()
        assert self.get_element("name").get_attribute("value") == person.company.name
        self.company_modal_utils._fill_modal(name="New Company Name")
        self.company_modal_utils.confirm_button("edit").click()
        assert "New Company Name" in self.company_modal_utils.wait_for_view_modal().text
        self.company_modal_utils.cancel_button("view").click()
        assert (
            self.get_element("modal-view-person-CompanyBadge").text
            == "New Company Name".upper()
        )


class TestJobApplicationUpdatesPage(BaseTablePage):
    """Test class for Job Application Update Page functionalities"""

    endpoint = "job-application-updates"
    page_url = "job-application-updates"
    entry_type = "jobApplicationUpdate"
    required_fields = ["job_id", "type", "date"]
    columns = ["jobBadge", "date", "note", "created_at"]
    test_data = {
        "date": dt.datetime(
            year=2025, month=3, day=5, hour=3, minute=30, tzinfo=dt.timezone.utc
        ),
        "job_id": "Senior Python Developer (Tech Corp)",
        "note": "Received automated confirmation email",
        "type": "Received",
    }
    model = models.JobApplicationUpdate

    def create_entries(self, count: int = 1) -> list[models.JobApplicationUpdate]:
        """Create job application update entries (linked to a shared job) owned by the logged-in user.

        The job is titled "Senior Python Developer" at "Tech Corp" so it can be selected via ``test_data``.
        """

        company = self.user.create_company(
            name="Tech Corp", url="https://techcorp.com", description="Tech company"
        )
        job = self.user.create_job(
            title="Senior Python Developer", company_id=company.id
        )
        return [
            self.user.create_job_application_update(
                job,
                type="received",
                date=dt.datetime(
                    year=2025, month=3, day=5, hour=3, minute=30, tzinfo=dt.timezone.utc
                ),
                note="Received automated confirmation email",
            )
            for _ in range(count)
        ]


class TestInterviewPage(BaseTablePage):
    """Test class for Job Application Update Page functionalities"""

    endpoint = "interviews"
    page_url = "interviews"
    entry_type = "interview"
    required_fields = ["job_id", "type", "date"]
    columns = ["jobBadge", "type", "date", "created_at"]
    test_data = {
        "date": dt.datetime(
            year=2025, month=3, day=5, hour=3, minute=30, tzinfo=dt.timezone.utc
        ),
        "job_id": "Senior Python Developer (Tech Corp)",
        "note": "Received automated confirmation email",
        "attendance_type": "On-site",
        "type": "HR",
    }
    model = models.Interview

    def _create_job(self) -> models.Job:
        """Create the job (with company) that interviews are linked to"""

        company = self.user.create_company(
            name="Tech Corp", url="https://techcorp.com", description="Tech company"
        )
        return self.user.create_job(
            title="Senior Python Developer", company_id=company.id
        )

    def create_entries(self, count: int = 1) -> list[models.Interview]:
        """Create interview entries (linked to a shared job) owned by the logged-in user"""

        job = self._create_job()
        return [
            self.user.create_interview(
                job,
                type="HR",
                attendance_type="on-site",
                date=dt.datetime(
                    year=2025, month=3, day=5, hour=3, minute=30, tzinfo=dt.timezone.utc
                ),
                note="Initial screening",
            )
            for _ in range(count)
        ]

    def _create_interview_with_interviewer(self) -> models.Interview:
        """Create an interview with a single interviewer for the badge tests"""

        job = self._create_job()
        person = self.user.create_person(
            first_name="Jane",
            last_name="Doe",
            email="jane@test.com",
            phone="1234567890",
            role="Engineer",
            linkedin_url="https://linkedin.com/in/jane",
            company_id=job.company_id,
        )
        interview = self.user.create_interview(
            job, type="HR", attendance_type="on-site", note="Screening"
        )
        interview.interviewers = [person]
        self.db.commit()
        return interview

    def test_table_interviewers_badge(self) -> None:
        """Test that the person badge is displayed correctly in the table"""

        interview = self._create_interview_with_interviewer()
        self.refresh()
        self.table_utils.wait_for_table_load()
        self.get_element("table-row-1-interviewerBadges-0").click()
        self.person_modal_utils.check_person_view_modal(interview.interviewers[0])

    def test_modal_interviewers_badge(self) -> None:
        """Test that the person badge is displayed correctly in the modal"""

        interview = self._create_interview_with_interviewer()
        self.refresh()
        self.table_utils.wait_for_table_load()
        self.table_utils.table_row_click(interview.id)
        self.modal_utils.wait_for_view_modal()
        self.get_element("modal-view-interview-person-0").click()
        self.person_modal_utils.check_person_view_modal(interview.interviewers[0])


class TestJobPage(BaseTablePage):
    """Test class for Job Application Update Page functionalities"""

    endpoint = "jobs"
    page_url = "jobs"
    entry_type = "job"
    required_fields = ["title"]
    columns = ["title", "company", "location", "created_at"]
    test_data = {
        "job": {
            "title": "Senior Python Developer",
            "salary_min": 80000,
            "salary_max": 130000,
            "description": "Lead backend development using Python and modern frameworks. Work with a talented team to build scalable web applications.",
            "url": "https://techcorp.com/jobs/senior_python_developer1",
            "company_id": "Oxford PV",
            "note": "Excellent opportunity for senior developer",
            "attendance_type": "Hybrid",
        },
        "application": {
            "application_date": dt.datetime.now(),
            "application_url": "https://techcorp.com/apply/senior-python",
            "application_status": "Applied",
            "applied_via": "Aggregator",
            "application_note": "Submitted application with cover letter",
        },
    }
    duplicate_fields = ["url"]
    model = models.Job

    def create_entries(self, count: int = 1) -> list[models.Job]:
        """Create job entries (linked to a shared company) owned by the logged-in user.

        The company is named "Oxford PV" so it can be selected from the modal via ``test_data``.
        """

        company = self.user.create_company(
            name="Oxford PV", url="https://oxfordpv.com", description="Solar technology"
        )
        return [
            self.user.create_job(
                title=f"Job {i}",
                company_id=company.id,
                description=f"Description {i}",
                attendance_type="hybrid",
                source_type="other",
                salary_min=50000,
                salary_max=80000,
                salary_currency="GBP",
            )
            for i in range(count)
        ]

    def test_add_interview(self) -> None:
        """Test adding an interview through the job view modal"""

        job = self.load_entries()[0]
        interview_data = dict(
            date=dt.datetime(
                year=2025, month=4, day=10, hour=10, minute=0, tzinfo=dt.timezone.utc
            ),
            type="HR",
            attendance_type="On-site",
            note="Initial HR screening interview",
        )

        self.table_utils.table_row_click(job.id)
        self.modal_utils.wait_for_view_modal()
        self.get_element("application-tab").click()
        interview_count = len(self.interview_table_utils.table_rows)
        self.interview_table_utils.add_entity_button.click()
        self.interview_modal_utils._fill_modal(**interview_data)
        self.interview_modal_utils.confirm_button("edit").click()
        self.interview_modal_utils.wait_for_edit_modal_close()
        assert len(self.interview_table_utils.table_rows) == interview_count + 1
        self.interview_table_utils.table_rows[0].click()
        interview_id = self.interview_table_utils.get_row_id(0)
        interview = (
            self.db.query(models.Interview)
            .filter(models.Interview.id == interview_id)
            .first()
        )
        self.interview_modal_utils.check_interview_view_modal(interview, False)

    def test_modify_interview(self) -> None:
        """Test modifying an interview through the job view modal"""

        job = self.create_entries()[0]
        self.user.create_interview(
            job, type="HR", attendance_type="on-site", note="Initial screening"
        )
        self.refresh()

        interview_data = dict(
            type="Technical",
            attendance_type="Remote",
            note="Technical deep-dive interview",
        )

        # Open job view modal and navigate to the job application tab
        self.table_utils.table_row_click(job.id)
        self.modal_utils.wait_for_view_modal()
        self.get_element("application-tab").click()

        # Count the number of rows and determine the interview ID
        interview_id = self.interview_table_utils.get_row_id(0)
        self.interview_table_utils.table_rows[0].click()

        # Switch to edit mode and modify the interview
        self.interview_modal_utils.edit_button("view").click()
        self.interview_modal_utils._fill_modal(**interview_data)
        self.interview_modal_utils.confirm_button("edit").click()
        self.interview_modal_utils.wait_for_edit_modal_close()

        # Check the db entry to ensure the modifications were saved
        self.db.expire_all()
        interview = (
            self.db.query(models.Interview)
            .filter(models.Interview.id == interview_id)
            .first()
        )
        assert interview.type == "Technical"
        assert interview.attendance_type == "remote"
        assert interview.note == interview_data["note"]

        # Verify the interview view modal displays the updated information
        self.interview_modal_utils.check_interview_view_modal(interview, False)

    def test_add_job_application_update(self) -> None:
        """Test adding a job application update through the job view modal"""

        job = self.load_entries()[0]
        update_data = dict(
            date=dt.datetime(
                year=2025, month=4, day=15, hour=14, minute=0, tzinfo=dt.timezone.utc
            ),
            type="Received",
            note="Scheduled first round interview",
        )

        self.table_utils.table_row_click(job.id)
        self.modal_utils.wait_for_view_modal()
        self.get_element("application-tab").click()
        update_count = len(self.jobApplicationUpdate_table_utils.table_rows)
        self.jobApplicationUpdate_table_utils.add_entity_button.click()
        self.jobApplicationUpdate_modal_utils._fill_modal(**update_data)
        self.jobApplicationUpdate_modal_utils.confirm_button("edit").click()
        self.jobApplicationUpdate_modal_utils.wait_for_edit_modal_close()
        assert len(self.jobApplicationUpdate_table_utils.table_rows) == update_count + 1
        self.jobApplicationUpdate_table_utils.table_rows[0].click()
        update_id = self.jobApplicationUpdate_table_utils.get_row_id(0)
        update = (
            self.db.query(models.JobApplicationUpdate)
            .filter(models.JobApplicationUpdate.id == update_id)
            .first()
        )
        self.jobApplicationUpdate_modal_utils.check_update_view_modal(update, False)

    def test_modify_job_application_update(self) -> None:
        """Test modifying a job application update through the job view modal"""

        job = self.create_entries()[0]
        self.user.create_job_application_update(
            job,
            type="received",
            note="Initial update",
            date=dt.datetime(
                year=2025, month=3, day=5, hour=3, minute=30, tzinfo=dt.timezone.utc
            ),
        )
        self.refresh()

        update_data = dict(
            type="Sent",
            note="Rescheduled interview to next week",
        )

        # Open job view modal and navigate to the job application tab
        self.table_utils.table_row_click(job.id)
        self.modal_utils.wait_for_view_modal()
        self.get_element("application-tab").click()

        # Find the first update row and get its ID
        update_id = self.jobApplicationUpdate_table_utils.get_row_id(0)
        self.jobApplicationUpdate_table_utils.table_rows[0].click()

        # Switch to edit mode and modify the update
        self.jobApplicationUpdate_modal_utils.edit_button("view").click()
        self.jobApplicationUpdate_modal_utils._fill_modal(**update_data)
        self.jobApplicationUpdate_modal_utils.confirm_button("edit").click()
        self.jobApplicationUpdate_modal_utils.wait_for_edit_modal_close()

        # Check the db entry to ensure the modifications were saved
        self.db.expire_all()
        update = (
            self.db.query(models.JobApplicationUpdate)
            .filter(models.JobApplicationUpdate.id == update_id)
            .first()
        )
        assert update.type == "sent"
        assert update.note == update_data["note"]

        # Verify the update view modal displays the updated information
        self.jobApplicationUpdate_modal_utils.check_update_view_modal(update, False)


class TestSpeculativeApplicationPage(BaseTablePage):
    """Test class for Job Application Update Page functionalities"""

    endpoint = "speculative-applications"
    page_url = "speculative-applications"
    entry_type = "speculativeApplication"
    required_fields = ["title"]
    test_data = {"company_id": "LocalBiz"}
    duplicate_fields = ["company_id"]
    model = models.SpeculativeApplication

    def create_entries(self, count: int = 1) -> list[models.SpeculativeApplication]:
        """Create speculative application entries owned by the logged-in user.

        Each application targets its own company (a company may only have one speculative application
        in the UI). A spare "LocalBiz" company is created so it can be selected from the modal via
        ``test_data`` without colliding with the seeded applications."""

        self.user.create_company(
            name="LocalBiz",
            url="https://localbiz.com",
            description="Small local business",
        )
        applications = []
        for i in range(count):
            company = self.user.create_company(
                name=f"SpecCompany {i}",
                url=f"https://spec{i}.com",
                description=f"Description {i}",
            )
            applications.append(
                self.user.create_speculative_application(
                    company,
                    date=dt.datetime(
                        year=2025,
                        month=1,
                        day=8,
                        hour=9,
                        minute=30,
                        tzinfo=dt.timezone.utc,
                    ),
                )
            )
        return applications
