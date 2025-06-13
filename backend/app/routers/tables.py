from fastapi import APIRouter, Depends, status, Request
from fastapi import HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app import models, database, oauth2, schemas


def generate_crud_router(
    *,
    table_model: models.Base,  # SQLAlchemy model
    create_schema: BaseModel,  # Pydantic schema for creation
    update_schema: BaseModel,  # Pydantic schema for updates
    out_schema: BaseModel,  # Pydantic schema for output
    endpoint: str,  # e.g. "companies"
    not_found_msg: str = "Entry not found",
) -> APIRouter:
    """Generate a FastAPI router with standard CRUD endpoints for a given table.

    :param table_model: SQLAlchemy model class representing the database table.
    :param create_schema: Pydantic schema used for creating new entries.
    :param update_schema: Pydantic schema used for updating existing entries.
    :param out_schema: Pydantic schema used for serialising output.
    :param endpoint: Endpoint name (used as route prefix and tag).
    :param not_found_msg: Default message when an entry is not found.
    :return: Configured APIRouter instance with CRUD endpoints.
    """
    router = APIRouter(prefix=f"/{endpoint}", tags=[endpoint])

    # noinspection PyTypeHints
    @router.get("/", response_model=list[out_schema])
    def get_all(
        request: Request,
        db: Session = Depends(database.get_db),
        current_user: models.User = Depends(oauth2.get_current_user),
        limit: int = 10,
    ):
        """Retrieve all entries for the current user.
        :param request: FastAPI request object to access query parameters
        :param db: Database session.
        :param current_user: Authenticated user.
        :param limit: Maximum number of entries to return.
        :return: List of entries."""

        # Start with base query
        query = db.query(table_model).filter(table_model.owner_id == current_user.id)

        # Get all query parameters except 'limit'
        filter_params = dict(request.query_params)
        filter_params.pop("limit", None)  # Remove limit from filters

        # Apply filters for each parameter that matches a table column
        for param_name, param_value in filter_params.items():
            if hasattr(table_model, param_name):
                column = getattr(table_model, param_name)

                # Handle different data types
                try:
                    # Try to convert to appropriate type based on column type
                    if hasattr(column.type, "python_type"):
                        if column.type.python_type == int:
                            param_value = int(param_value)
                        elif column.type.python_type == float:
                            param_value = float(param_value)
                        elif column.type.python_type == bool:
                            param_value = param_value.lower() in ("true", "1", "yes", "on")

                    # Add filter to query
                    query = query.filter(column == param_value)

                except (ValueError, TypeError):
                    # If conversion fails, treat as string comparison
                    query = query.filter(column == param_value)

        return query.limit(limit).all()

    @router.get("/{entry_id}", response_model=out_schema)
    def get_one(
        entry_id: int,
        db: Session = Depends(database.get_db),
        current_user: models.User = Depends(oauth2.get_current_user),
    ):
        """Get an entry by ID.
        :param entry_id: The entry ID.
        :param db: The database session.
        :param current_user: The current user.
        :returns: The entry if found.
        :raises: HTTPException with a 404 status code if the entry is not found.
        :raises: HTTPException with a 403 status code if not authorised to perform the requested action."""

        entry = db.query(table_model).filter(table_model.id == entry_id).first()

        if not entry:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=not_found_msg)

        if entry.owner_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action"
            )

        return entry

    @router.post("/", status_code=status.HTTP_201_CREATED, response_model=out_schema)
    def create(
        item: create_schema,
        db: Session = Depends(database.get_db),
        current_user: models.User = Depends(oauth2.get_current_user),
    ):
        """Create a new entry.
        :param item: Data for the new entry.
        :param db: Database session.
        :param current_user: Authenticated user.
        :return: The created entry."""

        new_entry = table_model(**item.model_dump(), owner_id=current_user.id)
        db.add(new_entry)
        db.commit()
        db.refresh(new_entry)
        return new_entry

    @router.put("/{entry_id}", response_model=out_schema)
    def update(
        entry_id: int,
        item: update_schema,
        db: Session = Depends(database.get_db),
        current_user: models.User = Depends(oauth2.get_current_user),
    ):
        """Update an entry by ID.
        :param entry_id: The entry ID.
        :param item: The updated data.
        :param db: The database session.
        :param current_user: The current user.
        :returns: The updated entry.
        :raises: HTTPException with a 404 status code if an entry is not found.
        :raises: HTTPException with a 403 status code if not authorised to perform the requested action.
        :raises: HTTPException with a 400 status code if no field is provided for the update."""

        entry_query = db.query(table_model).filter(table_model.id == entry_id)
        entry = entry_query.first()

        if not entry:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=not_found_msg)

        if entry.owner_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action"
            )

        # Check if there are fields to update
        updated_dict = item.model_dump(exclude_defaults=True)
        if not updated_dict:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No fields provided for update")

        # Update the entry with the new data
        entry_query.update(updated_dict, synchronize_session=False)
        db.commit()

        # Return the updated entry
        return entry_query.first()

    @router.delete("/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
    def delete(
        entry_id: int,
        db: Session = Depends(database.get_db),
        current_user: models.User = Depends(oauth2.get_current_user),
    ):
        """Delete an entry by ID.
        :param entry_id: The entry ID.
        :param db: The database session.
        :param current_user: The current user.
        :returns: Dict with a deletion status message.
        :raises: HTTPException with a 404 status code if an entry is not found.
        :raises: HTTPException with a 403 status code if not authorised to perform the requested action."""

        entry_query = db.query(table_model).filter(table_model.id == entry_id)
        entry = entry_query.first()

        if not entry:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=not_found_msg)

        if entry.owner_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action"
            )

        entry_query.delete(synchronize_session=False)
        db.commit()

        return entry_query

    return router


