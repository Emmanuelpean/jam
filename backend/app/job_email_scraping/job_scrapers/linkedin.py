"""LinkedIn Job Scraper using Brightdata"""

from app.job_email_scraping.job_scrapers import JobResult, JobInfo, Salary
from app.job_email_scraping.job_scrapers.brightdata import BrightdataJobScraper


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
            raw=str(job_data),
        )


if __name__ == "__main__":
    scraper = LinkedinBrightdataJobScraper(["4313361652"])
    job_data1 = scraper.scrape_job()
    print(job_data1[0])
