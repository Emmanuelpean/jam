from app import schemas
from conftest import CRUDTestBase


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


class TestJobCRUD(CRUDTestBase):
    endpoint = "/jobs"
    schema = schemas.Job
    out_schema = schemas.JobOut
    test_data = "test_jobs"
    add_fixture = ["test_persons", "test_locations", "test_keywords"]
    create_data = [
        # Jobs using existing locations, companies, and keywords
        {
            "title": "Senior Python Developer",
            "salary_min": 80000,
            "salary_max": 130000,
            "description": "Lead backend development using Python and modern frameworks.",
            "personal_rating": 9,
            "url": "https://example.com/jobs/senior_python_developer",
            "company_id": 1,  # First test company
            "location_id": 2,  # Oxford city
        },
        {
            "title": "Full Stack JavaScript Developer",
            "salary_min": 65000,
            "salary_max": 105000,
            "description": "Build end-to-end web applications with React and Node.js.",
            "personal_rating": 8,
            "url": "https://example.com/jobs/fullstack_js_developer",
            "company_id": 2,  # Second test company
            "location_id": 1,  # OX5 1HN postcode location
        },
        {
            "title": "Remote React Developer",
            "salary_min": 60000,
            "salary_max": 95000,
            "description": "Build modern React applications for distributed team.",
            "personal_rating": 7,
            "url": "https://example.com/jobs/remote_react_developer",
            "company_id": 1,
            "location_id": 4,  # Remote location
        },
        {
            "title": "Cloud Engineer",
            "salary_min": 75000,
            "salary_max": 120000,
            "description": "Design and maintain AWS cloud infrastructure.",
            "personal_rating": 8,
            "url": "https://example.com/jobs/cloud_engineer",
            "company_id": 2,
            "location_id": 3,  # UK country location
        },
        {
            "title": "Frontend Developer",
            "salary_min": 55000,
            "salary_max": 85000,
            "description": "Create beautiful user interfaces with React and JavaScript.",
            "personal_rating": 6,
            "url": "https://example.com/jobs/frontend_developer",
            "company_id": 1,
            "location_id": 5,  # OX5 1HN + UK location
        },
        {
            "title": "DevOps Engineer",
            "salary_min": 70000,
            "salary_max": 110000,
            "description": "Automate deployment pipelines and manage AWS infrastructure.",
            "personal_rating": 7,
            "url": "https://example.com/jobs/devops_engineer",
            "company_id": 2,
            "location_id": 2,  # Oxford city
        },
        {
            "title": "Junior JavaScript Developer",
            "salary_min": 45000,
            "salary_max": 65000,
            "description": "Entry-level position for new graduates with JavaScript training.",
            "personal_rating": 5,
            "url": "https://example.com/jobs/junior_js_developer",
            "company_id": 1,
            "location_id": 1,  # OX5 1HN postcode
        },
        {
            "title": "Remote Python Data Engineer",
            "salary_min": 85000,
            "salary_max": 125000,
            "description": "Process large datasets and build data pipelines using Python.",
            "personal_rating": 9,
            "url": "https://example.com/jobs/remote_python_data_engineer",
            "company_id": 2,
            "location_id": 4,  # Remote
        },
        {
            "title": "Full Stack React Engineer",
            "salary_min": 70000,
            "salary_max": 100000,
            "description": "Develop complete web applications using React, Node.js, and AWS.",
            "personal_rating": 8,
            "url": "https://example.com/jobs/fullstack_react_engineer",
            "company_id": 1,
            "location_id": 3,  # UK country
        },
        {
            "title": "Senior Node.js Developer",
            "salary_min": 75000,
            "salary_max": 115000,
            "description": "Build scalable backend services with Node.js and cloud technologies.",
            "personal_rating": 8,
            "url": "https://example.com/jobs/senior_nodejs_developer",
            "company_id": 2,
            "location_id": 5,  # OX5 1HN + UK
        },
        {
            "title": "Remote Full Stack Developer",
            "salary_min": 65000,
            "salary_max": 95000,
            "description": "Work remotely on diverse projects using modern tech stack.",
            "personal_rating": 7,
            "url": "https://example.com/jobs/remote_fullstack",
            "company_id": 1,
            "location_id": 4,  # Remote
        },
        {
            "title": "AWS Solutions Architect",
            "salary_min": 90000,
            "salary_max": 140000,
            "description": "Design and implement cloud solutions using AWS services.",
            "personal_rating": 9,
            "url": "https://example.com/jobs/aws_solutions_architect",
            "company_id": 2,
            "location_id": 2,  # Oxford city
        },
        {
            "title": "React Frontend Specialist",
            "salary_min": 60000,
            "salary_max": 90000,
            "description": "Specialize in building complex React applications and components.",
            "personal_rating": 7,
            "url": "https://example.com/jobs/react_frontend_specialist",
            "company_id": 1,
            "location_id": 1,  # OX5 1HN postcode
        },
        {
            "title": "Python Backend Engineer",
            "salary_min": 70000,
            "salary_max": 105000,
            "description": "Develop robust backend systems and APIs using Python.",
            "personal_rating": 8,
            "url": "https://example.com/jobs/python_backend_engineer",
            "company_id": 2,
            "location_id": 3,  # UK country
        },
        {
            "title": "Multi-Stack Developer",
            "salary_min": 65000,
            "salary_max": 100000,
            "description": "Work across the full technology stack with Python, JavaScript, React, Node.js, and AWS.",
            "personal_rating": 8,
            "url": "https://example.com/jobs/multi_stack_developer",
            "company_id": 1,
            "location_id": 4,  # Remote
        },
    ]
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
    create_data = [
        {
            "date": "2024-01-15T10:00:00",
            "url": "https://company1.com/apply/senior-python",
            "job_id": 1,
            "status": "Applied",
            "note": "Submitted application with cover letter",
        },
        {
            "date": "2024-01-16T14:30:00",
            "url": "https://company2.com/apply/fullstack-js",
            "job_id": 2,
            "status": "Interview Scheduled",
            "note": "Phone screening scheduled for next week",
        },
        {"date": "2024-01-17T09:15:00", "job_id": 3, "status": "Applied", "note": "Applied through LinkedIn"},
        {
            "date": "2024-01-18T16:45:00",
            "url": "https://company3.com/careers/cloud-engineer",
            "job_id": 4,
            "status": "Rejected",
            "note": "Not enough cloud experience",
        },
        {"date": "2024-01-19T11:20:00", "job_id": 5, "status": "Applied"},
    ]
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
    create_data = [
        {
            "date": "2024-01-20T09:30:00",
            "location_id": 1,
            "jobapplication_id": 1,
            "note": "First round technical interview",
        },
        {
            "date": "2024-01-21T14:00:00",
            "location_id": 2,
            "jobapplication_id": 2,
            "note": "HR screening call",
        },
        {
            "date": "2024-01-22T10:15:00",
            "jobapplication_id": 3,
            "note": "Remote technical assessment",
        },
        {
            "date": "2024-01-23T16:30:00",
            "location_id": 1,
            "jobapplication_id": 4,
            "note": "Final round with team lead",
        },
        {
            "date": "2024-01-24T11:45:00",
            "location_id": 3,
            "jobapplication_id": 5,
            "note": "Cultural fit interview",
        },
    ]
    update_data = {
        "note": "Interview went very well - positive feedback",
        "date": "2024-01-20T10:00:00",
        "id": 1,
    }
