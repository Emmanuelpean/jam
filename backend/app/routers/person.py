"""Person route"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app import models, database, schemas, oauth2
from app.routers.utils import _get_all_entries, _get_entry_by_id, _update_entry, _create_entry, _delete_entry

router = APIRouter(prefix="/persons", tags=["persons"])


@router.get("/", response_model=list[schemas.PersonOut])
def get_all_persons(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(oauth2.get_current_user),
    limit: int = 10,
):
    """Get all persons for the current user.
    :param db: The database session.
    :param current_user: The current user.
    :param limit: The maximum number of persons to return.
    :returns: A list of persons."""

    return _get_all_entries(
        table=models.Person,
        db=db,
        current_user=current_user,
        limit=limit,
    )


@router.get("/{person_id}", response_model=schemas.PersonOut)
def get_person(
    person_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(oauth2.get_current_user),
):
    """Get a person by ID.
    :param person_id: The person ID.
    :param db: The database session.
    :param current_user: The current user.
    :returns: The person if found."""

    return _get_entry_by_id(
        table=models.Person,
        entry_id=person_id,
        db=db,
        current_user=current_user,
        not_found_message="Person not found",
    )


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.PersonOut)
def create_person(
    person: schemas.Person,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(oauth2.get_current_user),
):
    """Create a new person.
    :param person: The person data.
    :param db: The database session.
    :param current_user: The current user.
    :returns: The created person."""

    return _create_entry(
        table=models.Person,
        entry_data=person,
        db=db,
        current_user=current_user,
    )


@router.delete("/{person_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_person(
    person_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(oauth2.get_current_user),
):
    """Delete a person by ID.
    :param person_id: The person ID.
    :param db: The database session.
    :param current_user: The current user.
    :returns: Dict with deletion status message."""

    return _delete_entry(
        table=models.Person,
        entry_id=person_id,
        db=db,
        current_user=current_user,
        not_found_message="Person not found",
    )


@router.put("/{person_id}", response_model=schemas.PersonOut)
def update_person(
    person_id: int,
    updated_person: schemas.PersonUpdate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(oauth2.get_current_user),
):
    """Update a person by ID.
    :param person_id: The person ID.
    :param updated_person: The updated person data.
    :param db: The database session.
    :param current_user: The current user.
    :returns: The updated person."""

    return _update_entry(
        table=models.Person,
        entry_id=person_id,
        updated_data=updated_person,
        db=db,
        current_user=current_user,
        not_found_message="Person not found",
    )
