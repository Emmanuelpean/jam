"""API router for dashboard data"""

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app import models, database, oauth2, schemas

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/")
def get_dashboard_data(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(oauth2.get_current_user),
) -> dict:
    """Get dashboard data including job applications, interviews, and job application updates.
    :param db: Database session
    :param current_user: Authenticated user"""

    now = datetime.now(timezone.utc)

    # ---------------------------------------------------- ALL DATA ----------------------------------------------------

    # Jobs
    job_query = db.query(models.Job).filter(models.Job.owner_id == current_user.id)
    jobs = job_query.all()

    # Job Applications (jobs with an application date or status)
    job_application_query = job_query.filter(
        or_(models.Job.application_date.isnot(None), models.Job.application_status.isnot(None))
    )
    job_applications = job_application_query.all()

    # Pending Job Applications (not rejected or withdrawn)
    job_application_pending = job_application_query.filter(
        models.Job.application_status.notin_(["rejected", "withdrawn"])
    ).all()

    # Interviews
    interview_query = db.query(models.Interview).filter(models.Interview.owner_id == current_user.id)
    interviews = interview_query.all()

    # Job Application Updates
    updates = (
        db.query(models.JobApplicationUpdate).filter(models.JobApplicationUpdate.owner_id == current_user.id).all()
    )

    # --------------------------------------------------- STATISTICS ---------------------------------------------------

    statistics = {
        "jobs": len(jobs),
        "job_applications": len(job_applications),
        "job_application_pending": len(job_application_pending),
        "interviews": len(interviews),
    }

    # -------------------------------------------------- NEED CHASING --------------------------------------------------

    needs_chase = []
    for job in job_application_pending:
        # Convert job application to Pydantic schema to access computed fields
        job_schema = schemas.JobOut.model_validate(job, from_attributes=True)

        # If we have a last update date, check if it's older than the threshold
        last_update = job_schema.days_since_last_update
        snooze_date = job_schema.followup_snooze_datetime
        if last_update is not None and last_update > current_user.chase_threshold:
            if snooze_date is not None and snooze_date > now:
                continue
            needs_chase.append(job_schema)

    # ----------------------------------------------------- UPDATES ----------------------------------------------------

    # Create unified update objects
    all_updates = []

    # Add job applications as "Application" updates
    for job in job_applications:
        if job.application_date is not None:
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
    all_updates = all_updates[: current_user.update_limit]

    # ---------------------------------------------- UPCOMING INTERVIEWS -----------------------------------------------

    upcoming_interviews = interview_query.filter(models.Interview.date >= now).order_by(models.Interview.date).all()
    upcoming_interviews = [
        schemas.InterviewOut.model_validate(interview, from_attributes=True) for interview in upcoming_interviews
    ]

    # --------------------------------=-------------- UPCOMING DEADLINES -----------------------------------------------

    upcoming_deadlines = (
        job_query.filter(models.Job.application_date.is_(None), models.Job.application_status.is_(None))
        .filter((models.Job.deadline - now) <= timedelta(days=current_user.deadline_threshold))
        .filter((models.Job.deadline - now) > timedelta(days=0))
        .order_by(models.Job.deadline)
        .all()
    )
    upcoming_deadlines = [schemas.JobOut.model_validate(job, from_attributes=True) for job in upcoming_deadlines]

    return dict(
        statistics=statistics,
        needs_chase=needs_chase,
        all_updates=all_updates,
        upcoming_interviews=upcoming_interviews,
        upcoming_deadlines=upcoming_deadlines,
    )
