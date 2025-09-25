from app import schemas
from conftest import CRUDTestBase
from tests.utils.table_data import SETTINGS_DATA


# ---------------------------------------------------- SIMPLE TABLES ---------------------------------------------------


class TestSettingsCRUD(CRUDTestBase):
    endpoint = "/settings"
    admin_only = True
    create_schema = schemas.SettingCreate
    out_schema = schemas.SettingOut
    test_data = "test_settings"
    create_data = SETTINGS_DATA
    update_data = {
        "id": 1,
        "name": "New setting name",
    }
