"""Start / stop / status / log endpoints for the external service-monitoring runner."""

import datetime as dt

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app import models
from app.core.oauth2 import get_current_user
from app.database import get_db
from app.external_service_monitoring.service.schemas import ServiceMonitoringServiceLogOut
from app.external_service_monitoring.service.sync import EsmService, esm_service_runner
from app.service_runner import routers

esm_service_router = APIRouter(
    prefix="/external-service-monitoring-service",
    tags=["external-service-monitoring-service"],
)


@esm_service_router.post("/start")
def start(
    current_user: models.User = Depends(get_current_user),
) -> dict:
    """Start the service-monitoring runner. Admin only."""

    return routers.start_scraper(esm_service_runner, current_user, 24)


@esm_service_router.post("/stop")
def stop(
    current_user: models.User = Depends(get_current_user),
) -> dict:
    """Stop the service-monitoring runner. Admin only."""

    return routers.stop_scraper(esm_service_runner, current_user)


@esm_service_router.get("/status")
def status(
    current_user: models.User = Depends(get_current_user),
) -> dict:
    """Get the current runner status. Admin only."""

    return routers.scraper_status(esm_service_runner, current_user)


@esm_service_router.get("/logs")
def get_logs(
    lines: int = Query(100, ge=1, le=10000),
    current_user: models.User = Depends(get_current_user),
):
    """Get the last N lines of the runner log file. Admin only."""

    return routers.get_service_logs(EsmService.service_name, lines, current_user)


esm_service_log_router = APIRouter(
    prefix="/external-service-monitoring-service-logs",
    tags=["external-service-monitoring-service-logs"],
)


@esm_service_log_router.get("/", response_model=list[ServiceMonitoringServiceLogOut])
def get_service_logs_by_date_range(
    start_date: dt.datetime | None = Query(None, description="Start date for filtering (ISO format)"),
    end_date: dt.datetime | None = Query(None, description="End date for filtering (ISO format)"),
    delta_days: int | None = Query(None, description="Number of days to go back in time"),
    limit: int | None = Query(None, description="Maximum number of logs to return"),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List service log entries within a date range, newest first. Admin only."""

    return routers.get_service_logs_by_date_range(
        start_date,
        end_date,
        delta_days,
        limit,
        current_user,
        db,
        models.ExternalServiceMonitoringServiceLog,
    )


@esm_service_log_router.get("/latest", response_model=ServiceMonitoringServiceLogOut)
def get_latest(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get the most recent service log entry. Admin only."""

    return routers.get_latest(current_user, db, models.ExternalServiceMonitoringServiceLog)
