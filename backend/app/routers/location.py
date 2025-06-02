"""Location route"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app import models, database, schemas, oauth2
from app.routers.utils import _get_all_entries, _get_entry_by_id, _update_entry, _create_entry, _delete_entry

router = APIRouter(prefix="/locations", tags=["locations"])


@router.get("/", response_model=list[schemas.LocationOut])
def get_all_locations(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(oauth2.get_current_user),
    limit: int = 10,
):
    """Get all locations for the current user.
    :param db: The database session.
    :param current_user: The current user.
    :param limit: The maximum number of locations to return.
    :returns: A list of locations."""

    return _get_all_entries(
        table=models.Location,
        db=db,
        current_user=current_user,
        limit=limit,
    )


@router.get("/{location_id}", response_model=schemas.LocationOut)
def get_location(
    location_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(oauth2.get_current_user),
):
    """Get a location by ID.
    :param location_id: The location ID.
    :param db: The database session.
    :param current_user: The current user.
    :returns: The location if found."""

    return _get_entry_by_id(
        table=models.Location,
        entry_id=location_id,
        db=db,
        current_user=current_user,
        not_found_message="Location not found",
    )


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.LocationOut)
def create_location(
    location: schemas.Location,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(oauth2.get_current_user),
):
    """Create a new location.
    :param location: The location data.
    :param db: The database session.
    :param current_user: The current user.
    :returns: The created location."""

    return _create_entry(
        table=models.Location,
        entry_data=location,
        db=db,
        current_user=current_user,
    )


@router.delete("/{location_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_location(
    location_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(oauth2.get_current_user),
):
    """Delete a location by ID.
    :param location_id: The location ID.
    :param db: The database session.
    :param current_user: The current user.
    :returns: Dict with deletion status message."""

    return _delete_entry(
        table=models.Location,
        entry_id=location_id,
        db=db,
        current_user=current_user,
        not_found_message="Location not found",
    )


@router.put("/{location_id}", response_model=schemas.LocationOut)
def update_location(
    location_id: int,
    updated_location: schemas.LocationUpdate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(oauth2.get_current_user),
):
    """Update a location by ID.
    :param location_id: The location ID.
    :param updated_location: The updated location data.
    :param db: The database session.
    :param current_user: The current user.
    :returns: The updated location."""

    return _update_entry(
        table=models.Location,
        entry_id=location_id,
        updated_data=updated_location,
        db=db,
        current_user=current_user,
        not_found_message="Location not found",
    )
