"""Centralized test data for both conftest.py and generate_test_data.py"""

USERS_DATA = [
    {
        "email": "emmanuel.pean@gmail.com",
        "password": "$2b$12$Dwf3QPkI2SSbcXkqw3gxkOTr9WZxVjSEkBfOLR4KuzW9zX/xfBjmW",
        "id": 1,
    },
    {
        "email": "jane.smith@example.com",
        "password": "$2b$12$hashed_password_here",
        "id": 2,
    },
    {
        "email": "mike.johnson@example.com",
        "password": "$2b$12$hashed_password_here",
        "id": 3,
    },
    {
        "email": "sarah.wilson@example.com",
        "password": "$2b$12$hashed_password_here",
        "id": 4,
    },
    {
        "email": "admin@example.com",
        "password": "$2b$12$hashed_password_here",
        "id": 5,
    },
]

# Company test data
COMPANIES_DATA = [
    {
        "name": "Tech Corp",
        "description": "A leading technology company specializing in web applications",
        "url": "https://techcorp.com",
        "owner_id": 1,
        "id": 1,
    },
    {
        "name": "StartupXYZ",
        "description": "An innovative startup focused on AI-driven solutions",
        "url": "https://startupxyz.com",
        "owner_id": 1,
        "id": 2,
    },
    {
        "name": "Oxford PV",
        "description": "Oxford-based company specializing in photovoltaic technology",
        "url": "https://oxfordpv.com",
        "owner_id": 1,
        "id": 3,
    },
    {
        "name": "WebSolutions Ltd",
        "description": "Full-service web development and digital marketing agency",
        "url": "https://websolutions.com",
        "owner_id": 2,
        "id": 4,
    },
    {
        "name": "DataTech Industries",
        "description": "Big data analytics and business intelligence solutions",
        "url": "https://datatech.com",
        "owner_id": 2,
        "id": 5,
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
        "id": 1,
    },
    {
        "postcode": "90210",
        "city": "Beverly Hills",
        "country": "USA",
        "remote": False,
        "owner_id": 1,
        "id": 2,
    },
    {
        "postcode": "SW1A 1AA",
        "city": "London",
        "country": "UK",
        "remote": False,
        "owner_id": 2,
        "id": 3,
    },
    {
        "city": "San Francisco",
        "country": "USA",
        "remote": True,
        "owner_id": 1,
        "id": 4,
    },
    {
        "country": "Germany",
        "remote": True,
        "owner_id": 2,
        "id": 5,
    },
    {
        "postcode": "OX1 2JD",
        "city": "Oxford",
        "country": "UK",
        "remote": False,
        "owner_id": 1,
        "id": 6,
    },
    {
        "country": "Canada",
        "remote": True,
        "owner_id": 2,
        "id": 7,
    },
]

# Aggregator test data
AGGREGATORS_DATA = [
    {
        "name": "LinkedIn",
        "url": "https://linkedin.com/jobs",
        "owner_id": 1,
        "id": 1,
    },
    {
        "name": "Indeed",
        "url": "https://indeed.com",
        "owner_id": 1,
        "id": 2,
    },
    {
        "name": "Glassdoor",
        "url": "https://glassdoor.com",
        "owner_id": 1,
        "id": 3,
    },
    {
        "name": "AngelList",
        "url": "https://angel.co",
        "owner_id": 2,
        "id": 4,
    },
    {
        "name": "Stack Overflow Jobs",
        "url": "https://stackoverflow.com/jobs",
        "owner_id": 2,
        "id": 5,
    },
]

