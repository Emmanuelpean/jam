"""NHS job scraper module"""

import datetime as dt
import re

from apify_client import ApifyClient

from app.config import settings
from app.job_email_scraping.schemas import Salary, JobInfo, JobResult


class NhsJobScraper:
    """Scraper for NHS job listings."""

    base_url = "https://beta.jobs.nhs.uk/candidate/jobadvert/"

    def __init__(self, job_ids: str | list[str]) -> None:
        """Initialize the scraper with headers and delay settings.
        :param job_ids: The job listing ID(s)"""

        self.job_ids = [job_ids] if isinstance(job_ids, str) else job_ids
        self.job_urls = [f"{self.base_url}{job_id}" for job_id in self.job_ids]

    def scrape_job(self) -> list[JobResult]:
        """Scrape job data from a specific NHS job listing URL"""

        client = ApifyClient(settings.apify_api_key)

        run_input = {
            "proxy": {
                "useApifyProxy": True,
                "apifyProxyGroups": ["RESIDENTIAL"],
            },
            "startUrls": self.job_urls,
        }

        actor_id = "memo23/nhs-scraper"

        run = client.actor(actor_id).call(run_input=run_input)
        job_data = client.dataset(run["defaultDatasetId"]).list_items().items
        if not job_data:
            raise Exception("No job data found.")

        processed_job_data = []
        for job in job_data:

            # Deadline
            try:
                deadline = dt.datetime.strptime(job.get("closingDate"), "%d %B %Y")
            except:
                deadline = None

            # Salary
            pattern = r"(?P<currency>£)\s*(?P<min>[\d,]+)\s*to\s*(?P=currency)\s*(?P<max>[\d,]+).*?(?P<frequency>a year|per annum)"
            match = re.search(pattern, job.get("salary") or "", re.IGNORECASE)

            min_salary = max_salary = None
            currency = None
            if match:
                frequency = match.group("frequency").lower()
                if "year" in frequency or "annum" in frequency:
                    currency = match.group("currency")
                    min_salary = int(match.group("min").replace(",", ""))
                    max_salary = int(match.group("max").replace(",", ""))

            # Description
            description = [job.get("jobSummaryText"), job.get("mainDutiesText"), job.get("aboutUsText")]
            description = "\n\n".join([d for d in description if d])

            # Raise an exception if planned downtime
            if (
                job.get("title") == "NHS Jobs: Planned downtime"
                or job.get("title") == "Sorry, there is a problem with the service"
            ):
                raise Exception(job.get("title"))

            processed_job_data.append(
                JobResult(
                    company=job.get("employer") or None,
                    location=" ".join(job.get("employerAddress", "")) or None,
                    job=JobInfo(
                        title=job.get("title") or None,
                        description=description or None,
                        deadline=deadline,
                        salary=Salary(
                            min_amount=min_salary,
                            max_amount=max_salary,
                            currency=currency,
                        ),
                    ),
                    raw=str(job),
                )
            )

        return processed_job_data


if __name__ == "__main__":
    scraper = NhsJobScraper("M9043-25-0282")
    nhsjob_data = scraper.scrape_job()
    print(nhsjob_data)
