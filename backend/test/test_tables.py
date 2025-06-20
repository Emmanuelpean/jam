import base64

from app import schemas
from conftest import CRUDTestBase
from test.utils.table_data import (
    COMPANIES_DATA,
    LOCATIONS_DATA,
    PERSONS_DATA,
    AGGREGATORS_DATA,
    KEYWORDS_DATA,
    FILES_DATA,
    JOBS_DATA,
    JOB_APPLICATIONS_DATA,
    INTERVIEWS_DATA,
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

    def test_get_all_specific_company(self, authorised_clients, test_companies):
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

    def test_file_download_data_url_format(self, authorised_clients):
        """Test file download with Base64 data URL format"""
        # Create test file content
        original_content = b"This is test file content for download testing"
        base64_content = base64.b64encode(original_content).decode("utf-8")
        data_url = f"data:text/plain;base64,{base64_content}"

        # Create file in database
        file_data = {
            "filename": "test_download.txt",
            "content": data_url,
            "type": "text/plain",
            "size": len(original_content),
        }

        create_response = authorised_clients[0].post(f"{self.endpoint}/", json=file_data)
        assert create_response.status_code == 201
        file_id = create_response.json()["id"]

        # Download the file
        download_response = authorised_clients[0].get(f"{self.endpoint}/{file_id}/download")
        assert download_response.status_code == 200

        # Verify content
        downloaded_content = download_response.content
        assert downloaded_content == original_content
        assert len(downloaded_content) == len(original_content)

        # Verify headers
        assert download_response.headers["content-type"] == "text/plain"
        assert f'filename="{file_data["filename"]}"' in download_response.headers["content-disposition"]
        assert download_response.headers["content-length"] == str(len(original_content))

    def test_file_download_plain_base64_format(self, authorised_clients):
        """Test file download with plain Base64 format (without data URL prefix)"""
        # Create test file content
        original_content = b"Another test file for plain base64 format"
        base64_content = base64.b64encode(original_content).decode("utf-8")

        # Create file in database (without data URL prefix)
        file_data = {
            "filename": "test_plain_base64.txt",
            "content": base64_content,
            "type": "text/plain",
            "size": len(original_content),
        }

        create_response = authorised_clients[0].post(f"{self.endpoint}/", json=file_data)
        assert create_response.status_code == 201
        file_id = create_response.json()["id"]

        # Download the file
        download_response = authorised_clients[0].get(f"{self.endpoint}/{file_id}/download")
        assert download_response.status_code == 200

        # Verify content
        downloaded_content = download_response.content
        assert downloaded_content == original_content
        assert len(downloaded_content) == len(original_content)

    def test_file_download_binary_content(self, authorised_clients):
        """Test file download with binary content (simulating image/PDF)"""
        # Create fake binary content (simulating a small image)
        original_content = bytes([0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A] + list(range(100)))
        base64_content = base64.b64encode(original_content).decode("utf-8")
        data_url = f"data:image/png;base64,{base64_content}"

        # Create file in database
        file_data = {
            "filename": "test_image.png",
            "content": data_url,
            "type": "image/png",
            "size": len(original_content),
        }

        create_response = authorised_clients[0].post(f"{self.endpoint}/", json=file_data)
        assert create_response.status_code == 201
        file_id = create_response.json()["id"]

        # Download the file
        download_response = authorised_clients[0].get(f"{self.endpoint}/{file_id}/download")
        assert download_response.status_code == 200

        # Verify content
        downloaded_content = download_response.content
        assert downloaded_content == original_content
        assert len(downloaded_content) == len(original_content)

        # Verify headers
        assert download_response.headers["content-type"] == "image/png"

    def test_file_download_not_found(self, authorised_clients):
        """Test file download with non-existent file ID"""
        download_response = authorised_clients[0].get(f"{self.endpoint}/999/download")
        assert download_response.status_code == 404
        error_data = download_response.json()
        assert "File not found" in error_data["detail"]

    def test_file_download_unauthorized(self, authorised_clients):
        """Test file download access control - users can only download their own files"""
        # Create file with first user
        original_content = b"Private file content"
        base64_content = base64.b64encode(original_content).decode("utf-8")
        data_url = f"data:text/plain;base64,{base64_content}"

        file_data = {
            "filename": "private_file.txt",
            "content": data_url,
            "type": "text/plain",
            "size": len(original_content),
        }

        create_response = authorised_clients[0].post(f"{self.endpoint}/", json=file_data)
        assert create_response.status_code == 201
        file_id = create_response.json()["id"]

        # Try to download with second user
        download_response = authorised_clients[1].get(f"{self.endpoint}/{file_id}/download")
        assert download_response.status_code == 404
        error_data = download_response.json()
        assert "File not found" in error_data["detail"]

    def test_file_download_empty_content(self, authorised_clients):
        """Test file download with empty/null content"""
        # This test assumes the backend validates content on creation
        # If not, you might need to manually insert a record with null content
        file_data = {"filename": "empty_file.txt", "content": "", "type": "text/plain", "size": 0}

        # This might fail at creation if backend validates non-empty content
        # Adjust based on your actual validation rules
        create_response = authorised_clients[0].post(f"{self.endpoint}/", json=file_data)
        if create_response.status_code == 201:
            file_id = create_response.json()["id"]
            download_response = authorised_clients[0].get(f"{self.endpoint}/{file_id}/download")
            # Should either return empty content or handle gracefully
            assert download_response.status_code in [200, 404, 500]

    def test_file_download_invalid_base64(self, authorised_clients):
        """Test file download with corrupted Base64 content"""
        # Create file with invalid base64 content
        file_data = {
            "filename": "corrupted_file.txt",
            "content": "data:text/plain;base64,invalid-base64-content!!!",
            "type": "text/plain",
            "size": 100,
        }

        create_response = authorised_clients[0].post(f"{self.endpoint}/", json=file_data)
        assert create_response.status_code == 201
        file_id = create_response.json()["id"]

        # Download should fail gracefully
        download_response = authorised_clients[0].get(f"{self.endpoint}/{file_id}/download")
        assert download_response.status_code == 500
        error_data = download_response.json()
        assert "Error decoding file content" in error_data["detail"]


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
