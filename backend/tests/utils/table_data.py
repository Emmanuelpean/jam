"""Centralised test data for both conftest.py and seed_database.py"""

from datetime import datetime, timedelta, timezone
from itertools import groupby

from tests.utils.files import load_all_resource_files

RESOURCE_FILES = load_all_resource_files()


current_date = datetime.now(timezone.utc)
DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S%z"
DATE_FORMAT = "%Y-%m-%d"


USER_DATA = [
    {
        "email": "test_user@test.com",
        "password": "test_password",
    },
    {
        "email": "test_admin@test.com",
        "password": "test_password_admin",
        "is_admin": True,
    },
    {
        "email": "user3@live.co.uk",
        "password": "password3",
    },
    {
        "email": "user4@example.com",
        "password": "password4",
    },
]


SETTINGS_DATA = [
    {
        "name": "allowlist",
        "value": ",".join([data["email"] for data in USER_DATA] + ["newuser@user.com"]),
        "description": "Emails allowed to sign up",
    },
    {
        "name": "default_person_role",
        "value": "Recruiter",
        "description": "Default role for new persons",
    },
]


COMPANY_DATA = [
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
        "name": "CloudFirst Inc",
        "description": None,
        "url": "https://cloudfirst.io",
        "owner_id": 1,
    },
    {
        "name": "Minimal Corp",
        "owner_id": 1,
    },
    {
        "name": "No URL Company",
        "description": "Company without website",
        "owner_id": 1,
    },
    {
        "name": "Enterprise Solutions",
        "description": "Large enterprise software solutions provider with comprehensive digital transformation services",
        "url": "https://enterprise-solutions.com",
        "owner_id": 1,
    },
    {
        "name": "LocalBiz",
        "description": "Small local business",
        "url": "https://localbiz.com",
        "owner_id": 1,
    },
    {
        "name": "Tech Corp",  # DUPLICATE from user 1
        "description": "A leading technology company specializing in web applications",
        "url": "https://techcorp.com",
        "owner_id": 2,
    },
    {
        "name": "StartupXYZ",  # DUPLICATE from user 1
        "description": "An innovative startup focused on AI-driven solutions",
        "url": "https://startupxyz.com",
        "owner_id": 2,
    },
    {
        "name": "InnovateTech Solutions",
        "description": "AI and machine learning consulting company",
        "url": "https://innovatetech.ai",
        "owner_id": 2,
    },
    {
        "name": "GreenEnergy Corp",
        "description": "Renewable energy and sustainability solutions",
        "url": "https://greenenergy.com",
        "owner_id": 2,
    },
    {
        "name": "FinanceFlow Ltd",
        "description": "Financial technology and payment processing",
        "url": "https://financeflow.com",
        "owner_id": 2,
    },
    {
        "name": "HealthTech Solutions",
        "description": "Healthcare technology and medical devices",
        "owner_id": 2,
    },
]


LOCATION_DATA = [
    {
        "postcode": "10001",
        "city": "New York",
        "country": "United States",
        "owner_id": 1,
    },
    {
        "postcode": "90210",
        "city": "Beverly Hills",
        "country": "United States",
        "owner_id": 1,
    },
    {
        "postcode": "SW1A 1AA",
        "city": "London",
        "country": "United Kingdom",
        "owner_id": 1,
    },
    {
        "city": "San Francisco",
        "country": "United States",
        "owner_id": 1,
    },
    {
        "country": "Germany",
        "owner_id": 1,
    },
    {
        "postcode": "OX1 2JD",
        "city": "Oxford",
        "country": "United Kingdom",
        "owner_id": 1,
    },
    {
        "country": "Canada",
        "owner_id": 1,
    },
    {
        "postcode": "75001",
        "city": "Paris",
        "country": "France",
        "owner_id": 1,
    },
    {
        "postcode": "10115",
        "country": "Germany",
        "owner_id": 1,
    },
    {
        "city": "Tokyo",
        "country": "Japan",
        "owner_id": 1,
    },
    {
        "postcode": "M5V 3A8",
        "city": "Toronto",
        "country": "Canada",
        "owner_id": 1,
    },
    {
        "city": "Amsterdam",
        "country": "Netherlands",
        "owner_id": 1,
    },
    {
        "country": "Brazil",
        "owner_id": 1,
    },
    {
        "postcode": "SW1A 1AA",
        "city": "London",
        "country": "United Kingdom",
        "owner_id": 2,
    },
    {
        "postcode": "OX1 2JD",
        "city": "Oxford",
        "country": "United Kingdom",
        "owner_id": 2,
    },
    {
        "postcode": "M1 1AA",
        "city": "Manchester",
        "country": "United Kingdom",
        "owner_id": 2,
    },
    {
        "city": "Edinburgh",
        "country": "United Kingdom",
        "owner_id": 2,
    },
    {
        "country": "United Kingdom",
        "owner_id": 2,
    },
    {
        "postcode": "BS1 1AA",
        "city": "Bristol",
        "country": "United Kingdom",
        "owner_id": 2,
    },
]


AGGREGATOR_DATA = [
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
        "name": "RemoteOK",
        "url": "https://remoteok.io",
        "owner_id": 1,
    },
    {
        "name": "WeWorkRemotely",
        "url": "https://weworkremotely.com",
        "owner_id": 1,
    },
    {
        "name": "Upwork",
        "url": "https://upwork.com",
        "owner_id": 1,
    },
    {
        "name": "Freelancer",
        "url": "https://freelancer.com",
        "owner_id": 1,
    },
    {
        "name": "ZipRecruiter",
        "url": "https://ziprecruiter.com",
        "owner_id": 1,
    },
    {
        "name": "LinkedIn",
        "url": "https://linkedin.com/jobs",
        "owner_id": 2,
    },
    {
        "name": "Indeed",
        "url": "https://indeed.com",
        "owner_id": 2,
    },
    {
        "name": "TotalJobs",
        "url": "https://totaljobs.com",
        "owner_id": 2,
    },
    {
        "name": "Reed",
        "url": "https://reed.co.uk",
        "owner_id": 2,
    },
    {
        "name": "CV-Library",
        "url": "https://cv-library.co.uk",
        "owner_id": 2,
    },
    {
        "name": "Jobsite",
        "url": "https://jobsite.co.uk",
        "owner_id": 2,
    },
]


KEYWORD_DATA = [
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
    {
        "name": "Redis",
        "owner_id": 1,
    },
    {
        "name": "GraphQL",
        "owner_id": 1,
    },
    {
        "name": "Microservices",
        "owner_id": 1,
    },
    {
        "name": "CI/CD",
        "owner_id": 1,
    },
    {
        "name": "Terraform",
        "owner_id": 1,
    },
    {
        "name": "Jenkins",
        "owner_id": 1,
    },
    {
        "name": "Scrum",
        "owner_id": 1,
    },
    {
        "name": "Python",
        "owner_id": 2,
    },
    {
        "name": "JavaScript",
        "owner_id": 2,
    },
    {
        "name": "Java",
        "owner_id": 2,
    },
    {
        "name": "Spring Boot",
        "owner_id": 2,
    },
    {
        "name": "MySQL",
        "owner_id": 2,
    },
    {
        "name": "Flutter",
        "owner_id": 2,
    },
]


