from app import models, schemas
from app.routers import generate_data_table_crud_router

# Settings router
settings_router = generate_data_table_crud_router(
    table_model=models.Setting,
    create_schema=schemas.SettingCreate,
    update_schema=schemas.SettingUpdate,
    out_schema=schemas.SettingOut,
    endpoint="settings",
    not_found_msg="Setting not found",
    admin_only=True,
)
