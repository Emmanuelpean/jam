"""Routers for the core module."""

from app.core.routers.auth import login_router, register_router, password_router
from app.core.routers.settings import settings_router
from app.core.routers.user import user_router, current_user_router, user_qualification_router
