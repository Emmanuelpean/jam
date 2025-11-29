"""LinkedIn and Indeed Job Scraper Module

This module provides functionality to scrape LinkedIn job postings using the BrightData API.
It offers a complete workflow to trigger data collection, monitor processing status, and
retrieve scraped job information."""

import re
import time

import cloudscraper
import requests
from bs4 import BeautifulSoup
from pydantic import BaseModel, Field
from tqdm import tqdm

from app.config import settings


# --------------------------------------------------- PYDANTIC MODELS --------------------------------------------------


class Salary(BaseModel):
    min_amount: float | None = None
    max_amount: float | None = None
    currency: str | None = None


class JobInfo(BaseModel):
    title: str | None = None
    description: str | None = None
    url: str | None = None
    salary: Salary = Field(default_factory=Salary)


class JobResult(BaseModel):
    company: str | None = None
    company_id: str | None = None
    location: str | None = None
    job: JobInfo
    raw: str | dict


# ------------------------------------------------- BRIGHTDATA SCRAPER -------------------------------------------------


class BrightdataJobScraper(object):
    """Job Scraper
    :ivar base_url: Base URL for the job platform
    :ivar name: Name of the job platform
    :ivar poll_interval: Time interval (in seconds) between polling attempts
    :ivar max_attempts: Maximum number of polling attempts"""

    base_url: str = ""
    name: str = ""
    poll_interval: int | float = 2
    max_attempts: int = 60

    def __init__(
        self,
        job_ids: str | list[str],
    ) -> None:
        """Object constructor
        :param job_ids: List of job IDs to scrape"""

        self.job_ids = [job_ids] if isinstance(job_ids, str) else job_ids
        self.job_urls = [f"{self.base_url}{job_id}" for job_id in self.job_ids]
        self.poll_interval = self.poll_interval
        self.max_attempts *= len(self.job_ids)

        # Load credentials from the secrets file
        self.api_key = settings.brightdata_api_key
        self.dataset_id = getattr(settings, f"brightdata_{self.name}_dataset_id")

    def _get_snapshot(self) -> str:
        """Get the snapshot id"""

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        trigger_url = "https://api.brightdata.com/datasets/v3/trigger"
        params = {
            "dataset_id": self.dataset_id,
            "include_errors": "true",
        }
        data = [{"url": job_url} for job_url in self.job_urls]
        response = requests.post(trigger_url, headers=headers, params=params, json=data)
        if response.status_code != 200:
            raise Exception(f"Failed to trigger dataset: {response.status_code} {response.text}")
        snapshot_id = response.json().get("snapshot_id")
        if not snapshot_id:
            raise Exception(f"No snapshot_id returned: {response.text}")

        return snapshot_id

    def _wait_for_data(self, snapshot_id: str) -> None:
        """Wait for the job data associated with a specific snapshot id to be ready
        :param snapshot_id: Snapshot ID"""

        progress_url = f"https://api.brightdata.com/datasets/v3/progress/{snapshot_id}"
        headers = {"Authorization": f"Bearer {self.api_key}"}

        # Create progress bar for polling attempts
        with tqdm(total=self.max_attempts, desc="Waiting for data", unit="attempt") as pbar:
            for attempt in range(self.max_attempts):
                progress_resp = requests.get(progress_url, headers=headers)
                if progress_resp.status_code not in (200, 202):
                    raise Exception(f"Failed to get snapshot status: {progress_resp.status_code} {progress_resp.text}")

                status = progress_resp.json().get("status")

                # Update progress bar description with current status
                pbar.set_description(f"Status: {status}")

                if status.lower() == "ready":
                    pbar.update(self.max_attempts - attempt)  # Complete the bar
                    break
                elif status.lower() == "failed":
                    raise Exception("Snapshot processing failed.")

                pbar.update(1)
                time.sleep(self.poll_interval)
            else:
                raise TimeoutError("Snapshot data not ready after maximum attempts.")

    def _retrieve_data(self, snapshot_id: str) -> list[dict]:
        """Retrieve the job data associated with the snapshot id
        :param snapshot_id: Snapshot ID
        :return: Job data dictionary"""

        snapshot_url = f"https://api.brightdata.com/datasets/v3/snapshot/{snapshot_id}"
        params = {"format": "json"}
        headers = {"Authorization": f"Bearer {self.api_key}"}

        data_resp = requests.get(snapshot_url, headers=headers, params=params)
        attempted = 0
        while data_resp.status_code == 202 and attempted < 10:
            data_resp = requests.get(snapshot_url, headers=headers, params=params)
            attempted += 1
        json_data = data_resp.json()
        if data_resp.status_code != 200:
            raise Exception(f"Failed to get snapshot data: {data_resp.status_code} {data_resp.text}")
        if isinstance(json_data, list) and "error_code" in json_data[0]:
            raise Exception(f"Failed to get snapshot data: {json_data}")
        return json_data

    def _process_job_data(self, job_data: dict) -> JobResult:
        """Process job data to extract relevant information
        :param job_data: Job data dictionary
        :return: Dictionary containing job information"""

        raise AssertionError("This method should be implemented in subclasses.")

    def scrape_job(self) -> list[JobResult]:
        """Complete workflow to scrape a LinkedIn job"""

        snapshot_id = self._get_snapshot()
        self._wait_for_data(snapshot_id)
        data = self._retrieve_data(snapshot_id)
        return [self._process_job_data(d) for d in data]


