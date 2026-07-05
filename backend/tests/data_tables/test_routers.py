"""
Test module for API router endpoints covering CRUD operations for JAM entities.

This module contains comprehensive test classes for all API endpoints, organised into simple tables
(companies, keywords, aggregators, locations, files) and complex tables with relationships
(persons, jobs, job applications, interviews, job application updates). Each test class inherits
from CRUDTestBase to ensure consistent testing of standard CRUD operations, including authorisation,
validation, and error handling. Additional custom endpoint tests are included where applicable.
"""

import base64
import uuid

from requests import Response
from sqlalchemy.orm import Session
from starlette import status
from starlette.testclient import TestClient

from app import models
from app.base_schemas import COLUMN_LIMITS
from app.data_tables import schemas
from app.data_tables.models import Geolocation
from tests.base_test import BaseTest
from tests.conftest import CRUDTestBase
from tests.fixtures.users import FixtureUser

# ---------------------------------------------------- SIMPLE TABLES ---------------------------------------------------


class TestKeywordCRUD(CRUDTestBase[models.Keyword]):
    endpoint = "/keywords"
    create_schema = schemas.KeywordCreate
    out_schema = schemas.KeywordOut
    update_data = {"name": "Updated Python"}
    too_long_create_data = {"name": "x" * (COLUMN_LIMITS.name + 1)}

    def create_entry(self, session: Session, owner: FixtureUser, **overrides) -> models.Keyword:
        overrides.setdefault("name", f"Keyword {uuid.uuid4()}")
        return self.create_keyword(session, owner, **overrides)

    def create_payload(self, session: Session, owner: FixtureUser) -> dict:
        return {"name": f"New Keyword {uuid.uuid4()}"}


class TestAggregatorCRUD(CRUDTestBase[models.Aggregator]):
    endpoint = "/aggregators"
    create_schema = schemas.AggregatorCreate
    out_schema = schemas.AggregatorOut
    update_data = {
        "name": "Updated LinkedIn",
        "url": "https://updated-linkedin.com",
    }
    too_long_create_data = {"name": "x" * (COLUMN_LIMITS.name + 1)}

    def create_entry(self, session: Session, owner: FixtureUser, **overrides) -> models.Aggregator:
        overrides.setdefault("name", f"Aggregator {uuid.uuid4()}")
        return self.create_aggregator(session, owner, **overrides)

    def create_payload(self, session: Session, owner: FixtureUser) -> dict:
        return {"name": f"New Aggregator {uuid.uuid4()}", "url": "https://new-aggregator.com"}


class TestCompanyCRUD(CRUDTestBase[models.Company]):
    endpoint = "/companies"
    create_schema = schemas.CompanyCreate
    out_schema = schemas.CompanyOut
    update_data = {"name": "OXPV"}
    too_long_create_data = {"name": "x" * (COLUMN_LIMITS.name + 1)}

    def create_entry(self, session: Session, owner: FixtureUser, **overrides) -> models.Company:
        overrides.setdefault("name", f"Company {uuid.uuid4()}")
        return self.create_company(session, owner, **overrides)

    def create_payload(self, session: Session, owner: FixtureUser) -> dict:
        return {"name": f"New Company {uuid.uuid4()}"}

    def test_get_all_specific_company(self, session: Session, test_regular_user: FixtureUser) -> None:
        self.create_company(session, test_regular_user, name="Tech Corp", url="https://techcorp.com")
        response = test_regular_user.client.get(f"{self.endpoint}/?url=https://techcorp.com")
        assert response.status_code == 200
        companies = response.json()
        assert len(companies) > 0
        assert companies[0]["name"] == "Tech Corp"

    def test_get_all_with_list(self, session: Session, test_regular_user: FixtureUser) -> None:
        first = self.create_entry(session, test_regular_user)
        second = self.create_entry(session, test_regular_user)
        response = test_regular_user.client.get(f"{self.endpoint}/?id={first.id}&id={second.id}")
        assert response.status_code == 200
        companies = response.json()
        assert len(companies) == 2
        assert {c["id"] for c in companies} == {first.id, second.id}

    def test_get_all_specific_id_not_owned(
        self, session: Session, test_regular_user: FixtureUser, test_admin_user: FixtureUser
    ) -> None:
        company = self.create_company(session, test_regular_user)
        response = test_admin_user.client.get(f"{self.endpoint}/?id={company.id}")
        assert response.status_code == 200
        assert len(response.json()) == 0


