"""Admin endpoints for listing and acknowledging unified service errors."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.oauth2 import get_current_user
from app.models import User, Error
from app.routers.utility import assert_admin
from app.service_runner.schemas import ErrorOut, ErrorAcknowledgeRequest

service_error_router = APIRouter(prefix="/service-errors", tags=["service-errors"])


@service_error_router.get("/", response_model=list[ErrorOut])
def list_service_errors(
    scraped_job_id: int | None = Query(None, description="Filter by ScrapedJob id"),
    job_email_scraping_service_log_id: list[int] | None = Query(None, description="Filter by job email scraping run id(s)"),
    job_rating_service_log_id: list[int] | None = Query(None, description="Filter by job rating run id(s)"),
    external_service_monitoring_service_log_id: list[int] | None = Query(
        None, description="Filter by external service monitoring run id(s)"
    ),
    is_acknowledged: bool | None = Query(None, description="Filter by acknowledgement status"),
    limit: int | None = Query(None, ge=1, description="Maximum number of errors to return"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List service errors, newest first, optionally filtered by run(s) / job / status. Admin only."""

    assert_admin(current_user)

    query = db.query(Error)
    if scraped_job_id is not None:
        query = query.filter(Error.scraped_job_id == scraped_job_id)
    if job_email_scraping_service_log_id:
        query = query.filter(Error.job_email_scraping_service_log_id.in_(job_email_scraping_service_log_id))
    if job_rating_service_log_id:
        query = query.filter(Error.job_rating_service_log_id.in_(job_rating_service_log_id))
    if external_service_monitoring_service_log_id:
        query = query.filter(
            Error.external_service_monitoring_service_log_id.in_(external_service_monitoring_service_log_id)
        )
    if is_acknowledged is not None:
        query = query.filter(Error.is_acknowledged.is_(is_acknowledged))
    query = query.order_by(Error.created_at.desc(), Error.id.desc())
    if limit:
        query = query.limit(limit)
    return query.all()


@service_error_router.put("/acknowledge", response_model=list[ErrorOut])
def acknowledge_service_errors(
    request: ErrorAcknowledgeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Set the acknowledgement status of the given service errors. Admin only."""

    assert_admin(current_user)

    errors = db.query(Error).filter(Error.id.in_(request.ids)).all()
    for error in errors:
        error.is_acknowledged = request.is_acknowledged
    db.commit()
    for error in errors:
        db.refresh(error)
    return errors
