"""Module for generating CRUD routers for the JAM data tables"""

import base64
import datetime

from fastapi import APIRouter, Depends, status, Request, HTTPException, Response
from sqlalchemy import func
from sqlalchemy.orm import Session
from sqlalchemy.orm import joinedload

from app import models, database, oauth2, schemas


def generate_crud_router(
    *,
    table_model,  # SQLAlchemy model
    create_schema,  # Pydantic schema for creation
    update_schema,  # Pydantic schema for updates
    out_schema,  # Pydantic schema for output
    endpoint: str,  # e.g. "companies"
    not_found_msg: str = "Entry not found",
    many_to_many_fields: dict = None,
    router: APIRouter | None = None,
) -> APIRouter:
    """Generate a FastAPI router with standard CRUD endpoints for a given table.
    :param table_model: SQLAlchemy model class representing the database table.
    :param create_schema: Pydantic schema used for creating new entries.
    :param update_schema: Pydantic schema used for updating existing entries.
    :param out_schema: Pydantic schema used for serialising output.
    :param endpoint: Endpoint name (used as route prefix and tag).
    :param not_found_msg: Default message when an entry is not found.
    :param many_to_many_fields: Dict defining M2M relationships.
                               Format: {
                                   'field_name': {
                                       'table': association_table,
                                       'local_key': 'local_foreign_key',
                                       'remote_key': 'remote_foreign_key'
                                   }
                               }
    :param router: Optional router to which the endpoints will be added.
    :return: Configured APIRouter instance with CRUD endpoints."""

    if router is None:
        router = APIRouter(prefix=f"/{endpoint}", tags=[endpoint])

    def handle_many_to_many_create(
        db: Session,
        entry_id: int,
        item_data: dict,
    ):
        """Handle the creation of many-to-many relationships.
        :param db: Database session
        :param entry_id: ID of the entry to which the relationships are being added
        :param item_data: Data containing the relationships to be added"""

        if not many_to_many_fields:
            return

        for field_name, m2m_config in many_to_many_fields.items():

            if field_name in item_data and item_data[field_name] is not None:
                values = item_data[field_name]
                if isinstance(values, list):
                    association_table = m2m_config["table"]
                    local_key = m2m_config["local_key"]
                    remote_key = m2m_config["remote_key"]

                    # Insert the relationships
                    for value_id in values:
                        db.execute(association_table.insert().values(**{local_key: entry_id, remote_key: value_id}))

    def handle_many_to_many_update(
        db: Session,
        entry_id: int,
        item_data: dict,
    ):
        """Handle updating of many-to-many relationships.
        :param db: Database session
        :param entry_id: ID of the entry to which the relationships are being added
        :param item_data: Data containing the relationships to be added"""

        if not many_to_many_fields:
            return

        for field_name, m2m_config in many_to_many_fields.items():
            if field_name in item_data:
                association_table = m2m_config["table"]
                local_key = m2m_config["local_key"]
                remote_key = m2m_config["remote_key"]

                # Delete existing relationships
                db.execute(association_table.delete().where(getattr(association_table.c, local_key) == entry_id))

                # Add new relationships if provided
                values = item_data[field_name]
                if values is not None and isinstance(values, list):
                    for value_id in values:
                        db.execute(association_table.insert().values(**{local_key: entry_id, remote_key: value_id}))

    # noinspection PyTypeHints
    @router.get("/", response_model=list[out_schema])
    def get_all(
        request: Request,
        db: Session = Depends(database.get_db),
        current_user: models.User = Depends(oauth2.get_current_user),
        limit: int | None = None,
    ):
        """Retrieve all entries for the current user.
        :param request: FastAPI request object to access query parameters
        :param db: Database session.
        :param current_user: Authenticated user.
        :param limit: Maximum number of entries to return.
        :return: List of entries."""

        # Start with base query
        # noinspection PyTypeChecker
        query = db.query(table_model).filter(table_model.owner_id == current_user.id)

        # Get all query parameters except 'limit'
        filter_params = dict(request.query_params)
        filter_params.pop("limit", None)  # Remove limit from filters

        # Apply filters for each parameter that matches a table column
        for param_name, param_value in filter_params.items():
            if hasattr(table_model, param_name):
                column = getattr(table_model, param_name)

                # Handle null values - convert string "null" to actual None/NULL
                if param_value.lower() == "null":
                    query = query.filter(column.is_(None))
                    continue

                # Handle different data types
                try:
                    # Try to convert to appropriate type based on column type
                    if hasattr(column.type, "python_type"):
                        if column.type.python_type == int:
                            param_value = int(param_value)
                        elif column.type.python_type == float:
                            param_value = float(param_value)
                        elif column.type.python_type == bool:
                            param_value = param_value.lower() in ("true", "1", "yes", "on")

                    # Add filter to query
                    query = query.filter(column == param_value)

                except (ValueError, TypeError):
                    # If conversion fails, treat as string comparison
                    query = query.filter(column == param_value)

        return query.limit(limit).all()

    # noinspection PyTypeHints
    @router.get("/{entry_id}", response_model=out_schema)
    def get_one(
        entry_id: int,
        db: Session = Depends(database.get_db),
        current_user: models.User = Depends(oauth2.get_current_user),
    ):
        """Get an entry by ID.
        :param entry_id: The entry ID.
        :param db: The database session.
        :param current_user: The current user.
        :returns: The entry if found.
        :raises: HTTPException with a 404 status code if the entry is not found.
        :raises: HTTPException with a 403 status code if not authorised to perform the requested action."""

        # noinspection PyTypeChecker
        entry = db.query(table_model).filter(table_model.id == entry_id).first()

        if not entry:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=not_found_msg)

        if entry.owner_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to perform requested action",
            )

        return entry

    # noinspection PyTypeHints
    @router.post("/", status_code=status.HTTP_201_CREATED, response_model=out_schema)
    def create(
        item: create_schema,
        db: Session = Depends(database.get_db),
        current_user: models.User = Depends(oauth2.get_current_user),
    ):
        """Create a new entry.
        :param item: Data for the new entry.
        :param db: Database session.
        :param current_user: Authenticated user.
        :return: The created entry."""

        # Extract the item data and exclude many-to-many fields from main creation
        item_dict = item.model_dump()

        # Remove many-to-many fields from main creation data
        main_data = item_dict.copy()
        m2m_data = {}

        if many_to_many_fields:
            for field_name in many_to_many_fields.keys():
                if field_name in main_data:
                    m2m_data[field_name] = main_data.pop(field_name)

        # Create the main entry
        new_entry = table_model(**main_data, owner_id=current_user.id)
        db.add(new_entry)
        db.commit()
        db.refresh(new_entry)

        # Handle many-to-many relationships
        if m2m_data:
            handle_many_to_many_create(db, new_entry.id, m2m_data)
            db.commit()
            db.refresh(new_entry)

        return new_entry

    # noinspection PyTypeHints
    @router.put("/{entry_id}", response_model=out_schema)
    def update(
        entry_id: int,
        item: update_schema,
        db: Session = Depends(database.get_db),
        current_user: models.User = Depends(oauth2.get_current_user),
    ):
        """Update an entry by ID.
        :param entry_id: The entry ID.
        :param item: The updated data.
        :param db: The database session.
        :param current_user: The current user.
        :returns: The updated entry.
        :raises: HTTPException with a 404 status code if an entry is not found.
        :raises: HTTPException with a 403 status code if not authorised to perform the requested action.
        :raises: HTTPException with a 400 status code if no field is provided for the update."""

        # noinspection PyTypeChecker
        query = db.query(table_model).filter(table_model.id == entry_id)
        entry = query.first()

        if not entry:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=not_found_msg)

        if entry.owner_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action"
            )

        # Extract the item data
        item_dict = item.model_dump(exclude_unset=True)

        if not item_dict:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No fields provided for update")

        # Separate main fields from many-to-many fields
        main_data = item_dict.copy()
        m2m_data = {}

        if many_to_many_fields:
            for field_name in many_to_many_fields.keys():
                if field_name in main_data:
                    m2m_data[field_name] = main_data.pop(field_name)

        # Update main fields if any
        if main_data:
            query.update(main_data, synchronize_session=False)

        # Handle many-to-many relationships
        if m2m_data:
            handle_many_to_many_update(db, entry_id, m2m_data)

        db.commit()

        # Return the updated entry
        return query.first()

    @router.delete("/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
    def delete(
        entry_id: int,
        db: Session = Depends(database.get_db),
        current_user: models.User = Depends(oauth2.get_current_user),
    ):
        """Delete an entry by ID.
        :param entry_id: The entry ID.
        :param db: The database session.
        :param current_user: The current user.
        :returns: Dict with a deletion status message.
        :raises: HTTPException with a 404 status code if an entry is not found.
        :raises: HTTPException with a 403 status code if not authorised to perform the requested action."""

        # noinspection PyTypeChecker
        query = db.query(table_model).filter(table_model.id == entry_id)
        entry = query.first()

        if not entry:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=not_found_msg)

        if entry.owner_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action"
            )

        # Delete many-to-many relationships first if they exist
        if many_to_many_fields:
            for field_name, m2m_config in many_to_many_fields.items():
                association_table = m2m_config["table"]
                local_key = m2m_config["local_key"]

                db.execute(association_table.delete().where(getattr(association_table.c, local_key) == entry_id))

        query.delete(synchronize_session=False)
        db.commit()

        return query

    return router


