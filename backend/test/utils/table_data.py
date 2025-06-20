"""Centralized test data for both conftest.py and seed_database.py"""

from test.utils.files import load_all_resource_files

RESOURCE_FILES = load_all_resource_files()


USERS_DATA = [
    {
        "email": "emmanuel.pean@gmail.com",
        "password": "password1",
    },
    {
        "email": "jane.smith@example.com",
        "password": "password2",
    },
    {
        "email": "mike.johnson@example.com",
        "password": "password3",
    },
    {
        "email": "sarah.wilson@example.com",
        "password": "password4",
    },
    {
        "email": "admin@example.com",
        "password": "password5",
    },
]

# Company test data
COMPANIES_DATA = [
    {
        "name": "Tech Corp",
        "description": "A leading technology company specializing in web applications",
        "url": "https://techcorp.com",
        "owner_id": 1,
    },
    {
        "name": "StartupXYZ",
        "description": "An innovative startup focused on AI-driven solutions",
        "url": "https://startupxyz.com",
        "owner_id": 1,
    },
    {
        "name": "Oxford PV",
        "description": "Oxford-based company specializing in photovoltaic technology",
        "url": "https://oxfordpv.com",
        "owner_id": 1,
    },
    {
        "name": "WebSolutions Ltd",
        "description": "Full-service web development and digital marketing agency",
        "url": "https://websolutions.com",
        "owner_id": 1,
    },
    {
        "name": "DataTech Industries",
        "description": "Big data analytics and business intelligence solutions",
        "url": "https://datatech.com",
        "owner_id": 1,
    },
    {
        "name": "CloudNine Systems",
        "description": "Enterprise cloud infrastructure and DevOps solutions",
        "url": "https://cloudnine.com",
        "owner_id": 1,
    },
    {
        "name": "FinTech Solutions",
        "description": "Financial technology and blockchain innovations",
        "url": "https://fintechsol.com",
        "owner_id": 1,
    },
    {
        "name": "GreenEnergy Co",
        "description": "Renewable energy and sustainability technology",
        "url": "https://greenenergy.com",
        "owner_id": 1,
    },
]

# Location test data
LOCATIONS_DATA = [
    {
        "postcode": "10001",
        "city": "New York",
        "country": "USA",
        "remote": False,
        "owner_id": 1,
    },
    {
        "postcode": "90210",
        "city": "Beverly Hills",
        "country": "USA",
        "remote": False,
        "owner_id": 1,
    },
    {
        "postcode": "SW1A 1AA",
        "city": "London",
        "country": "UK",
        "remote": False,
        "owner_id": 1,
    },
    {
        "city": "San Francisco",
        "country": "USA",
        "remote": True,
        "owner_id": 1,
    },
    {
        "country": "Germany",
        "remote": True,
        "owner_id": 1,
    },
    {
        "postcode": "OX1 2JD",
        "city": "Oxford",
        "country": "UK",
        "remote": False,
        "owner_id": 1,
    },
    {
        "country": "Canada",
        "remote": True,
        "owner_id": 1,
    },
    {
        "postcode": "M5V 3A8",
        "city": "Toronto",
        "country": "Canada",
        "remote": False,
        "owner_id": 1,
    },
    {
        "postcode": "2000",
        "city": "Sydney",
        "country": "Australia",
        "remote": False,
        "owner_id": 1,
    },
    {
        "city": "Amsterdam",
        "country": "Netherlands",
        "remote": False,
        "owner_id": 1,
    },
]

# Aggregator test data
AGGREGATORS_DATA = [
    {
        "name": "LinkedIn",
        "url": "https://linkedin.com/jobs",
        "owner_id": 1,
    },
    {
        "name": "Indeed",
        "url": "https://indeed.com",
        "owner_id": 1,
    },
    {
        "name": "Glassdoor",
        "url": "https://glassdoor.com",
        "owner_id": 1,
    },
    {
        "name": "AngelList",
        "url": "https://angel.co",
        "owner_id": 1,
    },
    {
        "name": "Stack Overflow Jobs",
        "url": "https://stackoverflow.com/jobs",
        "owner_id": 1,
    },
    {
        "name": "Company Website",
        "url": "https://example.com/careers",
        "owner_id": 1,
    },
    {
        "name": "Recruiter",
        "url": "https://recruiter-portal.com",
        "owner_id": 1,
    },
    {
        "name": "Job Fair",
        "url": "https://jobfair.com",
        "owner_id": 1,
    },
]

