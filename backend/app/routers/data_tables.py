"""Module for generating CRUD routers for the JAM data tables"""

import base64
import datetime

from fastapi import APIRouter, Depends, status, HTTPException, Response
from sqlalchemy.orm import Session

from app import models, database, oauth2, schemas
from app.routers import generate_data_table_crud_router


# Person router
person_router = generate_data_table_crud_router(
    table_model=models.Person,
    create_schema=schemas.PersonCreate,
    update_schema=schemas.PersonUpdate,
    out_schema=schemas.PersonOut,
    endpoint="persons",
    not_found_msg="Person not found",
)

# Company router
company_router = generate_data_table_crud_router(
    table_model=models.Company,
    create_schema=schemas.CompanyCreate,
    update_schema=schemas.CompanyUpdate,
    out_schema=schemas.CompanyOut,
    endpoint="companies",
    not_found_msg="Company not found",
)

# Job router
job_router = generate_data_table_crud_router(
    table_model=models.Job,
    create_schema=schemas.JobCreate,
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
location_router = generate_data_table_crud_router(
    table_model=models.Location,
    create_schema=schemas.LocationCreate,
    update_schema=schemas.LocationUpdate,
    out_schema=schemas.LocationOut,
    endpoint="locations",
    not_found_msg="Location not found",
)

# Aggregator router
aggregator_router = generate_data_table_crud_router(
    table_model=models.Aggregator,
    create_schema=schemas.AggregatorCreate,
    update_schema=schemas.AggregatorUpdate,
    out_schema=schemas.AggregatorOut,
    endpoint="aggregators",
    not_found_msg="Aggregator not found",
)

# Interview router
interview_router = generate_data_table_crud_router(
    table_model=models.Interview,
    create_schema=schemas.InterviewCreate,
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

# Job Application Update router
job_application_update_router = generate_data_table_crud_router(
    table_model=models.JobApplicationUpdate,
    create_schema=schemas.JobApplicationUpdateCreate,
    update_schema=schemas.JobApplicationUpdateUpdate,
    out_schema=schemas.JobApplicationUpdateOut,
    endpoint="jobapplicationupdates",
    not_found_msg="Job Application Update not found",
)

# Keyword router
keyword_router = generate_data_table_crud_router(
    table_model=models.Keyword,
    create_schema=schemas.KeywordCreate,
    update_schema=schemas.KeywordUpdate,
    out_schema=schemas.KeywordOut,
    endpoint="keywords",
    not_found_msg="Keyword not found",
)

# File router
file_router = generate_data_table_crud_router(
    table_model=models.File,
    create_schema=schemas.FileCreate,
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
    jobs = (
        db.query(models.Job)
        .filter(models.Job.owner_id == current_user.id)
        .filter(models.Job.application_date.isnot(None))
        .limit(limit)
        .all()
    )

    # Get recent interviews
    # noinspection PyTypeChecker
    interviews = db.query(models.Interview).filter(models.Interview.owner_id == current_user.id).limit(limit).all()

    # Get recent job application updates
    # noinspection PyTypeChecker
    job_app_updates = (
        db.query(models.JobApplicationUpdate)
        .filter(models.JobApplicationUpdate.owner_id == current_user.id)
        .limit(limit)
        .all()
    )

    # Create unified update objects
    all_updates = []

    # Add job applications as "Application" updates
    for job in jobs:
        update_item = {
            "data": job,
            "date": job.application_date,
            "type": "Application",
            "job": job,
        }
        all_updates.append(update_item)

    # Add interviews as "Interview" updates
    for interview in interviews:
        update_item = {
            "data": interview,
            "date": interview.date,
            "type": "Interview",
            "job": interview.job,
        }
        all_updates.append(update_item)

    # Add job application updates
    for update in job_app_updates:
        update_item = {
            "data": update,
            "date": update.date,
            "type": "Job Application Update",
            "job": update.job,
        }
        all_updates.append(update_item)

    # Sort by date (most recent first) and apply the limit
    all_updates.sort(key=lambda x: x["date"], reverse=True)

    return all_updates[:limit]


@general_router.get("/stats")
def get_stats(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(oauth2.get_current_user),
):
    """Get general statistics about the application.
    :param db: Database session
    :param current_user: Authenticated user
    :return: Dictionary of general statistics"""

    # noinspection PyTypeChecker
    job_query = db.query(models.Job).filter(models.Job.owner_id == current_user.id)
    job_n = job_query.count()
    job_application_query = job_query.filter(models.Job.application_date.isnot(None))
    job_application_n = job_application_query.count()
    job_application_pending_n = job_application_query.filter(
        models.Job.application_status.notin_(["rejected", "withdrawn"])
    ).count()
    # noinspection PyTypeChecker
    interview_n = db.query(models.Interview).filter(models.Interview.owner_id == current_user.id).count()
    return {
        "jobs": job_n,
        "job_applications": job_application_n,
        "job_application_pending": job_application_pending_n,
        "interviews": interview_n,
    }


@general_router.get("/needs_chase", response_model=list[schemas.JobOut])
def get_needs_chase_job_applications(
    days: int = 30,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(oauth2.get_current_user),
):
    """Get jobs that need to be chased (followed up on) based on their job applications.
    A job needs to be chased if the last update on its application was more than X days ago.
    :param days: Number of days to check for follow-up
    :param db: Database session
    :param current_user: Authenticated user
    :return: List of jobs that need follow-up with additional metadata"""

    # Calculate the cutoff date
    now = datetime.datetime.now(datetime.UTC)

    # Query jobs that have job applications with active status
    # noinspection PyTypeChecker
    jobs = (
        db.query(models.Job)
        .filter(models.Job.owner_id == current_user.id)
        .filter(models.Job.application_date.isnot(None))
        .filter(models.Job.application_status.notin_(["rejected", "withdrawn"]))
        .all()
    )

    # Filter by last update date in Python and prepare job data
    needs_chase = []
    for job in jobs:
        # Convert job application to Pydantic schema to access computed fields
        job_schema = schemas.JobOut.model_validate(job, from_attributes=True)

        if (job_schema.last_update_date - now) > datetime.timedelta(days=days):
            needs_chase.append(job)

    return needs_chase
