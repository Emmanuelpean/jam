"""CRUD router generator for data table operations.

Provides a factory function to generate FastAPI routers with standard CRUD endpoints,
including user ownership validation, query filtering, and many-to-many relationship handling."""

from typing import Any

from sqlalchemy.orm import Query
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status
from starlette.requests import Request

from app import database, models, oauth2


def filter_owned_relationships(
    obj: Any,
    current_user_id: int,
    processed_objects: set = None,
) -> Any:
    """Recursively filter out related objects that don't belong to the current user.
    :param obj: The SQLAlchemy model instance to filter
    :param current_user_id: The ID of the current user
    :param processed_objects: Set to track processed objects (prevents infinite recursion)"""

    if processed_objects is None:
        processed_objects = set()

    # Avoid infinite recursion
    obj_id = id(obj)
    if obj_id in processed_objects:
        return obj
    processed_objects.add(obj_id)

    # Get the SQLAlchemy mapper for this object
    if not hasattr(obj, "__mapper__"):
        return obj

    mapper = obj.__mapper__

    # Iterate through all relationships
    for relationship_prop in mapper.relationships:
        attr_name = relationship_prop.key
        related_value = getattr(obj, attr_name, None)

        if related_value is None:
            continue

        # Handle list relationships (one-to-many, many-to-many)
        if isinstance(related_value, list):
            filtered_list = []
            for item in related_value:
                # Check if item has owner_id and if it matches current user
                if hasattr(item, "owner_id"):
                    if item.owner_id == current_user_id:
                        # Recursively filter this item too
                        filtered_item = filter_owned_relationships(item, current_user_id, processed_objects)
                        filtered_list.append(filtered_item)
                else:
                    # Keep items without owner_id (like system data)
                    filtered_item = filter_owned_relationships(item, current_user_id, processed_objects)
                    filtered_list.append(filtered_item)

            # Replace the relationship with filtered list
            setattr(obj, attr_name, filtered_list)

        # Handle single relationships (many-to-one, one-to-one)
        else:
            if hasattr(related_value, "owner_id"):
                if related_value.owner_id != current_user_id:
                    # Set to None if not owned by current user
                    setattr(obj, attr_name, None)
                else:
                    # Recursively filter the related object
                    filtered_related = filter_owned_relationships(related_value, current_user_id, processed_objects)
                    setattr(obj, attr_name, filtered_related)
            else:
                # Keep and recursively filter items without owner_id
                filtered_related = filter_owned_relationships(related_value, current_user_id, processed_objects)
                setattr(obj, attr_name, filtered_related)

    return obj


def filter_query(
    query: Query,
    table_model,
    filter_params: dict,
) -> Query:
    """Apply filters to a SQLAlchemy query based on provided parameters.
    :param query: The SQLAlchemy query object.
    :param table_model: The SQLAlchemy model class representing the table.
    :param filter_params: Dict of parameters to filter by (e.g., from request query).
    :return: The filtered query object."""

    for param_name, param_value in filter_params.items():
        if hasattr(table_model, param_name):
            column = getattr(table_model, param_name)

            # Handle null values - convert string "null" to actual None/NULL
            if param_value.lower() == "null":
                query = query.filter(column.is_(None))
                continue

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
                # noinspection PyTypeChecker
                query = query.filter(column == param_value)

            except (ValueError, TypeError):
                # If conversion fails, treat as string comparison
                # noinspection PyTypeChecker
                query = query.filter(column == param_value)

    return query