# Keyword test data
KEYWORDS_DATA = [
    {
        "name": "Python",
        "owner_id": 1,
    },
    {
        "name": "JavaScript",
        "owner_id": 1,
    },
    {
        "name": "React",
        "owner_id": 1,
    },
    {
        "name": "Node.js",
        "owner_id": 1,
    },
    {
        "name": "TypeScript",
        "owner_id": 1,
    },
    {
        "name": "PostgreSQL",
        "owner_id": 1,
    },
    {
        "name": "FastAPI",
        "owner_id": 1,
    },
    {
        "name": "Machine Learning",
        "owner_id": 1,
    },
    {
        "name": "DevOps",
        "owner_id": 1,
    },
    {
        "name": "Docker",
        "owner_id": 1,
    },
    {
        "name": "Kubernetes",
        "owner_id": 1,
    },
    {
        "name": "AWS",
        "owner_id": 1,
    },
    {
        "name": "REST API",
        "owner_id": 1,
    },
    {
        "name": "Git",
        "owner_id": 1,
    },
    {
        "name": "Agile",
        "owner_id": 1,
    },
    {
        "name": "Java",
        "owner_id": 1,
    },
    {
        "name": "Spring Boot",
        "owner_id": 1,
    },
    {
        "name": "Vue.js",
        "owner_id": 1,
    },
    {
        "name": "Angular",
        "owner_id": 1,
    },
    {
        "name": "MongoDB",
        "owner_id": 1,
    },
]

# Person test data
PERSONS_DATA = [
    {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@techcorp.com",
        "phone": "1234567890",
        "linkedin_url": "https://linkedin.com/in/johndoe",
        "role": "Senior Engineering Manager",
        "company_id": 1,  # Tech Corp
        "owner_id": 1,
    },
    {
        "first_name": "Jane",
        "last_name": "Smith",
        "email": "jane.smith@startupxyz.com",
        "linkedin_url": "https://linkedin.com/in/janesmith",
        "role": "Product Manager",
        "company_id": 2,  # StartupXYZ
        "owner_id": 1,
    },
    {
        "first_name": "Mike",
        "last_name": "Taylor",
        "phone": "9876543210",
        "role": "Lead Developer",
        "company_id": 1,  # Tech Corp
        "owner_id": 1,
    },
    {
        "first_name": "Emily",
        "last_name": "Davis",
        "email": "emily.davis@startupxyz.com",
        "role": "DevOps Engineer",
        "company_id": 2,  # StartupXYZ
        "owner_id": 1,
    },
    {
        "first_name": "Chris",
        "last_name": "Brown",
        "linkedin_url": "https://linkedin.com/in/chrisbrown",
        "role": "Data Science Manager",
        "company_id": 1,  # Tech Corp
        "owner_id": 1,
    },
    {
        "first_name": "Sarah",
        "last_name": "Wilson",
        "email": "sarah.wilson@oxfordpv.com",
        "role": "Technical Recruiter",
        "company_id": 3,  # Oxford PV
        "owner_id": 1,
    },
    {
        "first_name": "Alex",
        "last_name": "Johnson",
        "email": "alex.johnson@websolutions.com",
        "role": "Full Stack Developer",
        "company_id": 4,  # WebSolutions Ltd
        "owner_id": 1,
    },
    {
        "first_name": "Lisa",
        "last_name": "Chen",
        "email": "lisa.chen@datatech.com",
        "role": "Data Scientist",
        "company_id": 5,  # DataTech Industries
        "owner_id": 1,
    },
    {
        "first_name": "Robert",
        "last_name": "Martinez",
        "phone": "555-0123",
        "role": "Cloud Architect",
        "company_id": 6,  # CloudNine Systems
        "owner_id": 1,
    },
    {
        "first_name": "Anonymous",
        "last_name": "Recruiter",
        "company_id": None,
        "owner_id": 1,
    },
]

