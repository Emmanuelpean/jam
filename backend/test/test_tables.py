from app import schemas
from conftest import CRUDTestBase

from test.table_data import (
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

    def test_get_all_specific_company(self, authorized_client1, test_companies):
        response = authorized_client1.get(f"{self.endpoint}/?url=https://techcorp.com")
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


# --------------------------------------------------- COMPLEX TABLES ---------------------------------------------------


class TestPersonCRUD(CRUDTestBase):
    endpoint = "/persons"
    schema = schemas.Person
    out_schema = schemas.PersonOut
    test_data = "test_persons"
    add_fixture = "test_companies"
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
    add_fixture = ["test_jobs"]
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
