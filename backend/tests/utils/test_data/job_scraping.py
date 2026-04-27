"""Test data for job scraping service tests."""

import datetime as dt

from tests.utils.job_email_resources import LINKEDIN_EMAIL_3_BODY
from tests.utils.test_data.utils import CURRENT_DATE, DATETIME_FORMAT

# ----------------------------------------------------- JOB EMAILS -----------------------------------------------------

JOB_EMAIL_DATA = [
    {
        "owner_id": 1,
        "external_email_id": "linkedin_alert_001",
        "alert_name": "Python Developer",
        "job_found_n": 15,
        "subject": "10 new jobs matching Python Developer",
        "sender": "jobs-noreply@linkedin.com",
        "date_received": "2024-01-15 09:30:00",
        "platform": "linkedin",
        "service_log_id": 1,
        "body": LINKEDIN_EMAIL_3_BODY,
    },
    {
        "owner_id": 1,
        "external_email_id": "indeed_alert_001",
        "alert_name": "Software Engineer",
        "job_found_n": 15,
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
        "alert_name": "Data Scientist",
        "job_found_n": 15,
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
        "alert_name": "Weekly Digest",
        "job_found_n": 2,
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
        "alert_name": "Similar Jobs",
        "job_found_n": 17,
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
        "alert_name": "Frontend Developer",
        "job_found_n": 2,
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
        "alert_name": "Java Developer",
        "job_found_n": 1,
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
        "alert_name": "Mobile App Developer",
        "job_found_n": 1,
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
        "alert_name": "AI & Machine Learning",
        "job_found_n": 0,
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
        "alert_name": "Sustainability & Green Tech",
        "job_found_n": 0,
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
        "alert_name": "Full Stack Developer",
        "job_found_n": 0,
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
        "alert_name": "Software Engineer Daily",
        "job_found_n": 0,
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


# ---------------------------------------------- JOB SCRAPING SERVICE LOGS ---------------------------------------------

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


# --------------------------------------------- JOB SCRAPING PLATFORM STATS --------------------------------------------

JOB_SCRAPING_PLATFORM_STAT_DATA = [
    {
        "name": "linkedin",
        "job_found_ids": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
        "job_scrape_succeeded_ids": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
        "job_scrape_failed_ids": [51, 52],
        "job_scrape_copied_ids": [14, 15, 16],
        "email_saved_ids": [1, 2, 3, 4, 5],
        "email_skipped_ids": [6],
        "service_log_id": 1,
    },
    {
        "name": "indeed",
        "job_found_ids": [17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28],
        "job_scrape_succeeded_ids": [17, 18, 19, 20, 21, 22, 23, 24, 25],
        "job_scrape_failed_ids": [48, 50],
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
        "job_scrape_succeeded_ids": list(range(29, 51)) + list(range(59, 64)),
        "job_scrape_failed_ids": [53, 68],
        "job_scrape_copied_ids": list(range(65, 75)),
        "email_saved_ids": list(range(9, 21)),
        "email_skipped_ids": [21, 22, 23],
        "service_log_id": 2,
    },
    {
        "name": "indeed",
        "job_found_ids": list(range(75, 83)),
        "job_scrape_succeeded_ids": list(range(75, 81)),
        "job_scrape_failed_ids": [60],
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
        "job_scrape_failed_ids": [],
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
        "job_scrape_failed_ids": [54],
        "job_scrape_copied_ids": [135, 136],
        "email_saved_ids": [39, 40, 41, 42],
        "email_skipped_ids": [43],
        "service_log_id": 7,
    },
    {
        "name": "cv-library",
        "job_found_ids": [49],
        "job_scrape_succeeded_ids": [],
        "job_scrape_failed_ids": [49],
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

# --------------------------------------------- JOB SCRAPING SERVICE ERRORS --------------------------------------------

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

# -------------------------------------------------- SCRAPING FILTERS --------------------------------------------------

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

# -------------------------------------------- SCRAPING FAVOURITE FILTERS ---------------------------------------------

SCRAPING_FAVOURITE_FILTER_DATA = [
    {
        "owner_id": 1,
        "type": "title",
        "operator": "contains",
        "value": "Python",
        "is_active": True,
        "case_sensitive": False,
    },
    {
        "owner_id": 1,
        "type": "attendance_type",
        "operator": "equals",
        "value": "remote",
        "is_active": True,
        "case_sensitive": False,
    },
    {
        "owner_id": 1,
        "type": "salary_min",
        "operator": "greater_than",
        "value": "100000",
        "is_active": True,
        "case_sensitive": False,
    },
    {
        "owner_id": 1,
        "type": "title",
        "operator": "contains",
        "value": "Data",
        "is_active": False,
        "case_sensitive": False,
    },
    {
        "owner_id": 2,
        "type": "title",
        "operator": "contains",
        "value": "Engineer",
        "is_active": True,
        "case_sensitive": False,
    },
    {
        "owner_id": 2,
        "type": "location_country",
        "operator": "equals",
        "value": "United Kingdom",
        "is_active": True,
        "case_sensitive": False,
    },
]

# ---------------------------------------------------- SCRAPED JOBS ----------------------------------------------------

SCRAPED_JOB_DATA = [
    {
        "external_job_id": "3789012345",
        "platform": "linkedin",
        "owner_id": 1,
        "is_scraped": True,
        "is_processed": True,
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
        "geolocation_id": 18,
        "deadline": "2024-01-01 00:00:00",
        "parsed_location": "San Francisco",
    },
    {
        "external_job_id": "987654321",
        "platform": "indeed",
        "owner_id": 1,
        "is_scraped": True,
        "is_processed": True,
        "title": "Full Stack Engineer",
        "company": "StartupXYZ",
        "attendance_type": "remote",
        "salary_min": 90000.0,
        "salary_max": 130000.0,
        "description": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Ut vitae nunc sed metus elementum \n        dignissim. Class aptent taciti sociosqu ad litora torquent per conubia nostra, per inceptos himenaeos. \n        Donec vulputate felis nulla. Cras ac urna in diam maximus euismod. Quisque laoreet ex vel felis tristique, \n        id viverra mi fermentum. Nullam hendrerit justo odio, tempor varius lectus venenatis placerat. Nunc blandit, \n        purus non ornare condimentum, tortor nisi euismod ipsum, ut dictum quam ex a neque. Sed rhoncus purus eu felis \n        placerat blandit. Curabitur rutrum consequat enim nec rutrum. Praesent gravida sem a justo ullamcorper blandit. \n        Vestibulum rutrum sem augue, eu malesuada elit dignissim nec. Aenean cursus feugiat elit, eget mattis risus \n        dignissim id. In sit amet hendrerit nisi. Ut venenatis leo ut odio eleifend, eget mollis sem vulputate. \n        Phasellus finibus eget quam eget iaculis. Maecenas ullamcorper varius nisi, eu porta nulla iaculis vel. \n        Donec bibendum nisl viverra odio vehicula molestie. Sed laoreet lorem vel enim porta, id facilisis risus \n        scelerisque. Donec vehicula, arcu ut vestibulum tincidunt, urna nulla tristique neque, id faucibus dui magna \n        eget nisi. Mauris fringilla sagittis aliquet. Quisque facilisis vulputate diam, sit amet lacinia lectus commodo \n        in. Phasellus quis aliquam ex. Fusce in ornare est.",
        "salary_currency": "GBP",
        "url": "https://indeed.com/viewjob?jk=987654321",
        "scrape_datetime": "2025-08-22T09:45:32.789012+00:00",
        "service_log_id": 1,
        "deadline": "2024-01-01 00:00:00",
    },
    {
        "external_job_id": "1122334455",
        "platform": "linkedin",
        "owner_id": 1,
        "is_scraped": True,
        "is_processed": True,
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
        "geolocation_id": 19,
        "parsed_location": "New York",
    },
    {
        "external_job_id": "5566778899",
        "platform": "indeed",
        "owner_id": 1,
        "is_scraped": True,
        "is_processed": True,
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
        "is_processed": True,
        "title": "Backend Developer",
        "scrape_datetime": "2025-08-25T13:42:17.345678+00:00",
        "url": "test",
        "service_log_id": 1,
    },
    {
        "external_job_id": "4123456789",
        "platform": "linkedin",
        "owner_id": 2,
        "is_scraped": True,
        "is_processed": True,
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
        "geolocation_id": 20,
        "parsed_location": "London, UK",
    },
    {
        "external_job_id": "totaljobs_567890",
        "platform": "totaljobs",
        "owner_id": 2,
        "is_scraped": True,
        "is_processed": True,
        "title": "Flutter Developer",
        "description": "Join our healthcare tech team to build mobile applications...",
        "company": "HealthTech Solutions",
        "attendance_type": "remote",
        "location": "UK (remote)",
        "location_country": "United Kingdom",
        "salary_min": 50000.0,
        "salary_max": 70000.0,
        "salary_currency": "GBP",
        "url": "https://totaljobs.com/job/flutter-healthcare-567890",
        "scrape_datetime": "2025-09-03T14:22:45.789012+00:00",
        "service_log_id": 1,
        "geolocation_id": 21,
        "parsed_location": "UK",
    },
    {
        "external_job_id": "reed_345678",
        "platform": "reed",
        "owner_id": 2,
        "is_scraped": True,
        "is_processed": True,
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
        "geolocation_id": 22,
        "parsed_location": "Edinburgh, UK",
    },
    {
        "external_job_id": "jobsite_901234",
        "platform": "jobsite",
        "owner_id": 2,
        "is_scraped": True,
        "is_processed": True,
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
        "geolocation_id": 23,
        "parsed_location": "Manchester, UK",
    },
    {
        "external_job_id": "soft1sdf23456789",
        "platform": "indeed",
        "owner_id": 1,
        "is_scraped": True,
        "is_processed": True,
        "url": "test",
        "title": "Senior Python Developer 2",
        "service_log_id": 1,
        "company": "StartupXYZ",
        "location": "London",
        "location_city": "London",
        "exclusion_filter_id": 2,
        "geolocation_id": 24,
        "parsed_location": "London",
    },
    {
        "external_job_id": "soft1sdf23456789r3",
        "platform": "indeed",
        "owner_id": 1,
        "is_scraped": True,
        "is_processed": True,
        "url": "test",
        "title": "Senior Python Developer",
        "company": "StartupXYZ",
        "service_log_id": 1,
        "exclusion_filter_id": 2,
    },
    {
        "external_job_id": "job_1110",
        "platform": "linkedin",
        "owner_id": 1,
        "is_scraped": True,
        "is_processed": True,
        "title": "Senior Python Developer",
        "description": "We are looking for an experienced developer to join our growing team...",
        "company": "TechCorp Inc",
        "location": "London, UK (hybrid)",
        "deadline": "3000-01-01 00:00:00",
        "location_city": "London",
        "location_country": "United Kingdom",
        "salary_min": 75000.0,
        "salary_max": 95000.0,
        "salary_currency": "GBP",
        "attendance_type": "hybrid",
        "url": "https://linkedin.com/jobs/view/job_1110",
        "scrape_datetime": "2025-01-15T10:00:00.000+00:00",
        "service_log_id": 1,
        "geolocation_id": 20,
        "parsed_location": "London, UK",
    },
    {
        "external_job_id": "job_1111",
        "platform": "linkedin",
        "owner_id": 1,
        "is_scraped": True,
        "is_processed": True,
        "title": "Full Stack Engineer",
        "description": "Join our innovative startup and help build cutting-edge solutions...",
        "company": "StartupXYZ",
        "location": "Manchester, UK (remote)",
        "location_city": "Manchester",
        "location_country": "United Kingdom",
        "salary_min": 60000.0,
        "salary_max": 80000.0,
        "salary_currency": "GBP",
        "attendance_type": "remote",
        "url": "https://linkedin.com/jobs/view/job_1111",
        "scrape_datetime": "2025-01-14T11:30:00.000+00:00",
        "service_log_id": 1,
        "geolocation_id": 23,
        "parsed_location": "Manchester, UK",
    },
    {
        "external_job_id": "job_1116",
        "platform": "linkedin",
        "owner_id": 1,
        "is_scraped": True,
        "is_processed": True,
        "title": "ML Engineer",
        "description": "Help shape the future of our platform with your technical expertise...",
        "company": "InnovateTech Solutions",
        "location": "Leeds, UK (on-site)",
        "location_city": "Leeds",
        "location_country": "United Kingdom",
        "salary_min": 70000.0,
        "salary_max": 95000.0,
        "salary_currency": "GBP",
        "attendance_type": "on-site",
        "url": "https://linkedin.com/jobs/view/job_1116",
        "scrape_datetime": "2025-01-09T12:00:00.000+00:00",
        "service_log_id": 1,
        "geolocation_id": 25,
        "parsed_location": "Leeds, UK",
    },
    {
        "external_job_id": "job_1117",
        "platform": "linkedin",
        "owner_id": 1,
        "is_scraped": True,
        "is_processed": True,
        "title": "Frontend Developer",
        "description": "Work remotely with a global team on mission-critical applications...",
        "company": "Digital Dynamics",
        "location": "Liverpool, UK (remote)",
        "location_city": "Liverpool",
        "location_country": "United Kingdom",
        "salary_min": 50000.0,
        "salary_max": 65000.0,
        "salary_currency": "GBP",
        "attendance_type": "remote",
        "url": "https://linkedin.com/jobs/view/job_1117",
        "scrape_datetime": "2025-01-08T15:45:00.000+00:00",
        "service_log_id": 1,
        "geolocation_id": 26,
        "parsed_location": "Liverpool, UK",
    },
    {
        "external_job_id": "job_1118",
        "platform": "linkedin",
        "owner_id": 1,
        "is_scraped": True,
        "is_processed": True,
        "title": "React Developer",
        "description": "We are looking for an experienced developer to join our growing team...",
        "company": "Future Systems",
        "location": "Cardiff, UK (hybrid)",
        "location_city": "Cardiff",
        "location_country": "United Kingdom",
        "salary_min": 52000.0,
        "salary_max": 68000.0,
        "salary_currency": "GBP",
        "attendance_type": "hybrid",
        "url": "https://linkedin.com/jobs/view/job_1118",
        "scrape_datetime": "2025-01-07T10:30:00.000+00:00",
        "service_log_id": 1,
        "geolocation_id": 27,
        "parsed_location": "Cardiff, UK",
    },
    {
        "external_job_id": "job_1119",
        "platform": "linkedin",
        "owner_id": 1,
        "is_scraped": True,
        "is_processed": True,
        "title": "Vue.js Developer",
        "description": "Join our innovative startup and help build cutting-edge solutions...",
        "company": "Quantum Labs",
        "location": "Newcastle, UK (on-site)",
        "location_city": "Newcastle",
        "location_country": "United Kingdom",
        "salary_min": 48000.0,
        "salary_max": 62000.0,
        "salary_currency": "GBP",
        "attendance_type": "on-site",
        "url": "https://linkedin.com/jobs/view/job_1119",
        "scrape_datetime": "2025-01-06T09:00:00.000+00:00",
        "service_log_id": 1,
        "geolocation_id": 28,
        "parsed_location": "Newcastle, UK",
    },
    {
        "external_job_id": "job_1125",
        "platform": "linkedin",
        "owner_id": 1,
        "is_scraped": True,
        "is_processed": True,
        "is_imported": True,
        "title": "Site Reliability Engineer",
        "description": "Exciting opportunity to work with modern technologies in an agile environment...",
        "company": "Neural Networks Inc",
        "location": "London, UK (hybrid)",
        "location_city": "London",
        "location_country": "United Kingdom",
        "salary_min": 80000.0,
        "salary_max": 100000.0,
        "salary_currency": "GBP",
        "attendance_type": "hybrid",
        "url": "https://linkedin.com/jobs/view/job_1125",
        "scrape_datetime": "2024-12-31T10:00:00.000+00:00",
        "service_log_id": 1,
        "geolocation_id": 20,
        "parsed_location": "London, UK",
    },
    {
        "external_job_id": "job_1126",
        "platform": "linkedin",
        "owner_id": 1,
        "is_scraped": True,
        "is_processed": True,
        "is_imported": True,
        "title": "Cloud Architect",
        "description": "Work on challenging projects with a talented team of engineers...",
        "company": "CyberSecure Ltd",
        "location": "Manchester, UK (remote)",
        "location_city": "Manchester",
        "location_country": "United Kingdom",
        "salary_min": 90000.0,
        "salary_max": 120000.0,
        "salary_currency": "GBP",
        "attendance_type": "remote",
        "url": "https://linkedin.com/jobs/view/job_1126",
        "scrape_datetime": "2024-12-30T11:30:00.000+00:00",
        "service_log_id": 1,
        "geolocation_id": 23,
        "parsed_location": "Manchester, UK",
    },
    {
        "external_job_id": "job_1127",
        "platform": "linkedin",
        "owner_id": 1,
        "is_scraped": True,
        "is_processed": True,
        "is_imported": True,
        "title": "Security Engineer",
        "description": "Build scalable systems that impact millions of users...",
        "company": "GreenTech Energy",
        "location": "Birmingham, UK (on-site)",
        "location_city": "Birmingham",
        "location_country": "United Kingdom",
        "salary_min": 72000.0,
        "salary_max": 92000.0,
        "salary_currency": "GBP",
        "attendance_type": "on-site",
        "url": "https://linkedin.com/jobs/view/job_1127",
        "scrape_datetime": "2024-12-29T14:15:00.000+00:00",
        "service_log_id": 1,
        "geolocation_id": 29,
        "parsed_location": "Birmingham, UK",
    },
    {
        "external_job_id": "job_1128",
        "platform": "linkedin",
        "owner_id": 1,
        "is_scraped": True,
        "is_processed": True,
        "is_imported": True,
        "title": "Blockchain Developer",
        "description": "Collaborate with cross-functional teams to deliver high-quality software...",
        "company": "SmartCity Solutions",
        "location": "Edinburgh, UK (hybrid)",
        "location_city": "Edinburgh",
        "location_country": "United Kingdom",
        "salary_min": 68000.0,
        "salary_max": 88000.0,
        "salary_currency": "GBP",
        "attendance_type": "hybrid",
        "url": "https://linkedin.com/jobs/view/job_1128",
        "scrape_datetime": "2024-12-28T16:00:00.000+00:00",
        "service_log_id": 1,
        "geolocation_id": 22,
        "parsed_location": "Edinburgh, UK",
    },
    {
        "external_job_id": "job_1129",
        "platform": "linkedin",
        "owner_id": 1,
        "is_scraped": True,
        "is_processed": True,
        "is_imported": True,
        "title": "QA Engineer",
        "description": "Help shape the future of our platform with your technical expertise...",
        "company": "BioTech Innovations",
        "location": "Bristol, UK (remote)",
        "location_city": "Bristol",
        "location_country": "United Kingdom",
        "salary_min": 45000.0,
        "salary_max": 60000.0,
        "salary_currency": "GBP",
        "attendance_type": "remote",
        "url": "https://linkedin.com/jobs/view/job_1129",
        "scrape_datetime": "2024-12-27T09:30:00.000+00:00",
        "service_log_id": 1,
        "geolocation_id": 30,
        "parsed_location": "Bristol, UK",
    },
    {
        "external_job_id": "job_1130",
        "platform": "linkedin",
        "owner_id": 1,
        "is_scraped": True,
        "is_processed": True,
        "is_active": False,
        "title": "Technical Lead",
        "description": "Work remotely with a global team on mission-critical applications...",
        "company": "AI Research Corp",
        "location": "Glasgow, UK (hybrid)",
        "location_city": "Glasgow",
        "location_country": "United Kingdom",
        "salary_min": 85000.0,
        "salary_max": 110000.0,
        "salary_currency": "GBP",
        "attendance_type": "hybrid",
        "url": "https://linkedin.com/jobs/view/job_1130",
        "scrape_datetime": "2024-12-26T12:45:00.000+00:00",
        "service_log_id": 1,
        "geolocation_id": 31,
        "parsed_location": "Glasgow, UK",
    },
    {
        "external_job_id": "job_1131",
        "platform": "linkedin",
        "owner_id": 1,
        "is_scraped": True,
        "is_processed": True,
        "is_active": False,
        "title": "Engineering Manager",
        "description": "We are looking for an experienced developer to join our growing team...",
        "company": "BlockChain Ventures",
        "location": "Leeds, UK (on-site)",
        "location_city": "Leeds",
        "location_country": "United Kingdom",
        "salary_min": 95000.0,
        "salary_max": 125000.0,
        "salary_currency": "GBP",
        "attendance_type": "on-site",
        "url": "https://linkedin.com/jobs/view/job_1131",
        "scrape_datetime": "2024-12-25T15:00:00.000+00:00",
        "service_log_id": 1,
        "geolocation_id": 25,
        "parsed_location": "Leeds, UK",
    },
    {
        "external_job_id": "job_1132",
        "platform": "linkedin",
        "owner_id": 1,
        "is_scraped": True,
        "is_processed": True,
        "is_active": False,
        "title": "Principal Engineer",
        "description": "Join our innovative startup and help build cutting-edge solutions...",
        "company": "CloudScale Systems",
        "location": "Liverpool, UK (remote)",
        "location_city": "Liverpool",
        "location_country": "United Kingdom",
        "salary_min": 100000.0,
        "salary_max": 140000.0,
        "salary_currency": "GBP",
        "attendance_type": "remote",
        "url": "https://linkedin.com/jobs/view/job_1132",
        "scrape_datetime": "2024-12-24T08:15:00.000+00:00",
        "service_log_id": 1,
        "geolocation_id": 26,
        "parsed_location": "Liverpool, UK",
    },
    {
        "external_job_id": "job_1133",
        "platform": "linkedin",
        "owner_id": 1,
        "is_scraped": True,
        "is_processed": True,
        "title": "Staff Engineer",
        "description": "Exciting opportunity to work with modern technologies in an agile environment...",
        "company": "DevOps Masters",
        "salary_min": 88000.0,
        "salary_max": 115000.0,
        "salary_currency": "GBP",
        "attendance_type": "remote",
        "url": "https://linkedin.com/jobs/view/job_1133",
        "scrape_datetime": "2024-12-23T10:30:00.000+00:00",
        "service_log_id": 1,
    },
    {
        "external_job_id": "job_1134",
        "platform": "linkedin",
        "owner_id": 1,
        "is_scraped": True,
        "is_processed": True,
        "title": "Solutions Architect",
        "description": "Work on challenging projects with a talented team of engineers...",
        "company": "Enterprise Solutions Ltd",
        "salary_min": 92000.0,
        "salary_max": 120000.0,
        "salary_currency": "GBP",
        "attendance_type": "remote",
        "url": "https://linkedin.com/jobs/view/job_1134",
        "scrape_datetime": "2024-12-22T13:00:00.000+00:00",
        "service_log_id": 1,
    },
    {
        "external_job_id": "job_1135",
        "platform": "linkedin",
        "owner_id": 1,
        "is_scraped": True,
        "is_processed": True,
        "title": "Platform Engineer",
        "description": "Build scalable systems that impact millions of users...",
        "company": "TechCorp Inc",
        "salary_min": 70000.0,
        "salary_max": 90000.0,
        "salary_currency": "GBP",
        "url": "https://linkedin.com/jobs/view/job_1135",
        "scrape_datetime": "2024-12-21T15:45:00.000+00:00",
        "service_log_id": 1,
    },
    {
        "external_job_id": "job_1136",
        "platform": "linkedin",
        "owner_id": 1,
        "is_scraped": True,
        "is_processed": True,
        "title": "Infrastructure Engineer",
        "description": "Collaborate with cross-functional teams to deliver high-quality software...",
        "company": "StartupXYZ",
        "salary_min": 65000.0,
        "salary_max": 85000.0,
        "salary_currency": "GBP",
        "url": "https://linkedin.com/jobs/view/job_1136",
        "scrape_datetime": "2024-12-20T09:15:00.000+00:00",
        "service_log_id": 1,
    },
    {
        "external_job_id": "job_1137",
        "platform": "linkedin",
        "owner_id": 1,
        "is_scraped": True,
        "is_processed": True,
        "title": "Database Administrator",
        "description": "Help shape the future of our platform with your technical expertise...",
        "company": "CloudTech Solutions",
        "salary_min": 58000.0,
        "salary_max": 75000.0,
        "salary_currency": "GBP",
        "url": "https://linkedin.com/jobs/view/job_1137",
        "scrape_datetime": "2024-12-19T11:30:00.000+00:00",
        "service_log_id": 1,
    },
    {
        "external_job_id": "job_1138",
        "platform": "linkedin",
        "owner_id": 1,
        "is_scraped": True,
        "is_processed": True,
        "title": "Business Intelligence Developer",
        "description": "Work remotely with a global team on mission-critical applications...",
        "company": "DataSoft Ltd",
        "location": "Cambridge, UK (hybrid)",
        "location_city": "Cambridge",
        "location_country": "United Kingdom",
        "attendance_type": "hybrid",
        "url": "https://linkedin.com/jobs/view/job_1138",
        "scrape_datetime": "2024-12-18T14:00:00.000+00:00",
        "service_log_id": 1,
        "geolocation_id": 32,
        "parsed_location": "Cambridge, UK",
    },
    {
        "external_job_id": "job_1139",
        "platform": "linkedin",
        "owner_id": 1,
        "is_scraped": True,
        "is_processed": True,
        "title": "ETL Developer",
        "description": "We are looking for an experienced developer to join our growing team...",
        "company": "FinTech Innovations",
        "location": "Oxford, UK (on-site)",
        "location_city": "Oxford",
        "location_country": "United Kingdom",
        "attendance_type": "on-site",
        "url": "https://linkedin.com/jobs/view/job_1139",
        "scrape_datetime": "2024-12-17T16:30:00.000+00:00",
        "service_log_id": 1,
        "geolocation_id": 33,
        "parsed_location": "Oxford, UK",
    },
    {
        "external_job_id": "job_1140",
        "platform": "linkedin",
        "owner_id": 1,
        "is_scraped": True,
        "is_processed": True,
        "title": "Big Data Engineer",
        "description": "Join our innovative startup and help build cutting-edge solutions...",
        "company": "HealthTech Solutions",
        "location": "Reading, UK (remote)",
        "location_city": "Reading",
        "location_country": "United Kingdom",
        "attendance_type": "remote",
        "url": "https://linkedin.com/jobs/view/job_1140",
        "scrape_datetime": "2024-12-16T08:45:00.000+00:00",
        "service_log_id": 1,
        "geolocation_id": 34,
        "parsed_location": "Reading, UK",
    },
    {
        "external_job_id": "job_1141",
        "platform": "linkedin",
        "owner_id": 1,
        "is_scraped": True,
        "is_processed": True,
        "title": "Senior Python Developer",
        "description": "Exciting opportunity to work with modern technologies in an agile environment...",
        "company": "InnovateTech Solutions",
        "location": "Brighton, UK",
        "location_city": "Brighton",
        "location_country": "United Kingdom",
        "url": "https://linkedin.com/jobs/view/job_1141",
        "scrape_datetime": "2024-12-15T12:15:00.000+00:00",
        "service_log_id": 1,
        "geolocation_id": 35,
        "parsed_location": "Brighton, UK",
    },
    {
        "external_job_id": "job_1142",
        "platform": "linkedin",
        "owner_id": 1,
        "is_scraped": True,
        "is_processed": True,
        "title": "Full Stack Engineer",
        "description": "Work on challenging projects with a talented team of engineers...",
        "company": "Digital Dynamics",
        "location": "Southampton, UK",
        "location_city": "Southampton",
        "location_country": "United Kingdom",
        "url": "https://linkedin.com/jobs/view/job_1142",
        "scrape_datetime": "2024-12-14T14:45:00.000+00:00",
        "service_log_id": 1,
        "geolocation_id": 36,
        "parsed_location": "Southampton, UK",
    },
    {
        "external_job_id": "job_1143",
        "platform": "linkedin",
        "owner_id": 1,
        "is_scraped": True,
        "is_processed": True,
        "title": "DevOps Engineer",
        "description": "Build scalable systems that impact millions of users...",
        "company": "Future Systems",
        "location": "Nottingham, UK (hybrid)",
        "location_city": "Nottingham",
        "location_country": "United Kingdom",
        "salary_min": 60000.0,
        "salary_max": 78000.0,
        "salary_currency": "GBP",
        "attendance_type": "hybrid",
        "url": "https://linkedin.com/jobs/view/job_1143",
        "scrape_datetime": "2024-12-13T10:00:00.000+00:00",
        "service_log_id": 1,
        "geolocation_id": 37,
        "parsed_location": "Nottingham, UK",
    },
    {
        "external_job_id": "job_1146",
        "platform": "linkedin",
        "owner_id": 1,
        "is_scraped": True,
        "is_processed": True,
        "title": "Data Engineer",
        "description": "Work remotely with a global team on mission-critical applications...",
        "company": "CyberSecure Ltd",
        "location": "Manchester, UK (hybrid)",
        "location_city": "Manchester",
        "location_country": "United Kingdom",
        "salary_min": 62000.0,
        "salary_max": 80000.0,
        "salary_currency": "GBP",
        "attendance_type": "hybrid",
        "url": "https://linkedin.com/jobs/view/job_1146",
        "scrape_datetime": "2024-12-10T15:45:00.000+00:00",
        "service_log_id": 1,
        "geolocation_id": 23,
        "parsed_location": "Manchester, UK",
    },
    {
        "external_job_id": "job_1147",
        "platform": "linkedin",
        "owner_id": 1,
        "is_scraped": True,
        "is_processed": True,
        "title": "ML Engineer",
        "description": "We are looking for an experienced developer to join our growing team...",
        "company": "GreenTech Energy",
        "location": "Birmingham, UK (on-site)",
        "location_city": "Birmingham",
        "location_country": "United Kingdom",
        "salary_min": 72000.0,
        "salary_max": 95000.0,
        "salary_currency": "GBP",
        "attendance_type": "on-site",
        "url": "https://linkedin.com/jobs/view/job_1147",
        "scrape_datetime": "2024-12-09T09:00:00.000+00:00",
        "service_log_id": 1,
        "geolocation_id": 29,
        "parsed_location": "Birmingham, UK",
    },
    {
        "external_job_id": "job_1148",
        "platform": "linkedin",
        "owner_id": 1,
        "is_scraped": True,
        "is_processed": True,
        "title": "Frontend Developer",
        "description": "Join our innovative startup and help build cutting-edge solutions...",
        "company": "SmartCity Solutions",
        "location": "Edinburgh, UK (remote)",
        "location_city": "Edinburgh",
        "location_country": "United Kingdom",
        "salary_min": 48000.0,
        "salary_max": 62000.0,
        "salary_currency": "GBP",
        "attendance_type": "remote",
        "url": "https://linkedin.com/jobs/view/job_1148",
        "scrape_datetime": "2024-12-08T10:30:00.000+00:00",
        "service_log_id": 1,
        "geolocation_id": 22,
        "parsed_location": "Edinburgh, UK",
    },
    {
        "external_job_id": "job_1149",
        "platform": "linkedin",
        "owner_id": 1,
        "is_scraped": True,
        "is_processed": True,
        "title": "React Developer",
        "description": "Exciting opportunity to work with modern technologies in an agile environment...",
        "company": "BioTech Innovations",
        "location": "Bristol, UK (hybrid)",
        "location_city": "Bristol",
        "location_country": "United Kingdom",
        "salary_min": 55000.0,
        "salary_max": 72000.0,
        "salary_currency": "GBP",
        "attendance_type": "hybrid",
        "url": "https://linkedin.com/jobs/view/job_1149",
        "scrape_datetime": "2024-12-07T12:00:00.000+00:00",
        "service_log_id": 1,
        "geolocation_id": 30,
        "parsed_location": "Bristol, UK",
    },
    {
        "external_job_id": "job_1153",
        "platform": "linkedin",
        "owner_id": 1,
        "is_scraped": True,
        "is_processed": True,
        "title": "AI Software Developer",
        "description": "Work on challenging projects with a talented team of engineers...",
        "company": "AI Research Corp",
        "location": "Glasgow, UK (hybrid)",
        "location_city": "Glasgow",
        "location_country": "United Kingdom",
        "salary_min": 75000.0,
        "salary_max": 98000.0,
        "salary_currency": "GBP",
        "attendance_type": "hybrid",
        "url": "https://linkedin.com/jobs/view/job_1153",
        "scrape_datetime": "2024-12-03T10:15:00.000+00:00",
        "service_log_id": 1,
        "geolocation_id": 31,
        "parsed_location": "Glasgow, UK",
    },
    {
        "external_job_id": "job_1154",
        "platform": "linkedin",
        "owner_id": 1,
        "is_scraped": True,
        "is_processed": True,
        "title": "iOS Developer",
        "description": "Build scalable systems that impact millions of users...",
        "company": "BlockChain Ventures",
        "location": "Leeds, UK (on-site)",
        "location_city": "Leeds",
        "location_country": "United Kingdom",
        "salary_min": 58000.0,
        "salary_max": 75000.0,
        "salary_currency": "GBP",
        "attendance_type": "on-site",
        "url": "https://linkedin.com/jobs/view/job_1154",
        "scrape_datetime": "2024-12-02T11:45:00.000+00:00",
        "service_log_id": 1,
        "geolocation_id": 25,
        "parsed_location": "Leeds, UK",
    },
    {
        "external_job_id": "job_1155",
        "platform": "linkedin",
        "owner_id": 1,
        "is_scraped": True,
        "is_processed": True,
        "title": "Android Developer",
        "description": "Collaborate with cross-functional teams to deliver high-quality software...",
        "company": "CloudScale Systems",
        "location": "Liverpool, UK (remote)",
        "location_city": "Liverpool",
        "location_country": "United Kingdom",
        "salary_min": 55000.0,
        "salary_max": 72000.0,
        "salary_currency": "GBP",
        "attendance_type": "remote",
        "url": "https://linkedin.com/jobs/view/job_1155",
        "scrape_datetime": "2024-12-01T13:30:00.000+00:00",
        "service_log_id": 1,
        "geolocation_id": 26,
        "parsed_location": "Liverpool, UK",
    },
    {
        "external_job_id": "job_1156",
        "platform": "linkedin",
        "owner_id": 1,
        "is_scraped": True,
        "is_processed": True,
        "title": "Site Reliability Engineer",
        "description": "Help shape the future of our platform with your technical expertise...",
        "company": "DevOps Masters",
        "location": "Cardiff, UK (hybrid)",
        "location_city": "Cardiff",
        "location_country": "United Kingdom",
        "salary_min": 68000.0,
        "salary_max": 88000.0,
        "salary_currency": "GBP",
        "attendance_type": "hybrid",
        "url": "https://linkedin.com/jobs/view/job_1156",
        "scrape_datetime": "2024-11-30T15:00:00.000+00:00",
        "service_log_id": 1,
        "geolocation_id": 27,
        "parsed_location": "Cardiff, UK",
    },
    {
        "external_job_id": "job_1157",
        "platform": "linkedin",
        "owner_id": 1,
        "is_scraped": True,
        "is_processed": True,
        "title": "Cloud Architect",
        "description": "Work remotely with a global team on mission-critical applications...",
        "company": "Enterprise Solutions Ltd",
        "location": "Newcastle, UK (remote)",
        "location_city": "Newcastle",
        "location_country": "United Kingdom",
        "salary_min": 85000.0,
        "salary_max": 115000.0,
        "salary_currency": "GBP",
        "attendance_type": "remote",
        "url": "https://linkedin.com/jobs/view/job_1157",
        "scrape_datetime": "2024-11-29T09:45:00.000+00:00",
        "service_log_id": 1,
        "geolocation_id": 28,
        "parsed_location": "Newcastle, UK",
    },
    {
        "external_job_id": "job_1158",
        "platform": "linkedin",
        "owner_id": 1,
        "is_scraped": True,
        "is_processed": True,
        "title": "Security Engineer",
        "description": "We are looking for an experienced developer to join our growing team...",
        "company": "TechCorp Inc",
        "location": "London, UK (on-site)",
        "location_city": "London",
        "location_country": "United Kingdom",
        "salary_min": 78000.0,
        "salary_max": 100000.0,
        "salary_currency": "GBP",
        "attendance_type": "on-site",
        "url": "https://linkedin.com/jobs/view/job_1158",
        "scrape_datetime": "2024-11-28T11:15:00.000+00:00",
        "service_log_id": 1,
        "geolocation_id": 20,
        "parsed_location": "London, UK",
    },
    {
        "external_job_id": "job_1159",
        "platform": "linkedin",
        "owner_id": 1,
        "is_scraped": True,
        "is_processed": True,
        "title": "Blockchain Developer",
        "description": "Join our innovative startup and help build cutting-edge solutions...",
        "company": "StartupXYZ",
        "location": "Manchester, UK (hybrid)",
        "location_city": "Manchester",
        "location_country": "United Kingdom",
        "salary_min": 70000.0,
        "salary_max": 92000.0,
        "salary_currency": "GBP",
        "attendance_type": "hybrid",
        "url": "https://linkedin.com/jobs/view/job_1159",
        "scrape_datetime": "2024-11-27T13:45:00.000+00:00",
        "service_log_id": 1,
        "geolocation_id": 23,
        "parsed_location": "Manchester, UK",
    },
    # Scraping Failed
    {
        "external_job_id": "2468135790",
        "platform": "indeed",
        "owner_id": 1,
        "is_failed": True,
        "is_processed": True,
        "scrape_error": [
            {"datetime": "2025-08-18T08:30:00+00:00", "error": "Page not found - job posting may have been removed"}
        ],
        "title": "Data Engineer",
        "scrape_datetime": "2025-08-18T08:30:55.567890+00:00",
        "is_imported": True,
        "url": "test",
        "service_log_id": 1,
        "exclusion_filter_id": 1,
    },
    {
        "external_job_id": "cvlib_678901",
        "platform": "cv-library",
        "owner_id": 2,
        "is_failed": True,
        "is_processed": True,
        "scrape_error": [
            {"datetime": "2025-09-07T11:45:00+00:00", "error": "Access denied - company blocked scraping"}
        ],
        "title": "Sustainability Software Engineer",
        "scrape_datetime": "2025-09-07T11:45:28.456789+00:00",
        "url": "test",
        "service_log_id": 1,
    },
    {
        "external_job_id": "soft123456789",
        "platform": "indeed",
        "owner_id": 2,
        "is_failed": True,
        "is_processed": True,
        "scrape_error": [
            {"datetime": "2025-09-11T15:30:00+00:00", "error": "Rate limit exceeded - retry after 24 hours"}
        ],
        "title": "Software Engineer",
        "scrape_datetime": "2025-09-11T15:30:42.678901+00:00",
        "url": "test",
        "service_log_id": 1,
    },
    {
        "external_job_id": "job_1120",
        "platform": "linkedin",
        "owner_id": 1,
        "is_failed": True,
        "is_processed": True,
        "scrape_error": [
            {"datetime": "2025-01-05T11:15:00+00:00", "error": "Page not found - job posting may have been removed"}
        ],
        "title": "Angular Developer",
        "url": "test",
        "scrape_datetime": "2025-01-05T11:15:00.000+00:00",
        "service_log_id": 1,
    },
    {
        "external_job_id": "job_1121",
        "platform": "linkedin",
        "owner_id": 1,
        "is_failed": True,
        "is_processed": True,
        "scrape_error": [{"datetime": "2025-01-04T14:30:00+00:00", "error": "Scraping blocked - rate limit exceeded"}],
        "title": "Data Scientist",
        "url": "test",
        "scrape_datetime": "2025-01-04T14:30:00.000+00:00",
        "service_log_id": 1,
    },
    {
        "external_job_id": "job_1122",
        "platform": "linkedin",
        "owner_id": 1,
        "is_failed": True,
        "is_processed": True,
        "scrape_error": [
            {"datetime": "2025-01-03T16:45:00+00:00", "error": "Access denied - company blocked scraping"}
        ],
        "title": "AI Software Developer",
        "url": "test",
        "scrape_datetime": "2025-01-03T16:45:00.000+00:00",
        "service_log_id": 1,
    },
    {
        "external_job_id": "job_1123",
        "platform": "linkedin",
        "owner_id": 1,
        "is_failed": True,
        "is_processed": True,
        "scrape_error": [
            {"datetime": "2025-01-02T08:00:00+00:00", "error": "Rate limit exceeded - retry after 24 hours"}
        ],
        "title": "iOS Developer",
        "url": "test",
        "scrape_datetime": "2025-01-02T08:00:00.000+00:00",
        "service_log_id": 1,
    },
    {
        "external_job_id": "job_1124",
        "platform": "linkedin",
        "owner_id": 1,
        "is_failed": True,
        "is_processed": True,
        "scrape_error": [
            {"datetime": "2025-01-01T13:20:00+00:00", "error": "Connection timeout - server not responding"}
        ],
        "title": "Android Developer",
        "url": "test",
        "scrape_datetime": "2025-01-01T13:20:00.000+00:00",
        "service_log_id": 1,
    },
    {
        "external_job_id": "job_1150",
        "platform": "linkedin",
        "owner_id": 1,
        "is_failed": True,
        "is_processed": True,
        "scrape_error": [{"datetime": "2024-12-06T14:15:00+00:00", "error": "Invalid job posting format"}],
        "title": "Vue.js Developer",
        "url": "test",
        "scrape_datetime": "2024-12-06T14:15:00.000+00:00",
        "service_log_id": 1,
    },
    {
        "external_job_id": "job_1151",
        "platform": "linkedin",
        "owner_id": 1,
        "is_failed": True,
        "is_processed": True,
        "scrape_error": [
            {"datetime": "2024-12-05T16:30:00+00:00", "error": "Page not found - job posting may have been removed"}
        ],
        "title": "Angular Developer",
        "url": "test",
        "scrape_datetime": "2024-12-05T16:30:00.000+00:00",
        "service_log_id": 1,
    },
    {
        "external_job_id": "job_1152",
        "platform": "linkedin",
        "owner_id": 1,
        "is_failed": True,
        "is_processed": True,
        "scrape_error": [
            {"datetime": "2024-12-04T08:45:00+00:00", "error": "Connection timeout - server not responding"}
        ],
        "title": "Data Scientist",
        "url": "test",
        "scrape_datetime": "2024-12-04T08:45:00.000+00:00",
        "service_log_id": 1,
    },
    # Not processed
    {
        "external_job_id": "job_1112",
        "platform": "linkedin",
        "owner_id": 1,
        "is_processed": False,
        "title": "DevOps Engineer",
        "description": "Exciting opportunity to work with modern technologies in an agile environment...",
        "company": "CloudTech Solutions",
        "location": "Birmingham, UK (on-site)",
        "location_city": "Birmingham",
        "location_country": "United Kingdom",
        "salary_min": 65000.0,
        "salary_max": 85000.0,
        "salary_currency": "GBP",
        "attendance_type": "on-site",
        "url": "https://linkedin.com/jobs/view/job_1112",
        "scrape_datetime": "2025-01-13T09:15:00.000+00:00",
        "service_log_id": 1,
        "geolocation_id": 29,
        "parsed_location": "Birmingham, UK",
    },
    {
        "external_job_id": "9988776655",
        "platform": "indeed",
        "owner_id": 1,
        "is_processed": False,
        "scrape_error": [{"datetime": "2025-08-20T19:25:00+00:00", "error": "Scraping blocked - rate limit exceeded"}],
        "title": "ML Engineer",
        "scrape_datetime": "2025-08-20T19:25:08.678901+00:00",
        "is_active": False,
        "url": "test",
        "service_log_id": 1,
        "exclusion_filter_id": 1,
    },
    {
        "external_job_id": "job_1161",
        "platform": "indeed",
        "owner_id": 1,
        "is_processed": False,
        "title": "Data Analyst",
        "url": "https://indeed.com/viewjob?jk=job_1161",
        "service_log_id": 1,
    },
    {
        "external_job_id": "job_1113",
        "platform": "linkedin",
        "owner_id": 1,
        "is_processed": False,
        "title": "Software Engineer",
        "description": "Work on challenging projects with a talented team of engineers...",
        "company": "DataSoft Ltd",
        "location": "Edinburgh, UK (hybrid)",
        "location_city": "Edinburgh",
        "location_country": "United Kingdom",
        "salary_min": 55000.0,
        "salary_max": 70000.0,
        "salary_currency": "GBP",
        "attendance_type": "hybrid",
        "url": "https://linkedin.com/jobs/view/job_1113",
        "scrape_datetime": "2025-01-12T14:45:00.000+00:00",
        "service_log_id": 1,
        "geolocation_id": 22,
        "parsed_location": "Edinburgh, UK",
    },
    {
        "external_job_id": "job_1114",
        "platform": "linkedin",
        "owner_id": 1,
        "is_processed": False,
        "title": "Backend Developer",
        "description": "Build scalable systems that impact millions of users...",
        "company": "FinTech Innovations",
        "location": "Bristol, UK (remote)",
        "location_city": "Bristol",
        "location_country": "United Kingdom",
        "salary_min": 58000.0,
        "salary_max": 75000.0,
        "salary_currency": "GBP",
        "attendance_type": "remote",
        "url": "https://linkedin.com/jobs/view/job_1114",
        "scrape_datetime": "2025-01-11T16:20:00.000+00:00",
        "service_log_id": 1,
        "geolocation_id": 30,
        "parsed_location": "Bristol, UK",
    },
    # Skipped
    {
        "external_job_id": "job_1115",
        "platform": "linkedin",
        "owner_id": 1,
        "is_skipped": True,
        "skip_reason": "You reached your month quota for job scraping.",
        "is_processed": True,
        "title": "Data Engineer",
        "description": "Collaborate with cross-functional teams to deliver high-quality software...",
        "company": "HealthTech Solutions",
        "location": "Glasgow, UK (hybrid)",
        "location_city": "Glasgow",
        "location_country": "United Kingdom",
        "salary_min": 62000.0,
        "salary_max": 82000.0,
        "salary_currency": "GBP",
        "attendance_type": "hybrid",
        "url": "https://linkedin.com/jobs/view/job_1115",
        "scrape_datetime": "2025-01-10T08:30:00.000+00:00",
        "service_log_id": 1,
        "geolocation_id": 31,
        "parsed_location": "Glasgow, UK",
    },
    {
        "external_job_id": "job_1144",
        "platform": "linkedin",
        "owner_id": 1,
        "is_processed": True,
        "title": "Software Engineer",
        "description": "Collaborate with cross-functional teams to deliver high-quality software...",
        "company": "Quantum Labs",
        "location": "Sheffield, UK (on-site)",
        "location_city": "Sheffield",
        "location_country": "United Kingdom",
        "is_skipped": True,
        "skip_reason": "Quota",
        "salary_min": 52000.0,
        "salary_max": 68000.0,
        "salary_currency": "GBP",
        "attendance_type": "on-site",
        "url": "https://linkedin.com/jobs/view/job_1144",
        "scrape_datetime": "2024-12-12T11:30:00.000+00:00",
        "service_log_id": 1,
        "geolocation_id": 38,
        "parsed_location": "Sheffield, UK",
    },
    {
        "external_job_id": "job_1145",
        "platform": "linkedin",
        "owner_id": 1,
        "is_processed": True,
        "title": "Backend Developer",
        "description": "Help shape the future of our platform with your technical expertise...",
        "company": "Neural Networks Inc",
        "location": "London, UK (remote)",
        "location_city": "London",
        "is_skipped": True,
        "skip_reason": "Quota",
        "location_country": "United Kingdom",
        "salary_min": 65000.0,
        "salary_max": 85000.0,
        "salary_currency": "GBP",
        "attendance_type": "remote",
        "url": "https://linkedin.com/jobs/view/job_1145",
        "scrape_datetime": "2024-12-11T13:15:00.000+00:00",
        "service_log_id": 1,
        "geolocation_id": 20,
        "parsed_location": "London, UK",
    },
    # Closed
    {
        "external_job_id": "job_1159rg",
        "platform": "linkedin",
        "owner_id": 1,
        "is_closed": True,
        "is_scraped": True,
        "is_processed": True,
        "title": "Blockchain Developer 2",
        "description": "Join our innovative startup and help build cutting-edge solutions...",
        "company": "StartupXYZ",
        "location": "Manchester, UK (hybrid)",
        "location_city": "Manchester",
        "location_country": "United Kingdom",
        "salary_min": 70000.0,
        "salary_max": 92000.0,
        "salary_currency": "GBP",
        "attendance_type": "hybrid",
        "url": "https://linkedin.com/jobs/view/job_1159",
        "scrape_datetime": "2024-11-27T13:45:00.000+00:00",
        "service_log_id": 1,
        "geolocation_id": 23,
        "parsed_location": "Manchester, UK",
    },
    # Scraping retry
    {
        "external_job_id": "job_11sefwfw59rg",
        "platform": "linkedin",
        "owner_id": 1,
        "is_closed": False,
        "is_scraped": False,
        "is_processed": False,
        "retry_count": 1,
        "scrape_error": [
            {"datetime": "2025-08-18T08:30:00+00:00", "error": "Page not found - job posting may have been removed"}
        ],
        "title": "Blockchain Developer 3",
        "description": "Join our innovative startup and help build cutting-edge solutions...",
        "company": "StartupXYZ",
        "location": "Manchester, UK (hybrid)",
        "location_city": "Manchester",
        "location_country": "United Kingdom",
        "salary_min": 70000.0,
        "salary_max": 92000.0,
        "salary_currency": "GBP",
        "attendance_type": "hybrid",
        "url": "https://linkedin.com/jobs/view/job_1159",
        "scrape_datetime": "2024-11-27T13:45:00.000+00:00",
        "service_log_id": 1,
        "geolocation_id": 23,
        "parsed_location": "Manchester, UK",
    },
]


def find_index(**kwargs) -> int | None:
    """Find the scraped job index for the given kwargs."""

    for index, scraped_job in enumerate(SCRAPED_JOB_DATA):
        if all([scraped_job.get(key) == value for key, value in kwargs.items()]):
            return index
    return None


SCRAPED_JOB_SCRAPED = find_index(is_scraped=True)
SCRAPED_JOB_NOT_PROCESSED_INDEX = find_index(is_processed=False)
SCRAPED_JOB_FAILED_INDEX = find_index(is_failed=True)
SCRAPED_JOB_SKIPPED_INDEX = find_index(is_skipped=True)

EMAIL_SCRAPEDJOB_MAPPINGS = [
    # owner_id=1 emails -> owner_id=1 jobs (ids: 1-5, 10-48, 51-68)
    {"email_id": 1, "scraped_job_ids": [1, 2, 4, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21]},
    {"email_id": 2, "scraped_job_ids": [3, 5, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34]},
    {"email_id": 3, "scraped_job_ids": [2, 5, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47]},
    {"email_id": 5, "scraped_job_ids": [48, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68]},
    # owner_id=2 emails -> owner_id=2 jobs (ids: 6-9, 49-50)
    {"email_id": 4, "scraped_job_ids": [6, 7]},
    {"email_id": 6, "scraped_job_ids": [49, 50]},
    {"email_id": 7, "scraped_job_ids": [8]},
    {"email_id": 8, "scraped_job_ids": [9]},
]
