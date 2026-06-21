"""Geolocation router"""

from fastapi import APIRouter, Body, Depends
from sqlalchemy.orm import Session

from app import models, database
from app.core import oauth2
from app.data_tables.schemas import GeolocationOut
from app.geolocation.geolocation import geocode_location

router = APIRouter(prefix="/geolocation", tags=["geolocation"])


@router.post("/", response_model=GeolocationOut)
def geolocate(
    string: str = Body(...),
    db: Session = Depends(database.get_db),
    _current_user: models.User = Depends(oauth2.get_current_user),
) -> models.Geolocation | None:
    """Geocode a location string."""

    return geocode_location(string, db)