# Job test data with deadline and source_id
JOBS_DATA = [
    {
        "title": "Senior Python Developer",
        "salary_min": 80000,
        "salary_max": 130000,
        "description": "Lead backend development using Python and modern frameworks. Work with a talented team to build scalable web applications.",
        "personal_rating": 5,
        "url": "https://techcorp.com/jobs/senior_python_developer",
        "company_id": 1,  # Tech Corp
        "location_id": 2,  # Beverly Hills
        "note": "Excellent opportunity for senior developer",
        "deadline": "2024-02-15T23:59:59",
        "source_id": 1,  # LinkedIn
        "owner_id": 1,
    },
    {
        "title": "Full Stack JavaScript Developer",
        "salary_min": 65000,
        "salary_max": 105000,
        "description": "Build end-to-end web applications with React and Node.js. Join our dynamic startup environment.",
        "personal_rating": 4,
        "url": "https://startupxyz.com/jobs/fullstack_js_developer",
        "company_id": 2,  # StartupXYZ
        "location_id": 1,  # New York
        "note": "Great team culture mentioned in reviews",
        "deadline": "2024-02-20T17:00:00",
        "source_id": 2,  # Indeed
        "owner_id": 1,
    },
    {
        "title": "Remote React Developer",
        "salary_min": 60000,
        "salary_max": 95000,
        "description": "Build modern React applications for distributed team. Full remote position with flexible hours.",
        "personal_rating": 3,
        "url": "https://techcorp.com/jobs/remote_react_developer",
        "company_id": 1,  # Tech Corp
        "location_id": 4,  # San Francisco (remote)
        "deadline": "2024-03-01T12:00:00",
        "source_id": 6,  # Company Website
        "owner_id": 1,
    },
    {
        "title": "Cloud Engineer",
        "salary_min": 75000,
        "salary_max": 120000,
        "description": "Design and maintain AWS cloud infrastructure. Experience with Kubernetes and Docker required.",
        "personal_rating": 4,
        "url": "https://startupxyz.com/jobs/cloud_engineer",
        "company_id": 2,  # StartupXYZ
        "location_id": 3,  # London
        "deadline": "2024-02-28T23:59:59",
        "source_id": 3,  # Glassdoor
        "owner_id": 1,
    },
    {
        "title": "Frontend Developer",
        "salary_min": 55000,
        "salary_max": 85000,
        "description": "Create beautiful user interfaces with React and JavaScript. Focus on user experience and modern design.",
        "personal_rating": 2,
        "url": "https://techcorp.com/jobs/frontend_developer",
        "company_id": 1,  # Tech Corp
        "location_id": 5,  # Germany (remote)
        "source_id": 5,  # Stack Overflow Jobs
        "owner_id": 1,
    },
    {
        "title": "Backend Developer",
        "description": "Looking for a backend developer with Python experience. FastAPI knowledge preferred.",
        "location_id": 4,  # San Francisco (remote)
        "deadline": "2024-04-15T18:00:00",
        "source_id": 7,  # Recruiter
        "owner_id": 1,
    },
    {
        "title": "Software Engineer Intern",
        "description": "Summer internship opportunity for computer science students. Great learning environment.",
        "personal_rating": 1,
        "company_id": 3,  # Oxford PV
        "deadline": "2024-03-31T23:59:59",
        "source_id": 8,  # Job Fair
        "owner_id": 1,
    },
    {
        "title": "DevOps Engineer",
        "salary_min": 70000,
        "salary_max": 110000,
        "description": "Manage CI/CD pipelines and cloud infrastructure. Docker and Kubernetes experience required.",
        "personal_rating": 4,
        "url": "https://cloudnine.com/careers/devops",
        "company_id": 6,  # CloudNine Systems
        "location_id": 8,  # Toronto
        "deadline": "2024-02-25T16:00:00",
        "source_id": 1,  # LinkedIn
        "owner_id": 1,
    },
    {
        "title": "Data Scientist",
        "salary_min": 85000,
        "salary_max": 135000,
        "description": "Analyze large datasets and build machine learning models. Python and R experience required.",
        "personal_rating": 5,
        "url": "https://datatech.com/jobs/data-scientist",
        "company_id": 5,  # DataTech Industries
        "location_id": 9,  # Sydney
        "deadline": "2024-03-10T09:00:00",
        "source_id": 4,  # AngelList
        "owner_id": 1,
    },
    {
        "title": "Java Spring Developer",
        "salary_min": 70000,
        "salary_max": 115000,
        "description": "Develop enterprise applications using Java and Spring Boot. Microservices architecture experience preferred.",
        "personal_rating": 3,
        "url": "https://websolutions.com/careers/java-dev",
        "company_id": 4,  # WebSolutions Ltd
        "location_id": 10,  # Amsterdam
        "source_id": 2,  # Indeed
        "owner_id": 1,
    },
    {
        "title": "Blockchain Developer",
        "salary_min": 90000,
        "salary_max": 150000,
        "description": "Build decentralized applications and smart contracts. Solidity and Web3 experience required.",
        "personal_rating": 5,
        "url": "https://fintechsol.com/jobs/blockchain",
        "company_id": 7,  # FinTech Solutions
        "location_id": 7,  # Canada (remote)
        "deadline": "2024-02-18T23:59:59",
        "source_id": 4,  # AngelList
        "owner_id": 1,
    },
    {
        "title": "Sustainability Tech Lead",
        "salary_min": 95000,
        "salary_max": 140000,
        "description": "Lead development of renewable energy management systems. IoT and embedded systems experience preferred.",
        "personal_rating": 4,
        "company_id": 8,  # GreenEnergy Co
        "location_id": 6,  # Oxford
        "deadline": "2024-03-05T15:30:00",
        "source_id": 6,  # Company Website
        "owner_id": 1,
    },
    {
        "title": "Junior Web Developer",
        "salary_min": 40000,
        "salary_max": 60000,
        "description": "Entry-level position for recent graduates. Training provided in modern web technologies.",
        "personal_rating": 2,
        "company_id": 4,  # WebSolutions Ltd
        "location_id": 3,  # London
        "source_id": 8,  # Job Fair
        "owner_id": 1,
    },
    {
        "title": "Technical Product Manager",
        "salary_min": 100000,
        "salary_max": 160000,
        "description": "Bridge technical and business teams. Previous engineering experience required.",
        "personal_rating": 5,
        "url": "https://startupxyz.com/careers/tech-pm",
        "company_id": 2,  # StartupXYZ
        "location_id": 1,  # New York
        "deadline": "2024-02-22T12:00:00",
        "source_id": 7,  # Recruiter
        "owner_id": 1,
    },
    {
        "title": "Mobile App Developer",
        "salary_min": 65000,
        "salary_max": 100000,
        "description": "Develop cross-platform mobile applications. React Native experience preferred.",
        "personal_rating": 3,
        "company_id": 1,  # Tech Corp
        "location_id": 4,  # San Francisco (remote)
        "source_id": 5,  # Stack Overflow Jobs
        "owner_id": 1,
    },
]

