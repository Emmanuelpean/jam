"""NHS job scraper module"""

import datetime as dt
import re

from app.job_email_scraping.job_scrapers.apify import ApifyJobScraper
from app.job_email_scraping.schemas import Salary, JobInfo, JobResult


class NhsJobScraper(ApifyJobScraper):
    """Scraper for NHS job listings."""

    base_url = "https://beta.jobs.nhs.uk/candidate/jobadvert/"
    name = "nhs"
    actor_id = "memo23/nhs-scraper"

    def _process_job_data(self, job_data: dict) -> JobResult:
        """Process job data to extract relevant information
        :param job_data: Job data dictionary
        :return: JobResult containing job information"""

        # Deadline
        deadline = None
        is_closed = False
        if job_data.get("closingDate", "").upper() == "THIS JOB IS NOW CLOSED":
            is_closed = True
        else:
            try:
                deadline = dt.datetime.strptime(job_data.get("closingDate"), "%d %B %Y")
            except:
                pass

        # Salary
        pattern = r"(?P<currency>£)\s*(?P<min>[\d,]+)\s*to\s*(?P=currency)\s*(?P<max>[\d,]+).*?(?P<frequency>a year|per annum)"
        match = re.search(pattern, job_data.get("salary") or "", re.IGNORECASE)

        min_salary = max_salary = None
        currency = None
        if match:
            frequency = match.group("frequency").lower()
            if "year" in frequency or "annum" in frequency:
                currency = match.group("currency")
                min_salary = int(match.group("min").replace(",", ""))
                max_salary = int(match.group("max").replace(",", ""))

        # Description
        description = [job_data.get("jobSummaryText"), job_data.get("mainDutiesText"), job_data.get("aboutUsText")]
        description = "\n\n".join([d for d in description if d])

        # Raise an exception if planned downtime
        if (
            job_data.get("title") == "NHS Jobs: Planned downtime"
            or job_data.get("title") == "Sorry, there is a problem with the service"
        ):
            raise Exception(job_data.get("title"))

        return JobResult(
            company=job_data.get("employer") or None,
            location=" ".join(job_data.get("employerAddress", "")) or None,
            job=JobInfo(
                title=job_data.get("title") or None,
                description=description or None,
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
    scraper = NhsJobScraper("H9001-26-0286")
    nhsjob_data = scraper.scrape_job()
    print(nhsjob_data)