# ------------------------------------------------- INDEED SCRAPER -------------------------------------------------


class IndeedBrightdataJobScraper(BrightdataJobScraper):
    """LinkedIn Scraper"""

    base_url = "https://www.indeed.com/viewjob?jk="
    name = "indeed"
    poll_interval: int | float = 10
    max_attempts: int = 100

    def _process_job_data(self, job_data: dict) -> JobResult:
        """Process job data to extract relevant information
        :param job_data: Job data dictionary
        :return: Dictionary containing job information"""

        # Extract the yearly salary
        salary_pattern = (
            r"£(\d+(?:,\d+)?(?:k|K)?(?:\.\d+)?)\s*[-–]\s*£(\d+(?:,\d+)?(?:k|K)?(?:\.\d+)?)\s+(?:a|per)\s+(?:year|annum)"
        )
        salary_range = job_data.get("salary_formatted")
        if salary_range and (match := re.search(salary_pattern, salary_range)):
            min_amount = float(match.group(1).replace(",", ""))
            max_amount = float(match.group(2).replace(",", ""))
            currency = "GBP"
        else:
            min_amount = None
            max_amount = None
            currency = None

        return JobResult(
            company=job_data.get("company_name"),
            company_id=job_data.get("company_url"),
            location=job_data.get("location"),
            job=JobInfo(
                title=job_data.get("job_title"),
                description=job_data.get("description_text", "").strip("Show more Show less") or None,
                url=job_data.get("url"),
                salary=Salary(
                    min_amount=min_amount,
                    max_amount=max_amount,
                    currency=currency,
                ),
            ),
            raw=job_data,
        )


def extract_indeed_jobs_from_email(body: str) -> list[JobResult]:
    """Extract job information directly from an Indeed email body
    Note: Salary parsing is only compatible with GBP
    :param body: Email body content as string
    :return: List of dictionaries containing job information"""

    jobs = []

    # Split the email body by job entries
    # Look for patterns that indicate job separations
    job_sections = body.split("\n\n")[2:-4]

    for section in job_sections:
        if not section.strip():
            continue

        job_info = parse_indeed_job_section(section)
        if job_info:
            jobs.append(job_info)

    return jobs


def parse_indeed_job_section(section: str) -> JobResult | None:
    """Parse a single job section from an Indeed email and return JobResult model
    :param section: Job section as string
    :return: JobResult model or None if parsing fails"""

    lines = [line.strip() for line in section.strip().split("\n") if line.strip()]
    if len(lines) < 2:
        return None

    # Title
    title = lines[0]

    # Company & Location
    if " - " in lines[1]:
        company, location = [p.strip() for p in lines[1].split(" - ", 1)]
    else:
        company, location = lines[1], None

    # Salary
    salary_pattern = r"£([\d,]+(?:\.\d{2})?)\s*-\s*£([\d,]+(?:\.\d{2})?)\s*a\s*year"
    salary_min = None
    salary_max = None

    for line in lines:
        match = re.search(salary_pattern, line, re.IGNORECASE)
        if match:
            try:
                salary_min = float(match.group(1).replace(",", ""))
                salary_max = float(match.group(2).replace(",", ""))
            except ValueError:
                pass
            break

    # --- Description ---
    url = None
    description_lines = []

    for line in lines[2:]:  # skip first two lines (title, company/location)

        # Skip salary lines
        if re.search(salary_pattern, line, re.IGNORECASE):
            continue

        # Skip "just posted"/"3 days ago"
        elif re.search(r"(just posted|(\d+\s+(day|hour)s?\s+ago))", line, re.IGNORECASE):
            continue

        # URLs
        elif line.startswith("http"):
            url = line
            continue

        # Skip "Easily apply"
        elif re.search(r"easily apply|apply now", line, re.IGNORECASE):
            continue

        elif line:
            description_lines.append(line)

    description = " ".join(description_lines).strip()
    description = re.sub(r"\s+", " ", description)

    if not title:
        return None
    else:
        return JobResult(
            company=company or None,
            company_id=None,
            location=location or None,
            job=JobInfo(
                title=title,
                description=description,
                url=url,
                salary=Salary(
                    min_amount=salary_min,
                    max_amount=salary_max,
                    currency="GBP" if salary_min or salary_max else None,
                ),
            ),
            raw=section.strip(),
        )


