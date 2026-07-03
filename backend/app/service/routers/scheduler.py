"""Admin endpoints for the service scheduler itself: its runtime status and its own log file.

These describe the scheduler process (the SCHEDULER=true worker), as opposed to /services,
which is about the individual services it runs."""

from fastapi import APIRouter, Depends, Query

from app.core.oauth2 import get_current_user
from app.models import User
from app.routers.utility import assert_admin
from app.service.scheduler import service_scheduler, ServiceScheduler
from app.utilities.logger import AppLogger

scheduler_router = APIRouter(prefix="/service-scheduler", tags=["service-scheduler"])


@scheduler_router.get("/status")
def get_scheduler_status(current_user: User = Depends(get_current_user)) -> dict:
    """Return the scheduler's runtime status (running, poll interval, last log line). Admin only."""

    assert_admin(current_user)
    return service_scheduler.status()


@scheduler_router.get("/logs")
def get_scheduler_logs(
    lines: int = Query(100, ge=1),
    current_user: User = Depends(get_current_user),
) -> dict:
    """Get the last N lines of the scheduler's log file. Admin only.
    :param lines: Number of lines to retrieve (default 100).
    :param current_user: Current authenticated user."""

    assert_admin(current_user)
    return AppLogger.read_logger(ServiceScheduler.service_name).read_log_tail(lines)
