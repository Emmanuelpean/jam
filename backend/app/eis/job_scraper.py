"""
LinkedIn Job Scraper Module

This module provides functionality to scrape LinkedIn job postings using the BrightData API.
It offers a complete workflow to trigger data collection, monitor processing status, and
retrieve scraped job information.
"""

import json
import os
import re
import time

import requests
from tqdm import tqdm


class JobScrapper(object):
    """Job Scraper"""

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
        self.secrets_file = os.path.join(os.path.dirname(__file__), "eis_secrets.json")
        self.poll_interval = self.poll_interval
        self.max_attempts *= len(self.job_ids)

        # Load credentials from the secrets file
        credentials = self._load_credentials()
        self.api_key = credentials["api_key"]
        self.dataset_id = credentials[f"{self.name}_dataset_id"]

    def _load_credentials(self) -> dict:
        """Load BrightData credentials from the secrets file"""

        if not os.path.exists(self.secrets_file):
            raise FileNotFoundError(
                f"Secrets file '{self.secrets_file}' not found. "
                "Please create it with your BrightData API credentials."
            )

        try:
            with open(self.secrets_file, "r") as f:
                secrets = json.load(f)
                return secrets["brightdata"]
        except (json.JSONDecodeError, KeyError) as e:
            raise ValueError(f"Invalid secrets file format or missing 'brightdata' section: {e}")

    def get_snapshot(self) -> str:
        """Get the snapshot id"""

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        # Step 1: Trigger the job and get snapshot_id
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

    def wait_for_data(self, snapshot_id: str) -> None:
        """Wait for the job data associated with a specific snapshot id to be ready
        :param snapshot_id: Snapshot ID"""

        # Step 2: Poll for status
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

    def retrieve_data(self, snapshot_id: str) -> list[dict]:
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
        if data_resp.status_code != 200:
            raise Exception(f"Failed to get snapshot data: {data_resp.status_code} {data_resp.text}")
        return data_resp.json()

    def process_job_data(self, job_data: dict) -> dict:
        """Process job data to extract relevant information
        :param job_data: Job data dictionary
        :return: Dictionary containing job information"""

        pass

    def scrape_job(self) -> list[dict]:
        """Complete workflow to scrape a LinkedIn job"""

        snapshot_id = self.get_snapshot()
        self.wait_for_data(snapshot_id)
        data = self.retrieve_data(snapshot_id)
        return [self.process_job_data(d) for d in data]


class IndeedJobScrapper(JobScrapper):
    """LinkedIn Scraper"""

    base_url = "https://www.indeed.com/viewjob?jk="
    name = "indeed"
    poll_interval: int | float = 10
    max_attempts: int = 100

    def process_job_data(self, job_data: dict) -> dict:
        """Process job data to extract relevant information
        :param job_data: Job data dictionary
        :return: Dictionary containing job information"""

        results = dict()
        results["company"] = job_data.get("company_name")
        results["company_id"] = job_data.get("company_url")
        results["location"] = job_data.get("location")
        results["job"] = dict()
        results["job"]["title"] = job_data.get("job_title")
        results["job"]["description"] = job_data.get("description_text").strip("Show more Show less")
        results["job"]["url"] = job_data.get("url")
        results["raw"] = job_data
        results["job"]["salary"] = dict(min_amount=None, max_amount=None)
        if salary_range := job_data.get("salary_formatted"):
            pattern = r"£(\d+(?:,\d+)?(?:k|K)?(?:\.\d+)?)\s*[-–]\s*£(\d+(?:,\d+)?(?:k|K)?(?:\.\d+)?)\s+(?:a|per)\s+(?:year|annum)"
            if match := re.search(pattern, salary_range):
                min_amount = float(match.group(1).replace(",", ""))
                max_amount = float(match.group(2).replace(",", ""))
                results["job"]["salary"]["min_amount"] = min_amount
                results["job"]["salary"]["max_amount"] = max_amount

        return results


class LinkedinJobScraper(JobScrapper):
    """LinkedIn Scraper"""

    base_url = "https://www.linkedin.com/jobs/view/"
    name = "linkedin"
    poll_interval: int | float = 2
    max_attempts: int = 60

    def process_job_data(self, job_data: dict) -> dict:
        """Process job data to extract relevant information
        :param job_data: Job data dictionary
        :return: Dictionary containing job information"""

        results = dict()
        results["company"] = job_data.get("company_name")
        results["company_id"] = job_data.get("company_id")
        results["location"] = job_data.get("job_location")
        results["job"] = dict()
        results["job"]["title"] = job_data.get("job_title")
        results["job"]["description"] = job_data.get("job_summary").strip("Show more Show less")
        results["job"]["url"] = job_data.get("url")
        results["job"]["salary"] = dict(min_amount=None, max_amount=None)
        results["raw"] = job_data
        base_salary = job_data.get("base_salary", {}) or {}
        currency = base_salary.get("currency") or ""
        payment_period = base_salary.get("payment_period") or ""

        if currency.lower() in ("£", "gbp") and payment_period.lower() == "yr":
            results["job"]["salary"]["min_amount"] = base_salary.get("min_amount")
            results["job"]["salary"]["max_amount"] = base_salary.get("max_amount")

        return results


