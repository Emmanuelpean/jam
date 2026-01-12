"""API router for exporting data"""

import csv
import io
import zipfile

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from app import database, models
from core import oauth2

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


@router.get("/")
def export_jobs_with_all_columns(
    db=Depends(database.get_db),
    current_user=Depends(oauth2.get_current_user),
) -> StreamingResponse:
    """Export jobs with all columns (except IDs) and related data as a single CSV file."""

    mem_zip = io.BytesIO()

    with zipfile.ZipFile(mem_zip, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        # Jobs
        jobs = db.query(models.Job).filter(models.Job.owner_id == current_user.id).all()
        job_output = io.StringIO()
        job_writer = csv.writer(job_output)
        additional_fields = [
            "Company",
            "Location",
            "Source Aggregator",
            "Application Aggregator",
            "Keywords",
            "Contacts",
            "Interviews",
            "Updates",
        ]
        job_writer.writerow(list(JOB_FIELDS.values()) + additional_fields)
        for job in jobs:
            row = [getattr(job, field) for field in JOB_FIELDS]
            company = job.company.name if job.company else ""
            location = job.location.name if job.location else ""
            source_agg = job.source.name if job.source else ""
            app_agg = job.application_aggregator.name if job.application_aggregator else ""
            keywords = "; ".join([k.name for k in job.keywords])
            contacts = "; ".join([f"{p.first_name} {p.last_name}" for p in job.contacts])
            interviews = "; ".join(
                [f"{i.date.strftime('%Y-%m-%d')} ({i.type}) (notes: {i.note})" for i in job.interviews]
            )
            updates = "; ".join([f"{u.date.strftime('%Y-%m-%d')} ({u.type}) (notes: {u.note})" for u in job.updates])
            job_writer.writerow(row + [company, location, source_agg, app_agg, keywords, contacts, interviews, updates])
        zf.writestr("jobs.csv", job_output.getvalue())

        # People
        people = db.query(models.Person).filter(models.Person.owner_id == current_user.id).all()
        people_output = io.StringIO()
        people_writer = csv.writer(people_output)
        people_writer.writerow(list(PERSON_FIELDS.values()) + ["Company"])
        for p in people:
            company_name = p.company.name if p.company else ""
            people_writer.writerow([getattr(p, field) for field in PERSON_FIELDS] + [company_name])
        zf.writestr("people.csv", people_output.getvalue())

        # Companies
        companies = db.query(models.Company).filter(models.Company.owner_id == current_user.id).all()
        companies_output = io.StringIO()
        companies_writer = csv.writer(companies_output)
        companies_writer.writerow(list(COMPANY_FIELDS.values()) + ["People"])
        for c in companies:
            people_list = "; ".join([f"{p.first_name} {p.last_name}" for p in c.persons])
            companies_writer.writerow([getattr(c, field) for field in COMPANY_FIELDS] + [people_list])
        zf.writestr("companies.csv", companies_output.getvalue())

        # Aggregators
        aggregators = db.query(models.Aggregator).filter(models.Aggregator.owner_id == current_user.id).all()
        aggregators_output = io.StringIO()
        aggregators_writer = csv.writer(aggregators_output)
        aggregators_writer.writerow(list(AGGREGATOR_FIELDS.values()))
        for a in aggregators:
            aggregators_writer.writerow([getattr(a, field) for field in AGGREGATOR_FIELDS])
        zf.writestr("aggregators.csv", aggregators_output.getvalue())

    mem_zip.seek(0)
    return StreamingResponse(
        mem_zip,
        media_type="application/x-zip-compressed",
        headers={"Content-Disposition": "attachment; filename=all_exports.zip"},
    )