# Person router
person_router = generate_crud_router(
    table_model=models.Person,
    create_schema=schemas.Person,
    update_schema=schemas.PersonUpdate,
    out_schema=schemas.PersonOut,
    endpoint="persons",
    not_found_msg="Person not found",
)

# Company router
company_router = generate_crud_router(
    table_model=models.Company,
    create_schema=schemas.Company,
    update_schema=schemas.CompanyUpdate,
    out_schema=schemas.CompanyOut,
    endpoint="companies",
    not_found_msg="Company not found",
)

# Job router
job_router = generate_crud_router(
    table_model=models.Job,
    create_schema=schemas.Job,
    update_schema=schemas.JobUpdate,
    out_schema=schemas.JobOut,
    endpoint="jobs",
    not_found_msg="Job not found",
    many_to_many_fields={
        "keywords": {"table": models.job_keyword_mapping, "local_key": "job_id", "remote_key": "keyword_id"},
        "contacts": {"table": models.job_contact_mapping, "local_key": "job_id", "remote_key": "person_id"},
    },
)

# Location router
location_router = generate_crud_router(
    table_model=models.Location,
    create_schema=schemas.Location,
    update_schema=schemas.LocationUpdate,
    out_schema=schemas.LocationOut,
    endpoint="locations",
    not_found_msg="Location not found",
)

