"""Router for tour-related endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from starlette import status

from app import database, models
from app.core.oauth2 import get_current_user

tour_router = APIRouter(prefix="/tour", tags=["tour"])


@tour_router.post("/clear-all", status_code=status.HTTP_204_NO_CONTENT)
def clear_all_tour_data(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Delete all tour data (is_tour=True) for the current user across all entities."""

    uid = current_user.id

    # Children before parents to respect FK constraints
    for obj in db.query(models.JobEmail).filter_by(owner_id=uid, is_tour=True).all():
        db.delete(obj)
    for obj in db.query(models.Interview).filter_by(owner_id=uid, is_tour=True).all():
        db.delete(obj)
    for obj in db.query(models.JobApplicationUpdate).filter_by(owner_id=uid, is_tour=True).all():
        db.delete(obj)
    for obj in db.query(models.SpeculativeApplication).filter_by(owner_id=uid, is_tour=True).all():
        db.delete(obj)
    db.flush()

    for obj in db.query(models.JobRating).filter_by(owner_id=uid, is_tour=True).all():
        db.delete(obj)
    for obj in db.query(models.ScrapedJob).filter_by(owner_id=uid, is_tour=True).all():
        db.delete(obj)
    for obj in db.query(models.UserQualification).filter_by(owner_id=uid, is_tour=True).all():
        db.delete(obj)
    for obj in db.query(models.Job).filter_by(owner_id=uid, is_tour=True).all():
        db.delete(obj)
    db.flush()

    for obj in db.query(models.Person).filter_by(owner_id=uid, is_tour=True).all():
        db.delete(obj)
    for obj in db.query(models.Company).filter_by(owner_id=uid, is_tour=True).all():
        db.delete(obj)
    for obj in db.query(models.Keyword).filter_by(owner_id=uid, is_tour=True).all():
        db.delete(obj)
    for obj in db.query(models.Aggregator).filter_by(owner_id=uid, is_tour=True).all():
        db.delete(obj)
    for obj in db.query(models.ScrapingExclusionFilter).filter_by(owner_id=uid, is_tour=True).all():
        db.delete(obj)

    db.commit()