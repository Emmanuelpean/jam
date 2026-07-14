"""Module for monitoring external services"""

from fastapi import APIRouter
from app.utilities.logger import AppLogger

provider_monitoring_history_router = APIRouter(
    prefix="/provider-monitoring-history", tags=["provider-monitoring-history"]
)