# File test data
FILES_DATA = [
    {
        "filename": "john_doe_cv_2024.pdf",
        "owner_id": 1,
        **RESOURCE_FILES["CV.pdf"],
    },
    {
        "filename": "cover_letter_senior_python.docx",
        "owner_id": 1,
        **RESOURCE_FILES["Cover Letter.docx"],
    },
    {
        "filename": "fullstack_developer_cv.pdf",
        "owner_id": 1,
        **RESOURCE_FILES["CV.pdf"],
    },
    {
        "filename": "portfolio_cover_letter.txt",
        "owner_id": 1,
        **RESOURCE_FILES["Cover Letter.txt"],
    },
    {
        "filename": "junior_cloud_cv.docx",
        "owner_id": 1,
        **RESOURCE_FILES["Cover Letter.docx"],
    },
    {
        "filename": "frontend_specialist_cv.pdf",
        "owner_id": 1,
        **RESOURCE_FILES["CV.pdf"],
    },
    {
        "filename": "data_scientist_cv.pdf",
        "owner_id": 1,
        **RESOURCE_FILES["CV.pdf"],
    },
    {
        "filename": "blockchain_dev_cover_letter.docx",
        "owner_id": 1,
        **RESOURCE_FILES["Cover Letter.docx"],
    },
]

