"""Centralized test data for both conftest.py and seed_database.py"""

from datetime import datetime

from tests.utils.files import load_all_resource_files

RESOURCE_FILES = load_all_resource_files()


USERS_DATA = [
    {
        "email": "test_user@test.com",
        "password": "test_password",
    },
    {
        "email": "emmanuel.pean@gmail.com",
        "password": "password2",
    },
    {
        "email": "jessicaaggood@live.co.uk",
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
    {
        "email": "developer@techstartup.com",
        "password": "password6",
    },
]


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
        "name": "CloudFirst Inc",
        "description": None,
        "url": "https://cloudfirst.io",
        "owner_id": 1,
    },
    {
        "name": "Minimal Corp",
        "owner_id": 1,  # Only required fields
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
]


LOCATIONS_DATA = [
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
]


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
    # New entries
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
]


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
    # New keywords for better coverage
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
]


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
        "first_name": "Anonymous",
        "last_name": "Recruiter",
        "company_id": None,
        "owner_id": 1,
    },
    {
        "first_name": "Tech",
        "last_name": "Recruiter",
        "role": "Talent Acquisition",
        "company_id": 3,  # Oxford PV
        "owner_id": 1,
    },
    # New entries with different combinations
    {
        "first_name": "Alex",
        "last_name": "Johnson",
        "email": "alex@cloudfirst.io",
        "phone": "5551234567",
        "linkedin_url": "https://linkedin.com/in/alexjohnson",
        "role": "CTO",
        "company_id": 6,  # CloudFirst Inc
        "owner_id": 1,
    },
    {
        "first_name": "Maria",
        "last_name": "Garcia",
        "email": "maria.garcia@enterprise.com",
        "role": "HR Director",
        "company_id": 9,  # Enterprise Solutions
        "owner_id": 1,
    },
    {
        "first_name": "David",
        "last_name": "Kim",
        "phone": "5559876543",
        "linkedin_url": "https://linkedin.com/in/davidkim",
        "company_id": None,  # Freelancer/Independent
        "owner_id": 1,
    },
    {
        "first_name": "Lisa",
        "last_name": "Chen",
        "email": "lisa@localbiz.com",
        "role": "Founder",
        "company_id": 10,  # LocalBiz
        "owner_id": 1,
    },
    {
        "first_name": "Robert",
        "last_name": "Anderson",
        "linkedin_url": "https://linkedin.com/in/robertanderson",
        "role": "Senior Developer",
        "company_id": 7,  # Minimal Corp
        "owner_id": 1,
    },
    {
        "first_name": "Jennifer",
        "last_name": "Brown",
        "phone": "5555551234",
        "role": "Product Owner",
        "company_id": 8,  # No URL Company
        "owner_id": 1,
    },
    {
        "first_name": "Michael",
        "last_name": "Wilson",
        "email": "m.wilson@datatech.com",
        "phone": "5557778888",
        "linkedin_url": "https://linkedin.com/in/michaelwilson",
        "role": "Data Scientist",
        "company_id": 5,  # DataTech Industries
        "owner_id": 1,
    },
    {
        "first_name": "Freelance",
        "last_name": "Developer",
        "email": "freelance@dev.com",
        "owner_id": 1,  # No company, minimal info
    },
]

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
        "location_id": 5,  # Berlin (remote)
        "owner_id": 1,
    },
    {
        "title": "Backend Developer",
        "description": "Looking for a backend developer with Python experience. FastAPI knowledge preferred.",
        "location_id": 4,  # San Francisco (remote)
        "owner_id": 1,
    },
    {
        "title": "Software Engineer Intern",
        "description": "Summer internship opportunity for computer science students. Great learning environment.",
        "personal_rating": 1,
        "company_id": 3,  # Oxford PV
        "owner_id": 1,
    },
    {
        "title": "Developer Position",
        "company_id": 3,  # Oxford PV
        "location_id": 5,  # Berlin (remote)
        "owner_id": 1,
    },
    # New entries with different parameter combinations
    {
        "title": "DevOps Engineer",
        "salary_min": 90000,
        "salary_max": 140000,
        "description": "Build and maintain CI/CD pipelines, manage cloud infrastructure",
        "personal_rating": 5,
        "url": "https://cloudfirst.io/careers/devops",
        "company_id": 6,  # CloudFirst Inc
        "location_id": 8,  # Paris
        "note": "Strong DevOps culture, great tools",
        "owner_id": 1,
    },
    {
        "title": "Data Scientist",
        "salary_min": 85000,
        "salary_max": 125000,
        "description": "Work with big data to derive insights and build ML models",
        "personal_rating": 4,
        "company_id": 5,  # DataTech Industries
        "location_id": 9,  # Germany (no city)
        "owner_id": 1,
    },
    {
        "title": "Vue.js Frontend Developer",
        "salary_min": 50000,
        "salary_max": 80000,
        "description": "Build modern SPAs with Vue.js and TypeScript",
        "url": "https://enterprise-solutions.com/jobs/vue-dev",
        "company_id": 9,  # Enterprise Solutions
        "location_id": 10,  # Tokyo
        "owner_id": 1,
    },
    {
        "title": "Remote Full Stack Engineer",
        "salary_min": 70000,
        "salary_max": 110000,
        "description": "Work remotely on full stack applications",
        "personal_rating": 3,
        "url": "https://localbiz.com/jobs/fullstack",
        "company_id": 10,  # LocalBiz
        "location_id": 11,  # Australia (remote)
        "note": "Small team, lots of autonomy",
        "owner_id": 1,
    },
    {
        "title": "Junior Developer",
        "salary_min": 40000,
        "salary_max": 60000,
        "description": "Entry-level position for new graduates",
        "personal_rating": 2,
        "company_id": 7,  # Minimal Corp
        "location_id": 12,  # Toronto
        "owner_id": 1,
    },
    {
        "title": "Freelance Web Developer",
        "description": "Contract position for web development projects",
        "location_id": 13,  # Amsterdam (remote)
        "note": "Flexible hours, project-based",
        "owner_id": 1,
    },
    {
        "title": "Mobile App Developer",
        "salary_min": 60000,
        "salary_max": 100000,
        "description": "Develop iOS and Android applications",
        "personal_rating": 4,
        "url": "https://websolutions.com/jobs/mobile-dev",
        "company_id": 4,  # WebSolutions Ltd
        "location_id": 14,  # Brazil (remote)
        "owner_id": 1,
    },
    {
        "title": "Minimum Required Job",
        "owner_id": 1,
    },
    {
        "title": "High Salary Position",
        "salary_min": 150000,
        "salary_max": 250000,
        "description": "Senior leadership role with high compensation",
        "personal_rating": 5,
        "company_id": 9,  # Enterprise Solutions
        "location_id": 1,  # New York
        "owner_id": 1,
    },
]


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
        "filename": "frontend_developer_cover_letter.docx",
        "owner_id": 1,
        **RESOURCE_FILES["Cover Letter.docx"],
    },
    # New entries
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
]


