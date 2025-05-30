"""Job route"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app import database, models, oauth2, schemas
from app.routers.utils import _get_all_entries, _get_entry_by_id, _update_entry, _create_entry, _delete_entry

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("/", response_model=list[schemas.JobOut])
def get_all_jobs(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(oauth2.get_current_user),
    limit: int = 10,
):
    """Get all jobs for the current user.
    :param db: The database session.
    :param current_user: The current user.
    :param limit: The maximum number of jobs to return.
    :returns: A list of jobs."""

    return _get_all_entries(
        table=models.Job,
        db=db,
        current_user=current_user,
        limit=limit,
    )


@router.get("/{job_id}", response_model=schemas.JobOut)
def get_job(
    job_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(oauth2.get_current_user),
):
    """Get a job by ID.
    :param job_id: The job ID.
    :param db: The database session.
    :param current_user: The current user.
    :returns: The job if found."""

    return _get_entry_by_id(
        table=models.Job,
        entry_id=job_id,
        db=db,
        current_user=current_user,
        not_found_message="Job not found",
    )


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.JobOut)
def create_job(
    job: schemas.Job,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(oauth2.get_current_user),
):
    """Create a new job.
    :param job: The job data.
    :param db: The database session.
    :param current_user: The current user.
    :returns: The created job."""

    return _create_entry(
        table=models.Job,
        entry_data=job,
        db=db,
        current_user=current_user,
    )


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_job(
    job_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(oauth2.get_current_user),
):
    """Delete a job by ID.
    :param job_id: The job ID.
    :param db: The database session.
    :param current_user: The current user.
    :returns: Dict with deletion status message."""

    return _delete_entry(
        table=models.Job,
        entry_id=job_id,
        db=db,
        current_user=current_user,
        not_found_message="Job not found",
    )


@router.put("/{job_id}", response_model=schemas.JobOut)
def update_job(
    job_id: int,
    updated_job: schemas.JobUpdate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(oauth2.get_current_user),
):
    """Update a job by ID.
    :param job_id: The job ID.
    :param updated_job: The updated job data.
    :param db: The database session.
    :param current_user: The current user.
    :returns: The updated job."""

    return _update_entry(
        table=models.Job,
        entry_id=job_id,
        updated_data=updated_job,
        db=db,
        current_user=current_user,
        not_found_message="Job not found",
    )
