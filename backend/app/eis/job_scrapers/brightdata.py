"""Brightdata Job Scraper Module

This module provides functionality to scrape job postings using the BrightData API."""

import time

import requests
from tqdm import tqdm

from app.config import settings
from app.eis.job_scrapers import JobResult


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