PERSON_DATA = [
    {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@techcorp.com",
        "phone": "1234567890",
        "linkedin_url": "https://linkedin.com/in/johndoe",
        "role": "Senior Engineering Manager",
        "company_id": 1,
        "owner_id": 1,
    },
    {
        "first_name": "Jane",
        "last_name": "Smith",
        "email": "jane.smith@startupxyz.com",
        "linkedin_url": "https://linkedin.com/in/janesmith",
        "role": "Product Manager",
        "company_id": 2,
        "owner_id": 1,
    },
    {
        "first_name": "Mike",
        "last_name": "Taylor",
        "phone": "9876543210",
        "role": "Lead Developer",
        "company_id": 1,
        "owner_id": 1,
    },
    {
        "first_name": "Emily",
        "last_name": "Davis",
        "email": "emily.davis@startupxyz.com",
        "role": "DevOps Engineer",
        "company_id": 2,
        "owner_id": 1,
    },
    {
        "first_name": "Chris",
        "last_name": "Brown",
        "linkedin_url": "https://linkedin.com/in/chrisbrown",
        "role": "Data Science Manager",
        "company_id": 1,
        "owner_id": 1,
    },
    {
        "first_name": "Sarah",
        "last_name": "Wilson",
        "email": "sarah.wilson@oxfordpv.com",
        "role": "Technical Recruiter",
        "company_id": 3,
        "owner_id": 1,
    },
    {
        "first_name": "Anonymous",
        "last_name": "Recruiter",
        "company_id": None,
        "owner_id": 1,
    },
    {
        "first_name": "Tech",
        "last_name": "Recruiter",
        "role": "Talent Acquisition",
        "company_id": 3,
        "owner_id": 1,
    },
    {
        "first_name": "Alex",
        "last_name": "Johnson",
        "email": "alex@cloudfirst.io",
        "phone": "5551234567",
        "linkedin_url": "https://linkedin.com/in/alexjohnson",
        "role": "CTO",
        "company_id": 6,
        "owner_id": 1,
    },
    {
        "first_name": "Maria",
        "last_name": "Garcia",
        "email": "maria.garcia@enterprise.com",
        "role": "HR Director",
        "company_id": 9,
        "owner_id": 1,
    },
    {
        "first_name": "David",
        "last_name": "Kim",
        "phone": "5559876543",
        "linkedin_url": "https://linkedin.com/in/davidkim",
        "company_id": None,
        "owner_id": 1,
    },
    {
        "first_name": "Lisa",
        "last_name": "Chen",
        "email": "lisa@localbiz.com",
        "role": "Founder",
        "company_id": 10,
        "owner_id": 1,
    },
    {
        "first_name": "Robert",
        "last_name": "Anderson",
        "linkedin_url": "https://linkedin.com/in/robertanderson",
        "role": "Senior Developer",
        "company_id": 7,
        "owner_id": 1,
    },
    {
        "first_name": "Jennifer",
        "last_name": "Brown",
        "phone": "5555551234",
        "role": "Product Owner",
        "company_id": 8,
        "owner_id": 1,
    },
    {
        "first_name": "Michael",
        "last_name": "Wilson",
        "email": "m.wilson@datatech.com",
        "phone": "5557778888",
        "linkedin_url": "https://linkedin.com/in/michaelwilson",
        "role": "Data Scientist",
        "company_id": 5,
        "owner_id": 1,
    },
    {
        "first_name": "Freelance",
        "last_name": "Developer",
        "email": "freelance@dev.com",
        "owner_id": 1,
    },
    {
        "first_name": "Jane",
        "last_name": "Smith",
        "email": "jane.smith@startupxyz.com",
        "linkedin_url": "https://linkedin.com/in/janesmith",
        "role": "Product Manager",
        "company_id": 12,
        "owner_id": 2,
    },
    {
        "first_name": "Alice",
        "last_name": "Thompson",
        "email": "alice@innovatetech.ai",
        "phone": "07700123456",
        "linkedin_url": "https://linkedin.com/in/alicethompson",
        "role": "Head of Engineering",
        "company_id": 13,
        "owner_id": 2,
    },
    {
        "first_name": "Bob",
        "last_name": "Williams",
        "email": "b.williams@greenenergy.com",
        "role": "Technical Recruiter",
        "company_id": 14,
        "owner_id": 2,
    },
    {
        "first_name": "Catherine",
        "last_name": "Jones",
        "phone": "07700987654",
        "linkedin_url": "https://linkedin.com/in/catjones",
        "role": "Senior Java Developer",
        "company_id": 15,
        "owner_id": 2,
    },
    {
        "first_name": "Daniel",
        "last_name": "Brown",
        "email": "dan.brown@healthtech.com",
        "role": "CTO",
        "company_id": 16,
        "owner_id": 2,
    },
    {
        "first_name": "Emma",
        "last_name": "Davis",
        "email": "emma@techcorp.com",
        "phone": "07700555444",
        "role": "Senior Software Engineer",
        "company_id": 11,
        "owner_id": 2,
    },
]