# Aggregator router
aggregator_router = generate_crud_router(
    table_model=models.Aggregator,
    create_schema=schemas.Aggregator,
    update_schema=schemas.AggregatorUpdate,
    out_schema=schemas.AggregatorOut,
    endpoint="aggregators",
    not_found_msg="Aggregator not found",
)

# Interview router
interview_router = generate_crud_router(
    table_model=models.Interview,
    create_schema=schemas.Interview,
    update_schema=schemas.InterviewUpdate,
    out_schema=schemas.InterviewOut,
    endpoint="interviews",
    not_found_msg="Interview not found",
    many_to_many_fields={
        "interviewers": {
            "table": models.interview_interviewer_mapping,
            "local_key": "interview_id",
            "remote_key": "person_id",
        },
    },
)


job_application_router = APIRouter(prefix="/jobapplications", tags=["Job Applications"])


@job_application_router.get("/needs_chase", response_model=list[schemas.JobToChaseOut])
def get_needs_chase_job_applications(
    days: int = 30,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(oauth2.get_current_user),
):
    """Get jobs for applications that need to be chased (followed up on).
    A job application needs to be chased if:
    1. Either:
       - No job application updates exist, and the application date is older than X days
       - Interview exists, and the latest interview is older than X days
       - Job application updates exist, and the latest update is older than X days
    :param days: Number of days to check for follow-up
    :param db: Database session
    :param current_user: Authenticated user
    :return: List of jobs for applications that need follow-up with additional metadata"""

    # Calculate the cutoff date
    cutoff_date = datetime.datetime.now(datetime.UTC) - datetime.timedelta(days=days)
    now = datetime.datetime.now(datetime.UTC)

    # Subquery to get the latest update date for each job application
    latest_update_subquery = (
        db.query(
            models.JobApplicationUpdate.job_application_id,
            func.max(models.JobApplicationUpdate.date).label("latest_update_date"),
        )
        .group_by(models.JobApplicationUpdate.job_application_id)
        .subquery()
    )

    # Subquery to get the latest interview date and count for each job application
    latest_interview_subquery = (
        db.query(
            models.Interview.job_application_id,
            func.max(models.Interview.date).label("latest_interview_date"),
            func.count(models.Interview.id).label("interview_count"),
        )
        .group_by(models.Interview.job_application_id)
        .subquery()
    )

    # Subquery to get the count of updates for each job application
    update_count_subquery = (
        db.query(
            models.JobApplicationUpdate.job_application_id,
            func.count(models.JobApplicationUpdate.id).label("update_count"),
        )
        .group_by(models.JobApplicationUpdate.job_application_id)
        .subquery()
    )

    # Main query to get jobs for applications that need chasing
    # noinspection PyTypeChecker
    query = (
        db.query(
            models.Job,
            models.JobApplication.date.label("application_date"),
            latest_update_subquery.c.latest_update_date,
            latest_interview_subquery.c.latest_interview_date,
            latest_interview_subquery.c.interview_count,
            update_count_subquery.c.update_count,
        )
        .join(models.JobApplication, models.Job.id == models.JobApplication.job_id)
        .outerjoin(latest_update_subquery, models.JobApplication.id == latest_update_subquery.c.job_application_id)
        .outerjoin(
            latest_interview_subquery, models.JobApplication.id == latest_interview_subquery.c.job_application_id
        )
        .outerjoin(update_count_subquery, models.JobApplication.id == update_count_subquery.c.job_application_id)
        .filter(models.JobApplication.owner_id == current_user.id)
        .filter(models.JobApplication.status.notin_(["Rejected", "Withdrawn"]))
        .filter(
            # Job application needs chasing if:
            # 1. No updates and no interviews exist, and application date is old enough, OR
            # 2. Updates exist but no interviews, and latest update is old enough, OR
            # 3. Interviews exist but no updates, and latest interview is old enough, OR
            # 4. Both updates and interviews exist, and the most recent of either is old enough
            (
                # Case 1: No updates, no interviews - check application date
                (latest_update_subquery.c.latest_update_date.is_(None))
                & (latest_interview_subquery.c.latest_interview_date.is_(None))
                & (models.JobApplication.date < cutoff_date)
            )
            | (
                # Case 2: Updates exist, no interviews - check latest update
                (latest_update_subquery.c.latest_update_date.is_not(None))
                & (latest_interview_subquery.c.latest_interview_date.is_(None))
                & (latest_update_subquery.c.latest_update_date < cutoff_date)
            )
            | (
                # Case 3: Interviews exist, no updates - check latest interview
                (latest_update_subquery.c.latest_update_date.is_(None))
                & (latest_interview_subquery.c.latest_interview_date.is_not(None))
                & (latest_interview_subquery.c.latest_interview_date < cutoff_date)
            )
            | (
                # Case 4: Both exist - check the most recent of either
                (latest_update_subquery.c.latest_update_date.is_not(None))
                & (latest_interview_subquery.c.latest_interview_date.is_not(None))
                & (
                    func.greatest(
                        latest_update_subquery.c.latest_update_date, latest_interview_subquery.c.latest_interview_date
                    )
                    < cutoff_date
                )
            )
        )
        .order_by(
            # Order by oldest first (most urgent) - use the most recent activity date
            func.coalesce(
                func.greatest(
                    latest_update_subquery.c.latest_update_date, latest_interview_subquery.c.latest_interview_date
                ),
                latest_update_subquery.c.latest_update_date,
                latest_interview_subquery.c.latest_interview_date,
                models.JobApplication.date,
            ).asc()
        )
    )

    results = query.all()

    # Process results to add metadata
    jobs_with_metadata = []
    for result in results:
        job = result[0]  # The Job object
        application_date = result[1]
        latest_update_date = result[2]
        latest_interview_date = result[3]
        interview_count = result[4] or 0
        update_count = result[5] or 0

        # Determine the most recent activity date and type
        most_recent_date = application_date
        last_update_type = "Application"

        if latest_update_date and (not most_recent_date or latest_update_date > most_recent_date):
            most_recent_date = latest_update_date
            last_update_type = f"Update #{update_count}"

        if latest_interview_date and (not most_recent_date or latest_interview_date > most_recent_date):
            most_recent_date = latest_interview_date
            last_update_type = f"Interview #{interview_count}"

        # Calculate days since last update
        days_since_last_update = (now - most_recent_date).days

        # Add metadata to the job object (as dynamic attributes)
        job.days_since_last_update = days_since_last_update
        job.last_update_type = last_update_type

        jobs_with_metadata.append(job)

    return jobs_with_metadata


