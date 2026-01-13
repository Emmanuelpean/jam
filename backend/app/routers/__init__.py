"""CRUD router generator for data table operations.

Provides a factory function to generate FastAPI routers with standard CRUD endpoints,
including user ownership validation, query filtering, and many-to-many relationship handling."""

from typing import Any, Callable

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Query
from sqlalchemy.orm import Session
from starlette import status
from starlette.requests import Request

from app import database, models
from app.core import oauth2

NOT_ALLOWED_EXCEPTION = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="Not authorised to perform requested action",
)


def filter_out_non_owned(
    entry: Any,
    current_user_id: int,
    processed_objects: set = None,
) -> Any:
    """Recursively filter out related objects that don't belong to the current user.
    :param entry: The SQLAlchemy model instance to filter
    :param current_user_id: The ID of the current user
    :param processed_objects: Set to track processed objects (prevents infinite recursion)
    :return: The filtered SQLAlchemy model instance"""

    if processed_objects is None:
        processed_objects = set()

    # Avoid infinite recursion
    obj_id = id(entry)
    if obj_id in processed_objects:
        return entry
    processed_objects.add(obj_id)

    # Get the SQLAlchemy mapper for this object
    if not hasattr(entry, "__mapper__"):
        return entry

    mapper = entry.__mapper__

    # Iterate through all relationships
    for relationship_prop in mapper.relationships:
        attr_name = relationship_prop.key
        related_value = getattr(entry, attr_name, None)

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
                        filtered_item = filter_out_non_owned(item, current_user_id, processed_objects)
                        filtered_list.append(filtered_item)
                else:
                    # Keep items without owner_id (like system data)
                    filtered_item = filter_out_non_owned(item, current_user_id, processed_objects)
                    filtered_list.append(filtered_item)

            # Replace the relationship with filtered list
            setattr(entry, attr_name, filtered_list)

        # Handle single relationships (many-to-one, one-to-one)
        else:
            if hasattr(related_value, "owner_id"):
                if related_value.owner_id != current_user_id:
                    # Set to None if not owned by current user
                    setattr(entry, attr_name, None)
                else:
                    # Recursively filter the related object
                    filtered_related = filter_out_non_owned(related_value, current_user_id, processed_objects)
                    setattr(entry, attr_name, filtered_related)
            else:
                # Keep and recursively filter items without owner_id
                filtered_related = filter_out_non_owned(related_value, current_user_id, processed_objects)
                setattr(entry, attr_name, filtered_related)

    return entry


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

    def convert_value(value, column) -> Any:
        """Convert a single value to the appropriate type based on column type."""
        # Handle null values
        if isinstance(value, str) and value.lower() == "null":
            return None

        # Try to convert to appropriate type based on column type
        try:
            if hasattr(column.type, "python_type"):
                python_type = column.type.python_type
                if python_type == int:
                    return int(value)
                elif python_type == float:
                    return float(value)
                elif python_type == bool:
                    return value.lower() in ("true", "1", "yes", "on")
            return value
        except (ValueError, TypeError, AttributeError):
            return value

    for param_name, param_value in filter_params.items():
        if not hasattr(table_model, param_name):
            continue

        col = getattr(table_model, param_name)

        # Handle list values
        if isinstance(param_value, list):
            converted_values = [convert_value(val, col) for val in param_value]
            query = query.filter(col.in_(converted_values))

        # Handle single values
        else:
            converted_value = convert_value(param_value, col)
            if converted_value is None:
                query = query.filter(col.is_(None))
            else:
                query = query.filter(col == converted_value)

    return query


def assert_admin(user: models.User) -> None:
    """Check if the user is an admin.
    :param user: The user to check."""

    if not user.is_admin:
        raise NOT_ALLOWED_EXCEPTION