def generate_data_table_crud_router(
    *,
    table_model,
    create_schema,
    update_schema,
    out_schema,
    endpoint: str,
    not_found_msg: str = "Entry not found",
    many_to_many_fields: dict | None = None,
    router: APIRouter | None = None,
    admin_only: bool = False,
) -> APIRouter:
    """Generate a FastAPI router with standard CRUD endpoints for a given table.
    :param table_model: SQLAlchemy model class representing the database table.
    :param create_schema: Pydantic schema used for creating new entries.
    :param update_schema: Pydantic schema used for updating existing entries.
    :param out_schema: Pydantic schema used for serialising output.
    :param endpoint: Endpoint name (used as route prefix and tag).
    :param not_found_msg: Default message when an entry is not found.
    :param many_to_many_fields: Dict defining M2M relationships.
                                Format: {'field_name': {
                                           'table': association_table,
                                           'local_key': 'local_foreign_key',
                                           'remote_key': 'remote_foreign_key'
                                           'related_model': RelatedModelClass}}
    :param router: Optional router to which the endpoints will be added.
    :param admin_only: If True, restrict access to admin users only.
    :return: Configured APIRouter instance with CRUD endpoints."""

    if router is None:
        router = APIRouter(prefix=f"/{endpoint}", tags=[endpoint])

    def check_authorisation(
        entry: Any,
        current_user: models.User,
    ) -> None:
        """Check if the user is allowed to perform the action on the entry.
        :param entry: The database entry.
        :param current_user: The current authenticated user."""

        error = HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorised to perform requested action",
        )

        # Raise the error if the table is admin only and the user is not an admin
        if admin_only and not current_user.is_admin:
            raise error

        # Raise the error if the entry has an owner_id and it does not match the current user's ID
        if hasattr(entry, "owner_id") and entry.owner_id != current_user.id:
            raise error

    def upsert_many_to_many(
        db: Session,
        entry_id: int,
        item_data: dict,
        owner_id: int,
        clear_existing: bool = False,
    ):
        """Handle creation or update of many-to-many relationships with owner check.
        ATTENTION: THIS IS NOT CURRENTLY COMPATIBLE WITH TABLES WITHOUT AN OWNER ID FIELD.
        :param db: Database session
        :param entry_id: ID of the entry to which the relationships are being added
        :param item_data: Data containing the relationships to be added
        :param owner_id: ID of the current user (owner)
        :param clear_existing: If True, delete existing relationships before adding new ones"""

        if not many_to_many_fields or not hasattr(table_model, "owner_id"):
            return

        for field_name, m2m_config in many_to_many_fields.items():
            if item_data.get(field_name) is not None:
                association_table = m2m_config["table"]
                local_key = m2m_config["local_key"]
                remote_key = m2m_config["remote_key"]
                related_model = m2m_config["related_model"]

                if clear_existing:
                    db.execute(association_table.delete().where(getattr(association_table.c, local_key) == entry_id))

                for value_id in item_data[field_name]:
                    # noinspection PyTypeChecker
                    related_obj = db.query(related_model).filter(related_model.id == value_id).first()
                    if related_obj and related_obj.owner_id == owner_id:
                        db.execute(association_table.insert().values(**{local_key: entry_id, remote_key: value_id}))

    # ------------------------------------------------------- GET ------------------------------------------------------

    # noinspection PyTypeHints
    @router.get("/", response_model=list[out_schema])
    def get_all(
        request: Request,
        db: Session = Depends(database.get_db),
        current_user: models.User = Depends(oauth2.get_current_user),
        limit: int | None = None,
    ):
        """Retrieve all entries for the current user.
        :param request: FastAPI request object to access query parameters
        :param db: Database session.
        :param current_user: Authenticated user.
        :param limit: Maximum number of entries to return.
        :return: List of entries."""

        # Start with base query
        if not admin_only:
            # noinspection PyTypeChecker
            query = db.query(table_model).filter(table_model.owner_id == current_user.id)
        elif current_user.is_admin:
            query = db.query(table_model)
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Not authorised to perform requested action"
            )

        # Get all query parameters except 'limit'
        filter_params = dict(request.query_params)
        filter_params.pop("limit", None)  # Remove limit from filters
        query = filter_query(query, table_model, filter_params)

        results = query.limit(limit).all()
        filtered_results = [filter_owned_relationships(result, current_user.id) for result in results]
        return filtered_results

    # noinspection PyTypeHints
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

        # noinspection PyTypeChecker
        entry = db.query(table_model).filter(table_model.id == entry_id).first()

        if not entry:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=not_found_msg)

        check_authorisation(entry, current_user)

        return filter_owned_relationships(entry, current_user.id)

    # ------------------------------------------------------ POST ------------------------------------------------------

    # noinspection PyTypeHints
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

        if admin_only and not current_user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Not authorised to perform requested action"
            )

        # Extract the item data and exclude many-to-many fields from main creation
        item_dict = item.model_dump()

        # Remove many-to-many fields from main creation data
        main_data = item_dict.copy()
        m2m_data = {}

        if many_to_many_fields:
            for field_name in many_to_many_fields.keys():
                if field_name in main_data:
                    m2m_data[field_name] = main_data.pop(field_name)

        if hasattr(table_model, "owner_id"):
            main_data["owner_id"] = current_user.id

        # Create the main entry
        new_entry = table_model(**main_data)
        db.add(new_entry)
        db.commit()
        db.refresh(new_entry)

        # Handle many-to-many relationships
        if m2m_data:
            upsert_many_to_many(db, new_entry.id, m2m_data, current_user.id)
            db.commit()
            db.refresh(new_entry)

        return filter_owned_relationships(new_entry, current_user.id)

    # ------------------------------------------------------- PUT ------------------------------------------------------

    # noinspection PyTypeHints
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

        # noinspection PyTypeChecker
        query = db.query(table_model).filter(table_model.id == entry_id)
        entry = query.first()

        if not entry:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=not_found_msg)

        check_authorisation(entry, current_user)

        # Extract the item data
        item_dict = item.model_dump(exclude_unset=True)

        if not item_dict:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No fields provided for update")

        # Separate main fields from many-to-many fields
        main_data = item_dict.copy()
        m2m_data = {}

        if many_to_many_fields:
            for field_name in many_to_many_fields.keys():
                if field_name in main_data:
                    m2m_data[field_name] = main_data.pop(field_name)

        # Update main fields if any
        if main_data:
            query.update(main_data, synchronize_session=False)

        # Handle many-to-many relationships
        if m2m_data:
            upsert_many_to_many(db, entry_id, m2m_data, current_user.id, True)

        db.commit()

        # Return the updated entry
        return filter_owned_relationships(query.first(), current_user.id)

    # ----------------------------------------------------- DELETE -----------------------------------------------------

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

        # noinspection PyTypeChecker
        query = db.query(table_model).filter(table_model.id == entry_id)
        entry = query.first()

        if not entry:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=not_found_msg)

        check_authorisation(entry, current_user)

        # Delete many-to-many relationships first if they exist
        if many_to_many_fields:
            for field_name, m2m_config in many_to_many_fields.items():
                association_table = m2m_config["table"]
                local_key = m2m_config["local_key"]

                db.execute(association_table.delete().where(getattr(association_table.c, local_key) == entry_id))

        query.delete(synchronize_session=False)
        db.commit()

    return router
