"""
LinkedIn Job Scraper Module

This module provides functionality to scrape LinkedIn job postings using the BrightData API.
It offers a complete workflow to trigger data collection, monitor processing status, and
retrieve scraped job information.
"""

import json
import os
import time

import requests


class JobScrapper(object):
    """LinkedIn Scraper"""

    base_url = ""
    name: str = ""

    def __init__(
        self,
        job_ids: str | list[str],
        poll_interval: int | float = 2,
        max_attempts: int = 60,
    ) -> None:

        self.job_ids = [job_ids] if isinstance(job_ids, str) else job_ids
        self.job_urls = [f"{self.base_url}{job_id}" for job_id in self.job_ids]
        self.secrets_file = os.path.join(os.path.dirname(__file__), "eis_secrets.json")
        self.poll_interval = poll_interval
        self.max_attempts = max_attempts * len(self.job_ids)

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
        """Wait for the job data associated with a specific snapshot id to be ready"""

        # Step 2: Poll for status
        progress_url = f"https://api.brightdata.com/datasets/v3/progress/{snapshot_id}"
        headers = {"Authorization": f"Bearer {self.api_key}"}

        for attempt in range(self.max_attempts):
            progress_resp = requests.get(progress_url, headers=headers)
            if progress_resp.status_code != 200:
                raise Exception(f"Failed to get snapshot status: {progress_resp.status_code} {progress_resp.text}")

            status = progress_resp.json().get("status")
            if status.lower() == "ready":
                break
            elif status.lower() == "failed":
                raise Exception("Snapshot processing failed.")

            print(f"Attempt {attempt + 1}/{self.max_attempts}: Status is '{status}', waiting...")
            time.sleep(self.poll_interval)
        else:
            raise TimeoutError("Snapshot data not ready after maximum attempts.")

    def retrieve_data(self, snapshot_id: str) -> dict:
        """Retrieve the job data associated with the snapshot id"""

        snapshot_url = f"https://api.brightdata.com/datasets/v3/snapshot/{snapshot_id}"
        params = {"format": "json"}
        headers = {"Authorization": f"Bearer {self.api_key}"}

        data_resp = requests.get(snapshot_url, headers=headers, params=params)
        if data_resp.status_code != 200:
            raise Exception(f"Failed to get snapshot data: {data_resp.status_code} {data_resp.text}")
        return data_resp.json()

    def scrape_job(self) -> dict:
        """Complete workflow to scrape a LinkedIn job"""
        print(f"Starting to scrape job: {self.job_ids}")

        # Get snapshot
        snapshot_id = self.get_snapshot()
        print(f"Snapshot created: {snapshot_id}")

        # Wait for data to be ready
        self.wait_for_data(snapshot_id)
        print("Data is ready!")

        # Retrieve the data
        data = self.retrieve_data(snapshot_id)
        print("Data retrieved successfully!")

        return data


class IndeedScrapper(JobScrapper):
    """LinkedIn Scraper"""

    base_url = "https://www.indeed.com/viewjob?jk="
    name = "indeed"


class LinkedinJobScraper(JobScrapper):
    base_url = "https://www.linkedin.com/jobs/view/"
    name = "linkedin"


# Usage example:
if __name__ == "__main__":
    # Now the API key and dataset_id are loaded from secrets.json
    # scraper = LinkedinJobScraper(["4270743052"])
    # job_data = scraper.scrape_job()
    # print(job_data)
    #
    scraper = IndeedScrapper("ea2a9f9f1e8a0899", 10, 100)
    job_data = scraper.scrape_job()
    print(job_data)
