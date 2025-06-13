import base64

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
        {"name": "TechStartup Inc"},  # Incomplete company data
    ]
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
    create_data = [
        {"name": "TypeScript"},
        {"name": "PostgreSQL"},
        {"name": "FastAPI"},
        {"name": "Machine Learning"},
        {"name": "DevOps"},
        {"name": "Docker"},
        {"name": "Kubernetes"},
        {"name": "AWS"},
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
        {"name": "AngelList", "url": "https://angel.co"},
        {"name": "Stack Overflow Jobs", "url": "https://stackoverflow.com/jobs"},
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
        {"city": "Berlin"},  # Incomplete location - only city
        {"country": "Canada"},  # Incomplete location - only country
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
            "role": "Senior Engineering Manager",
            "company_id": 1,
        },
        {
            "first_name": "Jane",
            "last_name": "Smith",
            "email": "jane.smith@example.com",
            "linkedin_url": "https://linkedin.com/in/janesmith",
            "role": "Product Manager",
            "company_id": 2,
        },
        {
            "first_name": "Mike",
            "last_name": "Taylor",
            "phone": "9876543210",
            "role": "Lead Developer",
            "company_id": 1,
        },
        {
            "first_name": "Emily",
            "last_name": "Davis",
            "email": "emily.davis@example.com",
            "role": "DevOps Engineer",
            "company_id": 2,
        },
        {
            "first_name": "Chris",
            "last_name": "Brown",
            "linkedin_url": "https://linkedin.com/in/chrisbrown",
            "role": "Data Science Manager",
            "company_id": 1,
        },
        {
            # Incomplete person - no company
            "first_name": "Anonymous",
            "last_name": "Recruiter",
            "company_id": None,
        },
        {
            # Incomplete person - no contact details but has company
            "first_name": "Tech",
            "last_name": "Recruiter",
            "role": "Talent Acquisition",
            "company_id": 3,  # Changed from 4 to 3 (Oxford PV from create_data)
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
            "location_id": 2,  # Beverly Hills
            "note": "Excellent opportunity for senior developer",
        },
        {
            "title": "Full Stack JavaScript Developer",
            "salary_min": 65000,
            "salary_max": 105000,
            "description": "Build end-to-end web applications with React and Node.js.",
            "personal_rating": 8,
            "url": "https://example.com/jobs/fullstack_js_developer",
            "company_id": 2,  # Second test company
            "location_id": 1,  # New York
            "note": "Great team culture mentioned in reviews",
        },
        {
            "title": "Remote React Developer",
            "salary_min": 60000,
            "salary_max": 95000,
            "description": "Build modern React applications for distributed team.",
            "personal_rating": 7,
            "url": "https://example.com/jobs/remote_react_developer",
            "company_id": 1,
            "location_id": 4,  # San Francisco (remote)
        },
        {
            "title": "Cloud Engineer",
            "salary_min": 75000,
            "salary_max": 120000,
            "description": "Design and maintain AWS cloud infrastructure.",
            "personal_rating": 8,
            "url": "https://example.com/jobs/cloud_engineer",
            "company_id": 2,
            "location_id": 3,  # London
        },
        {
            "title": "Frontend Developer",
            "salary_min": 55000,
            "salary_max": 85000,
            "description": "Create beautiful user interfaces with React and JavaScript.",
            "personal_rating": 6,
            "url": "https://example.com/jobs/frontend_developer",
            "company_id": 1,
            "location_id": 5,  # Germany (remote)
        },
        {
            # Incomplete job - no company
            "title": "Backend Developer",
            "description": "Looking for a backend developer with Python experience.",
            "company_id": None,
            "location_id": 4,  # San Francisco (remote)
        },
        {
            # Incomplete job - no location
            "title": "Software Engineer Intern",
            "description": "Summer internship opportunity for computer science students.",
            "personal_rating": 3,
            "company_id": 3,  # Third company from create_data
            "location_id": None,
        },
        {
            # Incomplete job - minimal information
            "title": "Developer Position",
            "company_id": 3,  # Third company from create_data
            "location_id": 5,  # Germany (remote) - changed from 6 to 5
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
            "cv": base64.b64encode(
                b"Sample CV content - John Doe, Software Engineer with 5 years experience..."
            ).decode("utf-8"),
            "cover_letter": base64.b64encode(
                b"Dear Hiring Manager, I am writing to express my interest in the position..."
            ).decode("utf-8"),
        },
        {
            "date": "2024-01-16T14:30:00",
            "url": "https://company2.com/apply/fullstack-js",
            "job_id": 2,
            "status": "Interview Scheduled",
            "note": "Phone screening scheduled for next week",
            "cv": base64.b64encode(
                b"Sample CV content - Full stack developer with React and Node.js experience..."
            ).decode("utf-8"),
            "cover_letter": None,  # No cover letter submitted
        },
        {
            "date": "2024-01-17T09:15:00",
            "job_id": 3,
            "status": "Applied",
            "note": "Applied through LinkedIn",
            "cv": None,  # No CV attached (used portfolio instead)
            "cover_letter": base64.b64encode(b"Portfolio-based application cover letter...").decode("utf-8"),
        },
        {
            "date": "2024-01-18T16:45:00",
            "url": "https://company3.com/careers/cloud-engineer",
            "job_id": 4,
            "status": "Rejected",
            "note": "Not enough cloud experience",
            "cv": base64.b64encode(b"Junior developer CV with limited cloud experience...").decode("utf-8"),
            "cover_letter": base64.b64encode(b"Standard cover letter for cloud engineer position...").decode("utf-8"),
        },
        {
            "date": "2024-01-19T11:20:00",
            "job_id": 5,
            "status": "Applied",
            "cv": base64.b64encode(b"Frontend specialist CV with React focus...").decode("utf-8"),
            "cover_letter": base64.b64encode(b"Frontend developer cover letter...").decode("utf-8"),
        },
        {
            # Incomplete application - no CV or cover letter
            "date": "2024-01-20T13:30:00",
            "job_id": 6,
            "status": "Applied",
            "note": "Quick application through company form",
            "cv": None,
            "cover_letter": None,
        },
    ]
    update_data = {
        "status": "Interview Completed",
        "note": "Technical interview went well",
        "cv": base64.b64encode(b"Updated CV with recent project experience...").decode("utf-8"),
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
            "location_id": 4,  # Remote
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
        {
            # Incomplete interview - no location specified
            "date": "2024-01-25T16:00:00",
            "location_id": None,
            "jobapplication_id": 6,
            "note": "Phone screening with recruiter. Location TBD.",
        },
        {
            # Incomplete interview - minimal information
            "date": "2024-01-26T09:00:00",
            "location_id": 7,  # Canada location (only country specified)
            "jobapplication_id": 1,  # Same application, second interview
            "note": None,
        },
    ]
    update_data = {
        "note": "Interview went very well - positive feedback",
        "date": "2024-01-20T10:00:00",
        "id": 1,
    }


