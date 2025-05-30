"""Aggregator route"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app import database, models, oauth2, schemas
from app.routers.utils import _get_all_entries, _get_entry_by_id, _update_entry, _create_entry, _delete_entry

router = APIRouter(prefix="/aggregators", tags=["aggregators"])


@router.get("/", response_model=list[schemas.AggregatorOut])
def get_all_aggregators(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(oauth2.get_current_user),
    limit: int = 10,
):
    """Get all aggregator aggregators.
    :param db: The database session.
    :param current_user: The current user.
    :param limit: The maximum number of aggregators to return.
    :returns: A list of aggregator aggregators."""

    return _get_all_entries(
        table=models.Aggregator,
        db=db,
        current_user=current_user,
        limit=limit,
    )


@router.get("/{aggregator_id}", response_model=schemas.AggregatorOut)
def get_aggregator(
    aggregator_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(oauth2.get_current_user),
):
    """Get an aggregator aggregator by ID.
    :param aggregator_id: The aggregator ID.
    :param db: The database session.
    :param current_user: The current user.
    :returns: The aggregator aggregator if found."""

    return _get_entry_by_id(
        table=models.Aggregator,
        entry_id=aggregator_id,
        db=db,
        current_user=current_user,
        not_found_message="Aggregator not found",
    )


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.AggregatorOut)
def create_aggregator(
    aggregator: schemas.Aggregator,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(oauth2.get_current_user),
):
    """Create a new aggregator aggregator.
    :param aggregator: The aggregator data.
    :param db: The database session.
    :param current_user: The current user.
    :returns: The created aggregator."""

    return _create_entry(
        table=models.Aggregator,
        entry_data=aggregator,
        db=db,
        current_user=current_user,
    )


@router.delete("/{aggregator_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_aggregator(
    aggregator_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(oauth2.get_current_user),
):
    """Delete an aggregator aggregator by ID.
    :param aggregator_id: The aggregator ID.
    :param db: The database session.
    :param current_user: The current user.
    :returns: Dict with deletion status message."""

    return _delete_entry(
        table=models.Aggregator,
        entry_id=aggregator_id,
        db=db,
        current_user=current_user,
        not_found_message="Aggregator not found",
    )


@router.put("/{aggregator_id}", response_model=schemas.AggregatorOut)
def update_aggregator(
    aggregator_id: int,
    updated_aggregator: schemas.AggregatorUpdate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(oauth2.get_current_user),
):
    """Update an aggregator aggregator by ID.
    :param aggregator_id: The aggregator ID.
    :param updated_aggregator: The updated aggregator data.
    :param db: The database session.
    :param current_user: The current user.
    :returns: The updated aggregator."""

    return _update_entry(
        table=models.Aggregator,
        entry_id=aggregator_id,
        updated_data=updated_aggregator,
        db=db,
        current_user=current_user,
        not_found_message="Aggregator not found",
    )