JOB_DATA = [
    {
        "title": "Senior Python Developer",
        "salary_min": 80000,
        "salary_max": 130000,
        "description": "Lead backend development using Python and modern frameworks. Work with a talented team to build scalable web applications.",
        "personal_rating": 5,
        "url": "https://techcorp.com/jobs/senior_python_developer",
        "company_id": 1,
        "location_id": 2,
        "note": "Excellent opportunity for senior developer",
        "attendance_type": "hybrid",
        "owner_id": 1,
        "source_id": 1,
        "application_date": "2024-01-15T10:00:00",
        "application_url": "https://techcorp.com/apply/senior-python",
        "application_status": "applied",
        "applied_via": "aggregator",
        "application_note": "Submitted application with cover letter",
        "cv_id": 3,
        "cover_letter_id": 3,
        "application_aggregator_id": 1,
    },
    {
        "title": "Full Stack JavaScript Developer",
        "salary_min": 65000,
        "salary_max": 105000,
        "description": "Build end-to-end web applications with React and Node.js. Join our dynamic startup environment.",
        "personal_rating": 4,
        "url": "https://startupxyz.com/jobs/fullstack_js_developer",
        "company_id": 2,
        "location_id": 1,
        "note": "Great team culture mentioned in reviews",
        "attendance_type": "on-site",
        "owner_id": 1,
        "source_id": 2,
        "application_date": "2024-01-16T14:30:00",
        "application_url": "https://startupxyz.com/apply/fullstack-js",
        "application_status": "interview",
        "applied_via": "aggregator",
        "application_note": "Phone screening scheduled for next week",
        "cv_id": 1,
        "cover_letter_id": None,
        "application_aggregator_id": 5,
    },
    {
        "title": "Remote React Developer",
        "salary_min": 60000,
        "salary_max": 95000,
        "description": "Build modern React applications for distributed team. Full remote position with flexible hours.",
        "personal_rating": 3,
        "url": "https://techcorp.com/jobs/remote_react_developer",
        "company_id": 1,
        "location_id": 4,
        "owner_id": 1,
        "source_id": 2,
        "application_date": "2024-01-17T09:15:00",
        "application_url": None,
        "application_status": "applied",
        "applied_via": "aggregator",
        "application_note": "Applied through LinkedIn",
        "cv_id": None,
        "cover_letter_id": 2,
        "application_aggregator_id": 4,
    },
    {
        "title": "Cloud Engineer",
        "salary_min": 75000,
        "salary_max": 120000,
        "description": "Design and maintain AWS cloud infrastructure. Experience with Kubernetes and Docker required.",
        "personal_rating": 4,
        "url": "https://startupxyz.com/jobs/cloud_engineer",
        "company_id": 2,
        "location_id": 3,
        "attendance_type": "hybrid",
        "owner_id": 1,
        "source_id": 2,
        "application_date": "2024-01-18T16:45:00",
        "application_url": "https://startupxyz.com/careers/cloud-engineer",
        "application_status": "rejected",
        "applied_via": "aggregator",
        "application_note": "Not enough cloud experience",
        "cv_id": 4,
        "cover_letter_id": 4,
        "application_aggregator_id": 7,
    },
    {
        "title": "Frontend Developer",
        "salary_min": 55000,
        "salary_max": 85000,
        "description": "Create beautiful user interfaces with React and JavaScript. Focus on user experience and modern design.",
        "personal_rating": 2,
        "url": "https://techcorp.com/jobs/frontend_developer",
        "company_id": 1,
        "location_id": 5,
        "attendance_type": "on-site",
        "owner_id": 1,
        "source_id": 4,
        "application_date": None,
        "application_url": None,
        "application_status": None,
        "applied_via": None,
        "application_note": None,
        "cv_id": None,
        "cover_letter_id": None,
        "application_aggregator_id": None,
    },
    {
        "title": "Backend Developer",
        "description": "Looking for a backend developer with Python experience. FastAPI knowledge preferred.",
        "location_id": 4,
        "attendance_type": "hybrid",
        "owner_id": 1,
        "source_id": 1,
        "application_date": "2024-01-20T13:30:00",
        "application_url": None,
        "application_status": "applied",
        "applied_via": None,
        "application_note": "Quick application through company form",
        "cv_id": None,
        "cover_letter_id": None,
        "application_aggregator_id": None,
    },
    {
        "title": "Software Engineer Intern",
        "description": "Summer internship opportunity for computer science students. Great learning environment.",
        "personal_rating": 1,
        "company_id": 3,
        "owner_id": 1,
        "source_id": 7,
        "application_date": None,
        "application_url": None,
        "application_status": None,
        "applied_via": None,
        "application_note": None,
        "cv_id": None,
        "cover_letter_id": None,
        "application_aggregator_id": None,
    },
    {
        "title": "Developer Position",
        "company_id": 3,
        "location_id": 5,
        "attendance_type": "hybrid",
        "owner_id": 1,
        "source_id": 9,
        "application_date": None,
        "application_url": None,
        "application_status": None,
        "applied_via": None,
        "application_note": None,
        "cv_id": None,
        "cover_letter_id": None,
        "application_aggregator_id": None,
        "deadline": (current_date + timedelta(days=10)).strftime(DATE_FORMAT),
    },
    {
        "title": "DevOps Engineer",
        "salary_min": 90000,
        "salary_max": 140000,
        "description": "Build and maintain CI/CD pipelines, manage cloud infrastructure",
        "personal_rating": 5,
        "url": "https://cloudfirst.io/careers/devops",
        "company_id": 6,
        "location_id": 8,
        "note": "Strong DevOps culture, great tools",
        "attendance_type": "hybrid",
        "owner_id": 1,
        "source_id": 9,
        "application_date": "2024-01-21T09:00:00",
        "application_url": "https://cloudfirst.io/apply/devops",
        "application_status": "interview",
        "applied_via": None,
        "application_note": "Technical interview scheduled",
        "cv_id": 8,
        "cover_letter_id": 10,
        "application_aggregator_id": None,
    },
    {
        "title": "Data Scientist",
        "salary_min": 85000,
        "salary_max": 125000,
        "description": "Work with big data to derive insights and build ML models",
        "personal_rating": 4,
        "company_id": 5,
        "location_id": 9,
        "attendance_type": "remote",
        "owner_id": 1,
        "source_id": 1,
        "application_date": "2024-01-22T11:15:00",
        "application_url": None,
        "application_status": "applied",
        "applied_via": None,
        "application_note": None,
        "cv_id": 9,
        "cover_letter_id": None,
        "application_aggregator_id": None,
    },
    {
        "title": "Vue.js Frontend Developer",
        "salary_min": 50000,
        "salary_max": 80000,
        "description": "Build modern SPAs with Vue.js and TypeScript",
        "url": "https://enterprise-solutions.com/jobs/vue-dev",
        "company_id": 9,
        "location_id": 10,
        "attendance_type": "on-site",
        "owner_id": 1,
        "source_id": 5,
        "application_date": "2024-01-23T15:45:00",
        "application_url": "https://enterprise-solutions.com/apply/vue-dev",
        "application_status": "rejected",
        "applied_via": None,
        "application_note": "Position filled internally",
        "cv_id": 6,
        "cover_letter_id": 12,
        "application_aggregator_id": None,
    },
    {
        "title": "Remote Full Stack Engineer",
        "salary_min": 70000,
        "salary_max": 110000,
        "description": "Work remotely on full stack applications",
        "personal_rating": 3,
        "url": "https://localbiz.com/jobs/fullstack",
        "company_id": 10,
        "location_id": 11,
        "note": "Small team, lots of autonomy",
        "attendance_type": "remote",
        "owner_id": 1,
        "source_id": 7,
        "application_date": "2024-01-24T08:30:00",
        "application_url": None,
        "application_status": "applied",
        "applied_via": None,
        "application_note": "Applied directly through website",
        "cv_id": 3,
        "cover_letter_id": None,
        "application_aggregator_id": None,
    },
    {
        "title": "Junior Developer",
        "salary_min": 40000,
        "salary_max": 60000,
        "description": "Entry-level position for new graduates",
        "personal_rating": 2,
        "company_id": 7,
        "location_id": 12,
        "attendance_type": "on-site",
        "owner_id": 1,
        "source_id": 8,
        "application_date": "2024-01-25T10:00:00",
        "application_url": None,
        "application_status": "interview",
        "applied_via": None,
        "application_note": None,
        "cv_id": 1,
        "cover_letter_id": 7,
        "application_aggregator_id": None,
        "deadline": (current_date + timedelta(days=10)).strftime(DATE_FORMAT),
    },
    {
        "title": "Freelance Web Developer",
        "description": "Contract position for web development projects",
        "location_id": 13,
        "note": "Flexible hours, project-based",
        "attendance_type": "remote",
        "owner_id": 1,
        "application_date": None,
        "application_url": None,
        "application_status": None,
        "applied_via": None,
        "application_note": None,
        "cv_id": None,
        "cover_letter_id": None,
        "application_aggregator_id": None,
    },
    {
        "title": "Mobile App Developer",
        "salary_min": 60000,
        "salary_max": 100000,
        "description": "Develop iOS and Android applications",
        "personal_rating": 4,
        "url": "https://websolutions.com/jobs/mobile-dev",
        "company_id": 4,
        "location_id": 12,
        "attendance_type": "hybrid",
        "owner_id": 1,
        "application_date": "2024-01-26T16:00:00",
        "application_url": "https://websolutions.com/apply/mobile-dev",
        "application_status": "applied",
        "applied_via": None,
        "application_note": "Excited about mobile development opportunity",
        "cv_id": 11,
        "cover_letter_id": None,
        "application_aggregator_id": None,
    },
    {
        "title": "Minimum Required Job",
        "attendance_type": "on-site",
        "owner_id": 1,
        "application_date": "2024-01-27T12:00:00",
        "application_url": None,
        "application_status": "applied",
        "applied_via": None,
        "application_note": None,
        "cv_id": None,
        "cover_letter_id": None,
        "application_aggregator_id": None,
    },
    {
        "title": "High Salary Position",
        "salary_min": 150000,
        "salary_max": 250000,
        "description": "Senior leadership role with high compensation",
        "personal_rating": 5,
        "company_id": 9,
        "location_id": 1,
        "attendance_type": "hybrid",
        "owner_id": 1,
        "application_date": "2024-01-28T14:20:00",
        "application_url": "https://enterprise-solutions.com/apply/high-salary",
        "application_status": "interview",
        "applied_via": None,
        "application_note": "Executive-level interview process",
        "cv_id": 8,
        "cover_letter_id": 2,
        "application_aggregator_id": None,
    },
    {
        "title": "Senior Python Developer",
        "salary_min": 75000,
        "salary_max": 120000,
        "description": "Lead backend development using Python and modern frameworks for fintech applications",
        "personal_rating": 4,
        "url": "https://financeflow.com/jobs/senior-python",
        "company_id": 15,
        "location_id": 15,
        "note": "Great fintech experience opportunity",
        "attendance_type": "hybrid",
        "owner_id": 2,
        "source_id": 14,
        "application_date": "2024-02-01T10:00:00",
        "application_status": "applied",
        "applied_via": "company",
        "cv_id": 13,
        "cover_letter_id": 13,
    },
    {
        "title": "Mobile App Developer",
        "salary_min": 50000,
        "salary_max": 70000,
        "description": "Build mobile applications using Flutter for healthcare sector",
        "personal_rating": 5,
        "company_id": 16,
        "location_id": 17,
        "attendance_type": "remote",
        "owner_id": 2,
        "source_id": 15,
        "application_date": "2024-02-03T14:30:00",
        "application_status": "interview",
        "applied_via": "aggregator",
        "cv_id": 14,
        "application_aggregator_id": 13,
    },
    {
        "title": "AI/ML Engineer",
        "salary_min": 65000,
        "salary_max": 95000,
        "description": "Develop machine learning models and AI solutions",
        "personal_rating": 5,
        "company_id": 13,
        "location_id": 18,
        "attendance_type": "hybrid",
        "owner_id": 2,
        "source_id": 15,
        "application_date": "2024-02-05T09:15:00",
        "application_status": "applied",
        "applied_via": "aggregator",
        "cover_letter_id": 14,
        "application_aggregator_id": 14,
    },
    {
        "title": "Sustainability Software Engineer",
        "salary_min": 55000,
        "salary_max": 75000,
        "description": "Develop software solutions for renewable energy management",
        "personal_rating": 3,
        "company_id": 14,
        "location_id": 19,
        "attendance_type": "on-site",
        "owner_id": 2,
        "source_id": 14,
        "application_date": None,
        "application_status": None,
    },
    {
        "title": "Full Stack Developer",
        "salary_min": 60000,
        "salary_max": 85000,
        "description": "Build end-to-end web applications using modern frameworks",
        "personal_rating": 4,
        "company_id": 12,
        "location_id": 16,
        "attendance_type": "hybrid",
        "owner_id": 2,
        "source_id": 15,
        "application_date": "2024-02-07T11:00:00",
        "application_status": "rejected",
        "applied_via": "company",
        "cv_id": 15,
        "cover_letter_id": 15,
    },
    {
        "title": "Software Engineer",
        "salary_min": 45000,
        "salary_max": 65000,
        "description": "Join our growing tech team to build innovative solutions",
        "personal_rating": 3,
        "company_id": 11,
        "location_id": 16,
        "attendance_type": "on-site",
        "owner_id": 2,
        "source_id": 13,
        "application_date": "2024-02-09T15:45:00",
        "application_status": "applied",
        "applied_via": "aggregator",
        "cv_id": 16,
        "application_aggregator_id": 11,
    },
]

JOB_APPLICATION_DATETIME = [current_date - timedelta(weeks=i) for i in range(len(JOB_DATA))]
for job_application, date in zip(JOB_DATA, JOB_APPLICATION_DATETIME):
    if job_application.get("application_date"):
        job_application["application_date"] = date.strftime(DATETIME_FORMAT)