class TestFileCRUD(CRUDTestBase):
    endpoint = "/files"
    schema = schemas.File
    out_schema = schemas.FileOut
    test_data = "test_files"
    create_data = [
        {
            "filename": "john_doe_cv_2024.pdf",
            "content": b"""John Doe - Software Engineer

EXPERIENCE:
- Senior Software Developer at TechCorp (2019-2024)
- Full Stack Developer at StartupXYZ (2017-2019)
- Junior Developer at WebSolutions (2015-2017)

SKILLS:
- Python, JavaScript, React, Node.js
- AWS, Docker, Kubernetes
- PostgreSQL, MongoDB
- Git, CI/CD, Agile methodologies

EDUCATION:
- B.S. Computer Science, University of Technology (2015)

CERTIFICATIONS:
- AWS Certified Solutions Architect
- Certified Kubernetes Administrator""",
            "type": "application/pdf",
            "size": 2048,
        },
        {
            "filename": "cover_letter_senior_python.pdf",
            "content": b"""Dear Hiring Manager,

I am writing to express my strong interest in the Senior Python Developer position at your company. With over 8 years of experience in full-stack development and a proven track record of delivering scalable solutions, I am excited about the opportunity to contribute to your team.

In my current role at TechCorp, I have:
- Led a team of 5 developers in building microservices architecture
- Implemented CI/CD pipelines that reduced deployment time by 60%
- Designed and developed RESTful APIs serving 1M+ requests daily
- Mentored junior developers and conducted code reviews

I am particularly drawn to your company's mission and would love to discuss how my experience with Python, React, and cloud technologies can help drive your projects forward.

Thank you for considering my application. I look forward to hearing from you.

Best regards,
John Doe""",
            "type": "application/pdf",
            "size": 1536,
        },
        {
            "filename": "fullstack_developer_cv.pdf",
            "content": b"Full stack developer CV with React and Node.js experience - detailed project portfolio included...",
            "type": "application/pdf",
            "size": 1792,
        },
        {
            "filename": "portfolio_cover_letter.txt",
            "content": b"Portfolio-based application cover letter highlighting creative projects and technical achievements...",
            "type": "text/plain",
            "size": 512,
        },
        {
            "filename": "junior_cloud_cv.docx",
            "content": b"Junior developer CV with limited cloud experience but strong fundamentals in AWS and containerization...",
            "type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "size": 1024,
        },
        {
            "filename": "cloud_engineer_cover_letter.pdf",
            "content": b"Standard cover letter for cloud engineer position emphasizing DevOps skills and infrastructure experience...",
            "type": "application/pdf",
            "size": 768,
        },
        {
            "filename": "frontend_specialist_cv.pdf",
            "content": b"Frontend specialist CV with React focus - includes modern JavaScript frameworks and UI/UX design experience...",
            "type": "application/pdf",
            "size": 1280,
        },
        {
            "filename": "frontend_developer_cover_letter.pdf",
            "content": b"Frontend developer cover letter showcasing responsive design skills and component library experience...",
            "type": "application/pdf",
            "size": 640,
        },
        {
            "filename": "updated_cv_2024.pdf",
            "content": b"Updated CV with recent project experience including microservices architecture and cloud-native development...",
            "type": "application/pdf",
            "size": 2304,
        },
    ]
    update_data = {
        "filename": "updated_john_doe_cv_2024.pdf",
        "size": 2560,
        "id": 1,
    }
