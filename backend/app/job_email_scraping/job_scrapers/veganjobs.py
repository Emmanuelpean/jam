"""veganjobs.com job scraper module"""

import re

import cloudscraper
from bs4 import BeautifulSoup

from app.job_email_scraping.schemas import Salary, JobInfo, JobResult


class VeganJobsJobScraper:
    """Scraper for veganjobs.com job listings."""

    base_url = "https://veganjobs.com/job/"

    def __init__(self, job_ids: str | list[str]) -> None:
        """Initialize the scraper with headers and delay settings.
        :param job_ids: The job ID(s)"""

        self.scraper = cloudscraper.create_scraper()
        self.job_ids = [job_ids] if isinstance(job_ids, str) else job_ids
        self.job_urls = [f"{self.base_url}{job_id}" for job_id in self.job_ids]

    def scrape_job_listing(self, job_url: str) -> JobResult:
        """Scrape job data from a specific veganjobs.com job listing URL
        :param job_url: The URL of the job listing to scrape"""

        response = self.scraper.get(job_url)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, "html.parser")

        # Defaults
        company = None
        title = None
        location = None

        # Title
        title_tag = soup.find("h2", class_="page-title")
        if title_tag:
            title = title_tag.get_text(strip=True)

        # Company
        company_tag = soup.find("div", class_="joblisting-meta-company-name")
        if company_tag:
            company = company_tag.get_text(strip=True)

        # Location
        location_tag = soup.find("li", class_="location")
        if location_tag:
            location = location_tag.get_text(strip=True)

        # Full text block
        container = soup.find("div", class_="job_listing-description")
        # noinspection PyArgumentList
        text_content = container.get_text(separator="\n", strip=True) if container else ""

        # Salary
        # salary_match = re.search(r"Salary:\s*(.+)", text_content)
        # salary_raw = salary_match.group(1).split("\n")[0] if salary_match else None

        # Description (remove salary)
        description = re.sub(r"Salary:.*", "", text_content, flags=re.DOTALL).strip()
        description = description.strip("Overwiew").strip()

        return JobResult(
            company=company,
            company_id=None,
            location=location,
            job=JobInfo(
                title=title,
                description=description,
                salary=Salary(
                    min_amount=None,
                    max_amount=None,
                    currency=None,
                ),
            ),
            raw=soup.text,
        )

    def scrape_job(self) -> list[JobResult]:
        """Scrape a single job listing from the given URL."""

        job_data = []
        for job_url in self.job_urls:
            for i in range(50):
                try:
                    job_data.append(self.scrape_job_listing(job_url))
                    break
                except:
                    pass
            else:
                raise AssertionError("Failed to scrape job listing after multiple attempts.")
        return job_data


if __name__ == "__main__":
    scraper = VeganJobsJobScraper("sharpen-strategy-remote-usa-operations-coordinator")
    veganjob_data = scraper.scrape_job()
    print(veganjob_data)
