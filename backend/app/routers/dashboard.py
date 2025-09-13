"""API router for dashboard data"""

import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import models, database, oauth2, schemas
from app.schemas import BaseModel

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


class UpdateItem(BaseModel):
    data: dict[str, schemas.JobOut | schemas.InterviewOut | schemas.JobApplicationUpdateOut]
    date: datetime.datetime
    type: str
    job: schemas.JobOut


class DashboardResponse(BaseModel):
    statistics: dict[str, int]
    needs_chase: list[schemas.JobOut]
    updates: list[UpdateItem]


@router.get("/", response_model=DashboardResponse)
def get_dashboard_data(
    update_limit: int = 20,
    chase_threshold: int = 30,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(oauth2.get_current_user),
) -> DashboardResponse:
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

        if (job_schema.last_update_date - datetime.datetime.now(datetime.UTC)) > datetime.timedelta(
            days=chase_threshold
        ):
            needs_chase.append(job)

    # ----------------------------------------------------- UPDATES ----------------------------------------------------

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
    for update in updates:
        update_item = {
            "data": update,
            "date": update.date,
            "type": "Job Application Update",
            "job": update.job,
        }
        all_updates.append(update_item)

    # Sort by date (most recent first) and apply the limit
    all_updates.sort(key=lambda x: x["date"], reverse=True)
    all_updates = all_updates[:update_limit]

    print(all_updates)

    return DashboardResponse(statistics=statistics, needs_chase=needs_chase, updates=all_updates)
