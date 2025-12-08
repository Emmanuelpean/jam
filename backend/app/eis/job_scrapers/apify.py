"""Apify Job Scraper Module

This module provides functionality to scrape job postings using the Apify API."""

import time

from apify_client import ApifyClient
from tqdm import tqdm

from app.config import settings
from app.eis.job_scrapers import JobResult


class ApifyJobScraper(object):
    """Job Scraper
    :ivar base_url: Base URL for the job platform
    :ivar name: Name of the job platform
    :ivar poll_interval: Time interval (in seconds) between polling attempts
    :ivar max_attempts: Maximum number of polling attempts
    :ivar actor_id: Apify actor ID to use for scraping"""

    base_url: str = ""
    name: str = ""
    poll_interval: int | float = 2
    max_attempts: int = 60
    actor_id: str = ""

    def __init__(self, job_ids: str | list[str]) -> None:
        """Object constructor
        :param job_ids: List of job IDs to scrape"""

        self.job_ids = [job_ids] if isinstance(job_ids, str) else job_ids
        self.job_urls = [f"{self.base_url}{job_id}" for job_id in self.job_ids]
        self.poll_interval = self.poll_interval
        self.max_attempts *= len(self.job_ids)

        # Load credentials from the secrets file
        self.api_key = settings.apify_api_key
        self.client = ApifyClient(self.api_key)

    def _start_actor_run(self) -> dict:
        """Start the Apify actor run
        :return: Actor run information"""

        run_input = {
            "startUrls": [{"url": job_url} for job_url in self.job_urls],
            "proxy": {"useApifyProxy": True, "apifyProxyGroups": ["RESIDENTIAL"]},
        }
        run = self.client.actor(self.actor_id).start(run_input=run_input)
        return run

    def _wait_for_data(self, run_id: str) -> None:
        """Wait for the actor run to complete
        :param run_id: Actor run ID"""

        # Create progress bar for polling attempts
        with tqdm(total=self.max_attempts, desc="Waiting for data", unit="attempt") as pbar:
            for attempt in range(self.max_attempts):
                run_info = self.client.run(run_id).get()
                status = run_info.get("status")

                # Update progress bar description with current status
                pbar.set_description(f"Status: {status}")

                if status == "SUCCEEDED":
                    pbar.update(self.max_attempts - attempt)  # Complete the bar
                    break
                elif status in ("FAILED", "ABORTED", "TIMED-OUT"):
                    raise Exception(f"Actor run {status.lower()}: {run_info}")

                pbar.update(1)
                time.sleep(self.poll_interval)
            else:
                raise TimeoutError("Actor run not complete after maximum attempts.")

    def _retrieve_data(self, dataset_id: str) -> list[dict]:
        """Retrieve the job data from the dataset
        :param dataset_id: Dataset ID
        :return: List of job data dictionaries"""

        items = self.client.dataset(dataset_id).list_items().items
        if not items:
            raise Exception("No data returned from actor run")
        return items

    def _process_job_data(self, job_data: dict) -> JobResult:
        """Process job data to extract relevant information
        :param job_data: Job data dictionary
        :return: Dictionary containing job information"""

        raise AssertionError("This method should be implemented in subclasses.")

    def scrape_job(self) -> list[JobResult]:
        """Complete workflow to scrape jobs using Apify"""

        run = self._start_actor_run()
        run_id = run.get("id")
        dataset_id = run.get("defaultDatasetId")

        if not run_id:
            raise Exception(f"No run_id returned: {run}")
        if not dataset_id:
            raise Exception(f"No defaultDatasetId returned: {run}")

        self._wait_for_data(run_id)
        data = self._retrieve_data(dataset_id)
        return [self._process_job_data(d) for d in data]
