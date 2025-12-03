"""NHS Jobs email parser"""

import datetime as dt
import re

from bs4 import BeautifulSoup

from app.eis.email_parsers import process_salary, Platform
from app.eis.job_scrapers import Salary, JobInfo, JobResult

BASE_URL = "https://beta.jobs.nhs.uk/candidate/jobadvert/"


def parse_nhs_job_email(body: str) -> list[JobResult]:
    """Parse NHS Jobs alert email and extract job information.
    :param str body: email body
    :return: list of JobResult objects containing job information"""

    soup = BeautifulSoup(body, "html.parser", from_encoding="utf-8")

    # Find all job sections (separated by <hr> tags)
    # Get the main content area
    content_td = soup.find("td", style=lambda value: value and "max-width:560px" in value)

    if not content_td:
        return []

    jobs = []

    # Find all job title links (they have the job URL)
    job_links = content_td.find_all("a", href=re.compile(r"beta\.jobs\.nhs\.uk/candidate/jobadvert/"))

    for job_link in job_links:
        # Initialise variables
        job_id = None
        location = None
        salary_currency = None
        salary_min = None
        salary_max = None
        deadline = None

        # Extract title and URL
        title = " ".join(job_link.get_text(strip=True).split())
        url = job_link.get("href", None)

        # Extract job ID from URL
        if url:
            # NHS Jobs URLs are in format: /candidate/jobadvert/CODE-YY-NNNN
            job_id_pattern = r"/candidate/jobadvert/([A-Z0-9\-]+)"
            match = re.search(job_id_pattern, url)
            if match:
                job_id = match.group(1)

        # Find the next table element which contains the job details
        next_table = job_link.find_next("table", role="presentation")

        if next_table:
            # Extract details from list items
            list_items = next_table.find_all("li")

            for item in list_items:
                text = item.get_text(strip=True)

                # Extract closing date
                if text.startswith("Closing Date:"):
                    if text.startswith("Closing Date:"):
                        date_str = text.replace("Closing Date:", "").strip()
                        try:
                            deadline = dt.datetime.strptime(date_str, "%d %b %Y")
                        except ValueError:
                            pass

                # Extract location
                elif text.startswith("Location:"):
                    location = text.replace("Location:", "").strip()

                # Extract salary (Pay)
                elif text.startswith("Pay:"):
                    salary_text = text.replace("Pay:", "").strip()
                    salary_pattern = r"([£$€])([\d,]+)\s+to\s+([£$€])([\d,]+)\s+a\s+(year|month|week|day|hour)"
                    match = re.search(salary_pattern, salary_text)
                    if match:
                        salary_frequency = match.group(5)
                        if salary_frequency == "year":
                            salary_currency = match.group(1)
                            salary_min = process_salary(match.group(2))
                            salary_max = process_salary(match.group(4))

        # Get the raw HTML for this job (from the job link up to the next <hr>)
        raw_html = str(job_link.find_parent())
        if next_table:
            raw_html += str(next_table)

        processed_url = BASE_URL + job_id
        # Create Pydantic objects
        salary = Salary(min_amount=salary_min, max_amount=salary_max, currency=salary_currency)
        job_info = JobInfo(title=title, url=processed_url, raw_url=url, salary=salary, deadline=deadline)
        job_result = JobResult(company="NHS", job_id=job_id, location=location, job=job_info, platform=Platform.NHS)
        jobs.append(job_result)

    return jobs
