"""FastAPI routers for the job email scraping service endpoints.

Provides REST API endpoints for managing job alert emails, scraped job postings,
and service execution logs with CRUD operations and admin access controls."""

import datetime as dt
import json
from typing import Literal

from fastapi import Depends, HTTPException
from sqlalchemy import and_, asc, case, desc, distinct, false, func, or_
from sqlalchemy.orm import Session, joinedload
from starlette import status

from app import models
from app.core.oauth2 import get_current_user
from app.database import get_db
from app.job_email_scraping import schemas
from app.job_email_scraping.filtering import rule_to_sql_predicate
from app.routers.utility import generate_data_table_crud_router

# GET endpoint for admin user to get all scraped jobs
scraped_job_router = generate_data_table_crud_router(
    table_model=models.ScrapedJob,
    out_schema=schemas.ScrapedJobOut,
    endpoint="scraped-jobs",
    not_found_msg="Scraped Job not found",
    allowed_actions=["get_all"],
    admin_only=True,
)


@scraped_job_router.get(
    "/paged", response_model=schemas.PaginatedScrapedJobResponse | schemas.PaginatedScrapedJobIdsResponse
)
def get_all(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
    page: int = 0,
    page_size: int = 10,
    sort_by: str = "scrape_datetime",
    sort_direction: Literal["asc", "desc"] = "desc",
    show_past_deadline: bool = False,
    since_last_login: bool = False,
    favourites_only: bool = False,
    errors_only: bool = False,
    search: str | None = None,
    filters: str | None = None,
    ids_only: bool = False,
) -> dict:
    """Retrieve paginated scraped jobs for the current user that have not been imported, are active and successfully scraped.
    :param db: Database session
    :param current_user: Current user
    :param page: Page number
    :param page_size: Page size
    :param sort_by: sort key
    :param sort_direction: sort direction
    :param show_past_deadline: Show scraped jobs with past deadlines
    :param since_last_login: Only show jobs created since last login
    :param favourites_only: Only show jobs that are in the user's favourites
    :param errors_only: Only show jobs that failed to be scraped or rated
    :param search: Search term
    :param filters: JSON-encoded filter object
    :param ids_only: Return only IDs instead of full objects"""

    # Base query
    query = db.query(models.ScrapedJob)
    if not ids_only:
        query = query.options(joinedload(models.ScrapedJob.job_rating))  # Eager load rating for full response
    # noinspection PyComparisonWithNone
    query = (
        query.filter(models.ScrapedJob.owner_id == current_user.id)
        .filter(models.ScrapedJob.is_imported.is_(False))
        .filter(models.ScrapedJob.is_active.is_(True))
        .filter(models.ScrapedJob.exclusion_filter_id == None)
    )

    if favourites_only:
        fav_filters = (
            db.query(models.ScrapingFavouriteFilter)
            .filter(models.ScrapingFavouriteFilter.owner_id == current_user.id)
            .filter(models.ScrapingFavouriteFilter.is_active.is_(True))
            .all()
        )
        if fav_filters:
            fav_predicates = [rule_to_sql_predicate(f) for f in fav_filters]
            query = query.filter(or_(*fav_predicates))
        else:
            query = query.filter(false())  # Filter out all rows if no favourites

    # Errors only
    if errors_only:
        query = query.outerjoin(models.JobRating).filter(
            or_(
                models.ScrapedJob.is_failed.is_(True),
                models.JobRating.is_success.is_(False),
            )
        )

    # Total before deadline/login/search/column filters
    total = query.count()

    if not show_past_deadline and not errors_only:
        query = query.filter(
            or_(
                models.ScrapedJob.deadline.is_(None),
                models.ScrapedJob.deadline >= dt.datetime.now(dt.timezone.utc),
            ),
            models.ScrapedJob.is_closed.is_(False),
        )

    if since_last_login and current_user.previous_login:
        query = query.filter(models.ScrapedJob.created_at >= current_user.previous_login)

    # Apply search filter
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                models.ScrapedJob.title.ilike(search_term),
                models.ScrapedJob.company.ilike(search_term),
                models.ScrapedJob.location.ilike(search_term),
                models.ScrapedJob.description.ilike(search_term),
                models.ScrapedJob.platform.ilike(search_term),
            )
        )

    # Determine if we need a JobRating join (for filters or sorting)
    needs_rating_join = sort_by.startswith("job_rating.") and not errors_only
    filter_conditions = []

    # Parse JSON column filters
    if filters:
        filter_dict = json.loads(filters)
        for key, fval in filter_dict.items():
            ftype = fval.get("type")

            # Resolve the SQLAlchemy column
            if key.startswith("job_rating."):
                attr_name = key.split(".", 1)[1]
                if not hasattr(models.JobRating, attr_name):
                    continue
                col = getattr(models.JobRating, attr_name)
                needs_rating_join = True
            elif hasattr(models.ScrapedJob, key):
                col = getattr(models.ScrapedJob, key)
            else:
                continue

            if ftype == "text":
                value = (fval.get("value") or "").strip()
                if value:
                    filter_conditions.append(col.ilike(f"%{value}%"))

            elif ftype == "select":
                selected = fval.get("selected", [])
                if selected:
                    filter_conditions.append(col.in_(selected))

            elif ftype == "number":
                min_val = fval.get("min")
                max_val = fval.get("max")
                null_filter = fval.get("nullFilter")

                if null_filter == "null":
                    filter_conditions.append(col.is_(None))
                elif null_filter == "not_null":
                    filter_conditions.append(col.isnot(None))
                    if min_val is not None:
                        filter_conditions.append(col >= min_val)
                    if max_val is not None:
                        filter_conditions.append(col <= max_val)
                else:
                    if min_val is not None:
                        filter_conditions.append(col >= min_val)
                    if max_val is not None:
                        filter_conditions.append(col <= max_val)

            elif ftype == "date":
                from_val = fval.get("from")
                to_val = fval.get("to")
                if from_val:
                    filter_conditions.append(col >= from_val)
                if to_val:
                    filter_conditions.append(col <= to_val + "T23:59:59")

            elif ftype == "reference":
                selected_ids = fval.get("selectedIds", [])
                if selected_ids:
                    filter_conditions.append(col.in_([int(sid) for sid in selected_ids]))

    # Apply the join once if needed
    if needs_rating_join:
        query = query.outerjoin(models.JobRating)

    # Apply all filter conditions
    for cond in filter_conditions:
        query = query.filter(cond)

    # Apply sorting
    if sort_by.startswith("job_rating."):
        rating_attribute = sort_by.split(".", 1)[1]

        if hasattr(models.JobRating, rating_attribute):
            sort_column = getattr(models.JobRating, rating_attribute)

            if sort_direction == "desc":
                query = query.order_by(desc(sort_column).nulls_last())
            else:
                query = query.order_by(asc(sort_column).nulls_last())
        else:
            query = query.order_by(desc(models.ScrapedJob.scrape_datetime).nulls_last())
    elif hasattr(models.ScrapedJob, sort_by):
        sort_column = getattr(models.ScrapedJob, sort_by)
        if sort_direction == "desc":
            query = query.order_by(desc(sort_column).nulls_last())
        else:
            query = query.order_by(asc(sort_column).nulls_last())
    else:
        query = query.order_by(desc(models.ScrapedJob.scrape_datetime).nulls_last())

    # Get total filtered count before pagination
    total_filtered = query.count()

    # Calculate pagination
    offset = page * page_size
    total_pages = (total_filtered + page_size - 1) // page_size if total_filtered > 0 else 1

    if ids_only:
        ids = query.with_entities(models.ScrapedJob.id).offset(offset).limit(page_size).all()
        return {
            "items": [row[0] for row in ids],
            "total": total,
            "total_filtered": total_filtered,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
        }

    # Apply pagination
    results = query.offset(offset).limit(page_size).all()

    return {
        "items": results,
        "total": total,
        "total_filtered": total_filtered,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
    }


