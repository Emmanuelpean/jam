"""Generic service-log endpoints, shared by every service"""

import datetime as dt

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from starlette import status

from app.core.oauth2 import get_current_user
from app.database import get_db
from app.models import User
from app.routers.utility import assert_admin
from app.service.models import ServiceLog
from app.service.registry import get_service_log_view

service_log_router = APIRouter(prefix="/service-logs", tags=["service-logs"])


def _resolve_service_log_view(service_name: str) -> tuple[type[ServiceLog], type[BaseModel]]:
    """Return the (model, schema) for a service name, or raise 404 if unknown.
    :param service_name: Service registry key.
    :return: The (service-log model, output schema) tuple."""

    try:
        return get_service_log_view(service_name)
    except KeyError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Unknown service '{service_name}'")


@service_log_router.get("/{service_name}/")
def list_service_logs(
    service_name: str,
    start_date: dt.datetime | None = Query(None, description="Start date for filtering (ISO format)"),
    end_date: dt.datetime | None = Query(None, description="End date for filtering (ISO format)"),
    delta_days: int | None = Query(None, description="Number of days to go back in time"),
    limit: int | None = Query(None, description="Maximum number of logs to return"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List a service's run logs within a date range, newest first. Admin only."""

    assert_admin(current_user)
    model, schema = _resolve_service_log_view(service_name)

    query = db.query(model).filter(model.run_duration.is_not(None))
    if start_date:
        query = query.filter(model.run_datetime >= start_date)
    if end_date:
        query = query.filter(model.run_datetime <= end_date)
    if delta_days:
        query = query.filter(model.run_datetime >= dt.datetime.now() - dt.timedelta(days=delta_days))

    query = query.order_by(model.run_datetime.desc())
    if limit:
        query = query.limit(limit)

    return [schema.model_validate(row, from_attributes=True) for row in query.all()]


@service_log_router.get("/{service_name}/latest")
def latest_service_log(
    service_name: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return a service's most recent run log. Admin only."""

    assert_admin(current_user)
    model, schema = _resolve_service_log_view(service_name)

    row = db.query(model).order_by(model.run_datetime.desc()).first()
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No service logs found")
    return schema.model_validate(row, from_attributes=True)
