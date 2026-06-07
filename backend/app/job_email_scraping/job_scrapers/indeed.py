"""Indeed Job Scrapers"""

"""Indeed Job Scrapers"""

import re

from app.job_email_scraping.job_scrapers.apify import ApifyJobScraper
from app.job_email_scraping.job_scrapers.brightdata import BrightdataJobScraper
from app.job_email_scraping.schemas import Salary, JobInfo, JobResult


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
        title = job_data["jobInfoModel"]["jobInfoHeaderModel"]["jobTitle"]
        location = job_data["jobInfoModel"]["location"]["fullAddress"]
        company = job_data["jobInfoModel"]["jobInfoHeaderModel"]["companyName"]
        description = job_data["jobInfoModel"]["description"]["text"]

        return JobResult(
            company=company,
            location=location,
            job=JobInfo(
                title=title,
                description=description,
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