FILE_DATA = [
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
        "filename": "frontend_developer_cover_letter.docx",
        "owner_id": 1,
        **RESOURCE_FILES["Cover Letter.docx"],
    },
    {
        "filename": "devops_engineer_cv.pdf",
        "owner_id": 1,
        **RESOURCE_FILES["CV.pdf"],
    },
    {
        "filename": "data_scientist_resume.pdf",
        "owner_id": 1,
        **RESOURCE_FILES["CV.pdf"],
    },
    {
        "filename": "vue_developer_cover_letter.txt",
        "owner_id": 1,
        **RESOURCE_FILES["Cover Letter.txt"],
    },
    {
        "filename": "mobile_dev_portfolio.pdf",
        "owner_id": 1,
        **RESOURCE_FILES["CV.pdf"],
    },
    {
        "filename": "generic_cover_letter.docx",
        "owner_id": 1,
        **RESOURCE_FILES["Cover Letter.docx"],
    },
    {
        "filename": "john_doe_cv_2024.pdf",
        "owner_id": 2,
        **RESOURCE_FILES["CV.pdf"],
    },
    {
        "filename": "cover_letter_senior_python.docx",
        "owner_id": 2,
        **RESOURCE_FILES["Cover Letter.docx"],
    },
    {
        "filename": "java_developer_cv.pdf",
        "owner_id": 2,
        **RESOURCE_FILES["CV.pdf"],
    },
    {
        "filename": "mobile_dev_cover_letter.docx",
        "owner_id": 2,
        **RESOURCE_FILES["Cover Letter.docx"],
    },
    {
        "filename": "ai_engineer_portfolio.pdf",
        "owner_id": 2,
        **RESOURCE_FILES["CV.pdf"],
    },
    {
        "filename": "fullstack_developer_resume.txt",
        "owner_id": 2,
        **RESOURCE_FILES["Cover Letter.txt"],
    },
]


INTERVIEW_DATA = [
    {
        "date": "2024-01-20T09:30:00",
        "type": "HR",
        "location_id": 1,
        "job_id": 1,
        "note": "First round technical interview",
        "attendance_type": "on-site",
        "owner_id": 1,
    },
    {
        "date": "2024-01-21T14:00:00",
        "type": "Technical",
        "location_id": 2,
        "job_id": 2,
        "note": "HR screening call",
        "attendance_type": "remote",
        "owner_id": 1,
    },
    {
        "date": "2024-01-22T10:15:00",
        "type": "Management",
        "location_id": 4,  # Remote
        "job_id": 3,
        "note": "Remote technical assessment",
        "attendance_type": "remote",
        "owner_id": 1,
    },
    {
        "date": "2024-01-23T16:30:00",
        "type": "HR",
        "location_id": 1,
        "job_id": 4,
        "note": "Final round with team lead",
        "attendance_type": "on-site",
        "owner_id": 1,
    },
    {
        "date": "2024-01-24T11:45:00",
        "type": "Other",
        "location_id": 3,
        "job_id": 5,
        "note": "Cultural fit interview",
        "attendance_type": "on-site",
        "owner_id": 1,
    },
    {
        "date": "2024-01-26T09:00:00",
        "type": "HR",
        "location_id": 7,
        "job_id": 1,
        "note": None,
        "attendance_type": "on-site",
        "owner_id": 1,
    },
    {
        "date": "2024-01-29T10:30:00",
        "type": "Technical",
        "location_id": 8,
        "job_id": 6,
        "note": "Deep technical dive into infrastructure",
        "attendance_type": "on-site",
        "owner_id": 1,
    },
    {
        "date": "2024-01-30T15:00:00",
        "type": "Management",
        "location_id": 11,
        "job_id": 8,
        "note": "Meeting with team leads",
        "attendance_type": "remote",
        "owner_id": 1,
    },
    {
        "date": "2024-02-01T09:45:00",
        "type": "HR",
        "location_id": 12,
        "job_id": 10,
        "note": "Initial screening for junior position",
        "attendance_type": "on-site",
        "owner_id": 1,
    },
    {
        "date": "2024-02-02T11:00:00",
        "type": "Technical",
        "location_id": 12,
        "job_id": 11,
        "note": "Technical skills assessment for mobile development",
        "attendance_type": "remote",
        "owner_id": 1,
    },
    {
        "date": "2024-02-03T14:15:00",
        "type": "Other",
        "location_id": 1,
        "job_id": 13,
        "note": "Panel interview with executives",
        "attendance_type": "on-site",
        "owner_id": 1,
    },
    {
        "date": "2024-02-04T16:30:00",
        "type": "Management",
        "location_id": 5,
        "job_id": 7,
        "attendance_type": "remote",
        "owner_id": 1,
    },
    {
        "date": "2024-02-08T10:00:00",
        "type": "HR",
        "location_id": 15,
        "job_id": 18,
        "note": "Initial HR screening for Python role",
        "attendance_type": "remote",
        "owner_id": 2,
    },
    {
        "date": "2024-02-10T15:30:00",
        "type": "Technical",
        "location_id": 17,
        "job_id": 18,
        "note": "Technical interview for mobile development",
        "attendance_type": "remote",
        "owner_id": 2,
    },
    {
        "date": "2024-02-12T11:45:00",
        "type": "Management",
        "location_id": 18,
        "job_id": 19,
        "note": "Final round with engineering manager",
        "attendance_type": "on-site",
        "owner_id": 2,
    },
    {
        "date": "2024-02-14T09:00:00",
        "type": "HR",
        "location_id": 16,
        "job_id": 21,
        "note": "HR screening for StartupXYZ position",
        "attendance_type": "remote",
        "owner_id": 2,
    },
    {
        "date": "2024-02-16T14:15:00",
        "type": "Technical",
        "location_id": 16,
        "job_id": 22,
        "note": "Coding challenge and technical discussion",
        "attendance_type": "on-site",
        "owner_id": 2,
    },
    {
        "date": "2024-02-18T16:30:00",
        "type": "Other",
        "location_id": 19,
        "job_id": 20,
        "note": "Team culture fit interview",
        "attendance_type": "on-site",
        "owner_id": 2,
    },
]

interviews_sorted = sorted(INTERVIEW_DATA, key=lambda x: x["job_id"])
grouped = {k: list(v) for k, v in groupby(interviews_sorted, key=lambda x: x["job_id"])}
for update_key, date in zip(grouped, JOB_APPLICATION_DATETIME):
    for i, update in enumerate(grouped[update_key]):
        update["date"] = (date + timedelta(weeks=4) * (i + 1)).strftime(DATETIME_FORMAT)


JOB_APPLICATION_UPDATE_DATA = [
    {
        "date": "2024-01-15 14:30:00",
        "job_id": 1,  # Tech startup application
        "note": "Received automated confirmation email",
        "type": "received",
        "owner_id": 1,
    },
    {
        "date": "2024-01-18 09:15:00",
        "job_id": 1,
        "note": "HR recruiter called to schedule phone screening",
        "type": "received",
        "owner_id": 1,
    },
    {
        "date": "2024-01-22 16:45:00",
        "job_id": 2,  # Marketing agency application
        "note": "Application status changed to 'Under Review'",
        "type": "received",
        "owner_id": 1,
    },
    {
        "date": "2024-01-25 11:20:00",
        "job_id": 3,  # Finance corp application
        "note": "Received rejection email - position filled internally",
        "type": "received",
        "owner_id": 1,
    },
    {
        "date": "2024-01-28 13:10:00",
        "job_id": 4,  # Healthcare application
        "note": "Invited to complete online assessment",
        "type": "received",
        "owner_id": 1,
    },
    {
        "date": "2024-02-01 08:30:00",
        "job_id": 2,
        "note": "Scheduled for first round interview next week",
        "type": "received",
        "owner_id": 1,
    },
    {
        "date": "2024-02-03 15:45:00",
        "job_id": 5,  # Remote consulting application
        "note": "Application acknowledgment received",
        "type": "received",
        "owner_id": 1,
    },
    {
        "date": "2024-02-05 10:15:00",
        "job_id": 4,
        "note": "Completed technical assessment - awaiting results",
        "type": "sent",
        "owner_id": 1,
    },
    {
        "date": "2024-02-08 14:20:00",
        "job_id": 6,  # Another application
        "note": "Phone screening scheduled for tomorrow",
        "type": "sent",
        "owner_id": 1,
    },
    {
        "date": "2024-02-12 11:45:00",
        "job_id": 7,
        "note": "Application moved to final review stage",
        "type": "sent",
        "owner_id": 1,
    },
    {
        "date": "2024-02-15 09:30:00",
        "job_id": 8,
        "note": "Hiring manager wants to schedule video call",
        "type": "sent",
        "owner_id": 1,
    },
    {
        "date": "2024-02-18 16:10:00",
        "job_id": 9,
        "note": "Received offer letter - salary negotiation in progress",
        "type": "sent",
        "owner_id": 1,
    },
    {
        "date": "2024-02-20 13:25:00",
        "job_id": 10,
        "note": "Application automatically withdrawn due to inactivity",
        "type": "sent",
        "owner_id": 1,
    },
    {
        "date": "2024-02-22 10:40:00",
        "job_id": 2,
        "note": "Second round interview scheduled - panel interview",
        "type": "sent",
        "owner_id": 1,
    },
    {
        "date": "2024-02-25 14:55:00",
        "job_id": 11,
        "note": "Reference check completed",
        "type": "sent",
        "owner_id": 1,
    },
    {
        "date": "2024-02-02T11:30:00",
        "job_id": 18,
        "note": "Application received confirmation email",
        "type": "received",
        "owner_id": 2,
    },
    {
        "date": "2024-02-04T16:45:00",
        "job_id": 18,
        "note": "Invited for HR screening interview",
        "type": "received",
        "owner_id": 2,
    },
    {
        "date": "2024-02-06T09:20:00",
        "job_id": 19,
        "note": "Technical assessment link sent",
        "type": "received",
        "owner_id": 2,
    },
    {
        "date": "2024-02-07T14:10:00",
        "job_id": 18,
        "note": "Completed online coding challenge",
        "type": "sent",
        "owner_id": 2,
    },
    {
        "date": "2024-02-09T12:25:00",
        "job_id": 21,
        "note": "Application rejected - position filled internally",
        "type": "received",
        "owner_id": 2,
    },
    {
        "date": "2024-02-11T10:15:00",
        "job_id": 22,
        "note": "Second round interview scheduled",
        "type": "received",
        "owner_id": 2,
    },
]

