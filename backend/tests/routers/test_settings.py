"""Tests for the settings router."""

from app import schemas
from tests.conftest import CRUDTestBase
from tests.utils.test_data import SETTINGS_DATA


class TestSettingsCRUD(CRUDTestBase):
    endpoint = "/settings"
    admin_only = True
    create_schema = schemas.SettingCreate
    out_schema = schemas.SettingOut
    test_data_ref = "test_settings"
    create_data = SETTINGS_DATA
    update_data = {
        "id": 1,
        "name": "New setting name",
    }
