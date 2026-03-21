"""LinkedIn job alert email parser."""

import re

from bs4 import BeautifulSoup

from app.job_email_scraping.email_parsers.utils import process_salary, Platform
from app.job_email_scraping.schemas import Salary, JobInfo, JobResult

BASE_URL = "https://www.linkedin.com/jobs/view/"


def parse_linkedin_job_email(body: str) -> list[JobResult]:
    """Parse LinkedIn job alert email and extract job information.
    Compatible with both regular and forwarded email formats.

    :param str body: email body
    :return: list of JobResult objects containing job information
    """

    # Parse with BeautifulSoup
    soup = BeautifulSoup(body, "html.parser", from_encoding="utf-8")

    # Try primary method: Find all job cards with data-test-id (regular emails)
    job_cards = soup.find_all("td", {"data-test-id": "job-card"})

    # Fallback: If no job cards found, traverse up from title links (forwarded emails)
    if not job_cards:
        title_links = soup.find_all("a", class_="font-bold text-md leading-regular text-system-blue-50")

        # For each title link, find the parent TD that contains all job info
        seen_cards = set()
        for link in title_links:
            current = link
            # Traverse up the tree to find the job card container
            for _ in range(20):  # Max 20 levels up
                current = current.parent
                if current is None:
                    break

                if current.name == "td":
                    # Check if this TD contains both title and company info
                    has_title = (
                        current.find("a", class_="font-bold text-md leading-regular text-system-blue-50") is not None
                    )
                    has_company = (
                        current.find(
                            "p", class_="text-system-gray-100 text-xs leading-regular mt-0.5 line-clamp-1 text-ellipsis"
                        )
                        is not None
                    )

                    if has_title and has_company:
                        # Use id() to avoid duplicates
                        card_id = id(current)
                        if card_id not in seen_cards:
                            job_cards.append(current)
                            seen_cards.add(card_id)
                        break

    # Extract information from each job card
    jobs = []

    for card in job_cards:
        # Initialise variables
        title = None
        url = None
        job_id = None
        company = None
        location = None
        salary_currency = None
        salary_min = None
        salary_max = None

        # Extract job title and URL
        title_tag = card.find("a", class_="font-bold text-md leading-regular text-system-blue-50")
        if title_tag:
            title = " ".join(title_tag.get_text(strip=True).split())
            url = title_tag.get("href", None)

            if url:
                # Extract job ID - handle both normal integers and scientific notation
                jobid_pattern = r"linkedin\.com/(?:comm/)?jobs/view/([\d.e+]+)"
                matches = re.findall(jobid_pattern, url, re.IGNORECASE)
                if matches:
                    try:
                        # Convert scientific notation to integer string
                        job_id = str(int(float(matches[0])))
                    except (ValueError, OverflowError):
                        job_id = matches[0]
                else:
                    # Handle collection URLs (e.g. top-applicant) with currentJobId query param
                    current_job_match = re.search(r"[?&]currentJobId=(\d+)", url, re.IGNORECASE)
                    if current_job_match:
                        job_id = current_job_match.group(1)

        # Extract company name and location
        company_location_tag = card.find(
            "p", class_="text-system-gray-100 text-xs leading-regular mt-0.5 line-clamp-1 text-ellipsis"
        )
        if company_location_tag:
            text = company_location_tag.get_text(strip=True)
            parts = [part.strip() for part in text.split("·")]
            if len(parts) >= 2:
                company = " ".join(parts[0].split())
                location = " ".join(parts[1].split())

        # Extract salary information
        salary_tag = card.find("p", class_="text-system-gray-70 text-xs leading-regular mt-0.5")
        if salary_tag:
            salary_text = salary_tag.get_text(strip=True)
            match = re.search(r"([£$€])(\d+\.?\d*[KM]?)-([£$€])(\d+\.?\d*[KM]?)\s*/\s*(\w+)", salary_text)
            if match:
                salary_frequency = match.group(5)
                if salary_frequency == "year":
                    salary_currency = match.group(1)
                    salary_min = process_salary(match.group(2))
                    salary_max = process_salary(match.group(4))

        processed_url = BASE_URL + job_id
        # Create Pydantic objects
        salary = Salary(min_amount=salary_min, max_amount=salary_max, currency=salary_currency)
        job_info = JobInfo(title=title, url=processed_url, raw_url=url, salary=salary)
        job_result = JobResult(
            company=company, job_id=job_id, location=location, job=job_info, platform=Platform.LINKEDIN
        )
        jobs.append(job_result)

    return jobs


def extract_alert_name(alert_string: str) -> str | None:
    """Extract alert title from LinkedIn job alert email strings.
    :param str alert_string: alert string from email
    :return: extracted job title or None if not found"""

    # Pattern: Extract text between quotes
    pattern = r"“([^”]+)”"
    match = re.search(pattern, alert_string)
    if match:
        return match.group(1).strip()

    return None