job_application_updates_sorted = sorted(JOB_APPLICATION_UPDATE_DATA, key=lambda x: x["job_id"])
grouped = {k: list(v) for k, v in groupby(job_application_updates_sorted, key=lambda x: x["job_id"])}
for update_key, date in zip(grouped, JOB_APPLICATION_DATETIME):
    for i, update in enumerate(grouped[update_key]):
        update["date"] = (date + timedelta(weeks=4) * (i + 1)).strftime(DATETIME_FORMAT)


JOB_KEYWORD_MAPPINGS = [
    {"job_id": 1, "keyword_ids": [1, 2, 6, 7]},
    {"job_id": 2, "keyword_ids": [2, 3, 4, 13]},
    {"job_id": 3, "keyword_ids": [3, 2, 14]},
    {"job_id": 4, "keyword_ids": [12, 10, 11, 9]},
    {"job_id": 5, "keyword_ids": [2, 3, 14, 15]},
    {"job_id": 9, "keyword_ids": [9, 10, 11, 22, 23]},
    {"job_id": 10, "keyword_ids": [8, 1, 18]},
    {"job_id": 11, "keyword_ids": [16, 5, 2]},
    {"job_id": 12, "keyword_ids": [2, 3, 4, 1]},
    {"job_id": 13, "keyword_ids": [2, 14, 15]},
    {"job_id": 15, "keyword_ids": [2, 3, 17]},
    {"job_id": 18, "keyword_ids": [29, 26]},
    {"job_id": 19, "keyword_ids": [28, 26]},
    {"job_id": 20, "keyword_ids": [27, 26]},
    {"job_id": 21, "keyword_ids": [27]},
    {"job_id": 22, "keyword_ids": [26, 27]},
]


JOB_CONTACT_MAPPINGS = [
    {"job_id": 1, "person_ids": [1, 3]},
    {"job_id": 2, "person_ids": [2, 4]},
    {"job_id": 3, "person_ids": [1]},
    {"job_id": 4, "person_ids": [4]},
    {"job_id": 5, "person_ids": [5]},
    {"job_id": 9, "person_ids": [9]},
    {"job_id": 10, "person_ids": [15]},
    {"job_id": 11, "person_ids": [10]},
    {"job_id": 12, "person_ids": [12]},
    {"job_id": 13, "person_ids": [13]},
    {"job_id": 15, "person_ids": [11, 16]},
    {"job_id": 18, "person_ids": [20]},
    {"job_id": 19, "person_ids": [18]},
    {"job_id": 20, "person_ids": [17]},
    {"job_id": 21, "person_ids": [20]},
    {"job_id": 22, "person_ids": [21]},
]


INTERVIEW_INTERVIEWER_MAPPINGS = [
    {"interview_id": 1, "person_ids": [1]},
    {"interview_id": 2, "person_ids": [2]},
    {"interview_id": 3, "person_ids": [3, 5]},
    {"interview_id": 4, "person_ids": [1]},
    {"interview_id": 5, "person_ids": [4]},
    {"interview_id": 7, "person_ids": [9]},
    {"interview_id": 8, "person_ids": [12, 11]},
    {"interview_id": 9, "person_ids": [13]},
    {"interview_id": 10, "person_ids": [16]},
    {"interview_id": 11, "person_ids": [10, 15]},
    {"interview_id": 12, "person_ids": [15]},
    {"interview_id": 13, "person_ids": [19]},
    {"interview_id": 14, "person_ids": [20]},
    {"interview_id": 15, "person_ids": [18, 17]},
    {"interview_id": 16, "person_ids": [20]},
    {"interview_id": 17, "person_ids": [21]},
    {"interview_id": 18, "person_ids": [17, 19]},
]


