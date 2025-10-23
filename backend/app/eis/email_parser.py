import re

import cloudscraper


def pattern_extract(body: str, pattern: str) -> list[str]:
    """Extract job ids from a job body and return a list of job ids.
    :param str body: job body
    :param str pattern: job ids pattern"""

    job_ids = re.findall(pattern, body, re.IGNORECASE)
    return list(dict.fromkeys(job_ids))


def extract_veganjobs_job_ids(body: str) -> list[str]:
    """Extract VeganJobs job IDs from the email body
    :param body: email body content as string
    :return: list of unique VeganJobs job IDs"""

    pattern = r"https://(?:www\.)?veganjobs\.com/job/([^/\s]+)/?"
    return pattern_extract(body, pattern)


def extract_linkedin_job_ids(body: str) -> list[str]:
    """Extract LinkedIn job IDs from the email body
    :param body: email body content as string
    :return: list of unique LinkedIn job IDs"""

    pattern = r"linkedin\.com/(?:comm/)?jobs/view/(\d+)"
    return pattern_extract(body, pattern)


def get_indeed_redirected_url(job_url: str, max_attempts: int = 100) -> str:
    """Get the redirected URL from the Indeed job URL
    :param job_url: Indeed job URL
    :param max_attempts: max number of attempts to get redirected
    :return: redirected URL"""

    print("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA")
    print("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA")
    print("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA")
    print("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA")
    print("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA")

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


def extract_indeed_job_ids(body: str) -> list[str]:
    """Extract Indeed job advertisement IDs from email body URLs
    :param body: Email body content as string
    :return: List of unique Indeed job IDs"""

    pattern = r"https?://(?:uk\.)?indeed\.com/(?:pagead|rc)/clk/dl\?[^>\s]+"
    job_urls = pattern_extract(body, pattern)
    job_ids = []

    for url in job_urls:
        # Try to extract 'ad' parameter first (for pagead URLs)
        ad_match = re.search(r"[?&]mo=([^&>\s]+)", url, re.IGNORECASE)
        if ad_match:
            url = get_indeed_redirected_url(url)

        # Try to extract 'jk' parameter (for rc URLs)
        jk_match = re.search(r"[?&]jk=([^&>\s]+)", url, re.IGNORECASE)
        if jk_match:
            job_ids.append(jk_match.group(1))

    return list(dict.fromkeys(job_ids))
