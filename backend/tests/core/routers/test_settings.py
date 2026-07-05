"""Tests for the settings router."""

import uuid

from sqlalchemy.orm import Session

from app import models
from app.core import schemas
from tests.conftest import CRUDTestBase
from tests.fixtures.users import FixtureUser


class TestSettingsCRUD(CRUDTestBase[models.Setting]):
    endpoint = "/settings"
    admin_only = True
    create_schema = schemas.SettingCreate
    out_schema = schemas.SettingOut
    update_data = {"name": "New setting name"}

    def create_entry(self, session: Session, owner: FixtureUser, **overrides) -> models.Setting:
        overrides.setdefault("name", f"setting_{uuid.uuid4()}")
        overrides.setdefault("value", "some value")
        return self.create_setting(session, **overrides)

    def create_payload(self, session: Session, owner: FixtureUser) -> dict:
        return {"name": f"setting_{uuid.uuid4()}", "value": "some value"}
