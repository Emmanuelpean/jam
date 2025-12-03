"""VeganJobs job email parser"""

import re

from app.eis.email_parsers import Platform
from app.eis.job_scrapers import JobInfo, JobResult

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

        # If no job id, the processed_url is None
        if not job_id:
            processed_url = None
        else:
            processed_url = BASE_URL + job_id

        job_info = JobInfo(title=title, raw_url=url, url=processed_url)
        job_result = JobResult(
            company=company, job_id=job_id, location=location, job=job_info, platform=Platform.VEGANJOBS
        )
        jobs.append(job_result)

    return jobs