# JobApplication router
generate_crud_router(
    table_model=models.JobApplication,
    create_schema=schemas.JobApplication,
    update_schema=schemas.JobApplicationUpdate,
    out_schema=schemas.JobApplicationOut,
    endpoint="jobapplications",
    not_found_msg="Job Application not found",
    router=job_application_router,
)

job_application_update_router = generate_crud_router(
    table_model=models.JobApplicationUpdate,
    create_schema=schemas.JobApplicationUpdateIn,
    update_schema=schemas.JobApplicationUpdateUpdate,
    out_schema=schemas.JobApplicationUpdateOut,
    endpoint="jobapplicationupdates",
    not_found_msg="Job Application Update not found",
)

# Keyword router
keyword_router = generate_crud_router(
    table_model=models.Keyword,
    create_schema=schemas.Keyword,
    update_schema=schemas.KeywordUpdate,
    out_schema=schemas.KeywordOut,
    endpoint="keywords",
    not_found_msg="Keyword not found",
)

# File router
file_router = generate_crud_router(
    table_model=models.File,
    create_schema=schemas.File,
    update_schema=schemas.FileUpdate,
    out_schema=schemas.FileOut,
    endpoint="files",
    not_found_msg="File not found",
)


@file_router.get("/{file_id}/download")
def download_file(
    file_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(oauth2.get_current_user),
):
    """Download a file by ID.
    :param file_id: The file ID.
    :param db: The database session.
    :param current_user: The current user."""

    # Get file record from the database
    # noinspection PyTypeChecker
    file_record = (
        db.query(models.File).filter(models.File.id == file_id, models.File.owner_id == current_user.id).first()
    )

    if not file_record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")

    if not file_record.content:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File content not found")

    try:
        # Content is already a base64 string - just decode it
        if file_record.content.startswith("data:"):
            encoded_data = file_record.content.split(",", 1)[1]
            file_content = base64.b64decode(encoded_data)
        else:
            # Pure base64 string
            file_content = base64.b64decode(file_record.content)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error decoding file content: {str(e)}"
        )

    content_type = file_record.type if file_record.type else "application/octet-stream"

    return Response(
        content=file_content,
        media_type=content_type,
        headers={
            "Content-Disposition": f'attachment; filename="{file_record.filename}"',
            "Content-Length": str(len(file_content)),
        },
    )