# Keyword test data
KEYWORDS_DATA = [
    {
        "name": "Python",
        "owner_id": 1,
        "id": 1,
    },
    {
        "name": "JavaScript",
        "owner_id": 1,
        "id": 2,
    },
    {
        "name": "React",
        "owner_id": 1,
        "id": 3,
    },
    {
        "name": "Node.js",
        "owner_id": 1,
        "id": 4,
    },
    {
        "name": "TypeScript",
        "owner_id": 1,
        "id": 5,
    },
    {
        "name": "PostgreSQL",
        "owner_id": 1,
        "id": 6,
    },
    {
        "name": "FastAPI",
        "owner_id": 1,
        "id": 7,
    },
    {
        "name": "Machine Learning",
        "owner_id": 2,
        "id": 8,
    },
    {
        "name": "DevOps",
        "owner_id": 2,
        "id": 9,
    },
    {
        "name": "Docker",
        "owner_id": 2,
        "id": 10,
    },
    {
        "name": "Kubernetes",
        "owner_id": 2,
        "id": 11,
    },
    {
        "name": "AWS",
        "owner_id": 2,
        "id": 12,
    },
    {
        "name": "REST API",
        "owner_id": 1,
        "id": 13,
    },
    {
        "name": "Git",
        "owner_id": 1,
        "id": 14,
    },
    {
        "name": "Agile",
        "owner_id": 1,
        "id": 15,
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
        "id": 1,
    },
    {
        "first_name": "Jane",
        "last_name": "Smith",
        "email": "jane.smith@startupxyz.com",
        "linkedin_url": "https://linkedin.com/in/janesmith",
        "role": "Product Manager",
        "company_id": 2,  # StartupXYZ
        "owner_id": 1,
        "id": 2,
    },
    {
        "first_name": "Mike",
        "last_name": "Taylor",
        "phone": "9876543210",
        "role": "Lead Developer",
        "company_id": 1,  # Tech Corp
        "owner_id": 1,
        "id": 3,
    },
    {
        "first_name": "Emily",
        "last_name": "Davis",
        "email": "emily.davis@startupxyz.com",
        "role": "DevOps Engineer",
        "company_id": 2,  # StartupXYZ
        "owner_id": 1,
        "id": 4,
    },
    {
        "first_name": "Chris",
        "last_name": "Brown",
        "linkedin_url": "https://linkedin.com/in/chrisbrown",
        "role": "Data Science Manager",
        "company_id": 1,  # Tech Corp
        "owner_id": 1,
        "id": 5,
    },
    {
        "first_name": "Sarah",
        "last_name": "Wilson",
        "email": "sarah.wilson@oxfordpv.com",
        "role": "Technical Recruiter",
        "company_id": 3,  # Oxford PV
        "owner_id": 2,
        "id": 6,
    },
    {
        "first_name": "Anonymous",
        "last_name": "Recruiter",
        "company_id": None,
        "owner_id": 2,
        "id": 7,
    },
    {
        "first_name": "Tech",
        "last_name": "Recruiter",
        "role": "Talent Acquisition",
        "company_id": 3,  # Oxford PV
        "owner_id": 2,
        "id": 8,
    },
]

# Job test data
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
        "owner_id": 2,
    },
    {
        "title": "Software Engineer Intern",
        "description": "Summer internship opportunity for computer science students. Great learning environment.",
        "personal_rating": 1,
        "company_id": 3,  # Oxford PV
        "owner_id": 2,
    },
    {
        "title": "Developer Position",
        "company_id": 3,  # Oxford PV
        "location_id": 5,  # Berlin (remote)
        "owner_id": 2,
    },
]

# File test data
FILES_DATA = [
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
        "owner_id": 1,
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
        "owner_id": 1,
    },
    {
        "filename": "fullstack_developer_cv.pdf",
        "content": b"Full stack developer CV with React and Node.js experience - detailed project portfolio included...",
        "type": "application/pdf",
        "size": 1792,
        "owner_id": 1,
    },
    {
        "filename": "portfolio_cover_letter.txt",
        "content": b"Portfolio-based application cover letter highlighting creative projects and technical achievements...",
        "type": "text/plain",
        "size": 512,
        "owner_id": 1,
    },
    {
        "filename": "junior_cloud_cv.docx",
        "content": b"Junior developer CV with limited cloud experience but strong fundamentals in AWS and containerization...",
        "type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "size": 1024,
        "owner_id": 2,
    },
    {
        "filename": "cloud_engineer_cover_letter.pdf",
        "content": b"Standard cover letter for cloud engineer position emphasizing DevOps skills and infrastructure experience...",
        "type": "application/pdf",
        "size": 768,
        "owner_id": 2,
    },
    {
        "filename": "frontend_specialist_cv.pdf",
        "content": b"Frontend specialist CV with React focus - includes modern JavaScript frameworks and UI/UX design experience...",
        "type": "application/pdf",
        "size": 1280,
        "owner_id": 1,
    },
    {
        "filename": "frontend_developer_cover_letter.pdf",
        "content": b"Frontend developer cover letter showcasing responsive design skills and component library experience...",
        "type": "application/pdf",
        "size": 640,
        "owner_id": 1,
    },
    {
        "filename": "updated_cv_2024.pdf",
        "content": b"Updated CV with recent project experience including microservices architecture and cloud-native development...",
        "type": "application/pdf",
        "size": 2304,
        "owner_id": 2,
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
        "cv_id": 3,
        "cover_letter_id": 3,
        "owner_id": 1,
    },
    {
        "date": "2024-01-16T14:30:00",
        "url": "https://startupxyz.com/apply/fullstack-js",
        "job_id": 2,
        "status": "Interview Scheduled",
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
        "owner_id": 2,
    },
]