JOB_ALERT_EMAIL_DATA = [
    {
        "owner_id": 1,
        "external_email_id": "linkedin_alert_001",
        "subject": "10 new jobs matching Python Developer",
        "sender": "jobs-noreply@linkedin.com",
        "date_received": "2024-01-15 09:30:00",
        "platform": "linkedin",
        "service_log_id": 1,
        "body": """
        Hi there,

        We found 10 new jobs that match your preferences:

        1. Senior Python Developer at TechCorp
        https://www.linkedin.com/jobs/view/3789012345

        2. Python Backend Engineer at StartupInc
        https://www.linkedin.com/jobs/view/3789012346

        3. Full Stack Python Developer at DataSoft
        https://linkedin.com/comm/jobs/view/3789012347

        Best regards,
        LinkedIn Jobs Team
        """,
    },
    {
        "owner_id": 1,
        "external_email_id": "indeed_alert_001",
        "subject": "New job alerts for Software Engineer",
        "sender": "noreply@indeed.com",
        "date_received": "2024-01-16 14:45:00",
        "platform": "indeed",
        "service_log_id": 2,
        "body": """
        New jobs matching your search criteria:

        Software Engineer - Remote
        Apply here: https://indeed.com/pagead/clk/dl?mo=r&ad=job123456789&source=email

        Senior Software Engineer - London
        View job: https://uk.indeed.com/rc/clk/dl?jk=job987654321&from=email

        Python Developer - Manchester
        https://indeed.com/viewjob?jk=job555666777

        Don't miss out on these opportunities!
        Indeed Team
        """,
    },
    {
        "owner_id": 1,
        "external_email_id": "linkedin_alert_002",
        "subject": "Data Scientist positions you might like",
        "sender": "jobs-noreply@linkedin.com",
        "date_received": "2024-01-17 11:20:00",
        "platform": "linkedin",
        "service_log_id": 3,
        "body": """
        Hello,

        Check out these Data Scientist roles:

        Machine Learning Engineer
        https://www.linkedin.com/jobs/view/3801234567

        Senior Data Scientist at FinTech Ltd
        https://linkedin.com/comm/jobs/view/3801234568

        AI Research Scientist
        https://www.linkedin.com/jobs/view/3801234569

        Happy job hunting!
        LinkedIn
        """,
    },
    {
        "owner_id": 2,
        "external_email_id": "indeed_alert_002",
        "subject": "Your weekly job digest - 5 new matches",
        "sender": "alerts@indeed.com",
        "date_received": "2024-01-18 08:15:00",
        "platform": "indeed",
        "service_log_id": 4,
        "body": """
        Your weekly job digest is here!

        Data Analyst - Birmingham
        https://indeed.com/pagead/clk/dl?mo=r&ad=data123&ref=email

        Business Intelligence Developer
        https://uk.indeed.com/viewjob?jk=bi456789&utm_source=email

        Senior Data Engineer
        https://indeed.com/rc/clk/dl?jk=eng999888&campaign=weekly

        Python Data Scientist - Edinburgh
        https://uk.indeed.com/pagead/clk/dl?mo=r&ad=sci777666&source=digest

        ML Engineer - Glasgow
        https://indeed.com/viewjob?jk=ml444333&ref=weekly_digest

        Best of luck with your job search!
        Indeed
        """,
    },
    {
        "owner_id": 1,
        "external_email_id": "linkedin_alert_003",
        "subject": "3 jobs similar to ones you've viewed",
        "sender": "jobs-noreply@linkedin.com",
        "date_received": "2024-01-19 16:10:00",
        "platform": "linkedin",
        "service_log_id": 5,
        "body": """
        Based on your recent activity, here are some similar opportunities:

        DevOps Engineer at CloudTech
        https://www.linkedin.com/jobs/view/3812345678

        Site Reliability Engineer
        https://linkedin.com/comm/jobs/view/3812345679

        Infrastructure Engineer - Remote
        https://www.linkedin.com/jobs/view/3812345680

        View more jobs on LinkedIn
        """,
    },
    {
        "owner_id": 2,
        "external_email_id": "indeed_alert_003",
        "subject": "Frontend Developer jobs in your area",
        "sender": "job-alerts@indeed.co.uk",
        "date_received": "2024-01-20 12:30:00",
        "platform": "indeed",
        "service_log_id": 4,
        "body": """
        New Frontend Developer opportunities:

        React Developer - London
        https://uk.indeed.com/pagead/clk/dl?mo=r&ad=react123&loc=london

        Vue.js Developer - Manchester
        https://indeed.com/viewjob?jk=vue456789&location=manchester

        Angular Developer - Bristol
        https://uk.indeed.com/rc/clk/dl?jk=ng789012&city=bristol

        Full Stack JavaScript Developer
        https://indeed.com/pagead/clk/dl?mo=r&ad=js345678&type=fullstack

        Keep applying!
        Indeed UK
        """,
    },
    {
        "owner_id": 2,
        "external_email_id": "linkedin_alert_004",
        "subject": "Java Developer opportunities in your area",
        "sender": "jobs-noreply@linkedin.com",
        "date_received": "2024-02-01T08:30:00",
        "platform": "linkedin",
        "service_log_id": 5,
        "body": """
        New Java opportunities:
        
        Senior Java Developer - London
        https://linkedin.com/jobs/view/4123456789
        
        Java Spring Boot Developer - Manchester
        https://linkedin.com/jobs/view/4123456790
        
        Lead Java Developer - Birmingham
        https://linkedin.com/jobs/view/4123456791
        
        Best regards,
        LinkedIn Jobs Team
        """,
    },
    {
        "owner_id": 2,
        "external_email_id": "totaljobs_alert_001",
        "subject": "Mobile App Developer jobs near you",
        "sender": "alerts@totaljobs.com",
        "date_received": "2024-02-03T12:15:00",
        "platform": "totaljobs",
        "service_log_id": 6,
        "body": """
        Mobile development opportunities:
        
        Flutter Developer - Healthcare sector
        https://totaljobs.com/job/flutter-healthcare-567890
        
        iOS Developer - Fintech startup
        https://totaljobs.com/job/ios-fintech-234567
        
        React Native Developer - Remote
        https://totaljobs.com/job/react-native-remote-890123
        
        TotalJobs Team
        """,
    },
    {
        "owner_id": 2,
        "external_email_id": "reed_alert_001",
        "subject": "AI & Machine Learning weekly digest",
        "sender": "noreply@reed.co.uk",
        "date_received": "2024-02-05T16:40:00",
        "platform": "reed",
        "service_log_id": 7,
        "body": """
        This week's AI & ML roles:
        
        Machine Learning Engineer - Edinburgh
        https://reed.co.uk/jobs/ml-engineer-edinburgh/345678
        
        AI Software Developer - London
        https://reed.co.uk/jobs/ai-developer-london/456789
        
        Data Scientist - Manchester
        https://reed.co.uk/jobs/data-scientist-manchester/567890
        
        Happy job hunting!
        Reed
        """,
    },
    {
        "owner_id": 2,
        "external_email_id": "cvlibrary_alert_001",
        "subject": "Sustainability & Green Tech jobs",
        "sender": "jobs@cv-library.co.uk",
        "date_received": "2024-02-07T09:20:00",
        "platform": "cv-library",
        "service_log_id": 8,
        "body": """
        Green technology opportunities:
        
        Sustainability Software Engineer - Bristol
        https://cv-library.co.uk/job/sustainability-bristol-678901
        
        Renewable Energy Developer - Edinburgh
        https://cv-library.co.uk/job/renewable-edinburgh-789012
        
        Environmental Data Analyst - London
        https://cv-library.co.uk/job/environmental-london-890123
        
        CV-Library Team
        """,
    },
    {
        "owner_id": 2,
        "external_email_id": "jobsite_alert_001",
        "subject": "Full Stack Developer positions",
        "sender": "alerts@jobsite.co.uk",
        "date_received": "2024-02-09T14:30:00",
        "platform": "jobsite",
        "service_log_id": 9,
        "body": """
        Full stack development roles:
        
        Full Stack JavaScript Developer - Manchester
        https://jobsite.co.uk/job/fullstack-js-manchester-901234
        
        Python Full Stack Engineer - London
        https://jobsite.co.uk/job/python-fullstack-london-012345
        
        MEAN Stack Developer - Birmingham
        https://jobsite.co.uk/job/mean-stack-birmingham-123456
        
        Jobsite Team
        """,
    },
    {
        "owner_id": 2,
        "external_email_id": "indeed_alert_004",
        "subject": "Software Engineer jobs - Daily alerts",
        "sender": "noreply@indeed.com",
        "date_received": "2024-02-11T07:45:00",
        "platform": "indeed",
        "service_log_id": 5,
        "body": """
        Today's software engineering opportunities:
        
        Software Engineer - Tech Startup Oxford
        https://indeed.com/viewjob?jk=soft123456789
        
        Senior Software Engineer - London Fintech
        https://indeed.com/viewjob?jk=soft234567890
        
        Graduate Software Developer - Manchester
        https://indeed.com/viewjob?jk=soft345678901
        
        Indeed Team
        """,
    },
]


JOB_SCRAPED_DATA = [
    {
        "external_job_id": "3789012345",
        "owner_id": 1,
        "is_scraped": True,
        "is_failed": False,
        "title": "Senior Python Developer",
        "description": "We are looking for an experienced Python developer to join our team...",
        "company": "TechCorp Inc",
        "location": "San Francisco, CA",
        "salary_min": 120000.0,
        "salary_max": 160000.0,
        "url": "https://linkedin.com/jobs/view/3789012345",
        "scrape_datetime": "2025-08-15T14:32:18.123456+00:00",
    },
    {
        "external_job_id": "987654321",
        "owner_id": 1,
        "is_scraped": True,
        "is_failed": False,
        "title": "Full Stack Engineer",
        "description": "Join our growing startup as a full stack engineer...",
        "company": "StartupXYZ",
        "location": "Remote",
        "salary_min": 90000.0,
        "salary_max": 130000.0,
        "url": "https://indeed.com/viewjob?jk=987654321",
        "scrape_datetime": "2025-08-22T09:45:32.789012+00:00",
    },
    {
        "external_job_id": "1122334455",
        "owner_id": 1,
        "is_scraped": True,
        "is_failed": False,
        "title": "DevOps Engineer",
        "description": "Looking for a DevOps engineer with AWS experience...",
        "company": "CloudTech Solutions",
        "location": "New York, NY",
        "salary_min": 110000.0,
        "salary_max": 150000.0,
        "url": "https://linkedin.com/jobs/view/1122334455",
        "scrape_datetime": "2025-08-28T16:20:45.456789+00:00",
    },
    {
        "external_job_id": "5566778899",
        "owner_id": 1,
        "is_scraped": True,
        "is_failed": False,
        "title": "Software Engineer",
        "scrape_datetime": "2025-08-30T11:15:22.234567+00:00",
    },
    {
        "external_job_id": "1357924680",
        "owner_id": 1,
        "is_scraped": True,
        "is_failed": False,
        "title": "Backend Developer",
        "scrape_datetime": "2025-08-25T13:42:17.345678+00:00",
    },
    {
        "external_job_id": "2468135790",
        "owner_id": 1,
        "is_scraped": True,
        "is_failed": True,
        "scrape_error": "Page not found - job posting may have been removed",
        "title": "Data Engineer",
        "scrape_datetime": "2025-08-18T08:30:55.567890+00:00",
    },
    {
        "external_job_id": "9988776655",
        "owner_id": 1,
        "is_scraped": True,
        "is_failed": True,
        "scrape_error": "Scraping blocked - rate limit exceeded",
        "title": "ML Engineer",
        "scrape_datetime": "2025-08-20T19:25:08.678901+00:00",
    },
    {
        "external_job_id": "4123456789",
        "owner_id": 2,
        "is_scraped": True,
        "is_failed": False,
        "title": "Senior Java Developer",
        "description": "Looking for experienced Java developer with Spring Boot expertise...",
        "company": "FinTech Innovations Ltd",
        "location": "London, UK",
        "salary_min": 70000.0,
        "salary_max": 95000.0,
        "url": "https://linkedin.com/jobs/view/4123456789",
        "scrape_datetime": "2025-09-01T10:15:30.123456+00:00",
    },
    {
        "external_job_id": "totaljobs_567890",
        "owner_id": 2,
        "is_scraped": True,
        "is_failed": False,
        "title": "Flutter Developer",
        "description": "Join our healthcare tech team to build mobile applications...",
        "company": "HealthTech Solutions",
        "location": "Remote, UK",
        "salary_min": 50000.0,
        "salary_max": 70000.0,
        "url": "https://totaljobs.com/job/flutter-healthcare-567890",
        "scrape_datetime": "2025-09-03T14:22:45.789012+00:00",
    },
    {
        "external_job_id": "reed_345678",
        "owner_id": 2,
        "is_scraped": True,
        "is_failed": False,
        "title": "Machine Learning Engineer",
        "description": "Build cutting-edge ML solutions for AI startup...",
        "company": "InnovateTech Solutions",
        "location": "Edinburgh, UK",
        "salary_min": 65000.0,
        "salary_max": 90000.0,
        "url": "https://reed.co.uk/jobs/ml-engineer-edinburgh/345678",
        "scrape_datetime": "2025-09-05T09:33:12.345678+00:00",
    },
    {
        "external_job_id": "cvlib_678901",
        "owner_id": 2,
        "is_scraped": True,
        "is_failed": True,
        "scrape_error": "Access denied - company blocked scraping",
        "title": "Sustainability Software Engineer",
        "scrape_datetime": "2025-09-07T11:45:28.456789+00:00",
    },
    {
        "external_job_id": "jobsite_901234",
        "owner_id": 2,
        "is_scraped": True,
        "is_failed": False,
        "title": "Full Stack JavaScript Developer",
        "description": "Work with modern JavaScript frameworks in agile environment...",
        "company": "StartupXYZ",
        "location": "Manchester, UK",
        "salary_min": 55000.0,
        "salary_max": 80000.0,
        "url": "https://jobsite.co.uk/job/fullstack-js-manchester-901234",
        "scrape_datetime": "2025-09-09T13:20:15.567890+00:00",
    },
    {
        "external_job_id": "soft123456789",
        "owner_id": 2,
        "is_scraped": True,
        "is_failed": True,
        "scrape_error": "Rate limit exceeded - retry after 24 hours",
        "title": "Software Engineer",
        "scrape_datetime": "2025-09-11T15:30:42.678901+00:00",
    },
]