JOB_APPLICATIONS_DATA = [
    {
        "date": "2024-01-15T10:00:00",
        "url": "https://techcorp.com/apply/senior-python",
        "job_id": 1,
        "status": "Applied",
        "note": "Submitted application with cover letter",
        "cv_id": 3,
        "cover_letter_id": 3,
        "owner_id": 1,
    },
    {
        "date": "2024-01-16T14:30:00",
        "url": "https://startupxyz.com/apply/fullstack-js",
        "job_id": 2,
        "status": "Interview",
        "note": "Phone screening scheduled for next week",
        "cv_id": 1,
        "owner_id": 1,
    },
    {
        "date": "2024-01-17T09:15:00",
        "job_id": 3,
        "status": "Applied",
        "note": "Applied through LinkedIn",
        "cover_letter_id": 2,
        "owner_id": 1,
    },
    {
        "date": "2024-01-18T16:45:00",
        "url": "https://startupxyz.com/careers/cloud-engineer",
        "job_id": 4,
        "status": "Rejected",
        "note": "Not enough cloud experience",
        "cv_id": 4,
        "cover_letter_id": 4,
        "owner_id": 1,
    },
    {
        "date": "2024-01-20T13:30:00",
        "job_id": 6,
        "status": "Applied",
        "note": "Quick application through company form",
        "owner_id": 1,
    },
    # New entries with different combinations
    {
        "date": "2024-01-21T09:00:00",
        "url": "https://cloudfirst.io/apply/devops",
        "job_id": 9,  # DevOps Engineer
        "status": "Interview",
        "note": "Technical interview scheduled",
        "cv_id": 8,  # devops_engineer_cv.pdf
        "cover_letter_id": 10,  # vue_developer_cover_letter.txt
        "owner_id": 1,
    },
    {
        "date": "2024-01-22T11:15:00",
        "job_id": 10,  # Data Scientist
        "status": "Applied",
        "cv_id": 9,  # data_scientist_resume.pdf
        "owner_id": 1,
    },
    {
        "date": "2024-01-23T15:45:00",
        "url": "https://enterprise-solutions.com/apply/vue-dev",
        "job_id": 11,  # Vue.js Frontend Developer
        "status": "Rejected",
        "note": "Position filled internally",
        "cv_id": 6,
        "cover_letter_id": 12,  # generic_cover_letter.docx
        "owner_id": 1,
    },
    {
        "date": "2024-01-24T08:30:00",
        "job_id": 12,  # Remote Full Stack Engineer
        "status": "Applied",
        "note": "Applied directly through website",
        "cv_id": 3,
        "owner_id": 1,
    },
    {
        "date": "2024-01-25T10:00:00",
        "job_id": 13,  # Junior Developer
        "status": "Interview",
        "cv_id": 1,
        "cover_letter_id": 7,
        "owner_id": 1,
    },
    {
        "date": "2024-01-26T16:00:00",
        "url": "https://websolutions.com/apply/mobile-dev",
        "job_id": 15,  # Mobile App Developer
        "status": "Applied",
        "note": "Excited about mobile development opportunity",
        "cv_id": 11,  # mobile_dev_portfolio.pdf
        "owner_id": 1,
    },
    {
        "date": "2024-01-27T12:00:00",
        "job_id": 16,  # Minimum Required Job
        "status": "Applied",
        "owner_id": 1,  # Minimal application
    },
    {
        "date": "2024-01-28T14:20:00",
        "url": "https://enterprise-solutions.com/apply/high-salary",
        "job_id": 17,  # High Salary Position
        "status": "Interview",
        "note": "Executive-level interview process",
        "cv_id": 8,
        "cover_letter_id": 2,
        "owner_id": 1,
    },
]