# Interview test data
INTERVIEWS_DATA = [
    {
        "date": "2024-01-20T09:30:00",
        "location_id": 1,
        "jobapplication_id": 1,
        "note": "First round technical interview",
        "owner_id": 1,
    },
    {
        "date": "2024-01-21T14:00:00",
        "location_id": 2,
        "jobapplication_id": 2,
        "note": "HR screening call",
        "owner_id": 1,
    },
    {
        "date": "2024-01-22T10:15:00",
        "location_id": 4,  # Remote
        "jobapplication_id": 3,
        "note": "Remote technical assessment",
        "owner_id": 1,
    },
    {
        "date": "2024-01-23T16:30:00",
        "location_id": 1,
        "jobapplication_id": 4,
        "note": "Final round with team lead",
        "owner_id": 1,
    },
    {
        "date": "2024-01-24T11:45:00",
        "location_id": 3,
        "jobapplication_id": 5,
        "note": "Cultural fit interview",
        "owner_id": 1,
    },
    {
        "date": "2024-01-25T16:00:00",
        "location_id": None,
        "jobapplication_id": 6,
        "note": "Phone screening with recruiter. Location TBD.",
        "owner_id": 2,
    },
    {
        "date": "2024-01-26T09:00:00",
        "location_id": 7,  # Canada location
        "jobapplication_id": 1,  # Same application, second interview
        "note": None,
        "owner_id": 1,
    },
]

# Relationship mappings for many-to-many relationships
JOB_KEYWORD_MAPPINGS = [
    {"job_id": 1, "keyword_ids": [1, 2, 6, 7]},  # Senior Python Developer - Python, JavaScript, PostgreSQL, FastAPI
    {"job_id": 2, "keyword_ids": [2, 3, 4, 13]},  # Full Stack JS Developer - JavaScript, React, Node.js, REST API
    {"job_id": 3, "keyword_ids": [3, 2, 14]},  # Remote React Developer - React, JavaScript, Git
    {"job_id": 4, "keyword_ids": [12, 10, 11, 9]},  # Cloud Engineer - AWS, Docker, Kubernetes, DevOps
    {"job_id": 5, "keyword_ids": [2, 3, 14, 15]},  # Frontend Developer - JavaScript, React, Git, Agile
]

JOB_CONTACT_MAPPINGS = [
    {"job_id": 1, "person_ids": [1, 3]},  # Senior Python Developer - John Doe, Mike Taylor
    {"job_id": 2, "person_ids": [2, 4]},  # Full Stack JS Developer - Jane Smith, Emily Davis
    {"job_id": 3, "person_ids": [1]},  # Remote React Developer - John Doe
    {"job_id": 4, "person_ids": [4]},  # Cloud Engineer - Emily Davis
    {"job_id": 5, "person_ids": [5]},  # Frontend Developer - Chris Brown
]

INTERVIEW_INTERVIEWER_MAPPINGS = [
    {"interview_id": 1, "person_ids": [1]},  # First round - John Doe
    {"interview_id": 2, "person_ids": [2]},  # HR screening - Jane Smith
    {"interview_id": 3, "person_ids": [3, 5]},  # Remote assessment - Mike Taylor, Chris Brown
    {"interview_id": 4, "person_ids": [1]},  # Final round - John Doe
    {"interview_id": 5, "person_ids": [4]},  # Cultural fit - Emily Davis
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