SERVICE_LOG_DATA = [
    {
        "name": "Email Scraper Service",
        "run_duration": 45.2,
        "run_datetime": "2024-01-15 08:30:00",
        "is_success": True,
        "error_message": None,
        "job_success_n": 25,
        "job_fail_n": 2,
    },
    {
        "name": "Email Scraper Service",
        "run_duration": 123.8,
        "run_datetime": "2024-01-15 09:15:00",
        "is_success": True,
        "error_message": None,
        "job_success_n": 89,
        "job_fail_n": 5,
    },
    {
        "name": "Email Scraper Service",
        "run_duration": 67.4,
        "run_datetime": "2024-01-15 10:00:00",
        "is_success": False,
        "error_message": "Rate limit exceeded after 30 requests",
        "job_success_n": 15,
        "job_fail_n": 45,
    },
    {
        "name": "Email Scraper Service",
        "run_duration": 89.1,
        "run_datetime": "2024-01-15 11:30:00",
        "is_success": True,
        "error_message": None,
        "job_success_n": 73,
        "job_fail_n": 8,
    },
    {
        "name": "Email Scraper Service",
        "run_duration": 12.3,
        "run_datetime": "2024-01-15 12:00:00",
        "is_success": True,
        "error_message": None,
        "job_success_n": None,
        "job_fail_n": None,
    },
    {
        "name": "Email Scraper Service",
        "run_duration": 3.7,
        "run_datetime": "2024-01-15 13:45:00",
        "is_success": False,
        "error_message": "SMTP server connection timeout",
        "job_success_n": 0,
        "job_fail_n": 12,
    },
    {
        "name": "Email Scraper Service",
        "run_duration": 156.9,
        "run_datetime": "2024-01-15 14:20:00",
        "is_success": True,
        "error_message": None,
        "job_success_n": 234,
        "job_fail_n": 18,
    },
    {
        "name": "Email Scraper Service",
        "run_duration": 78.5,
        "run_datetime": "2024-01-15 15:30:00",
        "is_success": False,
        "error_message": "PDF parsing library crashed on corrupted file",
        "job_success_n": 45,
        "job_fail_n": 67,
    },
    {
        "name": "Email Scraper Service",
        "run_duration": 34.2,
        "run_datetime": "2024-01-16 08:00:00",
        "is_success": True,
        "error_message": None,
        "job_success_n": 156,
        "job_fail_n": 3,
    },
]
SERVICE_LOG_DATETIME = [current_date - timedelta(days=i) for i in range(len(SERVICE_LOG_DATA))]
for service_log, date in zip(SERVICE_LOG_DATA, SERVICE_LOG_DATETIME):
    service_log["run_datetime"] = date.strftime(DATETIME_FORMAT)


EMAIL_SCRAPEDJOB_MAPPINGS = [
    {"email_id": 1, "scraped_job_ids": [1, 2, 4]},
    {"email_id": 2, "scraped_job_ids": [3, 5]},
    {"email_id": 3, "scraped_job_ids": [2, 5]},
    {"email_id": 7, "scraped_job_ids": [8]},
    {"email_id": 8, "scraped_job_ids": [9]},
    {"email_id": 9, "scraped_job_ids": [10]},
    {"email_id": 10, "scraped_job_ids": [11]},
    {"email_id": 11, "scraped_job_ids": [12]},
]


def add_mappings(
    primary_data: list,
    secondary_data: list,
    mapping_data: list,
    primary_key: str,
    secondary_key: str,
    relationship_attr: str,
) -> None:
    """Generic function to add many-to-many relationships between data objects.
    :param primary_data: List of primary objects (e.g. jobs, interviews)
    :param secondary_data: List of secondary objects (e.g. keywords, persons)
    :param mapping_data: List of mapping dictionaries
    :param primary_key: Key name for primary object ID in mapping (e.g. "job_id", "interview_id")
    :param secondary_key: Key name for secondary object IDs in mapping (e.g. "keyword_ids", "person_ids")
    :param relationship_attr: Attribute name on a primary object for the relationship (e.g. "keywords", "contacts")"""

    for mapping in mapping_data:
        primary_obj = primary_data[mapping[primary_key] - 1]  # Convert to 0-based index
        secondary_ids = mapping[secondary_key]

        for secondary_id in secondary_ids:
            secondary_obj = secondary_data[secondary_id - 1]  # Convert to 0-based index
            getattr(primary_obj, relationship_attr).append(secondary_obj)


