"""API router for exporting data"""

import csv
import io
import zipfile
from typing import Iterable, Any

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from app import database, models
from app.core import oauth2

router = APIRouter(prefix="/export", tags=["export"])


JOB_FIELDS = {
    "title": "Job Title",
    "description": "Job Description",
    "salary_min": "Min. Salary",
    "salary_max": "Max. Salary",
    "personal_rating": "Personal Rating",
    "url": "Job URL",
    "deadline": "Application Deadline",
    "note": "Note",
    "attendance_type": "Attendance Type",
    "application_date": "Application Date",
    "application_url": "Application URL",
    "application_status": "Application Status",
    "application_note": "Application Note",
    "applied_via": "Applied Via",
    "created_at": "Created At",
    "modified_at": "Last Modified At",
}

COMPANY_FIELDS = {
    "name": "Company Name",
    "url": "Website",
    "description": "Description",
    "created_at": "Created At",
    "modified_at": "Last Modified At",
}

PERSON_FIELDS = {
    "first_name": "First Name",
    "last_name": "Last Name",
    "email": "Email",
    "phone": "Phone",
    "role": "Role",
    "linkedin_url": "LinkedIn URL",
    "created_at": "Created At",
    "modified_at": "Last Modified At",
}

AGGREGATOR_FIELDS = {
    "name": "Aggregator Name",
    "url": "Website",
    "created_at": "Created At",
    "modified_at": "Last Modified At",
}

SPECULATIVE_APPLICATION_FIELDS = {
    "date": "Application Date",
    "note": "Notes",
    "contact_email": "Contact Email",
    "created_at": "Created At",
    "modified_at": "Last Modified At",
}

SCRAPED_JOB_FIELDS = {
    "external_job_id": "External Job ID",
    "platform": "Source",
    "title": "Job Title",
    "description": "Job Description",
    "salary_min": "Min. Salary",
    "salary_max": "Max. Salary",
    "url": "Job URL",
    "deadline": "Application Deadline",
    "location": "Location",
    "attendance_type": "Attendance Type",
    "company": "Company",
    "created_at": "Created At",
    "modified_at": "Last Modified At",
}


def query_for_owner(
    db,
    model,
    current_owner: models.User,
) -> list[Any]:
    """Return all records for the current owner.
    :param db: Database session
    :param model: SQLAlchemy model to query
    :param current_owner: Current user
    :return: List of model instances belonging to the current owner"""

    return db.query(model).filter(model.owner_id == current_owner.id).all()


def write_csv(
    headers: list[str],
    rows: Iterable[list[Any]],
) -> str:
    """Write CSV content to a string.
    :param headers: List of CSV headers
    :param rows: Iterable of rows, each row is a list of values
    :return: CSV content as a string"""

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(headers)
    for row in rows:
        writer.writerow(row)
    return output.getvalue()


def get_model_rows(
    instance,
    fields: dict,
) -> list[Any]:
    """Extract ordered field values from a SQLAlchemy model.
    :param instance: SQLAlchemy model instance
    :param fields: Dictionary of field names to extract
    :return: List of field values in the order of the fields dictionary"""

    return [getattr(instance, field) for field in fields]


@router.get("/")
def export_all(
    db=Depends(database.get_db),
    current_user=Depends(oauth2.get_current_user),
) -> StreamingResponse:
    """Export all user data as a ZIP of CSV files.
    :param db: Database session
    :param current_user: Current authenticated user"""

    mem_zip = io.BytesIO()

    with zipfile.ZipFile(mem_zip, "w", zipfile.ZIP_DEFLATED) as zf:

        # Jobs
        jobs = query_for_owner(db, models.Job, current_user)
        job_rows = []
        for job in jobs:
            job_rows.append(
                get_model_rows(job, JOB_FIELDS)
                + [
                    job.company.name if job.company else "",
                    job.location.name if job.location else "",
                    job.source.name if job.source else "",
                    job.application_aggregator.name if job.application_aggregator else "",
                    "; ".join(k.name for k in job.keywords),
                    "; ".join(f"{p.first_name} {p.last_name}" for p in job.contacts),
                    "; ".join(f"{i.date:%Y-%m-%d} ({i.type}) (notes: {i.note})" for i in job.interviews),
                    "; ".join(f"{u.date:%Y-%m-%d} ({u.type}) (notes: {u.note})" for u in job.updates),
                ]
            )
        zf.writestr(
            "jobs.csv",
            write_csv(
                list(JOB_FIELDS.values())
                + [
                    "Company",
                    "Location",
                    "Source Aggregator",
                    "Application Aggregator",
                    "Keywords",
                    "Contacts",
                    "Interviews",
                    "Updates",
                ],
                job_rows,
            ),
        )

        # People
        people = query_for_owner(db, models.Person, current_user)
        zf.writestr(
            "people.csv",
            write_csv(
                list(PERSON_FIELDS.values()) + ["Company"],
                [get_model_rows(p, PERSON_FIELDS) + [p.company.name if p.company else ""] for p in people],
            ),
        )

        # Companies
        companies = query_for_owner(db, models.Company, current_user)
        zf.writestr(
            "companies.csv",
            write_csv(
                list(COMPANY_FIELDS.values()) + ["People"],
                [
                    get_model_rows(c, COMPANY_FIELDS) + ["; ".join(f"{p.first_name} {p.last_name}" for p in c.persons)]
                    for c in companies
                ],
            ),
        )

        # Aggregators
        aggregators = query_for_owner(db, models.Aggregator, current_user)
        zf.writestr(
            "aggregators.csv",
            write_csv(
                list(AGGREGATOR_FIELDS.values()),
                [get_model_rows(a, AGGREGATOR_FIELDS) for a in aggregators],
            ),
        )

        # Speculative Applications
        spec_apps = query_for_owner(db, models.SpeculativeApplication, current_user)
        zf.writestr(
            "speculative_applications.csv",
            write_csv(
                list(SPECULATIVE_APPLICATION_FIELDS.values()) + ["Company"],
                [
                    get_model_rows(sa, SPECULATIVE_APPLICATION_FIELDS) + [sa.company.name if sa.company else ""]
                    for sa in spec_apps
                ],
            ),
        )

        # Scraped Jobs
        scraped_jobs = query_for_owner(db, models.ScrapedJob, current_user)
        zf.writestr(
            "scraped_jobs.csv",
            write_csv(
                list(SCRAPED_JOB_FIELDS.values()) + ["Rating"],
                [
                    get_model_rows(sj, SCRAPED_JOB_FIELDS) + [sj.job_rating.overall_score if sj.job_rating else None]
                    for sj in scraped_jobs
                ],
            ),
        )

    mem_zip.seek(0)
    return StreamingResponse(
        mem_zip,
        media_type="application/x-zip-compressed",
        headers={"Content-Disposition": "attachment; filename=all_exports.zip"},
    )
