"""VeganJobs job email parser"""

import re

from app.job_email_scraping.email_parsers.utils import Platform
from app.job_email_scraping.schemas import JobInfo, JobResult

BASE_URL = "https://veganjobs.com/job/"


def parse_veganjobs_email(body: str) -> list[JobResult]:
    """Parse VeganJobs alert email and extract job information.
    :param str body: email body (plain text)
    :return: list of JobResult objects containing job information"""

    jobs = []

    # Split by job separators (==========================)
    separator_pattern = r"={20,}"
    parts = re.split(separator_pattern, body)

    if len(parts) < 2:
        return []

    # The jobs section is the second part (index 1)
    jobs_section = parts[1]

    # Pattern to match jobs with optional employment type prefix
    # Format: [Employment Type - ]Job Title
    #         Location: Location
    #         Company: Company Name
    #         View Details: URL
    job_pattern = (
        r"(?:^|\n)(?:[^\n]+ - )?([^\n]+)\n"
        r"Location: ([^\n]+)\n"
        r"Company: ([^\n]+)\n"
        r"View Details: (https://veganjobs\.com/job/[^\s\)]+)"
    )

    matches = re.finditer(job_pattern, jobs_section, re.MULTILINE)

    for match in matches:
        title = match.group(1).strip()
        location = match.group(2).strip()
        company = match.group(3).strip()
        url = match.group(4).strip()

        # Extract job_id from URL
        # URL format: https://veganjobs.com/job/company-location-title/
        job_id = None
        job_id_pattern = r"veganjobs\.com/job/([^/]+)/?$"
        id_match = re.search(job_id_pattern, url)
        if id_match:
            job_id = id_match.group(1)

        processed_url = BASE_URL + job_id
        job_info = JobInfo(title=title, raw_url=url, url=processed_url)
        job_result = JobResult(
            company=company, job_id=job_id, location=location, job=job_info, platform=Platform.VEGANJOBS
        )
        jobs.append(job_result)

    return jobs


def extract_alert_name(alert_string: str) -> str | None:
    """Extract alert title from VeganJobs job alert email strings.
    :param str alert_string: alert string from email
    :return: extracted job title or None if not found"""

    # Pattern: Extract text between quotes
    pattern = r'"([^"]+)"'
    match = re.search(pattern, alert_string)
    if match:
        return match.group(1).strip()

    return None