# Job Application test data
JOB_APPLICATIONS_DATA = [
    {
        "date": "2024-01-15T10:00:00",
        "url": "https://techcorp.com/apply/senior-python",
        "job_id": 1,
        "status": "Applied",
        "note": "Submitted application with cover letter",
        "cv_id": 1,
        "cover_letter_id": 2,
        "owner_id": 1,
    },
    {
        "date": "2024-01-16T14:30:00",
        "url": "https://startupxyz.com/apply/fullstack-js",
        "job_id": 2,
        "status": "Interview",
        "note": "Phone screening scheduled for next week",
        "cv_id": 3,
        "owner_id": 1,
    },
    {
        "date": "2024-01-17T09:15:00",
        "job_id": 3,
        "status": "Applied",
        "note": "Applied through LinkedIn",
        "cover_letter_id": 4,
        "owner_id": 1,
    },
    {
        "date": "2024-01-18T16:45:00",
        "url": "https://startupxyz.com/careers/cloud-engineer",
        "job_id": 4,
        "status": "Rejected",
        "note": "Not enough cloud experience",
        "cv_id": 5,
        "owner_id": 1,
    },
    {
        "date": "2024-01-19T11:20:00",
        "job_id": 9,
        "status": "Offer",
        "note": "Received offer! Negotiating salary",
        "cv_id": 7,
        "cover_letter_id": 8,
        "owner_id": 1,
    },
    {
        "date": "2024-01-20T13:30:00",
        "job_id": 11,
        "status": "Applied",
        "note": "Exciting blockchain opportunity",
        "cv_id": 1,
        "owner_id": 1,
    },
    {
        "date": "2024-01-21T08:45:00",
        "url": "https://fintechsol.com/apply",
        "job_id": 14,
        "status": "Interview",
        "note": "Technical interview scheduled",
        "cv_id": 3,
        "cover_letter_id": 2,
        "owner_id": 1,
    },
]

# Interview test data
INTERVIEWS_DATA = [
    {
        "date": "2024-01-20T09:30:00",
        "type": "HR",
        "location_id": 1,
        "jobapplication_id": 1,
        "note": "Initial HR screening call",
        "owner_id": 1,
    },
    {
        "date": "2024-01-21T14:00:00",
        "type": "Technical",
        "location_id": 2,
        "jobapplication_id": 2,
        "note": "Coding challenge and system design",
        "owner_id": 1,
    },
    {
        "date": "2024-01-22T10:15:00",
        "type": "Management",
        "location_id": 4,  # Remote
        "jobapplication_id": 2,
        "note": "Meeting with team lead",
        "owner_id": 1,
    },
    {
        "date": "2024-01-23T16:30:00",
        "type": "Technical",
        "location_id": 3,
        "jobapplication_id": 5,
        "note": "Machine learning case study",
        "owner_id": 1,
    },
    {
        "date": "2024-01-24T11:45:00",
        "type": "Final",
        "location_id": 1,
        "jobapplication_id": 5,
        "note": "Final round with CTO",
        "owner_id": 1,
    },
    {
        "date": "2024-01-25T15:00:00",
        "type": "HR",
        "location_id": 7,  # Canada remote
        "jobapplication_id": 7,
        "note": "Cultural fit interview",
        "owner_id": 1,
    },
    {
        "date": "2024-01-26T09:00:00",
        "type": "Technical",
        "location_id": 1,
        "jobapplication_id": 7,
        "note": "Blockchain architecture discussion",
        "owner_id": 1,
    },
]

