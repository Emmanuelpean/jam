"""API router for dashboard data"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import models, database, oauth2, schemas

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/")
def get_dashboard_data(
    update_limit: int = 20,
    chase_threshold: int = 30,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(oauth2.get_current_user),
):
    """Get dashboard data including job applications, interviews, and job application updates.
    :param update_limit: Maximum number of updates to return
    :param chase_threshold: Number of days to check for follow-up
    :param db: Database session
    :param current_user: Authenticated user"""

    # ---------------------------------------------------- ALL DATA ----------------------------------------------------

    # noinspection PyTypeChecker
    job_query = db.query(models.Job).filter(models.Job.owner_id == current_user.id)
    jobs = job_query.filter(models.Job.application_date.isnot(None)).all()

    job_application_query = job_query.filter(models.Job.application_date.isnot(None))

    job_application_pending = job_application_query.filter(
        models.Job.application_status.notin_(["rejected", "withdrawn"])
    ).all()

    # noinspection PyTypeChecker
    interviews = db.query(models.Interview).filter(models.Interview.owner_id == current_user.id).all()

    # noinspection PyTypeChecker
    updates = (
        db.query(models.JobApplicationUpdate).filter(models.JobApplicationUpdate.owner_id == current_user.id).all()
    )

    # --------------------------------------------------- STATISTICS ---------------------------------------------------

    statistics = {
        "jobs": len(jobs),
        "job_applications": job_application_query.count(),
        "job_application_pending": len(job_application_pending),
        "interviews": len(interviews),
    }

    # -------------------------------------------------- NEED CHASING --------------------------------------------------

    # Filter by last update date in Python and prepare job data
    needs_chase = []
    for job in job_application_pending:
        # Convert job application to Pydantic schema to access computed fields
        job_schema = schemas.JobOut.model_validate(job, from_attributes=True)

        # If we have a last update date, check if it's older than the threshold
        if job_schema.days_since_last_update is not None:
            if job_schema.days_since_last_update > chase_threshold:
                needs_chase.append(job_schema)

    # ----------------------------------------------------- UPDATES ----------------------------------------------------

    # Create unified update objects
    all_updates = []

    # Add job applications as "Application" updates
    for job in jobs:
        job_out = schemas.JobOut.model_validate(job, from_attributes=True)
        update_item = {
            "data": job_out,
            "date": job_out.application_date,
            "type": "Application",
            "job": job_out,
        }
        all_updates.append(update_item)

    # Add interviews as "Interview" updates
    for interview in interviews:
        interview_out = schemas.InterviewOut.model_validate(interview, from_attributes=True)
        job_out = schemas.JobOut.model_validate(interview.job, from_attributes=True)
        update_item = {
            "data": interview_out,
            "date": interview_out.date,
            "type": "Interview",
            "job": job_out,
        }
        all_updates.append(update_item)

    # Add job application updates
    for update in updates:
        update_out = schemas.JobApplicationUpdateOut.model_validate(update, from_attributes=True)
        job_out = schemas.JobOut.model_validate(update.job, from_attributes=True)
        update_item = {
            "data": update_out,
            "date": update_out.date,
            "type": "Job Application Update",
            "job": job_out,
        }
        all_updates.append(update_item)

    # Sort by date (most recent first) and apply the limit
    all_updates.sort(key=lambda x: x["date"], reverse=True)
    all_updates = all_updates[:update_limit]

    return dict(statistics=statistics, needs_chase=needs_chase, all_updates=all_updates)