INTERVIEWS_DATA = [
    {
        "date": "2024-01-20T09:30:00",
        "type": "HR",
        "location_id": 1,
        "jobapplication_id": 1,
        "note": "First round technical interview",
        "owner_id": 1,
    },
    {
        "date": "2024-01-21T14:00:00",
        "type": "Technical",
        "location_id": 2,
        "jobapplication_id": 2,
        "note": "HR screening call",
        "owner_id": 1,
    },
    {
        "date": "2024-01-22T10:15:00",
        "type": "Management",
        "location_id": 4,  # Remote
        "jobapplication_id": 3,
        "note": "Remote technical assessment",
        "owner_id": 1,
    },
    {
        "date": "2024-01-23T16:30:00",
        "type": "HR",
        "location_id": 1,
        "jobapplication_id": 4,
        "note": "Final round with team lead",
        "owner_id": 1,
    },
    {
        "date": "2024-01-24T11:45:00",
        "type": "Other",
        "location_id": 3,
        "jobapplication_id": 5,
        "note": "Cultural fit interview",
        "owner_id": 1,
    },
    {
        "date": "2024-01-26T09:00:00",
        "type": "HR",
        "location_id": 7,  # Canada location
        "jobapplication_id": 1,  # Same application, second interview
        "note": None,
        "owner_id": 1,
    },
    # New entries with different combinations
    {
        "date": "2024-01-29T10:30:00",
        "type": "Technical",
        "location_id": 8,  # Paris
        "jobapplication_id": 6,  # DevOps application
        "note": "Deep technical dive into infrastructure",
        "owner_id": 1,
    },
    {
        "date": "2024-01-30T15:00:00",
        "type": "Management",
        "location_id": 11,  # Australia (remote)
        "jobapplication_id": 8,  # Remote Full Stack application
        "note": "Meeting with team leads",
        "owner_id": 1,
    },
    {
        "date": "2024-02-01T09:45:00",
        "type": "HR",
        "location_id": 12,  # Toronto
        "jobapplication_id": 10,  # Junior Developer application
        "note": "Initial screening for junior position",
        "owner_id": 1,
    },
    {
        "date": "2024-02-02T11:00:00",
        "type": "Technical",
        "location_id": 14,  # Brazil (remote)
        "jobapplication_id": 11,  # Mobile App Developer
        "note": "Technical skills assessment for mobile development",
        "owner_id": 1,
    },
    {
        "date": "2024-02-03T14:15:00",
        "type": "Other",
        "location_id": 1,  # New York
        "jobapplication_id": 13,  # High Salary Position
        "note": "Panel interview with executives",
        "owner_id": 1,
    },
    {
        "date": "2024-02-04T16:30:00",
        "type": "Management",
        "location_id": 5,  # Germany (remote)
        "jobapplication_id": 7,  # Data Scientist application
        "owner_id": 1,  # Minimal interview info
    },
]