# ------------------------------------------------- LINKEDIN SCRAPER -------------------------------------------------


class LinkedinBrightdataJobScraper(BrightdataJobScraper):
    """LinkedIn Scraper"""

    base_url = "https://www.linkedin.com/jobs/view/"
    name = "linkedin"
    poll_interval: int | float = 2
    max_attempts: int = 60

    def _process_job_data(self, job_data: dict) -> JobResult:
        """Process the job json data to extract relevant information
        :param job_data: job data json
        :return: dictionary containing job information"""

        min_amount = max_amount = None
        salary_currency = None
        base_salary = job_data.get("base_salary")
        if base_salary:
            currency = base_salary.get("currency")
            payment_period = base_salary.get("payment_period")

            # Only extract salary if it's yearly
            if payment_period and payment_period.lower() == "yr":
                min_amount = base_salary.get("min_amount")
                max_amount = base_salary.get("max_amount")
                salary_currency = currency

        return JobResult(
            company=job_data.get("company_name"),
            company_id=job_data.get("company_id"),
            location=job_data.get("job_location"),
            job=JobInfo(
                title=job_data.get("job_title"),
                description=job_data.get("job_summary", "").strip("Show more Show less") or None,
                url=job_data.get("url"),
                salary=Salary(
                    min_amount=min_amount,
                    max_amount=max_amount,
                    currency=salary_currency,
                ),
            ),
            raw=job_data,
        )


# ------------------------------------------------- VEGANJOBS SCRAPER -------------------------------------------------


class VeganJobsJobScraper:
    """Scraper for veganjobs.com job listings."""

    base_url = "https://veganjobs.com/job/"

    def __init__(self, url: str) -> None:
        """Initialize the scraper with headers and delay settings.
        :param url: The job listing URL"""

        self.scraper = cloudscraper.create_scraper()
        self.url = self.base_url + url

    def scrape_job_listing(self) -> JobResult:
        """Scrape job data from a specific veganjobs.com job listing URL"""

        response = self.scraper.get(self.url)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, "html.parser")

        # Defaults
        company = None
        title = None
        location = None

        # Title
        title_tag = soup.find("h2", class_="page-title")
        if title_tag:
            title = title_tag.get_text(strip=True)

        # Company
        company_tag = soup.find("div", class_="joblisting-meta-company-name")
        if company_tag:
            company = company_tag.get_text(strip=True)

        # Location
        location_tag = soup.find("li", class_="location")
        if location_tag:
            location = location_tag.get_text(strip=True)

        # Full text block
        container = soup.find("div", class_="job_listing-description")
        # noinspection PyArgumentList
        text_content = container.get_text(separator="\n", strip=True) if container else ""

        # Salary
        # salary_match = re.search(r"Salary:\s*(.+)", text_content)
        # salary_raw = salary_match.group(1).split("\n")[0] if salary_match else None

        # Description (remove salary)
        description = re.sub(r"Salary:.*", "", text_content, flags=re.DOTALL).strip()
        description = description.strip("Overwiew").strip()

        return JobResult(
            company=company,
            company_id=None,
            location=location,
            job=JobInfo(
                title=title,
                description=description,
                url=self.url,
                salary=Salary(
                    min_amount=None,
                    max_amount=None,
                    currency=None,
                ),
            ),
            raw=soup.text,
        )

    def scrape_job(self) -> JobResult:
        """Scrape a single job listing from the given URL."""

        for i in range(10):
            try:
                return self.scrape_job_listing()
            except:
                pass
        raise AssertionError()


# Usage example:
if __name__ == "__main__":
    # Note: These test job ids may not be valid any more.

    # # LinkedIn job scraper example
    # scraper = LinkedinBrightdataJobScraper(["4313361652"])
    # job_data1 = scraper.scrape_job()
    # print(job_data1[0])
    #
    # Indeed job scraper example
    scraper = IndeedBrightdataJobScraper("a6c3277c505f0629")
    job_data1 = scraper.scrape_job()
    print(job_data1)
    #
    # # # VeganJobs scraper example
    # scraper = VeganJobsJobScraper("sharpen-strategy-remote-usa-operations-coordinator")
    # veganjob_data = scraper.scrape_job()
    # print(veganjob_data)
