"""Utility functions for email parsers"""

from enum import Enum

from bs4 import BeautifulSoup


def process_salary(salary_str: str) -> int | None:
    """Convert salary string with K/M suffix to numeric value.
    :param salary_str: Salary string with optional K/M suffix
    :return: Numeric salary value or None"""

    if not salary_str:
        return None

    # Remove any whitespace and commas
    salary_str = salary_str.strip().replace(",", "")

    # Check for K (thousands)
    if salary_str.endswith("K"):
        return int(float(salary_str[:-1]) * 1000)
    else:
        # Already a plain number
        try:
            return int(float(salary_str))
        except:
            return None


class Platform(str, Enum):
    """Platform Enum for job sources."""

    INDEED = "indeed"
    LINKEDIN = "linkedin"
    VEGANJOBS = "veganjobs"
    NHS = "nhs"


def remove_style_tags(body: str) -> str:
    """Remove <style> tags from HTML content.
    :param str body: HTML content
    :return: HTML content without <style> tags"""

    soup = BeautifulSoup(body, "html.parser", from_encoding="utf-8")
    for style in soup.find_all("style"):
        style.decompose()
    return str(soup)
