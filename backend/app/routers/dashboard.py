import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import models, database, oauth2, schemas

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
