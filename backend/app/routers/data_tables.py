"""Module for generating CRUD routers for the JAM data tables"""

import base64

from fastapi import Depends, status, HTTPException, Response
from sqlalchemy.orm import Session

from app import models, database, oauth2, schemas
from app.routers import generate_data_table_crud_router

# Settings router
settings_router = generate_data_table_crud_router(
    table_model=models.Settings,
    create_schema=schemas.SettingCreate,
    update_schema=schemas.SettingUpdate,
    out_schema=schemas.SettingOut,
    endpoint="settings",
    not_found_msg="Settings not found",
    admin_only=True,
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

# Aggregator router
aggregator_router = generate_data_table_crud_router(
    table_model=models.Aggregator,
    create_schema=schemas.AggregatorCreate,
    update_schema=schemas.AggregatorUpdate,
    out_schema=schemas.AggregatorOut,
    endpoint="aggregators",
    not_found_msg="Aggregator not found",
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

# Location router
location_router = generate_data_table_crud_router(
    table_model=models.Location,
    create_schema=schemas.LocationCreate,
    update_schema=schemas.LocationUpdate,
    out_schema=schemas.LocationOut,
    endpoint="locations",
    not_found_msg="Location not found",
)

# Person router
person_router = generate_data_table_crud_router(
    table_model=models.Person,
    create_schema=schemas.PersonCreate,
    update_schema=schemas.PersonUpdate,
    out_schema=schemas.PersonOut,
    endpoint="persons",
    not_found_msg="Person not found",
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