@scraped_job_router.get("/by-email/{email_id}", response_model=list[schemas.ScrapedJobOut])
def get_scraped_jobs_by_email(
    email_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get scraped jobs associated with a specific job email for the current user.
    :param email_id: ID of the job email
    :param current_user: Current authenticated user
    :param db: Database session
    :return: List of scraped jobs linked to the email"""

    email = (
        db.query(models.JobEmail)
        .filter(models.JobEmail.id == email_id)
        .filter(models.JobEmail.owner_id == current_user.id)
        .first()
    )
    if not email:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job email not found")
    return email.jobs


@scraped_job_router.get("/filtered-by-filter/{filter_id}", response_model=list[schemas.ScrapedJobOut])
def get_scraped_jobs_filtered_by_filter(
    filter_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get scraped jobs associated with a specific filter for the current user.
    :param filter_id: ID of the filter
    :param current_user: Current authenticated user
    :param db: Database session
    :return: List of scraped jobs associated with the filter"""

    scraped_jobs = (
        db.query(models.ScrapedJob)
        .filter(models.ScrapedJob.owner_id == current_user.id)
        .filter(models.ScrapedJob.exclusion_filter_id == filter_id)
        .all()
    )
    return scraped_jobs


@scraped_job_router.get("/platform-stats", response_model=list[schemas.PlatformAlertStats])
def get_platform_stats(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get count of scraped jobs, imported scraped jobs, and applied scraped jobs, grouped by platform and alert name
    for the current user.
    :param current_user: Current authenticated user
    :param db: Database session
    :return: List of platform alert stats grouped by platform and alert name"""

    query = (
        db.query(
            models.JobEmail.platform,
            models.JobEmail.alert_name,
            # 1. Scraped jobs
            func.count(distinct(models.ScrapedJob.id)).label("scraped_count"),
            # 2. Scraped jobs that have a linked Job entry
            func.count(distinct(case((models.Job.id.isnot(None), models.ScrapedJob.id)))).label("imported_count"),
            # 3. Scraped jobs whose linked Job has been applied to
            func.count(
                distinct(
                    case(
                        (
                            models.Job.has_application,
                            models.ScrapedJob.id,
                        )
                    )
                )
            ).label("applied_count"),
        )
        .join(models.JobEmail.jobs)
        .outerjoin(
            models.Job, and_(models.Job.scraped_job_id == models.ScrapedJob.id, models.Job.owner_id == current_user.id)
        )
        .filter(models.ScrapedJob.owner_id == current_user.id)
        .group_by(
            models.JobEmail.platform,
            models.JobEmail.alert_name,
        )
    )

    results = query.all()
    return [
        {
            "platform": result.platform or "Unknown",
            "alert_name": result.alert_name,
            "scraped_count": result.scraped_count,
            "imported_count": result.imported_count,
            "applied_count": result.applied_count,
        }
        for result in results
    ]


@scraped_job_router.get("/expired", response_model=list[schemas.ScrapedJobOut])
def get_expired(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Return all active scraped jobs that are expired: closed or past deadline."""
    now = dt.datetime.now(dt.timezone.utc)
    # noinspection PyComparisonWithNone
    return (
        db.query(models.ScrapedJob)
        .filter(models.ScrapedJob.owner_id == current_user.id)
        .filter(models.ScrapedJob.is_imported.is_(False))
        .filter(models.ScrapedJob.is_active.is_(True))
        .filter(models.ScrapedJob.exclusion_filter_id == None)
        .filter(
            or_(
                models.ScrapedJob.is_closed == True,
                and_(
                    models.ScrapedJob.deadline.isnot(None),
                    models.ScrapedJob.deadline < now,
                ),
            ),
        )
        .all()
    )


# PUT endpoint for regular users to update the entries
generate_data_table_crud_router(
    table_model=models.ScrapedJob,
    update_schema=schemas.ScrapedJobUpdate,
    out_schema=schemas.ScrapedJobOut,
    endpoint="scraped-jobs",
    not_found_msg="Scraped Job not found",
    allowed_actions=["put"],
    router=scraped_job_router,
)


@scraped_job_router.post("/tour-demo", response_model=schemas.ScrapedJobOut, status_code=status.HTTP_201_CREATED)
def create_tour_demo(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Create a demo scraped job for the guided tour. Idempotent: deletes any existing demo first."""
    now = dt.datetime.now(dt.timezone.utc)

    # Remove any leftover demo job from a previous tour run so the unique constraint never fires
    existing = (
        db.query(models.ScrapedJob)
        .filter(
            models.ScrapedJob.owner_id == current_user.id,
            models.ScrapedJob.external_job_id == f"tour-demo-{current_user.id}",
        )
        .first()
    )
    if existing:
        old_log_id = existing.service_log_id
        db.delete(existing)
        db.flush()
        if old_log_id is not None:
            old_log = db.query(models.JobEmailScrapingServiceLog).filter(
                models.JobEmailScrapingServiceLog.id == old_log_id
            ).first()
            if old_log:
                db.delete(old_log)
                db.flush()

    service_log = models.JobEmailScrapingServiceLog(
        run_datetime=now,
        is_success=True,
        user_found_ids=[],
        user_processed_ids=[],
        email_found_n=0,
    )
    db.add(service_log)
    db.flush()

    scraped_job = models.ScrapedJob(
        owner_id=current_user.id,
        service_log_id=service_log.id,
        external_job_id=f"tour-demo-{current_user.id}",
        platform="LinkedIn",
        is_processed=True,
        is_scraped=True,
        scrape_datetime=now,
        is_active=True,
        title="Senior Python Developer",
        company="Acme Corp",
        location_city="London",
        location_country="United Kingdom",
        attendance_type="hybrid",
        salary_min=70000,
        salary_max=90000,
        salary_currency="GBP",
        description="We are looking for a Senior Python Developer to join our growing engineering team. "
        "You will design and build scalable backend services, mentor junior developers, and collaborate "
        "closely with product and data teams.",
        url="https://www.linkedin.com/jobs/view/tour-demo",
    )
    db.add(scraped_job)
    db.commit()
    db.refresh(scraped_job)
    return scraped_job


@scraped_job_router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_scraped_job(
    id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Hard-delete a scraped job owned by the current user."""
    scraped_job = (
        db.query(models.ScrapedJob)
        .filter(models.ScrapedJob.id == id, models.ScrapedJob.owner_id == current_user.id)
        .first()
    )
    if not scraped_job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scraped Job not found")
    db.delete(scraped_job)
    db.commit()
