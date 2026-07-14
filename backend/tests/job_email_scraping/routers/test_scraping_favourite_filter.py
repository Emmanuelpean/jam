"""Tests for Scraping Favourite Filter router."""

import uuid

from sqlalchemy.orm import Session

from app import models
from app.job_email_scraping import schemas
from tests.conftest import CRUDTestBase
from tests.fixtures.users import FixtureUser


class TestScrapingFavouriteFilters(CRUDTestBase[models.ScrapingFavouriteFilter]):
    endpoint = "/scraping-favourite-filters"
    out_schema = schemas.ScrapingFavouriteFilterOut
    update_data = {"type": "title"}

    def create_entry(self, session: Session, owner: FixtureUser, **overrides) -> models.ScrapingFavouriteFilter:
        overrides.setdefault("value", f"kw-{uuid.uuid4()}")
        return owner.create_scraping_favourite_filter(**overrides)

    def create_payload(self, session: Session, owner: FixtureUser) -> dict:
        return {"type": "title", "operator": "contains", "value": f"kw-{uuid.uuid4()}"}
