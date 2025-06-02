"""Database CRUD Operations Module

This module provides a collection of reusable CRUD (Create, Read, Update, Delete) functions
for database operations across different entity types. These functions abstract common
database interaction patterns to promote code reuse and maintainability across routes.

The functions in this module:
- Handle database querying with owner-based filtering
- Provide appropriate error handling for common cases (not found, unauthorized)
- Support flexible partial updates
- Follow consistent patterns for database session management

Each function is designed to work with SQLAlchemy ORM models and FastAPI dependency injection,
making them suitable for use in route handlers throughout the application.

Example usage:
    @router.get("/{item_id}", response_model=schemas.ItemOut)
    def get_item(item_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
        return _get_entry_by_id(models.Item, item_id, db, current_user, "Item not found")"""

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app import models, schemas


def _get_all_entries(
    table: models.Base,
    db: Session,
    current_user: models.User,
    limit: int = 10,
):
    """Get all entries of a specific table for the current user.
    :param table: The table model class.
    :param db: The database session.
    :param current_user: The current user.
    :param limit: The maximum number of entries to return.
    :returns: A list of entries."""

    return db.query(table).filter(table.owner_id == current_user.id).limit(limit).all()


def _get_entry_by_id(
    table: models.Base,
    entry_id: int,
    db: Session,
    current_user: models.User,
    not_found_message: str = "Entry not found",
):
    """Get an entry by ID.
    :param table: The table model class.
    :param entry_id: The entry ID.
    :param db: The database session.
    :param current_user: The current user.
    :param not_found_message: Custom error message if entry is not found.
    :returns: The entry if found.
    :raises: HTTPException with 404 status code if entry not found.
    :raises: HTTPException with 403 status code if not authorized to perform requested action."""

    entry = db.query(table).filter(table.id == entry_id).first()

    if not entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=not_found_message)

    if entry.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action")

    return entry


def _create_entry(
    table: models.Base,
    entry_data: schemas.BaseModel,
    db: Session,
    current_user: models.User,
):
    """Create a new entry.
    :param table: The table model class.
    :param entry_data: The data for the new entry.
    :param db: The database session.
    :param current_user: The current user.
    :returns: The created entry."""

    new_entry = table(**entry_data.model_dump(), owner_id=current_user.id)
    db.add(new_entry)
    db.commit()
    db.refresh(new_entry)
    return new_entry


def _delete_entry(
    table: models.Base,
    entry_id: int,
    db: Session,
    current_user: models.User,
    not_found_message: str = "Entry not found",
):
    """Delete an entry by ID.
    :param table: The table model class.
    :param entry_id: The entry ID.
    :param db: The database session.
    :param current_user: The current user.
    :param not_found_message: Custom error message if entry is not found.
    :returns: Dict with deletion status message.
    :raises: HTTPException with 404 status code if entry not found.
    :raises: HTTPException with 403 status code if not authorized to perform requested action."""

    entry_query = db.query(table).filter(table.id == entry_id)
    entry = entry_query.first()

    if not entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=not_found_message)

    if entry.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action")

    entry_query.delete(synchronize_session=False)
    db.commit()

    return entry_query


def _update_entry(
    table: models.Base,
    entry_id: int,
    updated_data: schemas.BaseModel,
    db: Session,
    current_user: models.User,
    not_found_message: str = "Entry not found",
):
    """Update an entry by ID.
    :param table: The table model class.
    :param entry_id: The entry ID.
    :param updated_data: The updated data.
    :param db: The database session.
    :param current_user: The current user.
    :param not_found_message: Custom error message if entry is not found.
    :returns: The updated entry.
    :raises: HTTPException with 404 status code if entry not found.
    :raises: HTTPException with 403 status code if not authorized to perform requested action."""

    entry_query = db.query(table).filter(table.id == entry_id)
    entry = entry_query.first()

    if not entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=not_found_message)

    if entry.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action")

    # Check if there are fields to update
    updated_dict = updated_data.model_dump(exclude_defaults=True)
    if not updated_dict:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No fields provided for update")

    # Update the entry with the new data
    entry_query.update(updated_dict, synchronize_session=False)
    db.commit()

    # Return the updated entry
    return entry_query.first()
