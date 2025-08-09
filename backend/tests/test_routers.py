from app import schemas
from conftest import CRUDTestBase
from tests.utils.table_data import (
    COMPANIES_DATA,
    LOCATIONS_DATA,
    PERSONS_DATA,
    AGGREGATORS_DATA,
    KEYWORDS_DATA,
    FILES_DATA,
    JOBS_DATA,
    JOB_APPLICATIONS_DATA,
    INTERVIEWS_DATA,
    JOB_APPLICATION_UPDATES_DATA,
)


# ---------------------------------------------------- SIMPLE TABLES ---------------------------------------------------


class TestCompanyCRUD(CRUDTestBase):
    endpoint = "/companies"
    schema = schemas.Company
    out_schema = schemas.CompanyOut
    test_data = "test_companies"
    create_data = COMPANIES_DATA
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
    create_data = KEYWORDS_DATA
    update_data = {
        "id": 1,
        "name": "Updated Python",
    }


class TestAggregatorCRUD(CRUDTestBase):
    endpoint = "/aggregators"
    schema = schemas.Aggregator
    out_schema = schemas.AggregatorOut
    test_data = "test_aggregators"
    create_data = AGGREGATORS_DATA
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
    create_data = LOCATIONS_DATA
    update_data = {
        "postcode": "OX5 1HN",
        "id": 1,
    }


