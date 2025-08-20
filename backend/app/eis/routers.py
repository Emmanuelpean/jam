"""FastAPI routers for the email ingestion service (EIS) endpoints.

Provides REST API endpoints for managing job alert emails, scraped job postings,
and service execution logs with CRUD operations and admin access controls."""

from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.models import User
from app.eis import models, schemas
from app.routers import generate_data_table_crud_router
from app.database import get_db
from app.oauth2 import get_current_user


# Job Alert Email router
email_router = generate_data_table_crud_router(
    table_model=models.JobAlertEmail,
    create_schema=schemas.JobAlertEmailCreate,
    update_schema=schemas.JobAlertEmailUpdate,
    out_schema=schemas.JobAlertEmailOut,
    endpoint="jobalertemails",
    not_found_msg="Job alert email not found",
)


# Scraped Job router
scrapedjob_router = generate_data_table_crud_router(
    table_model=models.ScrapedJob,
    create_schema=schemas.ScrapedJobCreate,
    update_schema=schemas.ScrapedJobUpdate,
    out_schema=schemas.ScrapedJobOut,
    endpoint="scrapedjobs",
    not_found_msg="Scraped job not found",
)


# Email Ingestion Service Log router
eis_servicelog_router = APIRouter(prefix="/servicelogs", tags=["servicelogs"])


@eis_servicelog_router.get("/", response_model=list[schemas.EisServiceLogOut])
def get_service_logs_by_date_range(
    start_date: datetime | None = Query(None, description="Start date for filtering (ISO format)"),
    end_date: datetime | None = Query(None, description="End date for filtering (ISO format)"),
    delta_days: int | None = Query(None, description="Number of days to go back in time"),
    limit: int | None = Query(None, description="Maximum number of logs to return"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get service logs within a specified date range. Admin access required.
    :param start_date: Optional start date filter (inclusive)
    :param end_date: Optional end date filter (inclusive)
    :param limit: Optional limit for number of logs to return
    :param delta_days: Optional number of days to go back in time
    :param current_user: Current authenticated admin user
    :param db: Database session
    :return: list of service logs within the date range ordered by run_datetime descending"""

    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")

    query = db.query(models.EisServiceLog)

    # Apply date filters
    if start_date:
        query = query.filter(models.EisServiceLog.run_datetime >= start_date)
    if end_date:
        query = query.filter(models.EisServiceLog.run_datetime <= end_date)
    if delta_days:
        start_date = datetime.now() - timedelta(days=delta_days)
        query = query.filter(models.EisServiceLog.run_datetime >= start_date)

    # Order by run_datetime descending (most recent first)
    query = query.order_by(models.EisServiceLog.run_datetime.desc())

    # Apply limit if specified
    if limit:
        query = query.limit(limit)

    return query.all()
