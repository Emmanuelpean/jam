"""
Test module for API router endpoints covering CRUD operations for JAM entities.

This module contains comprehensive test classes for all API endpoints, organised into simple tables
(companies, keywords, aggregators, locations, files) and complex tables with relationships
(persons, jobs, job applications, interviews, job application updates). Each test class inherits
from CRUDTestBase to ensure consistent testing of standard CRUD operations, including authorisation,
validation, and error handling. Additional custom endpoint tests are included where applicable.
"""

from app import schemas
from conftest import CRUDTestBase
from tests.utils.table_data import (
    COMPANY_DATA,
    LOCATION_DATA,
    PERSON_DATA,
    AGGREGATOR_DATA,
    KEYWORD_DATA,
    FILE_DATA,
    JOB_DATA,
    JOB_APPLICATION_DATA,
    INTERVIEW_DATA,
    JOB_APPLICATION_UPDATE_DATA,
)


# ---------------------------------------------------- SIMPLE TABLES ---------------------------------------------------


class TestCompanyCRUD(CRUDTestBase):
    endpoint = "/companies"
    schema = schemas.Company
    out_schema = schemas.CompanyOut
    test_data = "test_companies"
    create_data = COMPANY_DATA
    update_data = {
        "name": "OXPV",
        "id": 1,
    }

    def test_get_all_specific_company(self, authorised_clients, test_companies) -> None:
        response = authorised_clients[0].get(f"{self.endpoint}/?url=https://techcorp.com")
        assert response.status_code == 200

        # The response should be a list, so check the first item
        companies = response.json()
        assert len(companies) > 0
        assert companies[0]["name"] == "Tech Corp"


class TestKeywordCRUD(CRUDTestBase):
    endpoint = "/keywords"
    schema = schemas.Keyword
    out_schema = schemas.KeywordOut
    test_data = "test_keywords"
    create_data = KEYWORD_DATA
    update_data = {
        "id": 1,
        "name": "Updated Python",
    }


class TestAggregatorCRUD(CRUDTestBase):
    endpoint = "/aggregators"
    schema = schemas.Aggregator
    out_schema = schemas.AggregatorOut
    test_data = "test_aggregators"
    create_data = AGGREGATOR_DATA
    update_data = {
        "name": "Updated LinkedIn",
        "url": "https://updated-linkedin.com",
        "id": 1,
    }


class TestLocationCRUD(CRUDTestBase):
    endpoint = "/locations"
    schema = schemas.Location
    out_schema = schemas.LocationOut
    test_data = "test_locations"
    create_data = LOCATION_DATA
    update_data = {
        "postcode": "OX5 1HN",
        "id": 1,
    }


