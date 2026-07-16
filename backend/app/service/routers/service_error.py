"""Admin endpoints for listing and acknowledging unified service errors."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.oauth2 import get_current_user
from app.models import User, ServiceError
from app.routers.utility import assert_admin
from app.service.schemas import ServiceErrorOut, ErrorAcknowledgeRequest, ServiceErrorCounts

service_error_router = APIRouter(prefix="/service-errors", tags=["service-errors"])


@service_error_router.get("/", response_model=list[ServiceErrorOut])
def list_service_errors(
    scraped_job_id: int | None = Query(None, description="Filter by ScrapedJob id"),
    scraping_log_ids: list[int] | None = Query(None, alias="job_email_scraping_service_log_id"),
    rating_log_ids: list[int] | None = Query(None, alias="job_rating_service_log_id"),
    monitoring_log_ids: list[int] | None = Query(None, alias="provider_monitoring_service_log_id"),
    acknowledged: bool | None = Query(None, alias="is_acknowledged"),
    limit: int | None = Query(None, ge=1, description="Maximum number of errors to return"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[ServiceErrorOut]:
    """List service errors, newest first, optionally filtered by run(s) / job / status. Admin only."""

    assert_admin(current_user)

    query = db.query(ServiceError)
    if scraped_job_id is not None:
        query = query.filter(ServiceError.scraped_job_id == scraped_job_id)
    if scraping_log_ids:
        query = query.filter(ServiceError.job_email_scraping_service_log_id.in_(scraping_log_ids))
    if rating_log_ids:
        query = query.filter(ServiceError.job_rating_service_log_id.in_(rating_log_ids))
    if monitoring_log_ids:
        query = query.filter(ServiceError.provider_monitoring_service_log_id.in_(monitoring_log_ids))
    if acknowledged is not None:
        query = query.filter(ServiceError.is_acknowledged.is_(acknowledged))
    query = query.order_by(ServiceError.created_at.desc(), ServiceError.id.desc())
    if limit:
        query = query.limit(limit)
    return query.all()


@service_error_router.get("/counts", response_model=ServiceErrorCounts)
def unacknowledged_error_counts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ServiceErrorCounts:
    """Count unacknowledged errors raised since the admin's previous login, per service. Admin only."""

    assert_admin(current_user)

    query = db.query(
        func.count(ServiceError.job_email_scraping_service_log_id),
        func.count(ServiceError.job_rating_service_log_id),
        func.count(ServiceError.provider_monitoring_service_log_id),
    ).filter(ServiceError.is_acknowledged.is_(False))
    if current_user.previous_login:
        query = query.filter(ServiceError.created_at >= current_user.previous_login)
    scraping, rating, monitoring = query.one()
    return ServiceErrorCounts(
        job_email_scraping=scraping,
        job_rating=rating,
        provider_monitoring=monitoring,
    )


@service_error_router.put("/acknowledge", response_model=list[ServiceErrorOut])
def acknowledge_service_errors(
    request: ErrorAcknowledgeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Set the acknowledgement status of the given service errors. Admin only."""

    assert_admin(current_user)

    errors = db.query(ServiceError).filter(ServiceError.id.in_(request.ids)).all()
    for error in errors:
        error.is_acknowledged = request.is_acknowledged
    db.commit()
    for error in errors:
        db.refresh(error)
    return errors
