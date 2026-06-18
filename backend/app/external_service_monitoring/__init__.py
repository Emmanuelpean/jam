from fastapi import APIRouter

external_service_monitoring_history_router = APIRouter(
    prefix="/external-service-monitoring-history", tags=["external-service-monitoring-history"]
)
