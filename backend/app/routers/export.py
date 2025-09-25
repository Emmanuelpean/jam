"""API router for exporting data"""

import csv
import io

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app import database, oauth2

router = APIRouter(prefix="/export", tags=["export"])

from app import models


@router.get("/")
def export_jobs_with_all_columns(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(oauth2.get_current_user),
):
    """Export jobs with all columns (except IDs) and related data as a single CSV file."""

    jobs = db.query(models.Job).filter(models.Job.owner_id == current_user.id).all()

    output = io.StringIO()
    writer = csv.writer(output)

    # List all job columns except IDs and foreign keys
    job_fields = [
        "title",
        "description",
        "salary_min",
        "salary_max",
        "personal_rating",
        "url",
        "deadline",
        "note",
        "attendance_type",
        "application_date",
        "application_url",
        "application_status",
        "application_note",
        "applied_via",
        "created_at",
        "modified_at",
    ]

    # Header with related fields
    writer.writerow(
        job_fields
        + [
            "Company",
            "Location",
            "Source Aggregator",
            "Application Aggregator",
            "Keywords",
            "Contacts",
            "Interviews",
            "Updates",
        ]
    )

    for job in jobs:
        row = [getattr(job, field) for field in job_fields]
        company = job.company.name if job.company else ""
        location = job.location.name if job.location else ""
        source_agg = job.source.name if job.source else ""
        app_agg = job.application_aggregator.name if job.application_aggregator else ""
        keywords = "; ".join([k.name for k in job.keywords])
        contacts = "; ".join([f"{p.first_name} {p.last_name}" for p in job.contacts])
        interviews = "; ".join([f"{i.date.strftime('%Y-%m-%d')} ({i.type})" for i in job.interviews])
        updates = "; ".join([f"{u.date.strftime('%Y-%m-%d')} ({u.type})" for u in job.updates])
        writer.writerow(row + [company, location, source_agg, app_agg, keywords, contacts, interviews, updates])

    output.seek(0)
    return StreamingResponse(
        output,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=jobs_export.csv"},
    )
