"""Module for monitoring external services"""

from fastapi import APIRouter
from app.utilities.logger import AppLogger

external_service_monitoring_history_router = APIRouter(
    prefix="/external-service-monitoring-history", tags=["external-service-monitoring-history"]
)