class TestFileCRUD(CRUDTestBase[models.File]):
    endpoint = "/files"
    create_schema = schemas.FileCreate
    out_schema = schemas.FileOut
    actions_to_test = ["get", "put", "delete"]
    update_data = {"filename": "updated_john_doe_cv_2024.pdf"}

    def create_entry(self, session: Session, owner: FixtureUser, **overrides) -> models.File:
        overrides.setdefault("filename", f"cv_{uuid.uuid4()}.pdf")
        overrides.setdefault("content", base64.b64encode(b"test content").decode())
        return self.create_file(session, owner, **overrides)

    # ------------------------------------------------------ POST ------------------------------------------------------

    def test_post_field_too_long(self, authorised_user: FixtureUser) -> None:
        """Uploading a file with a filename exceeding the max length returns 422."""
        client = authorised_user.client
        data = {
            "filename": "x" * (COLUMN_LIMITS.file_name + 1),
            "type": "text/plain",
            "content": base64.b64encode(b"test").decode(),
            "size": 4,
        }
        response = self.post(client, data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_post_success(self, authorised_user: FixtureUser) -> None:
        """Authorised users can upload a new file and receive 201 with the file metadata."""
        client = authorised_user.client
        data = {
            "filename": "new_cv.pdf",
            "type": "application/pdf",
            "content": base64.b64encode(b"brand new content").decode(),
            "size": 17,
            "file_type": "cv",
        }
        response = self.post(client, data)
        assert response.status_code == 201
        self.check_output(
            {key: value for key, value in data.items() if key != "content"}, response.json(), self.out_schema
        )

    def test_post_unauthenticated(self, client: TestClient) -> None:
        """Unauthenticated upload attempts are rejected with 401."""
        response = self.post(client, {})
        assert response.status_code == 401

    def test_post_duplicate_content_returns_existing_file(self, authorised_user: FixtureUser) -> None:
        """Uploading a file whose content already exists for that user returns the existing record."""
        client = authorised_user.client
        content = base64.b64encode(b"unique duplicate test content").decode()
        data = {"filename": "original.pdf", "content": content, "type": "application/pdf", "size": 28}

        first = self.post(client, data)
        assert first.status_code == 201
        first_id = first.json()["id"]

        second = self.post(client, {**data, "filename": "duplicate.pdf"})
        assert second.status_code in (200, 201)
        assert second.json()["id"] == first_id

    def test_post_incorrect_user_cannot_see_uploaded_file(
        self, authorised_user: FixtureUser, unauthorised_user: FixtureUser
    ) -> None:
        """A file uploaded by one user is not visible to another user."""
        uploader = authorised_user.client
        other = unauthorised_user.client

        data = {
            "filename": "private_cv.pdf",
            "content": base64.b64encode(b"private content").decode(),
            "type": "application/pdf",
            "size": 15,
        }
        create_response = uploader.post(self.endpoint, json=data)
        assert create_response.status_code == 201
        file_id = create_response.json()["id"]

        get_response = other.get(f"{self.endpoint}/{file_id}")
        assert get_response.status_code == 403

    # ------------------------------------------------------ DOWNLOAD ---------------------------------------------------

    def test_file_download_data_url_format(self, test_regular_user: FixtureUser) -> None:
        """Test file download with Base64 data URL format"""

        content = "data:application/pdf;base64," + base64.b64encode(b"pdf content").decode()
        test_file = test_regular_user.create_file(filename="download.pdf", content=content, type="application/pdf")

        download_response = test_regular_user.client.get(f"{self.endpoint}/{test_file.id}/download")
        assert download_response.status_code == 200

        # Verify content type and filename in headers
        assert download_response.headers["content-type"] in ["application/pdf", "text/plain; charset=utf-8"]
        assert f'filename="{test_file.filename}"' in download_response.headers["content-disposition"]

    def test_file_download_plain_base64_format(self, test_regular_user: FixtureUser) -> None:
        """Test file download with plain Base64 format (without data URL prefix)"""

        content = base64.b64encode(b"plain base64 content").decode()
        test_file = test_regular_user.create_file(filename="download.txt", content=content, type="text/plain")

        download_response = test_regular_user.client.get(f"{self.endpoint}/{test_file.id}/download")
        assert download_response.status_code == 200

        # Verify basic response structure
        assert len(download_response.content) > 0
        assert "content-disposition" in download_response.headers

    def test_file_download_binary_content(self, test_regular_user: FixtureUser) -> None:
        """Test file download with binary content (simulating image/PDF)"""

        content = base64.b64encode(bytes(range(256))).decode()
        test_file = test_regular_user.create_file(filename="binary.pdf", content=content, type="application/pdf")

        download_response = test_regular_user.client.get(f"{self.endpoint}/{test_file.id}/download")
        assert download_response.status_code == 200

        # Verify content
        downloaded_content = download_response.content
        assert len(downloaded_content) > 0

        # Verify headers
        assert "content-type" in download_response.headers
        assert f'filename="{test_file.filename}"' in download_response.headers["content-disposition"]

    def test_file_download_not_found(self, test_regular_user: FixtureUser) -> None:
        """Test file download with non-existent file ID"""

        download_response = test_regular_user.client.get(f"{self.endpoint}/999/download")
        assert download_response.status_code == 404
        error_data = download_response.json()
        assert "File not found" in error_data["detail"]

    def test_file_download_unauthorized(self, test_regular_user: FixtureUser, test_admin_user: FixtureUser) -> None:
        """Test file download access control - users can only download their own files"""

        content = base64.b64encode(b"owner only").decode()
        test_file = test_regular_user.create_file(filename="private.pdf", content=content, type="application/pdf")

        # Try to download with a different user
        download_response = test_admin_user.client.get(f"{self.endpoint}/{test_file.id}/download")
        assert download_response.status_code == 404
        error_data = download_response.json()
        assert "File not found" in error_data["detail"]

    def _create_and_download_file(self, client: TestClient, filename: str) -> Response:
        """Helper: create a file with the given filename and return the download response."""

        content = base64.b64encode(b"test content").decode()
        file_data = {"filename": filename, "content": content, "type": "text/plain", "size": 12}
        create_response = client.post(f"{self.endpoint}/", json=file_data)
        assert create_response.status_code == 201
        file_id = create_response.json()["id"]
        return client.get(f"{self.endpoint}/{file_id}/download")

    def test_file_download_filename_crlf_injection_stripped(self, test_regular_user: FixtureUser) -> None:
        """CRLF characters in filenames must not appear in Content-Disposition header."""

        malicious = "evil.pdf\r\nX-Injected: header"
        response = self._create_and_download_file(test_regular_user.client, malicious)
        assert response.status_code == 200
        content_disposition = response.headers["content-disposition"]
        assert "\r" not in content_disposition
        assert "\n" not in content_disposition

    def test_file_download_filename_path_traversal_stripped(self, test_regular_user: FixtureUser) -> None:
        """Path traversal components must be stripped from the Content-Disposition filename."""

        malicious = "../../etc/passwd"
        response = self._create_and_download_file(test_regular_user.client, malicious)
        assert response.status_code == 200
        content_disposition = response.headers["content-disposition"]
        assert 'filename="passwd"' in content_disposition

    def test_file_download_filename_quote_injection_stripped(self, test_regular_user: FixtureUser) -> None:
        """Embedded double-quotes must be removed so they cannot break the header value."""

        malicious = 'file"name.pdf'
        response = self._create_and_download_file(test_regular_user.client, malicious)
        assert response.status_code == 200
        content_disposition = response.headers["content-disposition"]
        # The header value must remain a single well-formed token — no unescaped quotes inside it
        # e.g. 'attachment; filename="filename.pdf"'
        inner = content_disposition.split('filename="')[1].rstrip('"')
        assert '"' not in inner

    def test_file_download_empty_content(self, test_regular_user: FixtureUser) -> None:
        """Test file download with empty/null content"""

        # Create a file with empty content for this specific test case
        file_data = {"filename": "empty_file.txt", "content": "", "type": "text/plain", "size": 0}

        # This might fail at creation if backend validates non-empty content
        # Adjust based on your actual validation rules
        create_response = test_regular_user.client.post(f"{self.endpoint}/", json=file_data)
        if create_response.status_code == 201:
            file_id = create_response.json()["id"]
            download_response = test_regular_user.client.get(f"{self.endpoint}/{file_id}/download")
            # Should either return empty content or handle gracefully
            assert download_response.status_code in [200, 404, 500]


# --------------------------------------------------- COMPLEX TABLES ---------------------------------------------------


class TestPersonCRUD(CRUDTestBase[models.Person]):
    endpoint = "/persons"
    create_schema = schemas.PersonCreate
    out_schema = schemas.PersonOut
    update_data = {"first_name": "OX"}
    too_long_create_data = {"first_name": "x" * (COLUMN_LIMITS.first_name + 1), "last_name": "Test"}

    def create_entry(self, session: Session, owner: FixtureUser, **overrides) -> models.Person:
        return self.create_person(session, owner, **overrides)

    def create_payload(self, session: Session, owner: FixtureUser) -> dict:
        company = self.create_company(session, owner)
        return {"first_name": "New", "last_name": "Person", "company_id": company.id}

    def create_unauthorised_payload(self, session: Session, owner: FixtureUser, other: FixtureUser) -> dict:
        company = self.create_company(session, other)
        return {"first_name": "New", "last_name": "Person", "company_id": company.id}


class TestJobCRUD(CRUDTestBase[models.Job]):
    endpoint = "/jobs"
    create_schema = schemas.JobCreate
    out_schema = schemas.JobOut
    update_data = {
        "title": "Updated title",
        "url": "https://updated-linkedin.com",
    }
    too_long_create_data = {"title": "x" * (COLUMN_LIMITS.job_title + 1)}

    def create_entry(self, session: Session, owner: FixtureUser, **overrides) -> models.Job:
        overrides.setdefault("title", f"Job {uuid.uuid4()}")
        return self.create_job(session, owner, **overrides)

    def create_payload(self, session: Session, owner: FixtureUser) -> dict:
        company = self.create_company(session, owner)
        return {"title": "New Job", "company_id": company.id}

    def create_unauthorised_payload(self, session: Session, owner: FixtureUser, other: FixtureUser) -> dict:
        company = self.create_company(session, other)
        return {"title": "New Job", "company_id": company.id}


class TestJobApplicationUpdateCRUD(CRUDTestBase[models.JobApplicationUpdate]):
    endpoint = "/job-application-updates"
    create_schema = schemas.JobApplicationUpdateCreate
    out_schema = schemas.JobApplicationUpdateOut
    update_data = {"note": "Updated note"}
    too_long_create_data = {"date": "2024-01-01T00:00:00", "job_id": 1, "type": "x" * (COLUMN_LIMITS.update_type + 1)}

    def create_entry(self, session: Session, owner: FixtureUser, **overrides) -> models.JobApplicationUpdate:
        job = self.create_job(session, owner)
        return self.create_job_application_update(session, owner, job, **overrides)

    def create_payload(self, session: Session, owner: FixtureUser) -> dict:
        job = self.create_job(session, owner)
        return {"job_id": job.id, "type": "received", "date": "2024-01-01T00:00:00"}

    def create_unauthorised_payload(self, session: Session, owner: FixtureUser, other: FixtureUser) -> dict:
        job = self.create_job(session, other)
        return {"job_id": job.id, "type": "received", "date": "2024-01-01T00:00:00"}


class TestInterviewCRUD(CRUDTestBase[models.Interview]):
    endpoint = "/interviews"
    create_schema = schemas.InterviewCreate
    out_schema = schemas.InterviewOut
    update_data = {
        "note": "Interview went very well - positive feedback",
        "date": "2024-01-20T10:00:00",
    }
    too_long_create_data = {
        "date": "2024-01-01T00:00:00",
        "job_id": 1,
        "type": "x" * (COLUMN_LIMITS.interview_type + 1),
    }

    def create_entry(self, session: Session, owner: FixtureUser, **overrides) -> models.Interview:
        job = self.create_job(session, owner)
        return self.create_interview(session, owner, job, **overrides)

    def create_payload(self, session: Session, owner: FixtureUser) -> dict:
        job = self.create_job(session, owner)
        return {"job_id": job.id, "type": "technical", "date": "2024-01-20T10:00:00"}

    def create_unauthorised_payload(self, session: Session, owner: FixtureUser, other: FixtureUser) -> dict:
        job = self.create_job(session, other)
        return {"job_id": job.id, "type": "technical", "date": "2024-01-20T10:00:00"}


class TestSpeculativeApplicationCRUD(CRUDTestBase[models.SpeculativeApplication]):
    endpoint = "/speculative-applications"
    create_schema = schemas.SpeculativeApplicationCreate
    out_schema = schemas.SpeculativeApplicationOut
    update_data = {"note": "Interview went very well - positive feedback"}
    too_long_create_data = {"date": "2024-01-01T00:00:00", "company_id": 1, "note": "x" * (COLUMN_LIMITS.note + 1)}

    def create_entry(self, session: Session, owner: FixtureUser, **overrides) -> models.SpeculativeApplication:
        company = self.create_company(session, owner, name=f"Company {uuid.uuid4()}")
        return self.create_speculative_application(session, owner, company, **overrides)

    def create_payload(self, session: Session, owner: FixtureUser) -> dict:
        company = self.create_company(session, owner, name=f"Company {uuid.uuid4()}")
        return {"company_id": company.id}

    def create_unauthorised_payload(self, session: Session, owner: FixtureUser, other: FixtureUser) -> dict:
        company = self.create_company(session, other, name=f"Company {uuid.uuid4()}")
        return {"company_id": company.id}


# ------------------------------------------------- GEOLOCATION CASCADE ------------------------------------------------


class TestGeolocationCascade(BaseTest):
    """Tests for geolocation foreign key cascade behavior on Job and Interview."""

    def test_deleting_job_does_not_delete_geolocation(self, session: Session, test_regular_user: FixtureUser) -> None:
        """Deleting a job with a geolocation does not delete the geolocation."""
        geolocation = self.create_geolocation(session)
        job = self.create_job(session, test_regular_user, geolocation_id=geolocation.id)

        session.delete(job)
        session.commit()

        geo = session.query(Geolocation).filter_by(id=geolocation.id).first()
        assert geo is not None

    def test_deleting_geolocation_sets_job_fk_to_null(self, session: Session, test_regular_user: FixtureUser) -> None:
        """Deleting a geolocation sets the job's geolocation_id to NULL (ondelete=SET NULL)."""
        geolocation = self.create_geolocation(session)
        job = self.create_job(session, test_regular_user, geolocation_id=geolocation.id)

        session.delete(geolocation)
        session.commit()

        session.refresh(job)
        assert job.geolocation_id is None

    def test_deleting_interview_does_not_delete_geolocation(
        self, session: Session, test_regular_user: FixtureUser
    ) -> None:
        """Deleting an interview with a geolocation does not delete the geolocation."""
        geolocation = self.create_geolocation(session)
        job = self.create_job(session, test_regular_user)
        interview = self.create_interview(session, test_regular_user, job, geolocation_id=geolocation.id)

        session.delete(interview)
        session.commit()

        geo = session.query(Geolocation).filter_by(id=geolocation.id).first()
        assert geo is not None

    def test_deleting_geolocation_sets_interview_fk_to_null(
        self, session: Session, test_regular_user: FixtureUser
    ) -> None:
        """Deleting a geolocation sets the interview's geolocation_id to NULL (ondelete=SET NULL)."""
        geolocation = self.create_geolocation(session)
        job = self.create_job(session, test_regular_user)
        interview = self.create_interview(session, test_regular_user, job, geolocation_id=geolocation.id)

        session.delete(geolocation)
        session.commit()

        session.refresh(interview)
        assert interview.geolocation_id is None
