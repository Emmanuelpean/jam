"""Job scraper module"""

from app.job_email_scraping.email_parsers.utils import Platform
from app.job_email_scraping.job_scrapers.indeed import IndeedApifyJobScraper
from app.job_email_scraping.job_scrapers.linkedin import LinkedinBrightdataJobScraper
from app.job_email_scraping.job_scrapers.nhs import NhsApifyJobScraper
from app.job_email_scraping.job_scrapers.veganjobs import VeganJobsJobScraper

SCRAPERS = {
    Platform.LINKEDIN: LinkedinBrightdataJobScraper,
    Platform.NHS: NhsApifyJobScraper,
    Platform.INDEED: IndeedApifyJobScraper,
    Platform.VEGANJOBS: VeganJobsJobScraper,
}