# Person router
person_router = generate_crud_router(
    table_model=models.Person,
    create_schema=schemas.Person,
    update_schema=schemas.PersonUpdate,
    out_schema=schemas.PersonOut,
    endpoint="persons",
    not_found_msg="Person not found",
)

# Company router
company_router = generate_crud_router(
    table_model=models.Company,
    create_schema=schemas.Company,
    update_schema=schemas.CompanyUpdate,
    out_schema=schemas.CompanyOut,
    endpoint="companies",
    not_found_msg="Company not found",
)

# Job router
job_router = generate_crud_router(
    table_model=models.Job,
    create_schema=schemas.Job,
    update_schema=schemas.JobUpdate,
    out_schema=schemas.JobOut,
    endpoint="jobs",
    not_found_msg="Job not found",
)

# Location router
location_router = generate_crud_router(
    table_model=models.Location,
    create_schema=schemas.Location,
    update_schema=schemas.LocationUpdate,
    out_schema=schemas.LocationOut,
    endpoint="locations",
    not_found_msg="Location not found",
)

# Aggregator router
aggregator_router = generate_crud_router(
    table_model=models.Aggregator,
    create_schema=schemas.Aggregator,
    update_schema=schemas.AggregatorUpdate,
    out_schema=schemas.AggregatorOut,
    endpoint="aggregators",
    not_found_msg="Aggregator not found",
)

# Interview router
interview_router = generate_crud_router(
    table_model=models.Interview,
    create_schema=schemas.Interview,
    update_schema=schemas.InterviewUpdate,
    out_schema=schemas.InterviewOut,
    endpoint="interviews",
    not_found_msg="Interview not found",
)

# JobApplication router
jobapplication_router = generate_crud_router(
    table_model=models.JobApplication,
    create_schema=schemas.JobApplication,
    update_schema=schemas.JobApplicationUpdate,
    out_schema=schemas.JobApplicationOut,
    endpoint="jobapplications",
    not_found_msg="Job Application not found",
)

# Keyword router
keyword_router = generate_crud_router(
    table_model=models.Keyword,
    create_schema=schemas.Keyword,
    update_schema=schemas.KeywordUpdate,
    out_schema=schemas.KeywordOut,
    endpoint="keywords",
    not_found_msg="Keyword not found",
)

# File router
file_router = generate_crud_router(
    table_model=models.File,
    create_schema=schemas.File,
    update_schema=schemas.FileUpdate,
    out_schema=schemas.FileOut,
    endpoint="files",
    not_found_msg="File not found",
)
