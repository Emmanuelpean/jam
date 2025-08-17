"""User route"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from app import utils, models, oauth2, database, schemas

user_router = APIRouter(prefix="/users", tags=["users"])


@user_router.get("/", response_model=list[schemas.UserOut])
def get_all_users(
    request: Request,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(oauth2.get_current_user),
):
    """Retrieve all users.
    :param request: FastAPI request object to access query parameters
    :param db: Database session.
    :param current_user: Authenticated user.
    :return: List of entries."""

    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view this resource")

    # noinspection PyTypeChecker
    query = db.query(models.User)

    # Get all query parameters
    filter_params = dict(request.query_params)

    # Apply filters for each parameter that matches a table column
    for param_name, param_value in filter_params.items():
        if hasattr(models.User, param_name):
            column = getattr(models.User, param_name)

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

    return query.all()


@user_router.get("/me", response_model=schemas.UserOut)
def get_current_user_profile(current_user: models.User = Depends(oauth2.get_current_user)):
    """Get the current user's profile.
    :param current_user: The current authenticated user."""

    return current_user


@user_router.get("/{entry_id}", response_model=schemas.UserOut)
def get_one_user(
    entry_id: int | None,
    current_user: models.User = Depends(oauth2.get_current_user),
    db: Session = Depends(database.get_db),
):
    """Get a user by ID."""

    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view this resource")

    # noinspection PyTypeChecker
    user = db.query(models.User).filter(models.User.id == entry_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@user_router.put("/me", response_model=schemas.UserOut)
def update_current_user_profile(
    user_update: schemas.UserUpdate,
    current_user: models.User = Depends(oauth2.get_current_user),
    db: Session = Depends(database.get_db),
):
    """Update the current user's profile.
    :param user_update: The user update data.
    :param current_user: The current authenticated user.
    :param db: The database session."""

    return update_user(current_user.id, user_update, current_user, db)


@user_router.put("/{entry_id}", response_model=schemas.UserOut)
def update_user(
    entry_id: int | None,
    user_update: schemas.UserUpdate,
    current_user: models.User = Depends(oauth2.get_current_user),
    db: Session = Depends(database.get_db),
):
    """Update a user by ID."""

    # Allow only admins or the matching user to update the data
    if not (current_user.is_admin or current_user.id == entry_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view this resource")

    user_update = user_update.model_dump(exclude_defaults=True)

    # Validate theme if provided
    if "theme" in user_update:
        valid_themes = ["strawberry", "blueberry", "raspberry", "mixed-berry", "forest-berry", "blackberry"]
        if user_update["theme"] not in valid_themes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid theme. Must be one of: {', '.join(valid_themes)}",
            )

    # Hash password if it's being updated
    if "password" in user_update:
        user_update["password"] = utils.hash_password(user_update["password"])

    # Get the user record to update
    # noinspection PyTypeChecker
    user_db = db.query(models.User).filter(models.User.id == entry_id).first()
    if not current_user.is_admin and not utils.verify_password(
        user_update.get("current_password", ""), user_db.password
    ):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect password")

    # Validate email
    users = db.query(models.User).filter(models.User.id != entry_id).all()
    emails = [u.email for u in users]
    if "email" in user_update and user_update["email"] in emails:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    # Update the user record
    for field, value in user_update.items():
        setattr(user_db, field, value)

    db.commit()
    db.refresh(user_db)
    return user_db


@user_router.post("/", status_code=201, response_model=schemas.UserOut)
def create_user(
    user: schemas.UserCreate,
    db: Session = Depends(database.get_db),
):
    """Create a new user.
    :param user: The user data.
    :param db: The database session."""

    # Get all users and check if the email is already registered
    users = db.query(models.User).all()
    emails = [u.email for u in users]
    if user.email in emails:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    # Hash the password and create the user
    user.password = utils.hash_password(user.password)
    # noinspection PyArgumentList
    new_user = models.User(**user.model_dump())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Add the remote location
    # noinspection PyArgumentList
    remote_location = models.Location(owner_id=new_user.id, remote=True)
    db.add(remote_location)

    return new_user