def extract_indeed_jobs_from_email(body: str) -> list[dict[str, str | dict]]:
    """Extract job information directly from an Indeed email body
    :param body: Email body content as string
    :return: List of dictionaries containing job information"""

    jobs = []

    # Split the email body by job entries
    # Look for patterns that indicate job separations
    job_sections = re.split(
        r"\n\n(?=[A-Z][^:\n]*\n[A-Z][^:\n]*(?:\s*-\s*[A-Za-z]+)?(?:\s*£[\d,]+ - £[\d,]+ a year)?)", body
    )

    for section in job_sections:
        if not section.strip():
            continue

        job_info = parse_indeed_job_section(section)
        if job_info:
            jobs.append(job_info)

    return jobs[2:-1]


def parse_indeed_job_section(section: str) -> dict[str, str] | None:
    """Parse a single job section from Indeed email
    :param section: Job section text
    :return: Dictionary with job information or None if parsing fails"""

    lines = [line.strip() for line in section.strip().split("\n") if line.strip()]

    if len(lines) < 2:
        return None

    # Initialize job info with flat structure first
    job_info = {
        "title": lines[0],
        "company": "",
        "location": "",
        "salary": "",
        "description": "",
        "url": "",
    }

    # First line is typically the job title
    # Second line is typically company - location or just company
    if len(lines) > 1:
        company_location_line = lines[1]

        # Try to split company and location
        # Pattern: "Company Name - Location"
        if " - " in company_location_line:
            parts = company_location_line.split(" - ", 1)
            job_info["company"] = parts[0].strip()
            job_info["location"] = parts[1].strip()
        else:
            job_info["company"] = company_location_line.strip()

    # Look for salary information
    salary_pattern = r"£([\d,]+(?:\.\d{2})?)\s*-\s*£([\d,]+(?:\.\d{2})?)\s*a\s*year"
    salary_min = None
    salary_max = None

    for line in lines:
        salary_match = re.search(salary_pattern, line, re.IGNORECASE)
        if salary_match:
            job_info["salary"] = f"£{salary_match.group(1)} - £{salary_match.group(2)} a year"
            # Parse numeric values for min/max
            try:
                salary_min = float(salary_match.group(1).replace(",", ""))
                salary_max = float(salary_match.group(2).replace(",", ""))
            except ValueError:
                pass
            break

    # Look for job description (usually starts after company/location and salary)
    description_lines = []
    found_description_start = False

    for i, line in enumerate(lines[2:], 2):  # Start from third line
        # Skip salary lines
        if re.search(salary_pattern, line, re.IGNORECASE):
            continue
        # Skip time indicators
        if re.search(r"(just posted|(\d+\s+(day|hour)s?\s+ago))", line, re.IGNORECASE):
            continue
        # Skip URLs
        if line.startswith("http"):
            job_info["url"] = line
            continue
        # Skip "Easily apply" type lines
        if re.search(r"easily apply|apply now", line, re.IGNORECASE):
            continue

        # This should be description content
        if line and not found_description_start:
            found_description_start = True

        if found_description_start:
            description_lines.append(line)

    job_info["description"] = " ".join(description_lines).strip()

    # Clean up description - remove common email artifacts
    job_info["description"] = re.sub(r"\s+", " ", job_info["description"])
    job_info["description"] = (
        job_info["description"][:500] + "..." if len(job_info["description"]) > 500 else job_info["description"]
    )

    # Try to find URL if not already found
    if not job_info["url"]:
        url_matches = re.findall(r"https?://(?:uk\.)?indeed\.com/(?:pagead|rc)/clk/dl\?[^>\s]+", section, re.IGNORECASE)
        if url_matches:
            job_info["url"] = url_matches[0]

    # Only return if we have at least title and company
    if not job_info["title"]:
        return None

    # Transform to match the structure of other scraper functions
    results = {
        "company": job_info["company"],
        "location": job_info["location"],
        "job": {
            "title": job_info["title"],
            "description": job_info["description"],
            "url": job_info["url"],
            "salary": {"min_amount": salary_min, "max_amount": salary_max},
        },
        "raw": section,
    }

    return results


# Usage example:
if __name__ == "__main__":
    # scraper = LinkedinJobScraper(["4280160167"])
    # job_data1 = scraper.scrape_job()
    # print(job_data1)

    scraper = IndeedJobScrapper("7b9119575c72cb5c")
    job_data1 = scraper.scrape_job()
    print(job_data1)