JOB_KEYWORD_MAPPINGS = [
    {"job_id": 1, "keyword_ids": [1, 2, 6, 7]},  # Senior Python Developer - Python, JavaScript, PostgreSQL, FastAPI
    {"job_id": 2, "keyword_ids": [2, 3, 4, 13]},  # Full Stack JS Developer - JavaScript, React, Node.js, REST API
    {"job_id": 3, "keyword_ids": [3, 2, 14]},  # Remote React Developer - React, JavaScript, Git
    {"job_id": 4, "keyword_ids": [12, 10, 11, 9]},  # Cloud Engineer - AWS, Docker, Kubernetes, DevOps
    {"job_id": 5, "keyword_ids": [2, 3, 14, 15]},  # Frontend Developer - JavaScript, React, Git, Agile
    # New mappings
    {"job_id": 9, "keyword_ids": [9, 10, 11, 22, 23]},  # DevOps Engineer - DevOps, Docker, Kubernetes, CI/CD, Terraform
    {"job_id": 10, "keyword_ids": [8, 1, 18]},  # Data Scientist - Machine Learning, Python, MongoDB
    {"job_id": 11, "keyword_ids": [16, 5, 2]},  # Vue.js Developer - Vue.js, TypeScript, JavaScript
    {"job_id": 12, "keyword_ids": [2, 3, 4, 1]},  # Remote Full Stack - JavaScript, React, Node.js, Python
    {"job_id": 13, "keyword_ids": [2, 14, 15]},  # Junior Developer - JavaScript, Git, Agile
    {"job_id": 15, "keyword_ids": [2, 3, 17]},  # Mobile App Developer - JavaScript, React, Angular
]

JOB_CONTACT_MAPPINGS = [
    {"job_id": 1, "person_ids": [1, 3]},  # Senior Python Developer - John Doe, Mike Taylor
    {"job_id": 2, "person_ids": [2, 4]},  # Full Stack JS Developer - Jane Smith, Emily Davis
    {"job_id": 3, "person_ids": [1]},  # Remote React Developer - John Doe
    {"job_id": 4, "person_ids": [4]},  # Cloud Engineer - Emily Davis
    {"job_id": 5, "person_ids": [5]},  # Frontend Developer - Chris Brown
    # New mappings
    {"job_id": 9, "person_ids": [9]},  # DevOps Engineer - Alex Johnson
    {"job_id": 10, "person_ids": [15]},  # Data Scientist - Michael Wilson
    {"job_id": 11, "person_ids": [10]},  # Vue.js Developer - Maria Garcia
    {"job_id": 12, "person_ids": [12]},  # Remote Full Stack - Lisa Chen
    {"job_id": 13, "person_ids": [13]},  # Junior Developer - Robert Anderson
    {"job_id": 15, "person_ids": [11, 16]},  # Mobile App Developer - David Kim, Freelance Developer
]

INTERVIEW_INTERVIEWER_MAPPINGS = [
    {"interview_id": 1, "person_ids": [1]},  # First round - John Doe
    {"interview_id": 2, "person_ids": [2]},  # HR screening - Jane Smith
    {"interview_id": 3, "person_ids": [3, 5]},  # Remote assessment - Mike Taylor, Chris Brown
    {"interview_id": 4, "person_ids": [1]},  # Final round - John Doe
    {"interview_id": 5, "person_ids": [4]},  # Cultural fit - Emily Davis
    # New mappings
    {"interview_id": 7, "person_ids": [9]},  # DevOps technical - Alex Johnson
    {"interview_id": 8, "person_ids": [12, 11]},  # Remote Full Stack - Lisa Chen, David Kim
    {"interview_id": 9, "person_ids": [13]},  # Junior Developer - Robert Anderson
    {"interview_id": 10, "person_ids": [16]},  # Mobile App - Freelance Developer
    {"interview_id": 11, "person_ids": [10, 15]},  # High Salary Position - Maria Garcia, Michael Wilson
    {"interview_id": 12, "person_ids": [15]},  # Data Scientist - Michael Wilson
]


