"""Tests for Scraping Favourite Filter router."""

from app.job_email_scraping import schemas
from tests.conftest import CRUDTestBase
from tests.utils.test_data.job_scraping import SCRAPING_FAVOURITE_FILTER_DATA


class TestScrapingFavouriteFilters(CRUDTestBase):
    endpoint = "/scraping-favourite-filters"
    out_schema = schemas.ScrapingFavouriteFilterOut
    test_data_ref = "test_scraping_favourite_filters"
    create_data = SCRAPING_FAVOURITE_FILTER_DATA
    update_data = {
        "id": 1,
        "type": "title",
    }
