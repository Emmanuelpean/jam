"""Test data for job scraping service tests."""

import datetime as dt
import random

from tests.utils.test_data.utils import CURRENT_DATE, DATETIME_FORMAT

JOB_EMAIL_DATA = [
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


JOB_SCRAPING_SERVICE_LOG_DATA = [
    {
        "run_duration": 45.2,
        "run_datetime": "2025-01-15 08:30:00",
        "is_success": True,
        "error_message": None,
        "user_processed_ids": [1, 2, 3, 4],
        "user_found_ids": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
    },
    {
        "run_duration": 123.8,
        "run_datetime": "2024-01-15 09:15:00",
        "is_success": True,
        "error_message": None,
        "user_processed_ids": [],
        "user_found_ids": [],
    },
    {
        "run_duration": 67.4,
        "run_datetime": "2024-01-15 10:00:00",
        "is_success": False,
        "error_message": "Rate limit exceeded after 30 requests",
        "user_processed_ids": [],
        "user_found_ids": [],
    },
    {
        "run_duration": 89.1,
        "run_datetime": "2024-01-15 11:30:00",
        "is_success": True,
        "error_message": None,
        "user_processed_ids": [],
        "user_found_ids": [],
    },
    {
        "run_duration": 12.3,
        "run_datetime": "2024-01-15 12:00:00",
        "is_success": True,
        "error_message": None,
        "user_processed_ids": [],
        "user_found_ids": [],
    },
    {
        "run_duration": 3.7,
        "run_datetime": "2024-01-15 13:45:00",
        "is_success": False,
        "error_message": "SMTP server connection timeout",
        "user_processed_ids": [],
        "user_found_ids": [],
    },
    {
        "run_duration": 156.9,
        "run_datetime": "2024-01-15 14:20:00",
        "is_success": True,
        "error_message": None,
        "user_processed_ids": [],
        "user_found_ids": [],
    },
    {
        "run_duration": 78.5,
        "run_datetime": "2024-01-15 15:30:00",
        "is_success": False,
        "error_message": "PDF parsing library crashed on corrupted file",
        "user_processed_ids": [],
        "user_found_ids": [],
    },
    {
        "run_duration": 34.2,
        "run_datetime": "2024-01-16 08:00:00",
        "is_success": True,
        "error_message": None,
        "user_processed_ids": [],
        "user_found_ids": [],
    },
]

SERVICE_LOG_DATETIME = [CURRENT_DATE - dt.timedelta(days=i) for i in range(len(JOB_SCRAPING_SERVICE_LOG_DATA))]
for service_log, date in zip(JOB_SCRAPING_SERVICE_LOG_DATA, SERVICE_LOG_DATETIME):
    service_log["run_datetime"] = date.strftime(DATETIME_FORMAT)


JOB_SCRAPING_PLATFORM_STAT_DATA = [
    {
        "name": "linkedin",
        "job_found_ids": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
        "job_scrape_succeeded_ids": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
        "job_scrape_failed_ids": [12, 13],
        "job_scrape_copied_ids": [14, 15, 16],
        "email_saved_ids": [1, 2, 3, 4, 5],
        "email_skipped_ids": [6],
        "service_log_id": 1,
    },
    {
        "name": "indeed",
        "job_found_ids": [17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28],
        "job_scrape_succeeded_ids": [17, 18, 19, 20, 21, 22, 23, 24, 25],
        "job_scrape_failed_ids": [26, 27],
        "job_scrape_copied_ids": [28],
        "email_saved_ids": [7, 8],
        "email_skipped_ids": [],
        "service_log_id": 1,
    },
    {
        "name": "veganjobs",
        "job_found_ids": [],
        "job_scrape_succeeded_ids": [],
        "job_scrape_failed_ids": [],
        "job_scrape_copied_ids": [],
        "email_saved_ids": [],
        "email_skipped_ids": [],
        "service_log_id": 1,
    },
    {
        "name": "linkedin",
        "job_found_ids": list(range(29, 69)),
        "job_scrape_succeeded_ids": list(range(29, 64)),
        "job_scrape_failed_ids": [64],
        "job_scrape_copied_ids": list(range(65, 75)),
        "email_saved_ids": list(range(9, 21)),
        "email_skipped_ids": [21, 22, 23],
        "service_log_id": 2,
    },
    {
        "name": "indeed",
        "job_found_ids": list(range(75, 83)),
        "job_scrape_succeeded_ids": list(range(75, 81)),
        "job_scrape_failed_ids": [81, 82],
        "job_scrape_copied_ids": [83, 84],
        "email_saved_ids": [24],
        "email_skipped_ids": [25],
        "service_log_id": 3,
    },
    {
        "name": "linkedin",
        "job_found_ids": list(range(85, 107)),
        "job_scrape_succeeded_ids": list(range(85, 105)),
        "job_scrape_failed_ids": [],
        "job_scrape_copied_ids": list(range(105, 109)),
        "email_saved_ids": list(range(26, 33)),
        "email_skipped_ids": [],
        "service_log_id": 4,
    },
    {
        "name": "indeed",
        "job_found_ids": list(range(109, 119)),
        "job_scrape_succeeded_ids": list(range(109, 118)),
        "job_scrape_failed_ids": [118],
        "job_scrape_copied_ids": [119],
        "email_saved_ids": [33, 34, 35],
        "email_skipped_ids": [36, 37],
        "service_log_id": 4,
    },
    {
        "name": "linkedin",
        "job_found_ids": list(range(120, 125)),
        "job_scrape_succeeded_ids": list(range(120, 124)),
        "job_scrape_failed_ids": [],
        "job_scrape_copied_ids": [],
        "email_saved_ids": [38],
        "email_skipped_ids": [],
        "service_log_id": 5,
    },
    {
        "name": "totaljobs",
        "job_found_ids": [125, 126, 127],
        "job_scrape_succeeded_ids": [125, 126, 127],
        "job_scrape_failed_ids": [],
        "job_scrape_copied_ids": [128],
        "email_saved_ids": [],
        "email_skipped_ids": [],
        "service_log_id": 6,
    },
    {
        "name": "linkedin",
        "job_found_ids": list(range(129, 135)),
        "job_scrape_succeeded_ids": list(range(129, 134)),
        "job_scrape_failed_ids": [134],
        "job_scrape_copied_ids": [135, 136],
        "email_saved_ids": [39, 40, 41, 42],
        "email_skipped_ids": [43],
        "service_log_id": 7,
    },
    {
        "name": "cv-library",
        "job_found_ids": [137, 138, 139, 140],
        "job_scrape_succeeded_ids": [],
        "job_scrape_failed_ids": [137, 138, 139, 140],
        "job_scrape_copied_ids": [],
        "email_saved_ids": [],
        "email_skipped_ids": [44, 45],
        "service_log_id": 8,
    },
    {
        "name": "jobsite",
        "job_found_ids": list(range(141, 148)),
        "job_scrape_succeeded_ids": list(range(141, 148)),
        "job_scrape_failed_ids": [],
        "job_scrape_copied_ids": [148, 149, 150],
        "email_saved_ids": [46, 47],
        "email_skipped_ids": [],
        "service_log_id": 9,
    },
]


JOB_SCRAPING_SERVICE_ERROR_DATA = [
    {
        "error_type": "ConnectionError",
        "message": "Failed to connect to LinkedIn API: Connection timeout after 30 seconds",
        "traceback": """Traceback (most recent call last):
  File "/app/scrapers/linkedin_scraper.py", line 145, in scrape_job
    response = requests.get(url, timeout=30)
  File "/usr/local/lib/python3.11/site-packages/requests/api.py", line 73, in get
    return request("get", url, **kwargs)
  File "/usr/local/lib/python3.11/site-packages/requests/sessions.py", line 589, in request
    resp = self.send(prep, **send_kwargs)
requests.exceptions.ConnectionError: HTTPSConnectionPool(host='www.linkedin.com', port=443): Max retries exceeded with url: /jobs/view/12345678""",
        "service_log_id": 1,
    },
    {
        "error_type": "SMTPAuthenticationError",
        "message": "SMTP authentication failed: Invalid credentials",
        "traceback": """Traceback (most recent call last):
  File "/app/email/gmail_client.py", line 89, in connect
    server.login(self.username, self.password)
  File "/usr/local/lib/python3.11/smtplib.py", line 750, in login
    raise SMTPAuthenticationError(code, resp)
smtplib.SMTPAuthenticationError: (535, b'5.7.8 Username and Password not accepted')""",
        "service_log_id": 1,
    },
    {
        "error_type": "PDFParseError",
        "message": "Failed to parse PDF: File appears to be corrupted",
        "traceback": """Traceback (most recent call last):
  File "/app/parsers/pdf_parser.py", line 56, in extract_text
    doc = fitz.open(pdf_path)
  File "/usr/local/lib/python3.11/site-packages/fitz/fitz.py", line 2156, in __init__
    _fitz.Document_swiginit(self, _fitz.new_Document(filename, stream, filetype, rect, width, height, fontsize))
RuntimeError: cannot open document: cannot recognize version""",
        "service_log_id": 1,
    },
    {
        "error_type": "RateLimitError",
        "message": "Rate limit exceeded: 429 Too Many Requests",
        "traceback": """Traceback (most recent call last):
  File "/app/scrapers/base_scraper.py", line 203, in fetch_page
    response = self.session.get(url)
  File "/usr/local/lib/python3.11/site-packages/requests/sessions.py", line 600, in get
    return self.request("GET", url, **kwargs)
  File "/app/scrapers/base_scraper.py", line 178, in request
    raise RateLimitError(f"Rate limit exceeded after {attempt_count} requests")
app.exceptions.RateLimitError: Rate limit exceeded after 30 requests""",
        "service_log_id": 1,
    },
    {
        "error_type": "DatabaseError",
        "message": "Failed to commit transaction: Deadlock detected",
        "traceback": """Traceback (most recent call last):
  File "/app/db/session.py", line 67, in save_jobs
    session.commit()
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/orm/session.py", line 1451, in commit
    self._transaction.commit(_to_root=self.future)
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/orm/session.py", line 844, in commit
    self._prepare_impl()
sqlalchemy.exc.OperationalError: (psycopg2.errors.DeadlockDetected) deadlock detected
DETAIL:  Process 12345 waits for ShareLock on transaction 67890""",
        "service_log_id": 2,
    },
    {
        "error_type": "ParserError",
        "message": "Failed to parse job details: Missing required field 'job_title'",
        "traceback": """Traceback (most recent call last):
  File "/app/parsers/job_parser.py", line 112, in parse_job_data
    title = soup.find("h1", class_="job-title").text.strip()
AttributeError: 'NoneType' object has no attribute 'text'

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/app/scrapers/indeed_scraper.py", line 234, in scrape_job
    job_data = self.parser.parse_job_data(html)
  File "/app/parsers/job_parser.py", line 115, in parse_job_data
    raise ParserError("Missing required field 'job_title'")
app.exceptions.ParserError: Missing required field 'job_title'""",
        "service_log_id": 3,
    },
    {
        "error_type": "ValidationError",
        "message": "Job data validation failed: Invalid salary format",
        "traceback": """Traceback (most recent call last):
  File "/app/models/job.py", line 89, in validate_salary
    return self._parse_salary_string(salary_str)
  File "/app/models/job.py", line 103, in _parse_salary_string
    raise ValueError(f"Unable to parse salary: {salary_str}")
ValueError: Unable to parse salary: £competitive + benefits

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/app/services/job_service.py", line 178, in create_job
    validated_job = Job.validate(job_data)
  File "/app/models/job.py", line 45, in validate
    raise ValidationError(f"Job data validation failed: {str(e)}")
app.exceptions.ValidationError: Job data validation failed: Invalid salary format""",
        "service_log_id": 4,
    },
    {
        "error_type": "TimeoutError",
        "message": "Selenium webdriver timeout: Page load exceeded 60 seconds",
        "traceback": """Traceback (most recent call last):
  File "/app/scrapers/selenium_scraper.py", line 156, in load_page
    WebDriverWait(self.driver, 60).until(
        EC.presence_of_element_located((By.CLASS_NAME, "job-details"))
    )
  File "/usr/local/lib/python3.11/site-packages/selenium/webdriver/support/wait.py", line 95, in until
    raise TimeoutException(message, screen, stacktrace)
selenium.common.exceptions.TimeoutException: Message: Timeout waiting for job-details element""",
        "service_log_id": 3,
    },
    {
        "error_type": "JSONDecodeError",
        "message": "Failed to parse API response: Invalid JSON",
        "traceback": """Traceback (most recent call last):
  File "/app/scrapers/api_scraper.py", line 201, in fetch_jobs
    data = response.json()
  File "/usr/local/lib/python3.11/site-packages/requests/models.py", line 975, in json
    return complexjson.loads(self.text, **kwargs)
  File "/usr/local/lib/python3.11/json/__init__.py", line 346, in loads
    return _default_decoder.decode(s)
  File "/usr/local/lib/python3.11/json/decoder.py", line 337, in decode
    obj, end = self.raw_decode(s, idx=_w(s, 0).end())
json.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)""",
        "service_log_id": 8,
    },
    {
        "error_type": "MemoryError",
        "message": "Out of memory while processing large dataset",
        "traceback": """Traceback (most recent call last):
  File "/app/services/batch_processor.py", line 145, in process_jobs
    all_jobs = session.query(Job).all()
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/orm/query.py", line 2893, in all
    return self._iter().all()
MemoryError: Unable to allocate 2.5 GiB for an array with shape (50000, 100) and data type object""",
        "service_log_id": 7,
    },
]


SCRAPING_FILTER_DATA = [
    {
        "owner_id": 1,
        "type": "title",
        "operator": "contains",
        "value": "Senior",
        "is_active": True,
        "case_sensitive": False,
    },
    {
        "owner_id": 1,
        "type": "company",
        "operator": "equals",
        "value": "StartupXYZ",
        "is_active": True,
        "case_sensitive": False,
    },
    {
        "owner_id": 1,
        "type": "location_city",
        "operator": "equals",
        "value": "New York",
        "is_active": True,
        "case_sensitive": False,
    },
    {
        "owner_id": 1,
        "type": "salary_min",
        "operator": "less_than",
        "value": "100000",
        "is_active": True,
        "case_sensitive": False,
    },
    {
        "owner_id": 1,
        "type": "title",
        "operator": "ends_with",
        "value": "Developer",
        "is_active": True,
        "case_sensitive": False,
    },
    {
        "owner_id": 1,
        "type": "title",
        "operator": "contains",
        "value": "Engineer",
        "is_active": False,
        "case_sensitive": False,
    },
    {
        "owner_id": 2,
        "type": "company",
        "operator": "not_contains",
        "value": "Tech",
        "is_active": True,
        "case_sensitive": False,
    },
    {
        "owner_id": 2,
        "type": "location_city",
        "operator": "equals",
        "value": "Manchester",
        "is_active": True,
        "case_sensitive": False,
    },
    {
        "owner_id": 2,
        "type": "attendance_type",
        "operator": "equals",
        "value": "remote",
        "is_active": True,
        "case_sensitive": False,
    },
    {
        "owner_id": 2,
        "type": "salary_max",
        "operator": "greater_than",
        "value": "90000",
        "is_active": True,
        "case_sensitive": False,
    },
    {
        "owner_id": 2,
        "type": "title",
        "operator": "starts_with",
        "value": "Machine",
        "is_active": True,
        "case_sensitive": False,
    },
    {
        "owner_id": 2,
        "type": "location_country",
        "operator": "not_equals",
        "value": "United Kingdom",
        "is_active": True,
        "case_sensitive": False,
    },
    {
        "owner_id": 1,
        "type": "title",
        "operator": "contains",
        "value": "Python",
        "is_active": True,
        "case_sensitive": True,
    },
    {
        "owner_id": 1,
        "type": "company",
        "operator": "starts_with",
        "value": "Cloud",
        "is_active": True,
        "case_sensitive": False,
    },
]


SCRAPED_JOB_DATA = [
    {
        "external_job_id": "3789012345",
        "platform": "linkedin",
        "owner_id": 1,
        "is_scraped": True,
        "is_failed": False,
        "title": "Senior Python Developer",
        "description": "We are looking for an experienced Python developer to join our team...",
        "company": "TechCorp Inc",
        "location": "San Francisco",
        "location_city": "San Francisco",
        "salary_min": 120000.0,
        "salary_max": 160000.0,
        "salary_currency": "GBP",
        "url": "https://linkedin.com/jobs/view/3789012345",
        "scrape_datetime": "2025-08-15T14:32:18.123456+00:00",
        "service_log_id": 1,
    },
    {
        "external_job_id": "987654321",
        "platform": "indeed",
        "owner_id": 1,
        "is_scraped": True,
        "is_failed": False,
        "title": "Full Stack Engineer",
        "description": "Join our growing startup as a full stack engineer...",
        "company": "StartupXYZ",
        "attendance_type": "remote",
        "salary_min": 90000.0,
        "salary_max": 130000.0,
        "salary_currency": "GBP",
        "url": "https://indeed.com/viewjob?jk=987654321",
        "scrape_datetime": "2025-08-22T09:45:32.789012+00:00",
        "service_log_id": 1,
    },
    {
        "external_job_id": "1122334455",
        "platform": "linkedin",
        "owner_id": 1,
        "is_scraped": True,
        "is_failed": False,
        "title": "DevOps Engineer",
        "description": "Looking for a DevOps engineer with AWS experience...",
        "company": "CloudTech Solutions",
        "location": "New York",
        "location_city": "New York",
        "salary_min": 110000.0,
        "salary_max": 150000.0,
        "salary_currency": "GBP",
        "url": "https://linkedin.com/jobs/view/1122334455",
        "scrape_datetime": "2025-08-28T16:20:45.456789+00:00",
        "service_log_id": 1,
    },
    {
        "external_job_id": "5566778899",
        "platform": "indeed",
        "owner_id": 1,
        "is_scraped": True,
        "is_failed": False,
        "salary_currency": "GBP",
        "title": "Software Engineer",
        "scrape_datetime": "2025-08-30T11:15:22.234567+00:00",
        "url": "test",
        "service_log_id": 1,
    },
    {
        "external_job_id": "1357924680",
        "platform": "linkedin",
        "owner_id": 1,
        "is_scraped": True,
        "is_failed": False,
        "title": "Backend Developer",
        "scrape_datetime": "2025-08-25T13:42:17.345678+00:00",
        "url": "test",
        "service_log_id": 1,
    },
    {
        "external_job_id": "2468135790",
        "platform": "indeed",
        "owner_id": 1,
        "is_scraped": True,
        "is_failed": True,
        "scrape_error": "Page not found - job posting may have been removed",
        "title": "Data Engineer",
        "scrape_datetime": "2025-08-18T08:30:55.567890+00:00",
        "is_imported": True,
        "url": "test",
        "service_log_id": 1,
    },
    {
        "external_job_id": "9988776655",
        "platform": "indeed",
        "owner_id": 1,
        "is_scraped": True,
        "is_failed": True,
        "scrape_error": "Scraping blocked - rate limit exceeded",
        "title": "ML Engineer",
        "scrape_datetime": "2025-08-20T19:25:08.678901+00:00",
        "is_active": False,
        "url": "test",
        "service_log_id": 1,
    },
    {
        "external_job_id": "4123456789",
        "platform": "linkedin",
        "owner_id": 2,
        "is_scraped": True,
        "is_failed": False,
        "title": "Senior Java Developer",
        "description": "Looking for experienced Java developer with Spring Boot expertise...",
        "company": "FinTech Innovations Ltd",
        "location": "London, UK",
        "location_city": "London",
        "salary_min": 70000.0,
        "salary_max": 95000.0,
        "salary_currency": "GBP",
        "url": "https://linkedin.com/jobs/view/4123456789",
        "scrape_datetime": "2025-09-01T10:15:30.123456+00:00",
        "service_log_id": 1,
    },
    {
        "external_job_id": "totaljobs_567890",
        "platform": "totaljobs",
        "owner_id": 2,
        "is_scraped": True,
        "is_failed": False,
        "title": "Flutter Developer",
        "description": "Join our healthcare tech team to build mobile applications...",
        "company": "HealthTech Solutions",
        "attendance_type": "remote",
        "location": "UK",
        "location_country": "United Kingdom",
        "salary_min": 50000.0,
        "salary_max": 70000.0,
        "salary_currency": "GBP",
        "url": "https://totaljobs.com/job/flutter-healthcare-567890",
        "scrape_datetime": "2025-09-03T14:22:45.789012+00:00",
        "service_log_id": 1,
    },
    {
        "external_job_id": "reed_345678",
        "platform": "reed",
        "owner_id": 2,
        "is_scraped": True,
        "is_failed": False,
        "title": "Machine Learning Engineer",
        "description": "Build cutting-edge ML solutions for AI startup...",
        "company": "InnovateTech Solutions",
        "location": "Edinburgh, UK",
        "location_city": "Edinburgh",
        "location_country": "United Kingdom",
        "salary_min": 65000.0,
        "salary_max": 90000.0,
        "salary_currency": "GBP",
        "url": "https://reed.co.uk/jobs/ml-engineer-edinburgh/345678",
        "scrape_datetime": "2025-09-05T09:33:12.345678+00:00",
        "service_log_id": 1,
        "filter_id": 1,
    },
    {
        "external_job_id": "cvlib_678901",
        "platform": "cv-library",
        "owner_id": 2,
        "is_scraped": True,
        "is_failed": True,
        "scrape_error": "Access denied - company blocked scraping",
        "title": "Sustainability Software Engineer",
        "scrape_datetime": "2025-09-07T11:45:28.456789+00:00",
        "url": "test",
        "service_log_id": 1,
    },
    {
        "external_job_id": "jobsite_901234",
        "platform": "jobsite",
        "owner_id": 2,
        "is_scraped": True,
        "is_failed": False,
        "title": "Full Stack JavaScript Developer",
        "description": "Work with modern JavaScript frameworks in agile environment...",
        "company": "StartupXYZ",
        "location": "Manchester, UK",
        "location_city": "Manchester",
        "location_country": "United Kingdom",
        "salary_min": 55000.0,
        "salary_max": 80000.0,
        "salary_currency": "GBP",
        "url": "https://jobsite.co.uk/job/fullstack-js-manchester-901234",
        "scrape_datetime": "2025-09-09T13:20:15.567890+00:00",
        "service_log_id": 1,
        "filter_id": 1,
    },
    {
        "external_job_id": "soft123456789",
        "platform": "indeed",
        "owner_id": 2,
        "is_scraped": True,
        "is_failed": True,
        "scrape_error": "Rate limit exceeded - retry after 24 hours",
        "title": "Software Engineer",
        "scrape_datetime": "2025-09-11T15:30:42.678901+00:00",
        "url": "test",
        "service_log_id": 1,
    },
    {
        "external_job_id": "soft1sdf23456789",
        "platform": "indeed",
        "owner_id": 1,
        "is_scraped": True,
        "url": "test",
        "title": "Senior Python Developer 2",
        "service_log_id": 1,
        "company": "StartupXYZ",
        "location": "London",
        "location_city": "London",
        "filter_id": 2,
    },
    {
        "external_job_id": "soft1sdf23456789r3",
        "platform": "indeed",
        "owner_id": 1,
        "is_scraped": True,
        "url": "test",
        "title": "Senior Python Developer",
        "company": "StartupXYZ",
        "service_log_id": 1,
        "filter_id": 2,
    },
]


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

companies = [
    "TechCorp Inc",
    "StartupXYZ",
    "CloudTech Solutions",
    "DataSoft Ltd",
    "FinTech Innovations",
    "HealthTech Solutions",
    "InnovateTech Solutions",
    "Digital Dynamics",
    "Future Systems",
    "Quantum Labs",
    "Neural Networks Inc",
    "CyberSecure Ltd",
    "GreenTech Energy",
    "SmartCity Solutions",
    "BioTech Innovations",
    "AI Research Corp",
    "BlockChain Ventures",
    "CloudScale Systems",
    "DevOps Masters",
    "Enterprise Solutions Ltd",
]

# Job titles pool
job_titles = [
    "Senior Python Developer",
    "Full Stack Engineer",
    "DevOps Engineer",
    "Software Engineer",
    "Backend Developer",
    "Data Engineer",
    "ML Engineer",
    "Senior Java Developer",
    "Flutter Developer",
    "Machine Learning Engineer",
    "Frontend Developer",
    "React Developer",
    "Vue.js Developer",
    "Angular Developer",
    "Data Scientist",
    "AI Software Developer",
    "iOS Developer",
    "Android Developer",
    "Sustainability Software Engineer",
    "Site Reliability Engineer",
    "Cloud Architect",
    "Security Engineer",
    "Blockchain Developer",
    "QA Engineer",
    "Technical Lead",
    "Engineering Manager",
    "Principal Engineer",
    "Staff Engineer",
    "Solutions Architect",
    "Platform Engineer",
    "Infrastructure Engineer",
    "Database Administrator",
    "Business Intelligence Developer",
    "ETL Developer",
    "Big Data Engineer",
]

# Cities pool
cities = [
    "London",
    "Manchester",
    "Birmingham",
    "Edinburgh",
    "Bristol",
    "Glasgow",
    "Leeds",
    "Liverpool",
    "Cardiff",
    "Newcastle",
    "Nottingham",
    "Sheffield",
    "Cambridge",
    "Oxford",
    "Reading",
    "Brighton",
    "Southampton",
]

# Job descriptions pool
descriptions = [
    "We are looking for an experienced developer to join our growing team...",
    "Join our innovative startup and help build cutting-edge solutions...",
    "Exciting opportunity to work with modern technologies in an agile environment...",
    "Work on challenging projects with a talented team of engineers...",
    "Build scalable systems that impact millions of users...",
    "Collaborate with cross-functional teams to deliver high-quality software...",
    "Help shape the future of our platform with your technical expertise...",
    "Work remotely with a global team on mission-critical applications...",
]

# Attendance types
attendance_types = ["remote", "on-site", "hybrid", None]

# Error messages for failed scrapes
error_messages = [
    "Page not found - job posting may have been removed",
    "Scraping blocked - rate limit exceeded",
    "Access denied - company blocked scraping",
    "Rate limit exceeded - retry after 24 hours",
    "Connection timeout - server not responding",
    "Invalid job posting format",
]

# Generate 50 scraped jobs
scraped_jobs = []
current_date = dt.datetime.now()

for i in range(50):
    external_id = f"job_111{i}"
    owner_id = 1
    is_scraped = True
    is_failed = random.random() < 0.15  # 15% failure rate
    is_imported = random.random() < 0.1 if not is_failed else False  # 10% imported
    is_active = random.random() < 0.95  # 95% active

    job = {
        "external_job_id": external_id,
        "platform": "linkedin",
        "owner_id": owner_id,
        "is_scraped": is_scraped,
        "is_failed": is_failed,
        "title": random.choice(job_titles),
        "scrape_datetime": (current_date - dt.timedelta(days=random.randint(0, 30))).strftime("%Y-%m-%dT%H:%M:%S.%f")[
            :-3
        ]
        + "+00:00",
        "url": f"https://linkedin.com/jobs/view/{external_id}" if not is_failed else "test",
        "is_imported": is_imported,
        "is_active": is_active,
        "service_log_id": 1,
    }

    if is_failed:
        job["scrape_error"] = random.choice(error_messages)
    else:
        # Add successful scrape data
        job["description"] = random.choice(descriptions)
        job["company"] = random.choice(companies)

        # 70% have location, 30% are remote/unspecified
        if random.random() < 0.7:
            job["location_city"] = random.choice(cities)
            job["location_country"] = "United Kingdom"
            job["location"] = f"{job['location_city']}, UK"

        # 60% have attendance type specified
        job["attendance_type"] = random.choice(attendance_types)

        # 80% have salary information
        if random.random() < 0.8:
            base_salary = random.randint(40000, 120000)
            job["salary_min"] = float(base_salary)
            job["salary_max"] = float(base_salary + random.randint(10000, 40000))
            job["salary_currency"] = "GBP"

    SCRAPED_JOB_DATA.append(job)
    EMAIL_SCRAPEDJOB_MAPPINGS[0]["scraped_job_ids"].append(i + 14)