general_router = APIRouter()


@general_router.get("/latest_updates")
def get_all_updates(
    limit: int = 20,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(oauth2.get_current_user),
):
    """Get all recent updates including job applications, interviews, and job application updates.
    :param limit: Maximum number of updates to return
    :param db: Database session
    :param current_user: Authenticated user
    :return: List of all recent updates sorted by date (most recent first)"""

    # Get recent job applications
    # noinspection PyTypeChecker
    job_applications = (
        db.query(models.JobApplication)
        .filter(models.JobApplication.owner_id == current_user.id)
        .options(
            joinedload(models.JobApplication.job).joinedload(models.Job.company),
            joinedload(models.JobApplication.job).joinedload(models.Job.location),
            joinedload(models.JobApplication.aggregator),
            joinedload(models.JobApplication.cv),
            joinedload(models.JobApplication.cover_letter),
        )
        .limit(limit)
        .all()
    )

    # Get recent interviews
    # noinspection PyTypeChecker
    interviews = (
        db.query(models.Interview)
        .join(models.JobApplication, models.Interview.job_application_id == models.JobApplication.id)
        .filter(models.JobApplication.owner_id == current_user.id)
        .options(
            joinedload(models.Interview.job_application)
            .joinedload(models.JobApplication.job)
            .joinedload(models.Job.company),
            joinedload(models.Interview.job_application).joinedload(models.JobApplication.aggregator),
            joinedload(models.Interview.job_application).joinedload(models.JobApplication.cv),
            joinedload(models.Interview.job_application).joinedload(models.JobApplication.cover_letter),
            joinedload(models.Interview.location),
        )
        .limit(limit)
        .all()
    )

    # Get recent job application updates
    # noinspection PyTypeChecker
    job_app_updates = (
        db.query(models.JobApplicationUpdate)
        .join(models.JobApplication, models.JobApplicationUpdate.job_application_id == models.JobApplication.id)
        .filter(models.JobApplication.owner_id == current_user.id)
        .options(
            joinedload(models.JobApplicationUpdate.job_application)
            .joinedload(models.JobApplication.job)
            .joinedload(models.Job.company),
            joinedload(models.JobApplicationUpdate.job_application).joinedload(models.JobApplication.aggregator),
            joinedload(models.JobApplicationUpdate.job_application).joinedload(models.JobApplication.cv),
            joinedload(models.JobApplicationUpdate.job_application).joinedload(models.JobApplication.cover_letter),
        )
        .limit(limit)
        .all()
    )

    # Create unified update objects
    all_updates = []

    # Add job applications as "Application" updates
    for job_application in job_applications:
        update_item = {
            "data": job_application,
            "date": job_application.date,
            "type": "Application",
            "job_title": job_application.job.title,
            "job_application": job_application,
        }
        all_updates.append(update_item)

    # Add interviews as "Interview" updates
    for interview in interviews:
        update_item = {
            "data": interview,
            "date": interview.date,
            "type": "Interview",
            "job_title": interview.job_application.job.title,
            "job_application": interview.job_application,
        }
        all_updates.append(update_item)

    # Add job application updates
    for update in job_app_updates:
        update_item = {
            "data": update,
            "date": update.date,
            "type": "Job Application Update",
            "job_title": update.job_application.job.title,
            "job_application": update.job_application,
        }
        all_updates.append(update_item)

    # Sort by date (most recent first) and apply the limit
    all_updates.sort(key=lambda x: x["date"], reverse=True)

    return all_updates[:limit]
