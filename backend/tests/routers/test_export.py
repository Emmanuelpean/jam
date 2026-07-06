"""Tests for export endpoint"""

import csv
import datetime as dt
import io
import zipfile

from sqlalchemy.orm import Session
from starlette.testclient import TestClient

from tests.base_test import BaseTest
from tests.fixtures.users import FixtureUser

EXPORT_FILES = {
    "jobs.csv",
    "people.csv",
    "companies.csv",
    "aggregators.csv",
    "speculative_applications.csv",
    "scraped_jobs.csv",
}


class TestExport(BaseTest):

    endpoint = "/export/"

    # -------------------------------------------- response helpers --------------------------------------------

    def get_export_zip(self, user: FixtureUser) -> zipfile.ZipFile:
        """Request the export endpoint and return the response as an opened ZIP archive."""
        response = user.client.get(self.endpoint)
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/x-zip-compressed"
        assert "attachment; filename=all_exports.zip" in response.headers["content-disposition"]
        return zipfile.ZipFile(io.BytesIO(response.content))

    @staticmethod
    def read_csv(zf: zipfile.ZipFile, name: str) -> list[dict]:
        """Read a CSV file from the archive into a list of row dicts (header-only files yield [])."""
        with zf.open(name) as f:
            return list(csv.DictReader(io.StringIO(f.read().decode("utf-8"))))

    # ------------------------------------------------- tests -------------------------------------------------

    def test_export_data(self, session: Session, test_regular_user: FixtureUser) -> None:
        """One record of each exported entity produces exactly one data row per CSV with the expected values."""

        company = test_regular_user.create_company(name="Acme Corp")
        aggregator = test_regular_user.create_aggregator()
        keyword = test_regular_user.create_keyword(name="Python")
        person = test_regular_user.create_person(first_name="Jane", last_name="Smith", company_id=company.id)
        job = test_regular_user.create_job(
            title="Backend Engineer", company_id=company.id, location="London", source_aggregator_id=aggregator.id
        )
        job.keywords.append(keyword)
        job.contacts.append(person)
        session.commit()
        test_regular_user.create_interview(job, note="Went well", date=dt.datetime(2026, 6, 1, tzinfo=dt.timezone.utc))
        test_regular_user.create_job_application_update(
            job, note="Application received", date=dt.datetime(2026, 6, 2, tzinfo=dt.timezone.utc)
        )
        test_regular_user.create_speculative_application(company, contact_email="jane@acme.com", note="Cold outreach")
        scraped_job = test_regular_user.create_scraped_job(title="Scraped Role", company="Scraped Co")
        test_regular_user.create_job_rating(scraped_job=scraped_job, overall_score=8, is_success=True)

        zf = self.get_export_zip(test_regular_user)
        assert set(zf.namelist()) == EXPORT_FILES

        [job_row] = self.read_csv(zf, "jobs.csv")
        assert job_row["Job Title"] == "Backend Engineer"
        assert job_row["Company"] == "Acme Corp"
        assert job_row["Location"] == "London"
        assert job_row["Source Aggregator"] == "LinkedIn"
        assert job_row["Keywords"] == "Python"
        assert job_row["Contacts"] == "Jane Smith"
        assert job_row["Interviews"] == "2026-06-01 (technical) (notes: Went well)"
        assert job_row["Updates"] == "2026-06-02 (received) (notes: Application received)"

        [person_row] = self.read_csv(zf, "people.csv")
        assert person_row["First Name"] == "Jane"
        assert person_row["Last Name"] == "Smith"
        assert person_row["Company"] == "Acme Corp"

        [company_row] = self.read_csv(zf, "companies.csv")
        assert company_row["Company Name"] == "Acme Corp"
        assert company_row["People"] == "Jane Smith"

        [aggregator_row] = self.read_csv(zf, "aggregators.csv")
        assert aggregator_row["Aggregator Name"] == "LinkedIn"

        [spec_row] = self.read_csv(zf, "speculative_applications.csv")
        assert spec_row["Company"] == "Acme Corp"
        assert spec_row["Contact Email"] == "jane@acme.com"
        assert spec_row["Notes"] == "Cold outreach"

        [scraped_row] = self.read_csv(zf, "scraped_jobs.csv")
        assert scraped_row["Job Title"] == "Scraped Role"
        assert scraped_row["Company"] == "Scraped Co"
        assert scraped_row["Rating"] == "8"

    def test_export_no_data(self, test_regular_user: FixtureUser) -> None:
        """With no owned data, every CSV contains only its header row."""

        zf = self.get_export_zip(test_regular_user)
        assert set(zf.namelist()) == EXPORT_FILES
        for name in EXPORT_FILES:
            assert self.read_csv(zf, name) == []

    def test_export_joins_multiple_related_entities(self, session: Session, test_regular_user: FixtureUser) -> None:
        """Many-to-many relationships are serialised as "; "-joined lists in the CSV cells."""

        company = test_regular_user.create_company()
        job = test_regular_user.create_job(title="Fullstack Dev", company_id=company.id)
        keywords = [
            test_regular_user.create_keyword(name="Python"),
            test_regular_user.create_keyword(name="Django"),
        ]
        contacts = [
            test_regular_user.create_person(first_name="Jane", last_name="Smith", company_id=company.id),
            test_regular_user.create_person(first_name="John", last_name="Doe", company_id=company.id),
        ]
        job.keywords.extend(keywords)
        job.contacts.extend(contacts)
        session.commit()

        zf = self.get_export_zip(test_regular_user)

        [job_row] = self.read_csv(zf, "jobs.csv")
        assert set(job_row["Keywords"].split("; ")) == {"Python", "Django"}
        assert set(job_row["Contacts"].split("; ")) == {"Jane Smith", "John Doe"}

        [company_row] = self.read_csv(zf, "companies.csv")
        assert set(company_row["People"].split("; ")) == {"Jane Smith", "John Doe"}

    def test_export_unauthorized(self, client: TestClient) -> None:
        """The export endpoint requires authentication."""

        assert client.get(self.endpoint).status_code == 401
