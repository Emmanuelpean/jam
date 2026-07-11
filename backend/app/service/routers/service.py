"""Admin endpoints for configuring scheduled services."""

import datetime as dt

from fastapi import APIRouter, Depends, Query
from fastapi import HTTPException
from sqlalchemy.orm import Session
from starlette import status

from app.core.oauth2 import get_current_user
from app.database import get_db
from app.models import Service
from app.models import User
from app.routers.utility import assert_admin
from app.service.registry import SERVICE_REGISTRY
from app.service.schemas import ServiceOut, ServiceUpdate
from app.utilities.logger import AppLogger

service_router = APIRouter(prefix="/services", tags=["services"])


def _get_service_by_name(db: Session, name: str) -> Service:
    """Fetch a service by name.
    :param db: Database session.
    :param name: Service registry key.
    :return: The matching Service row."""

    service = db.query(Service).filter(Service.name == name).first()
    if service is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Service '{name}' not found")
    return service


@service_router.get("/", response_model=list[ServiceOut])
def list_services(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all scheduled services. Admin only."""

    assert_admin(current_user)
    return db.query(Service).order_by(Service.display_name).all()


@service_router.patch("/{name}", response_model=ServiceOut)
def update_service(
    name: str,
    service_update: ServiceUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update a service's configuration (enable/disable, period, parameters). Admin only.
    Enabling a service that has no scheduled run seeds next_run_at to now so it runs on the
    scheduler's next poll (a past next_run_at is already due, so it is left untouched)."""

    assert_admin(current_user)
    service = _get_service_by_name(db, name)

    for field, value in service_update.model_dump(exclude_unset=True).items():
        setattr(service, field, value)

    # An enabled service needs a slot to run from; a past next_run_at is already due.
    if service.is_enabled and service.next_run_at is None:
        service.next_run_at = dt.datetime.now(dt.timezone.utc)

    db.commit()
    db.refresh(service)
    return service


@service_router.post("/{name}/run-now", response_model=ServiceOut)
def run_service_now(
    name: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Schedule a service to run on the scheduler's next poll by setting next_run_at to now.
    The service must be enabled for the scheduler to pick it up. Admin only."""

    assert_admin(current_user)
    service = _get_service_by_name(db, name)
    service.next_run_at = dt.datetime.now(dt.timezone.utc)
    db.commit()
    db.refresh(service)
    return service


@service_router.get("/{name}/logs")
def get_logs(
    name: str,
    lines: int = Query(100, ge=1),
    current_user: User = Depends(get_current_user),
) -> dict:
    """Get the last N lines of a service's log file. Admin only.
    :param name: Service registry key (also the log file / logger name).
    :param lines: Number of lines to retrieve (default 100).
    :param current_user: Current authenticated user."""

    assert_admin(current_user)
    if name not in SERVICE_REGISTRY:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Unknown service '{name}'")
    return AppLogger.read_logger(name).read_log_tail(lines)