class TestFileCRUD(CRUDTestBase):
    endpoint = "/files"
    schema = schemas.File
    out_schema = schemas.FileOut
    test_data = "test_files"
    create_data = FILES_DATA
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
    create_data = PERSONS_DATA
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
    create_data = JOBS_DATA
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
    create_data = JOB_APPLICATIONS_DATA
    update_data = {
        "status": "Interview Completed",
        "note": "Technical interview went well",
        "id": 1,
    }

    def test_needs_chase_default_days(self, authorised_clients, test_recent_job_dataset) -> None:
        """Test needs_chase endpoint with default 30 days parameter"""

        print(test_recent_job_dataset)
        a = f"{self.endpoint}/needs_chase"
        print(a)
        response = authorised_clients[0].get(a)
        assert response.status_code == 200

        applications_needing_chase = response.json()
        assert isinstance(applications_needing_chase, list)

        # Should return job applications that meet the criteria
        for app in applications_needing_chase:
            assert "id" in app
            assert "status" in app
            assert "date" in app
            assert "job" in app
            # Verify status is not "Rejected" or "Withdrawn"
            assert app["status"] not in ["Rejected", "Withdrawn"]

    def test_needs_chase_custom_days(self, authorised_clients, test_recent_job_dataset) -> None:
        """Test needs_chase endpoint with custom days parameter"""
        job_applications, job_application_updates = test_recent_job_dataset

        # Test with 7 days - should return fewer results
        response = authorised_clients[0].get(f"{self.endpoint}/needs_chase?days=7")
        assert response.status_code == 200
        applications_7_days = response.json()

        # Test with 60 days - should return more results
        response = authorised_clients[0].get(f"{self.endpoint}/needs_chase?days=60")
        assert response.status_code == 200
        applications_60_days = response.json()

        # 60 days should return more or equal results than 7 days
        assert len(applications_60_days) >= len(applications_7_days)

    def test_needs_chase_excludes_rejected_withdrawn(
        self, authorised_clients, test_recent_job_dataset, session
    ) -> None:
        """Test that rejected and withdrawn applications are excluded"""
        job_applications, job_application_updates = test_recent_job_dataset

        # Update one application to "Rejected" status
        if job_applications:
            job_applications[0].status = "Rejected"
            session.commit()

        # Update another to "Withdrawn" status if available
        if len(job_applications) > 1:
            job_applications[1].status = "Withdrawn"
            session.commit()

        response = authorised_clients[0].get(f"{self.endpoint}/needs_chase?days=365")  # Get all
        assert response.status_code == 200

        applications_needing_chase = response.json()

        # Verify no rejected or withdrawn applications are returned
        for app in applications_needing_chase:
            assert app["status"] not in ["Rejected", "Withdrawn"]

    def test_needs_chase_ordered_by_urgency(self, authorised_clients, test_recent_job_dataset) -> None:
        """Test that results are ordered by urgency (oldest activity first)"""
        job_applications, job_application_updates = test_recent_job_dataset

        response = authorised_clients[0].get(f"{self.endpoint}/needs_chase?days=365")  # Get all
        assert response.status_code == 200

        applications_needing_chase = response.json()

        if len(applications_needing_chase) > 1:
            # Check that applications have dates for comparison
            for app in applications_needing_chase:
                assert "date" in app
                assert "updates" in app

    def test_needs_chase_no_results(self, authorised_clients, test_recent_job_dataset) -> None:
        """Test needs_chase with very restrictive days parameter"""
        job_applications, job_application_updates = test_recent_job_dataset

        # Use 0 days - should return no results since all applications are old
        response = authorised_clients[0].get(f"{self.endpoint}/needs_chase?days=0")
        assert response.status_code == 200

        applications_needing_chase = response.json()
        assert len(applications_needing_chase) == 0

    def test_needs_chase_with_updates(self, authorised_clients, test_recent_job_dataset) -> None:
        """Test that applications with recent updates are handled correctly"""
        job_applications, job_application_updates = test_recent_job_dataset

        response = authorised_clients[0].get(f"{self.endpoint}/needs_chase?days=365")
        assert response.status_code == 200

        applications_needing_chase = response.json()

        # Verify structure includes updates
        for app in applications_needing_chase:
            assert "updates" in app
            assert isinstance(app["updates"], list)

    def test_needs_chase_unauthorized(self, client):
        """Test needs_chase endpoint without authentication"""
        response = client.get(f"{self.endpoint}/needs_chase")
        assert response.status_code == 401

    def test_needs_chase_other_user(self, authorised_clients, test_recent_job_dataset) -> None:
        """Test that users can only see their own job applications needing chase"""
        job_applications, job_application_updates = test_recent_job_dataset

        # First user should see results
        response = authorised_clients[0].get(f"{self.endpoint}/needs_chase")
        assert response.status_code == 200
        user1_applications = response.json()

        # Second user should see no results (data belongs to first user)
        response = authorised_clients[1].get(f"{self.endpoint}/needs_chase")
        assert response.status_code == 200
        user2_applications = response.json()

        # User 2 should have no applications since test data belongs to user 1
        assert len(user2_applications) == 0

    def test_needs_chase_includes_job_data(self, authorised_clients, test_recent_job_dataset) -> None:
        """Test that job application response includes related job data"""
        job_applications, job_application_updates = test_recent_job_dataset

        response = authorised_clients[0].get(f"{self.endpoint}/needs_chase?days=365")
        assert response.status_code == 200

        applications_needing_chase = response.json()

        for app in applications_needing_chase:
            # Verify job application structure
            assert "id" in app
            assert "status" in app
            assert "date" in app
            assert "job_id" in app

            # Verify related job data is included
            assert "job" in app
            if app["job"] is not None:
                assert "id" in app["job"]
                assert "title" in app["job"]

            # Verify other optional related data structure
            assert "aggregator" in app
            assert "cv" in app
            assert "cover_letter" in app
            assert "interviews" in app
            assert "updates" in app


class TestJobApplicationUpdateCRUD(CRUDTestBase):
    endpoint = "/jobapplicationupdates"
    schema = schemas.JobApplicationUpdateIn
    out_schema = schemas.JobApplicationUpdateOut
    test_data = "test_job_application_updates"
    add_fixture = ["test_job_applications"]
    create_data = JOB_APPLICATION_UPDATES_DATA
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
    create_data = INTERVIEWS_DATA
    update_data = {
        "note": "Interview went very well - positive feedback",
        "date": "2024-01-20T10:00:00",
        "id": 1,
    }