def generate_data_table_crud_router(
    *,
    table_model,
    create_schema=None,
    update_schema=None,
    out_schema=None,
    endpoint: str,
    not_found_msg: str = "Entry not found",
    many_to_many_fields: dict | None = None,
    router: APIRouter | None = None,
    admin_only: bool = False,
    allowed_actions: list[str] | None = None,
    transform: None | Callable = None,
    check_settings: None | Callable = None,
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
    :param allowed_actions: List of allowed actions (get, post, put, delete). If None, all are allowed.
    :param transform: Optional function to transform the data before saving.
    :param check_settings: Optional function to check that the operation is allowed by the settings before create or update.
    :return: Configured APIRouter instance with CRUD endpoints."""

    if router is None:
        router = APIRouter(prefix=f"/{endpoint}", tags=[endpoint])

    NOT_FOUND_EXCEPTION = HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=not_found_msg)

    if allowed_actions is None:
        allowed_actions = ["get", "post", "put", "delete"]

    def check_admin(current_user: models.User) -> None:
        """Raise an exception if the table is for admins only and if the user is not an admin.
        :param current_user: The current authenticated user."""

        if admin_only and not current_user.is_admin:
            raise NOT_ALLOWED_EXCEPTION

    def check_ownership(
        entry: Any,
        current_user: models.User,
    ) -> None:
        """Raise an exception if the user does not own the entry (if the entry has an owner_id field).
        :param entry: The database entry.
        :param current_user: The current authenticated user."""

        if hasattr(entry, "owner_id") and entry.owner_id != current_user.id:
            raise NOT_ALLOWED_EXCEPTION

    def upsert_many_to_many(
        db: Session,
        entry_id: int,
        item_data: dict,
        owner_id: int,
        clear_existing: bool = False,
    ):
        """Handle creation or update of many-to-many relationships with owner check.
        Ensures that if the entry being linked has an owner_id, it matches the current user's ID.
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
                    related_obj = db.query(related_model).filter(related_model.id == value_id).first()
                    if not related_obj:
                        continue

                    if not hasattr(related_obj, "owner_id") or getattr(related_obj, "owner_id") == owner_id:
                        db.execute(association_table.insert().values(**{local_key: entry_id, remote_key: value_id}))

    # ------------------------------------------------------- GET ------------------------------------------------------

    if "get" in allowed_actions or "get_all" in allowed_actions:

        @router.get("/", response_model=list[out_schema])  # noqa
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
            :return: List of entries.
            :raises: HTTPException with a 403 status code if not authorised to perform the requested action."""

            # Check if admin rights are needed
            check_admin(current_user)

            # Start with base query
            if not admin_only:
                query = db.query(table_model).filter(table_model.owner_id == current_user.id)
            elif current_user.is_admin:
                query = db.query(table_model)
            else:
                raise NOT_ALLOWED_EXCEPTION

            # Get all query parameters and handle multiple values
            filter_params = {}
            for key in request.query_params.keys():
                if key != "limit":  # Skip limit parameter
                    values = request.query_params.getlist(key)
                    # If only one value, store as single value; otherwise store as list
                    filter_params[key] = values[0] if len(values) == 1 else values

            query = filter_query(query, table_model, filter_params)

            results = query.limit(limit).all()
            return [filter_out_non_owned(result, current_user.id) for result in results]

    if "get" in allowed_actions or "get_one" in allowed_actions:

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

            # Check if admin rights are needed
            check_admin(current_user)

            # Get the entry
            entry = db.query(table_model).filter(table_model.id == entry_id).first()
            if not entry:
                raise NOT_FOUND_EXCEPTION

            # Ensure that the user is authorised to view this entry
            check_ownership(entry, current_user)

            return filter_out_non_owned(entry, current_user.id)

    # ------------------------------------------------------ POST ------------------------------------------------------

    if "post" in allowed_actions:

        @router.post("/", status_code=status.HTTP_201_CREATED, response_model=out_schema)
        def create(
            item: create_schema,  # noqa
            db: Session = Depends(database.get_db),
            current_user: models.User = Depends(oauth2.get_current_user),
        ):
            """Create a new entry.
            :param item: Data for the new entry.
            :param db: Database session.
            :param current_user: Authenticated user.
            :return: The created entry.
            :raises: HTTPException with a 403 status code if not authorised to perform the requested action."""

            # Check if admin rights are needed
            check_admin(current_user)

            # Check settings if a check function is provided
            if check_settings:
                check_settings(db, item)

            # Enforce a maximum of 10,000 entries
            counts = db.query(table_model).count()
            if counts >= 10_000:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Maximum number of entries reached")

            # Extract the item data and exclude many-to-many fields from main creation
            item_dict = item.model_dump()
            if transform:
                item_dict.update(transform(item_dict, db))

            # Remove many-to-many fields from main creation data
            main_data = item_dict.copy()
            m2m_data = {}

            if many_to_many_fields:
                for field_name in many_to_many_fields.keys():
                    if field_name in main_data:
                        m2m_data[field_name] = main_data.pop(field_name)

            # Add the owner id if the table has an owner_id field
            if hasattr(table_model, "owner_id"):
                main_data["owner_id"] = current_user.id

            # Create the main entry
            new_entry = table_model(**main_data)
            db.add(new_entry)
            try:
                db.commit()
                db.refresh(new_entry)
            except IntegrityError as e:
                db.rollback()
                if "duplicate key value violates unique constraint" in str(e.orig):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Update would violate a unique constraint",
                    )

            # Handle many-to-many relationships
            if m2m_data:
                upsert_many_to_many(db, new_entry.id, m2m_data, current_user.id)
                db.commit()
                db.refresh(new_entry)

            return filter_out_non_owned(new_entry, current_user.id)

    # ------------------------------------------------------- PUT ------------------------------------------------------

    if "put" in allowed_actions:

        @router.put("/{entry_id}", status_code=status.HTTP_200_OK, response_model=out_schema)
        def update(
            entry_id: int,
            item: update_schema,  # noqa
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

            # Check if admin rights are needed
            check_admin(current_user)

            # Check settings if a check function is provided
            if check_settings:
                check_settings(db, item)

            # Get the entry to update
            entry = db.query(table_model).filter(table_model.id == entry_id).first()
            if not entry:
                raise NOT_FOUND_EXCEPTION

            # Ensure that the user is authorised to modify this entry
            check_ownership(entry, current_user)

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

            # Apply transform to the merged data (existing entry + updates)
            if transform:
                merged_data = {c.name: getattr(entry, c.name) for c in entry.__table__.columns}
                merged_data.update(main_data)
                transformed_data = transform(merged_data, db)
                main_data.update(transformed_data)

            # Update the record
            for field, value in main_data.items():
                if isinstance(value, dict):
                    for k, v in value.items():
                        setattr(getattr(entry, field), k, v)
                else:
                    setattr(entry, field, value)

            # Handle many-to-many relationships
            if m2m_data:
                upsert_many_to_many(db, entry_id, m2m_data, current_user.id, True)

            try:
                db.commit()
                db.refresh(entry)
            except IntegrityError as e:
                db.rollback()
                if "duplicate key value violates unique constraint" in str(e.orig):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Update would violate a unique constraint",
                    )

            # Return the updated entry
            return filter_out_non_owned(entry, current_user.id)

    # ----------------------------------------------------- DELETE -----------------------------------------------------

    if "delete" in allowed_actions:

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

            # Check if admin rights are needed
            check_admin(current_user)

            # Get the entry to delete
            query = db.query(table_model).filter(table_model.id == entry_id)
            entry = query.first()
            if not entry:
                raise NOT_FOUND_EXCEPTION

            # Ensure that the user is authorised to delete this entry
            check_ownership(entry, current_user)

            # Delete many-to-many relationships first if they exist
            if many_to_many_fields:
                for field_name, m2m_config in many_to_many_fields.items():
                    association_table = m2m_config["table"]
                    local_key = m2m_config["local_key"]

                    db.execute(association_table.delete().where(getattr(association_table.c, local_key) == entry_id))

            query.delete(synchronize_session=False)
            db.commit()

    return router