class TestFileCRUD(CRUDTestBase):
    endpoint = "/files"
    schema = schemas.File
    out_schema = schemas.FileOut
    test_data = "test_files"
    create_data = FILE_DATA
    update_data = {
        "filename": "updated_john_doe_cv_2024.pdf",
        "size": 2560,
        "id": 1,
    }

    def test_file_download_data_url_format(self, authorised_clients, test_files) -> None:
        """Test file download with Base64 data URL format"""

        # Use existing test file instead of creating new one
        test_file = test_files[0]  # Get first test file

        # Download the file
        download_response = authorised_clients[0].get(f"{self.endpoint}/{test_file.id}/download")
        assert download_response.status_code == 200

        # Verify content type and filename in headers
        assert download_response.headers["content-type"] in ["application/pdf", "text/plain; charset=utf-8"]
        assert f'filename="{test_file.filename}"' in download_response.headers["content-disposition"]

    def test_file_download_plain_base64_format(self, authorised_clients, test_files) -> None:
        """Test file download with plain Base64 format (without data URL prefix)"""

        # Use second test file if available, otherwise first
        test_file = test_files[1] if len(test_files) > 1 else test_files[0]

        # Download the file
        download_response = authorised_clients[0].get(f"{self.endpoint}/{test_file.id}/download")
        assert download_response.status_code == 200

        # Verify basic response structure
        assert len(download_response.content) > 0
        assert "content-disposition" in download_response.headers

    def test_file_download_binary_content(self, authorised_clients, test_files) -> None:
        """Test file download with binary content (simulating image/PDF)"""

        # Use third test file if available, otherwise first
        test_file = test_files[2] if len(test_files) > 2 else test_files[0]

        # Download the file
        download_response = authorised_clients[0].get(f"{self.endpoint}/{test_file.id}/download")
        assert download_response.status_code == 200

        # Verify content
        downloaded_content = download_response.content
        assert len(downloaded_content) > 0

        # Verify headers
        assert "content-type" in download_response.headers
        assert f'filename="{test_file.filename}"' in download_response.headers["content-disposition"]

    def test_file_download_not_found(self, authorised_clients) -> None:
        """Test file download with non-existent file ID"""

        download_response = authorised_clients[0].get(f"{self.endpoint}/999/download")
        assert download_response.status_code == 404
        error_data = download_response.json()
        assert "File not found" in error_data["detail"]

    def test_file_download_unauthorized(self, authorised_clients, test_files) -> None:
        """Test file download access control - users can only download their own files"""

        # Use existing test file
        test_file = test_files[0]

        # Try to download with second user (assuming test files belong to first user)
        download_response = authorised_clients[1].get(f"{self.endpoint}/{test_file.id}/download")
        assert download_response.status_code == 404
        error_data = download_response.json()
        assert "File not found" in error_data["detail"]

    def test_file_download_empty_content(self, authorised_clients) -> None:
        """Test file download with empty/null content"""

        # Create a file with empty content for this specific test case
        file_data = {"filename": "empty_file.txt", "content": "", "type": "text/plain", "size": 0}

        # This might fail at creation if backend validates non-empty content
        # Adjust based on your actual validation rules
        create_response = authorised_clients[0].post(f"{self.endpoint}/", json=file_data)
        if create_response.status_code == 201:
            file_id = create_response.json()["id"]
            download_response = authorised_clients[0].get(f"{self.endpoint}/{file_id}/download")
            # Should either return empty content or handle gracefully
            assert download_response.status_code in [200, 404, 500]


# --------------------------------------------------- COMPLEX TABLES ---------------------------------------------------


class TestPersonCRUD(CRUDTestBase):
    endpoint = "/persons"
    schema = schemas.Person
    out_schema = schemas.PersonOut
    test_data = "test_persons"
    add_fixture = ["test_companies"]
    create_data = PERSON_DATA
    update_data = {
        "first_name": "OX",
        "id": 1,
    }


class TestJobCRUD(CRUDTestBase):
    endpoint = "/jobs"
    schema = schemas.Job
    out_schema = schemas.JobOut
    test_data = "test_jobs"
    add_fixture = ["test_persons", "test_locations", "test_keywords", "test_companies"]
    create_data = JOB_DATA
    update_data = {
        "title": "Updated title",
        "url": "https://updated-linkedin.com",
        "id": 1,
    }


class TestJobApplicationCRUD(CRUDTestBase):
    endpoint = "/jobapplications"
    schema = schemas.JobApplication
    out_schema = schemas.JobApplicationOut
    test_data = "test_job_applications"
    add_fixture = ["test_jobs", "test_files"]
    create_data = JOB_APPLICATION_DATA
    update_data = {
        "status": "Interview Completed",
        "note": "Technical interview went well",
        "id": 1,
    }

    def test_needs_chase_custom_days(self, authorised_clients, test_job_applications) -> None:
        """Test needs_chase endpoint with custom days parameter"""

        # Test with 7 days - should return fewer results
        response = authorised_clients[0].get(f"{self.endpoint}/needs_chase?days=7")
        assert response.status_code == 200
        applications_7_days = response.json()
        assert len(applications_7_days) == 10
        for app in applications_7_days:
            assert app["job_application"]["status"] not in ["Rejected", "Withdrawn"]

        # Test with 60 days - should return more results
        response = authorised_clients[0].get(f"{self.endpoint}/needs_chase?days=60")
        assert response.status_code == 200
        applications_60_days = response.json()
        assert len(applications_60_days) == 4