def validate_ownership_integrity_detailed(data_collections: dict) -> dict:
    """Comprehensive function that checks ownership integrity across all relationships in the database.
    Validates that:
    1. All direct foreign key relationships respect owner boundaries
    2. All many-to-many mapping relationships respect owner boundaries
    3. Provides detailed reporting of violations and statistics
    :param data_collections: Dictionary containing all data collections"""

    results = {
        "direct_foreign_key_violations": [],
        "mapping_violations": [],
        "statistics": {
            "tables_checked": 0,
            "entries_validated": 0,
            "relationships_validated": 0,
            "users_found": set(),
        },
        "edge_cases": [],
        "summary": {},
    }

    # Helper functions
    def find_owner_by_id(collection_name: str, entry_id: int) -> int | None:
        """Find owner_id of an entry by its ID (1-based)
        :param collection_name: Name of the data collection
        :param entry_id: 1-based ID of the entry"""

        collection = data_collections.get(collection_name, [])
        if isinstance(entry_id, (int, float)) and 1 <= entry_id <= len(collection):
            entry_ = collection[int(entry_id) - 1]  # Convert to 0-based index
            owner_id = entry_.get("owner_id")
            if owner_id is not None:
                results["statistics"]["users_found"].add(owner_id)
            return owner_id
        return None

    def log_edge_case(case_type: str, description: str, details: dict) -> None:
        """Log edge cases for analysis
        :param case_type: Type of edge case
        :param description: Description of the edge case
        :param details: Additional details about the case"""

        results["edge_cases"].append({"type": case_type, "description": description, "details": details})

    # Define all foreign key relationships
    fk_relationships = {
        "PERSON_DATA": [("company_id", "COMPANY_DATA", "optional")],  # Can be None
        "JOB_DATA": [
            ("company_id", "COMPANY_DATA", "optional"),
            ("location_id", "LOCATION_DATA", "optional"),
            ("source_id", "AGGREGATOR_DATA", "optional"),
            ("cv_id", "FILE_DATA", "optional"),
            ("cover_letter_id", "FILE_DATA", "optional"),
            ("application_aggregator_id", "AGGREGATOR_DATA", "optional"),
        ],
        "INTERVIEW_DATA": [
            ("location_id", "LOCATION_DATA", "optional"),
            ("job_id", "JOB_DATA", "required"),  # Should always have a job
        ],
        "JOB_APPLICATION_UPDATE_DATA": [("job_id", "JOB_DATA", "required")],  # Should always reference a job
    }

    print("=== OWNERSHIP INTEGRITY VALIDATION ===\n")

    # Phase 1: Validate direct foreign key relationships
    print("Phase 1: Validating direct foreign key relationships...")

    for table_name, relationships in fk_relationships.items():
        table_data = data_collections.get(table_name, [])
        if not table_data:
            continue

        results["statistics"]["tables_checked"] += 1
        print(f"  Checking {table_name}: {len(table_data)} entries")

        for entry_idx, entry in enumerate(table_data):
            results["statistics"]["entries_validated"] += 1
            entry_owner = entry.get("owner_id")

            # Track users
            if entry_owner is not None:
                results["statistics"]["users_found"].add(entry_owner)

            for fk_field, referenced_table, constraint in relationships:
                results["statistics"]["relationships_validated"] += 1
                fk_value = entry.get(fk_field)

                # Handle different constraint types
                if constraint == "required" and fk_value is None:
                    log_edge_case(
                        "missing_required_fk",
                        f"Required foreign key {fk_field} is None",
                        {"table": table_name, "entry_idx": entry_idx + 1},
                    )
                    continue

                if fk_value is not None:
                    referenced_owner = find_owner_by_id(referenced_table, fk_value)

                    if referenced_owner is None:
                        log_edge_case(
                            "invalid_fk_reference",
                            f"Foreign key {fk_field} references non-existent entry",
                            {
                                "table": table_name,
                                "entry_idx": entry_idx + 1,
                                "fk_value": fk_value,
                                "referenced_table": referenced_table,
                            },
                        )
                        continue

                    if referenced_owner != entry_owner:
                        results["direct_foreign_key_violations"].append(
                            {
                                "severity": "HIGH",
                                "table": table_name,
                                "entry_index": entry_idx + 1,
                                "entry_data": {
                                    k: v for k, v in entry.items() if k not in ["description", "body"]
                                },  # Exclude long text
                                "entry_owner": entry_owner,
                                "field": fk_field,
                                "referenced_id": fk_value,
                                "referenced_table": referenced_table,
                                "referenced_owner": referenced_owner,
                                "violation_type": "cross_user_reference",
                                "message": f"User {entry_owner} entry references {referenced_table} owned by user {referenced_owner}",
                            }
                        )

    # Phase 2: Validate mapping relationships
    print(f"\nPhase 2: Validating mapping relationships...")

    mapping_relationships = {
        "JOB_KEYWORD_MAPPINGS": {
            "primary_table": "JOB_DATA",
            "primary_id_field": "job_id",
            "secondary_table": "KEYWORD_DATA",
            "secondary_ids_field": "keyword_ids",
            "description": "Job-Keyword associations",
        },
        "JOB_CONTACT_MAPPINGS": {
            "primary_table": "JOB_DATA",
            "primary_id_field": "job_id",
            "secondary_table": "PERSON_DATA",
            "secondary_ids_field": "person_ids",
            "description": "Job-Contact person associations",
        },
        "INTERVIEW_INTERVIEWER_MAPPINGS": {
            "primary_table": "INTERVIEW_DATA",
            "primary_id_field": "interview_id",
            "secondary_table": "PERSON_DATA",
            "secondary_ids_field": "person_ids",
            "description": "Interview-Interviewer associations",
        },
        "EMAIL_SCRAPEDJOB_MAPPINGS": {
            "primary_table": "JOB_ALERT_EMAIL_DATA",
            "primary_id_field": "email_id",
            "secondary_table": "JOB_SCRAPED_DATA",
            "secondary_ids_field": "scraped_job_ids",
            "description": "Email-Scraped job associations",
        },
    }

    for mapping_name, config in mapping_relationships.items():
        mapping_data = data_collections.get(mapping_name, [])
        if not mapping_data:
            continue

        print(f"  Checking {mapping_name}: {len(mapping_data)} mappings - {config['description']}")

        for mapping_idx, mapping in enumerate(mapping_data):
            primary_id = mapping.get(config["primary_id_field"])
            secondary_ids = mapping.get(config["secondary_ids_field"], [])

            if primary_id is None:
                log_edge_case(
                    "missing_primary_id",
                    f"Mapping missing primary ID {config['primary_id_field']}",
                    {"mapping_table": mapping_name, "mapping_idx": mapping_idx + 1},
                )
                continue

            primary_owner = find_owner_by_id(config["primary_table"], primary_id)

            if primary_owner is None:
                log_edge_case(
                    "invalid_primary_reference",
                    f"Mapping references non-existent primary entry",
                    {"mapping_table": mapping_name, "primary_id": primary_id},
                )
                continue

            for secondary_id in secondary_ids:
                results["statistics"]["relationships_validated"] += 1
                secondary_owner = find_owner_by_id(config["secondary_table"], secondary_id)

                if secondary_owner is None:
                    log_edge_case(
                        "invalid_secondary_reference",
                        f"Mapping references non-existent secondary entry",
                        {"mapping_table": mapping_name, "secondary_id": secondary_id},
                    )
                    continue

                if primary_owner != secondary_owner:
                    results["mapping_violations"].append(
                        {
                            "severity": "MEDIUM",
                            "mapping_table": mapping_name,
                            "mapping_index": mapping_idx + 1,
                            "mapping_data": mapping,
                            "primary_table": config["primary_table"],
                            "primary_id": primary_id,
                            "primary_owner": primary_owner,
                            "secondary_table": config["secondary_table"],
                            "secondary_id": secondary_id,
                            "secondary_owner": secondary_owner,
                            "violation_type": "cross_user_mapping",
                            "message": f"Mapping connects {config['primary_table']} (user {primary_owner}) with {config['secondary_table']} (user {secondary_owner})",
                        }
                    )

    # Phase 3: Generate comprehensive summary
    print(f"\nPhase 3: Generating summary report...")

    total_violations = len(results["direct_foreign_key_violations"]) + len(results["mapping_violations"])

    results["summary"] = {
        "validation_status": "PASS" if total_violations == 0 else "FAIL",
        "total_violations": total_violations,
        "high_severity_violations": len(results["direct_foreign_key_violations"]),
        "medium_severity_violations": len(results["mapping_violations"]),
        "edge_cases_found": len(results["edge_cases"]),
        "tables_validated": results["statistics"]["tables_checked"],
        "entries_validated": results["statistics"]["entries_validated"],
        "relationships_validated": results["statistics"]["relationships_validated"],
        "unique_users": len(results["statistics"]["users_found"]),
        "user_ids_found": sorted(list(results["statistics"]["users_found"])),
    }

    return results


analysis_results = validate_ownership_integrity_detailed(
    {
        "COMPANY_DATA": COMPANY_DATA,
        "LOCATION_DATA": LOCATION_DATA,
        "PERSON_DATA": PERSON_DATA,
        "JOB_DATA": JOB_DATA,
        "INTERVIEW_DATA": INTERVIEW_DATA,
        "FILE_DATA": FILE_DATA,
        "KEYWORD_DATA": KEYWORD_DATA,
        "AGGREGATOR_DATA": AGGREGATOR_DATA,
        "JOB_APPLICATION_UPDATE_DATA": JOB_APPLICATION_UPDATE_DATA,
        "JOB_ALERT_EMAIL_DATA": JOB_ALERT_EMAIL_DATA,
        "JOB_SCRAPED_DATA": JOB_SCRAPED_DATA,
        "JOB_KEYWORD_MAPPINGS": JOB_KEYWORD_MAPPINGS,
        "JOB_CONTACT_MAPPINGS": JOB_CONTACT_MAPPINGS,
        "INTERVIEW_INTERVIEWER_MAPPINGS": INTERVIEW_INTERVIEWER_MAPPINGS,
        "EMAIL_SCRAPEDJOB_MAPPINGS": EMAIL_SCRAPEDJOB_MAPPINGS,
    }
)


if analysis_results["summary"]["validation_status"] == "FAIL":
    print("\n=== DETAILED VIOLATION REPORT ===\n")

    if analysis_results["direct_foreign_key_violations"]:
        print("Direct Foreign Key Violations:")
        for violation in analysis_results["direct_foreign_key_violations"]:
            print(violation)

    if analysis_results["mapping_violations"]:
        print("\nMapping Violations:")
        for violation in analysis_results["mapping_violations"]:
            print(violation)

    if analysis_results["edge_cases"]:
        print("\nEdge Cases:")
        for edge_case in analysis_results["edge_cases"]:
            print(edge_case)

    raise AssertionError("Ownership integrity validation failed - see report above.")
