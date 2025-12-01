"""Indeed Job Scraper using Brightdata"""

import re

from app.eis.job_scrapers import JobResult, JobInfo, Salary
from app.eis.job_scrapers.brightdata import BrightdataJobScraper


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
            raw=str(job_data),
        )


if __name__ == "__main__":
    # Indeed job scraper example
    scraper = IndeedBrightdataJobScraper("a6c3277c505f0629")
    job_data1 = scraper.scrape_job()
    print(job_data1)
