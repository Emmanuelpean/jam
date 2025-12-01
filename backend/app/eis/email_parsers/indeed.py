"""Indeed job alert email parser."""

import re

import cloudscraper
from bs4 import BeautifulSoup

from app.eis.email_parsers import process_salary, Platform
from app.eis.job_scrapers import Salary, JobInfo, JobResult

BASE_URL = "https://www.indeed.com/viewjob?jk="


def get_indeed_redirected_url(job_url: str, max_attempts: int = 100) -> str:
    """Get the redirected URL from the Indeed job URL
    :param job_url: Indeed job URL
    :param max_attempts: max number of attempts to get redirected
    :return: redirected URL"""

    iteration = 0
    url = job_url
    while "indeed.com/viewjob?jk" not in url:
        scraper = cloudscraper.create_scraper()
        response = scraper.get(job_url, allow_redirects=True)
        url = response.url
        iteration += 1
        if iteration > max_attempts:
            break
    return url


def parse_indeed_job_email(body: str) -> list[JobResult]:
    """Parse Indeed job alert email and extract job information.
    :param str body: path to the HTML file
    :return: list of dictionaries containing job information"""

    # Parse with BeautifulSoup
    soup = BeautifulSoup(body, "html.parser", from_encoding="utf-8")

    # Find all job sections (each job is in a td with class 'pb-24')
    job_sections = soup.find_all("td", {"class": "pb-24"})

    jobs = []

    for section in job_sections:
        # Initialise variables
        title = None
        url = None
        job_id = None
        company = None
        location = None
        salary_currency = None
        salary_min = None
        salary_max = None

        # Extract job title and URL
        title_h2 = section.find("h2")
        if title_h2:
            title_link = title_h2.find("a", class_="strong-text-link")
            if title_link:
                title = " ".join(title_link.get_text(strip=True).split())

                # URL
                url = title_link.get("href")

                # Job ID
                jobid_pattern = r"[?&]jk=([a-zA-Z0-9]+)"
                ad_match = re.search(jobid_pattern, url, re.IGNORECASE)
                if not ad_match:
                    redirected_url = get_indeed_redirected_url(url)
                else:
                    redirected_url = url

                matches = re.findall(jobid_pattern, redirected_url, re.IGNORECASE)
                if matches:
                    job_id = matches[0]

        # Company name
        company_table = section.find("table", {"role": "presentation"})
        if company_table:
            company_tds = company_table.find_all("td", style=lambda x: x and "padding:0 12px 0 0" in x)
            if company_tds:
                company = " ".join(company_tds[0].get_text(strip=True).split())

        # Location
        all_tds = section.find_all("td", {"align": "left", "valign": "top"})
        for td in all_tds:
            style = td.get("style", "")
            if "color:#2d2d2d;font-size:14px;line-height:21px" in style:
                text = td.get_text(strip=True)
                # Skip if it's the company (has rating sibling) or if it contains description text
                if len(text) < 50 and not td.find("table"):
                    # Check if this might be location by seeing if it comes after company info
                    location = text

        # Salary
        salary_table = section.find("table", {"bgcolor": "#f3f2f1"})
        if salary_table:
            salary_td = salary_table.find("td", style=lambda x: x and "padding:3px 8px 3px 8px" in x)
            if salary_td:
                salary_text = salary_td.get_text(strip=True)

                # Pattern for salaries like £39,906 - £42,254 a year
                match = re.search(r"([£$€])([\d,]+)\s*-\s*([£$€])([\d,]+)\s*a\s*(\w+)", salary_text)
                if match:
                    frequency = match.group(5)
                    if frequency == "year":
                        salary_currency = match.group(1)
                        salary_min = process_salary(match.group(2))
                        salary_max = process_salary(match.group(4))

                # Pattern for single salary like £40,000 a year
                match = re.search(r"([£$€])([\d,]+)\s*a\s*(\w+)", salary_text)
                if match:
                    frequency = match.group(3)
                    if frequency == "a year":
                        salary_currency = match.group(1)
                        salary_min = salary_max = process_salary(match.group(2))

        processed_url = BASE_URL + job_id
        salary = Salary(min_amount=salary_min, max_amount=salary_max, currency=salary_currency)
        job_info = JobInfo(title=title, url=processed_url, salary=salary, raw_url=url)
        job_result = JobResult(
            company=company, job_id=job_id, location=location, job=job_info, platform=Platform.INDEED
        )
        jobs.append(job_result)

    return jobs
