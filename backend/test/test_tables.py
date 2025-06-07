from conftest import CRUDTestBase
from app import schemas


class TestAggregatorCRUD(CRUDTestBase):
    endpoint = "/aggregators"
    schema = schemas.Aggregator
    out_schema = schemas.AggregatorOut
    test_data = "test_aggregators"
    create_data = [
        {"name": "LinkedIn", "url": "https://linkedin.com"},
        {"name": "Indeed", "url": "https://indeed.com"},
        {"name": "Glassdoor", "url": "https://glassdoor.com"},
    ]
    update_data = {
        "name": "Updated LinkedIn",
        "url": "https://updated-linkedin.com",
        "id": 1,
    }


class TestCompanyCRUD(CRUDTestBase):
    endpoint = "/companies"
    schema = schemas.Company
    out_schema = schemas.CompanyOut
    test_data = "test_companies"
    create_data = [
        {"name": "Oxford PV", "description": "an Oxford company"},
        {"name": "Oxford PV", "url": "oxfordpv.com"},
        {"name": "Oxford PV"},
    ]
    update_data = {
        "name": "OXPV",
        "id": 1,
    }


class TestJobCRUD(CRUDTestBase):
    endpoint = "/jobs"
    schema = schemas.Job
    out_schema = schemas.JobOut
    test_data = "test_jobs"
    create_data = [
        {
            "title": "Software Engineer",
            "salary_min": 50000,
            "salary_max": 100000,
            "description": "Design, develop, and maintain software solutions.",
            "personal_rating": 8,
            "url": "https://example.com/jobs/software_engineer",
        },
        {
            "title": "Data Scientist",
            "salary_min": 60000,
            "salary_max": 120000,
            "description": "Analyze complex datasets and derive insights.",
            "personal_rating": 9,
            "url": "https://example.com/jobs/data_scientist",
        },
        {
            "title": "Frontend Developer",
            "salary_min": 55000,
            "salary_max": 90000,
            "description": "Build interactive and responsive web interfaces.",
            "personal_rating": 7,
            "url": "https://example.com/jobs/frontend_developer",
        },
    ]
    update_data = {
        "title": "Updated title",
        "url": "https://updated-linkedin.com",
        "id": 1,
    }


class TestLocationCRUD(CRUDTestBase):
    endpoint = "/locations"
    schema = schemas.Location
    out_schema = schemas.LocationOut
    test_data = "test_locations"
    create_data = [
        {"postcode": "OX5 1HN"},
        {"city": "Oxford"},
        {"country": "UK"},
        {"remote": True},
        {"postcode": "OX5 1HN", "remote": True},
    ]
    update_data = {
        "postcode": "OX5 1HN",
        "id": 1,
    }


class TestPersonCRUD(CRUDTestBase):
    endpoint = "/persons"
    schema = schemas.Person
    out_schema = schemas.PersonOut
    test_data = "test_persons"
    add_fixture = ["test_companies", "test_locations"]
    create_data = [
        {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "phone": "1234567890",
            "linkedin_url": "https://linkedin.com/in/johndoe",
            "company_id": 1,
        },
        {
            "first_name": "Jane",
            "last_name": "Smith",
            "email": "jane.smith@example.com",
            "linkedin_url": "https://linkedin.com/in/janesmith",
            "company_id": 2,
        },
        {
            "first_name": "Mike",
            "last_name": "Taylor",
            "phone": "9876543210",
            "company_id": 1,
        },
        {
            "first_name": "Emily",
            "last_name": "Davis",
            "email": "emily.davis@example.com",
            "company_id": 2,
        },
        {
            "first_name": "Chris",
            "last_name": "Brown",
            "linkedin_url": "https://linkedin.com/in/chrisbrown",
            "company_id": 1,
        },
    ]
    update_data = {
        "first_name": "OX",
        "id": 1,
    }


class TestKeywordCRUD(CRUDTestBase):
    endpoint = "/keywords"
    schema = schemas.Keyword
    out_schema = schemas.KeywordOut
    test_data = "test_keywords"
    create_data = [
        {"name": "TypeScript"},
        {"name": "PostgreSQL"},
        {"name": "FastAPI"},
        {"name": "Machine Learning"},
        {"name": "DevOps"},
    ]
    update_data = {
        "id": 1,
        "name": "Updated Python",
    }
