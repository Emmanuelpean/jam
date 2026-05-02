"""Module for generating CRUD routers for the JAM data tables"""

import base64
import hashlib

from fastapi import Depends, status, HTTPException, Response
from sqlalchemy.orm import Session

from app import models, database
from app.config import settings
from app.core import oauth2
from app.data_tables import schemas
from app.geolocation.geolocation import geocode_location
from app.routers.utility import generate_data_table_crud_router

# ---------------------------------------------------- SIMPLE TABLES ---------------------------------------------------

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


# File router — POST is handled manually below for deduplication
file_router = generate_data_table_crud_router(
    table_model=models.File,
    create_schema=schemas.FileCreate,
    update_schema=schemas.FileUpdate,
    out_schema=schemas.FileOut,
    endpoint="files",
    not_found_msg="File not found",
    allowed_actions=["get", "put", "delete"],
)


@file_router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.FileOut)
def create_file(
    item: schemas.FileCreate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(oauth2.get_current_user),
):
    """Create a file, reusing an existing record if the same content was already uploaded."""

    max_bytes = settings.max_file_size_mb * 1024 * 1024
    if item.size > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds the maximum allowed size of {settings.max_file_size_mb} MB.",
        )

    content = item.content
    # Strip data URL prefix for hashing (e.g. "data:application/pdf;base64,...")
    raw_content = content.split(",", 1)[1] if content.startswith("data:") else content
    content_hash = hashlib.sha256(raw_content.encode()).hexdigest()

    existing = (
        db.query(models.File)
        .filter(models.File.owner_id == current_user.id, models.File.content_hash == content_hash)
        .first()
    )
    if existing:
        return existing

    new_file = models.File(**item.model_dump(), owner_id=current_user.id, content_hash=content_hash)
    db.add(new_file)
    db.commit()
    db.refresh(new_file)
    return new_file


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


# --------------------------------------------------- COMPLEX TABLES ---------------------------------------------------


def geocode_entry_location(entry: dict, db: Session, entry_data: dict | None = None) -> dict:
    """Geocode the location string on Job create/update.
    :param entry: The entry data dictionary.
    :param db: The database session.
    :param entry_data: optional original data of the entry
    :return: Dictionary with geolocation_id set."""

    location = entry.get("location") or (entry_data or {}).get("location")
    if location and location.strip():
        geolocation = geocode_location(location.strip(), db)
        return {"geolocation_id": geolocation.id if geolocation else None}
    return {"geolocation_id": None}


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
    transform=geocode_entry_location,
    many_to_many_fields={
        "keywords": {
            "table": models.job_keyword_mapping,
            "local_key": "job_id",
            "remote_key": "keyword_id",
            "related_model": models.Keyword,
        },
        "contacts": {
            "table": models.job_contact_mapping,
            "local_key": "job_id",
            "remote_key": "person_id",
            "related_model": models.Person,
        },
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
    transform=geocode_entry_location,
    many_to_many_fields={
        "interviewers": {
            "table": models.interview_interviewer_mapping,
            "local_key": "interview_id",
            "remote_key": "person_id",
            "related_model": models.Person,
        },
    },
)

# Job Application Update router
job_application_update_router = generate_data_table_crud_router(
    table_model=models.JobApplicationUpdate,
    create_schema=schemas.JobApplicationUpdateCreate,
    update_schema=schemas.JobApplicationUpdateUpdate,
    out_schema=schemas.JobApplicationUpdateOut,
    endpoint="job-application-updates",
    not_found_msg="Job Application Update not found",
)

# Speculative Application router
speculative_application_update_router = generate_data_table_crud_router(
    table_model=models.SpeculativeApplication,
    create_schema=schemas.SpeculativeApplicationCreate,
    update_schema=schemas.SpeculativeApplicationUpdate,
    out_schema=schemas.SpeculativeApplicationOut,
    endpoint="speculative-applications",
    not_found_msg="Speculative Application not found",
    many_to_many_fields={
        "contacts": {
            "table": models.speculative_application_contact_mapping,
            "local_key": "speculative_application_id",
            "remote_key": "person_id",
            "related_model": models.Person,
        },
    },
)