# Relationship mappings for many-to-many relationships
JOB_KEYWORD_MAPPINGS = [
    {"job_id": 1, "keyword_ids": [1, 7, 6, 13]},  # Senior Python Developer
    {"job_id": 2, "keyword_ids": [2, 3, 4, 13]},  # Full Stack JS Developer
    {"job_id": 3, "keyword_ids": [3, 2, 14, 15]},  # Remote React Developer
    {"job_id": 4, "keyword_ids": [12, 10, 11, 9]},  # Cloud Engineer
    {"job_id": 5, "keyword_ids": [2, 3, 14]},  # Frontend Developer
    {"job_id": 6, "keyword_ids": [1, 7, 13]},  # Backend Developer
    {"job_id": 8, "keyword_ids": [9, 10, 11, 12]},  # DevOps Engineer
    {"job_id": 9, "keyword_ids": [1, 8, 6]},  # Data Scientist
    {"job_id": 10, "keyword_ids": [16, 17, 13]},  # Java Spring Developer
    {"job_id": 11, "keyword_ids": [2, 1]},  # Blockchain Developer
    {"job_id": 12, "keyword_ids": [1, 2]},  # Sustainability Tech Lead
    {"job_id": 13, "keyword_ids": [2, 3, 14]},  # Junior Web Developer
    {"job_id": 14, "keyword_ids": [15, 1, 3]},  # Technical Product Manager
    {"job_id": 15, "keyword_ids": [2, 3, 18]},  # Mobile App Developer
]

JOB_CONTACT_MAPPINGS = [
    {"job_id": 1, "person_ids": [1, 3]},  # Senior Python Developer
    {"job_id": 2, "person_ids": [2, 4]},  # Full Stack JS Developer
    {"job_id": 3, "person_ids": [1]},  # Remote React Developer
    {"job_id": 4, "person_ids": [4]},  # Cloud Engineer
    {"job_id": 5, "person_ids": [5]},  # Frontend Developer
    {"job_id": 8, "person_ids": [9]},  # DevOps Engineer
    {"job_id": 9, "person_ids": [8]},  # Data Scientist
    {"job_id": 10, "person_ids": [7]},  # Java Spring Developer
    {"job_id": 11, "person_ids": [10]},  # Blockchain Developer
    {"job_id": 12, "person_ids": [6]},  # Sustainability Tech Lead
    {"job_id": 14, "person_ids": [2]},  # Technical Product Manager
]

INTERVIEW_INTERVIEWER_MAPPINGS = [
    {"interview_id": 1, "person_ids": [6]},  # HR screening
    {"interview_id": 2, "person_ids": [2, 4]},  # Technical interview
    {"interview_id": 3, "person_ids": [2]},  # Management interview
    {"interview_id": 4, "person_ids": [8]},  # ML case study
    {"interview_id": 5, "person_ids": [5, 8]},  # Final round
    {"interview_id": 6, "person_ids": [10]},  # Cultural fit
    {"interview_id": 7, "person_ids": [1, 3]},  # Blockchain discussion
]


def add_mappings(primary_data, secondary_data, mapping_data, primary_key, secondary_key, relationship_attr):
    """Generic function to add many-to-many relationships between data objects.
    :param primary_data: List of primary objects (e.g., jobs, interviews)
    :param secondary_data: List of secondary objects (e.g., keywords, persons)
    :param mapping_data: List of mapping dictionaries
    :param primary_key: Key name for primary object ID in mapping (e.g., "job_id", "interview_id")
    :param secondary_key: Key name for secondary object IDs in mapping (e.g., "keyword_ids", "person_ids")
    :param relationship_attr: Attribute name on primary object for the relationship (e.g., "keywords", "contacts")
    """
    for mapping in mapping_data:
        primary_obj = primary_data[mapping[primary_key] - 1]  # Convert to 0-based index
        secondary_ids = mapping[secondary_key]

        for secondary_id in secondary_ids:
            secondary_obj = secondary_data[secondary_id - 1]  # Convert to 0-based index
            getattr(primary_obj, relationship_attr).append(secondary_obj)