JOB_ALERT_EMAILS_DATA = [
    {
        "owner_id": 1,
        "external_email_id": "linkedin_alert_001",
        "subject": "10 new jobs matching Python Developer",
        "sender": "jobs-noreply@linkedin.com",
        "date_received": datetime(2024, 1, 15, 9, 30, 0),
        "platform": "linkedin",
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
        "date_received": datetime(2024, 1, 16, 14, 45, 0),
        "platform": "indeed",
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
        "owner_id": 2,
        "external_email_id": "linkedin_alert_002",
        "subject": "Data Scientist positions you might like",
        "sender": "jobs-noreply@linkedin.com",
        "date_received": datetime(2024, 1, 17, 11, 20, 0),
        "platform": "linkedin",
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
        "date_received": datetime(2024, 1, 18, 8, 15, 0),
        "platform": "indeed",
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
        "date_received": datetime(2024, 1, 19, 16, 10, 0),
        "platform": "linkedin",
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
        "owner_id": 3,
        "external_email_id": "indeed_alert_003",
        "subject": "Frontend Developer jobs in your area",
        "sender": "job-alerts@indeed.co.uk",
        "date_received": datetime(2024, 1, 20, 12, 30, 0),
        "platform": "indeed",
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
]

JOB_ALERT_EMAIL_JOBS_DATA = [
    # LinkedIn Alert 001 jobs (email_id will be 1 assuming it's the first email)
    {"email_id": 1, "external_job_id": "3789012345", "owner_id": 1},
    {"email_id": 1, "external_job_id": "3789012346", "owner_id": 1},
    {"email_id": 1, "external_job_id": "3789012347", "owner_id": 1},
    # Indeed Alert 001 jobs (email_id will be 2)
    {"email_id": 2, "external_job_id": "job123456789", "owner_id": 1},
    {"email_id": 2, "external_job_id": "job987654321", "owner_id": 1},
    {"email_id": 2, "external_job_id": "job555666777", "owner_id": 1},
    # LinkedIn Alert 002 jobs (email_id will be 3)
    {"email_id": 3, "external_job_id": "3801234567", "owner_id": 2},
    {"email_id": 3, "external_job_id": "3801234568", "owner_id": 2},
    {"email_id": 3, "external_job_id": "3801234569", "owner_id": 2},
    # Indeed Alert 002 jobs (email_id will be 4)
    {"email_id": 4, "external_job_id": "data123", "owner_id": 2},
    {"email_id": 4, "external_job_id": "bi456789", "owner_id": 2},
    {"email_id": 4, "external_job_id": "eng999888", "owner_id": 2},
    {"email_id": 4, "external_job_id": "sci777666", "owner_id": 2},
    {"email_id": 4, "external_job_id": "ml444333", "owner_id": 2},
    # LinkedIn Alert 003 jobs (email_id will be 5)
    {"email_id": 5, "external_job_id": "3812345678", "owner_id": 1},
    {"email_id": 5, "external_job_id": "3812345679", "owner_id": 1},
    {"email_id": 5, "external_job_id": "3812345680", "owner_id": 1},
    # Indeed Alert 003 jobs (email_id will be 6)
    {"email_id": 6, "external_job_id": "react123", "owner_id": 3},
    {"email_id": 6, "external_job_id": "vue456789", "owner_id": 3},
    {"email_id": 6, "external_job_id": "ng789012", "owner_id": 3},
    {"email_id": 6, "external_job_id": "js345678", "owner_id": 3},
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
    :param primary_data: List of primary objects (e.g., jobs, interviews)
    :param secondary_data: List of secondary objects (e.g., keywords, persons)
    :param mapping_data: List of mapping dictionaries
    :param primary_key: Key name for primary object ID in mapping (e.g., "job_id", "interview_id")
    :param secondary_key: Key name for secondary object IDs in mapping (e.g., "keyword_ids", "person_ids")
    :param relationship_attr: Attribute name on primary object for the relationship (e.g., "keywords", "contacts")"""

    for mapping in mapping_data:
        primary_obj = primary_data[mapping[primary_key] - 1]  # Convert to 0-based index
        secondary_ids = mapping[secondary_key]

        for secondary_id in secondary_ids:
            secondary_obj = secondary_data[secondary_id - 1]  # Convert to 0-based index
            getattr(primary_obj, relationship_attr).append(secondary_obj)
