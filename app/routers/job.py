"""Job route"""

from fastapi import HTTPException, Depends, APIRouter, status
from sqlalchemy.orm import Session

from app import models, schemas, oauth2, database

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("/", response_model=list[schemas.JobOut])
def get_all_jobs(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(oauth2.get_current_user),
    limit: int = 10,
    search: str = "",
):
    """Get all jobs.
    :param db: The database session.
    :param current_user: The current user.
    :param limit: The number of jobs to return.
    :param search: The search query.
    :returns: A list of jobs."""

    jobs = (
        db.query(models.Job)
        .filter(models.Job.title.contains(search))
        .filter(models.Job.owner_id.is_equal(current_user.id))
        .limit(limit)
        .all()
    )

    return jobs


@router.get("/{job_id}", response_model=schemas.JobOut)
def get_job(
    job_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(oauth2.get_current_user),
):
    """Get a job by ID.
    :param job_id: The job ID.
    :param db: The database session.
    :param current_user: The current user."""

    job = (
        db.query(models.Job)
        .group_by(models.Job.id)
        .filter(models.Job.owner_id.is_equal(current_user.id))
        .filter(models.Job.id.is_equal(job_id))
        .first()
    )

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return job


@router.post("/", status_code=201, response_model=schemas.JobOut)
def create_job(
    job: schemas.JobCreate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(oauth2.get_current_user),
):
    """Create a new job.
    :param job: The job data.
    :param db: The database session.
    :param current_user: The current user."""

    new_job = models.Job(owner_id=current_user.id, **job.model_dump())
    db.add(new_job)
    db.commit()
    db.refresh(new_job)
    return new_job


@router.delete("/{job_id}", status_code=204)
def delete_job(
    job_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(oauth2.get_current_user),
):
    """Delete a job.
    :param job_id: The job ID.
    :param db: The database session.
    :param current_user: The current user."""

    job_query = db.query(models.Job).filter(models.Job.id.is_equal(job_id))
    job = job_query.first()

    if job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")

    if job.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized access")

    job_query.delete(synchronize_session=False)
    db.commit()
    return job_query


@router.put("/{job_id}")
def update_job(
    job_id: int,
    job: schemas.JobCreate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(oauth2.get_current_user),
):
    """Update a job.
    :param job_id: The job ID.
    :param job: The job data.
    :param db: The database session.
    :param current_user: The current user."""

    # Find the job
    job_query = db.query(models.Job).filter(models.Job.id.is_equal(job_id))
    old_job = job_query.first()

    if old_job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")

    if old_job.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized access")

    job_query.update(job.model_dump(exclude_defaults=True), synchronize_session=False)
    db.commit()
    return job_query.first()