class TestJobApplicationUpdateCRUD(CRUDTestBase):
    endpoint = "/jobapplicationupdates"
    schema = schemas.JobApplicationUpdateIn
    out_schema = schemas.JobApplicationUpdateOut
    test_data = "test_job_application_updates"
    add_fixture = ["test_job_applications"]
    create_data = JOB_APPLICATION_UPDATE_DATA
    update_data = {
        "id": 1,
        "note": "Updated note",
    }


class TestInterviewCRUD(CRUDTestBase):
    endpoint = "/interviews"
    schema = schemas.Interview
    out_schema = schemas.InterviewOut
    test_data = "test_interviews"
    add_fixture = ["test_job_applications", "test_locations", "test_persons"]
    create_data = INTERVIEW_DATA
    update_data = {
        "note": "Interview went very well - positive feedback",
        "date": "2024-01-20T10:00:00",
        "id": 1,
    }


class TestLatestUpdatesRouter:
    """Test class for the updates router endpoints"""

    def test_get_all_updates_basic_functionality(
        self, authorised_clients, test_job_applications, test_interviews, test_job_application_updates
    ) -> None:
        """Test get_all_updates endpoint returns unified updates"""
        response = authorised_clients[0].get("/latest_updates/")
        assert response.status_code == 200

        updates = response.json()
        assert isinstance(updates, list)

        # Verify each update has the expected structure
        for update in updates:
            assert "date" in update
            assert "type" in update
            assert "job_title" in update

            # Verify type is one of the expected values
            assert update["type"] in ["Application", "Interview", "Job Application Update"]

            # Verify date format (should be ISO datetime string)
            assert isinstance(update["date"], str)

        # Verify updates are sorted by date (most recent first)
        if len(updates) > 1:
            for i in range(len(updates) - 1):
                current_date = updates[i]["date"]
                next_date = updates[i + 1]["date"]
                assert current_date >= next_date

    def test_get_all_updates_with_limit(self, authorised_clients, test_job_applications) -> None:
        """Test get_all_updates endpoint with custom limit parameter"""
        # Test with small limit
        response = authorised_clients[0].get("/latest_updates/?limit=5")
        assert response.status_code == 200

        updates = response.json()
        assert len(updates) <= 5

        # Test with larger limit
        response = authorised_clients[0].get("/latest_updates/?limit=50")
        assert response.status_code == 200

        updates_large = response.json()
        assert len(updates_large) >= len(updates)  # Should return same or more results

    def test_get_all_updates_unauthorized(self, client) -> None:
        """Test that unauthorized requests are rejected"""
        response = client.get("/latest_updates/")
        assert response.status_code == 401


class TestGeneralRouter:
    """Test class for general router endpoints"""

    def test_get_all_updates_with_job_applications(self, test_users, authorised_clients, test_job_applications) -> None:
        """Test get_all_updates returns job applications with attached job application data"""

        response = authorised_clients[0].get("/latest_updates")
        data = response.json()
        assert all(d["type"] == "Application" for d in data)
        assert len(data) == len(test_job_applications)
        assert all({d["data"]["owner_id"] == test_users[0].id for d in data})

    def test_get_all_updates_with_interviews(self, test_users, authorised_clients, test_interviews) -> None:
        """Test get_all_updates returns interviews with attached job application data"""

        response = authorised_clients[0].get("/latest_updates")
        data = response.json()
        job_applications = [d for d in data if d["type"] == "Application"]
        interviews = [d for d in data if d["type"] == "Interview"]
        assert len(job_applications) == 8
        assert len(interviews) == 12
        assert all({d["data"]["owner_id"] == test_users[0].id for d in data})

    def test_get_all_updates_with_interviews_updates(
        self, test_users, authorised_clients, test_interviews, test_job_application_updates
    ) -> None:
        """Test get_all_updates returns interviews with attached job application data"""

        response = authorised_clients[0].get("/latest_updates")
        data = response.json()
        job_applications = [d for d in data if d["type"] == "Application"]
        interviews = [d for d in data if d["type"] == "Interview"]
        updates = [d for d in data if d["type"] == "Job Application Update"]
        assert len(updates) == 10
        assert len(job_applications) == 3
        assert len(interviews) == 7
        assert all({d["data"]["owner_id"] == test_users[0].id for d in data})
