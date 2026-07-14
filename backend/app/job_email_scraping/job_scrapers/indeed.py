"""Indeed Job Scrapers"""

import re

from app.job_email_scraping.job_scrapers.apify import ApifyJobScraper
from app.job_email_scraping.job_scrapers.brightdata import BrightdataJobScraper
from app.job_email_scraping.schemas import Salary, JobInfo, JobResult


class IndeedBrightdataJobScraper(BrightdataJobScraper):
    """LinkedIn Scraper"""

    base_url = "https://www.indeed.com/viewjob?jk="
    name = "indeed"
    dataset_id = "gd_l4dx9j9sscpvs7no2"
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
        if salary_range and (match := re.search(salary_pattern, str(salary_range))):
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
                is_closed=job_data.get("is_closed", False),
                salary=Salary(
                    min_amount=min_amount,
                    max_amount=max_amount,
                    currency=currency,
                ),
            ),
            raw=str(job_data),
        )


class IndeedApifyJobScraper(ApifyJobScraper):
    """Indeed Scraper using Apify"""

    base_url = "https://www.indeed.com/viewjob?jk="
    name = "indeed"
    actor_id = "memo23/apify-indeed-cheerio-ppr"
    poll_interval: int | float = 10
    max_attempts: int = 100

    def _process_job_data(self, job_data: dict) -> JobResult:
        """Process job data to extract relevant information
        :param job_data: Job data dictionary from Apify Indeed actor
        :return: JobResult containing job information"""

        # Extract job info from nested structure
        title = job_data["positionName"]
        location = job_data["fullAddress"] if job_data["fullAddress"] else job_data["location"]
        company = job_data["company"]
        description = job_data["jobDescription"]
        remote = job_data["remote"]
        is_closed = job_data["expired"]
        deadline = job_data["expirationDate"]
        min_salary = job_data["salaryMin"]
        max_salary = job_data["salaryMax"]
        currency = job_data["currency"]

        return JobResult(
            company=company,
            location=location + " (Remote)" if remote else location,
            job=JobInfo(
                title=title,
                description=description,
                deadline=deadline,
                is_closed=is_closed,
                salary=Salary(
                    min_amount=min_salary,
                    max_amount=max_salary,
                    currency=currency,
                ),
            ),
            raw=str(job_data),
        )


if __name__ == "__main__":
    # Indeed job scraper example with Brightdata
    scraper = IndeedBrightdataJobScraper("758f2768706ab970")
    data = scraper.scrape_job()
    print(data)

    # # Indeed job scraper example with Apify
    scraper = IndeedApifyJobScraper("758f2768706ab970")
    data = scraper.scrape_job()
    print(data)
