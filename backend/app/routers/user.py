"""User route"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from app import utils, models, oauth2, database, schemas
from app.routers import filter_query

user_router = APIRouter(prefix="/users", tags=["users"])


def assert_admin(user: models.User) -> None:
    """Check if the user is an admin.
    :param user: The user to check."""

    if not user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorised to view this resource")


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

    assert_admin(current_user)

    query = db.query(models.User)

    # Get all query parameters
    filter_params = dict(request.query_params)
    query = filter_query(query, models.User, filter_params)

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

    assert_admin(current_user)

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

    user_update = user_update.model_dump(exclude_defaults=True)

    # Hash password if it's being updated
    if "password" in user_update:
        user_update["password"] = utils.hash_password(user_update["password"])

    # Determine if the user is updating the password or email
    requires_password_check = "password" in user_update or "email" in user_update

    # Get the user record to update
    # noinspection PyTypeChecker
    user_db = db.query(models.User).filter(models.User.id == current_user.id).first()
    current_password = user_update.get("current_password", "")

    # Update password/email
    if requires_password_check and not utils.verify_password(current_password, user_db.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="The current password is required")

    # Validate email
    # noinspection PyTypeChecker
    other_users = db.query(models.User).filter(models.User.id != current_user.id).all()
    emails = [u.email for u in other_users]
    if "email" in user_update and user_update["email"] in emails:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    # Update the user record
    for field, value in user_update.items():
        setattr(user_db, field, value)

    db.commit()
    db.refresh(user_db)
    return user_db


@user_router.put("/{entry_id}", response_model=schemas.UserOut)
def update_user(
    entry_id: int | None,
    user_update: schemas.UserUpdate,
    current_user: models.User = Depends(oauth2.get_current_user),
    db: Session = Depends(database.get_db),
):
    """Update a user by ID."""

    assert_admin(current_user)

    user_update = user_update.model_dump(exclude_defaults=True)

    # Hash password if it's being updated
    if "password" in user_update:
        user_update["password"] = utils.hash_password(user_update["password"])

    # Get the user record to update
    # noinspection PyTypeChecker
    user_db = db.query(models.User).filter(models.User.id == entry_id).first()

    # Validate email
    # noinspection PyTypeChecker
    other_users = db.query(models.User).filter(models.User.id != entry_id).all()
    emails = [u.email for u in other_users]
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

    # noinspection PyTypeChecker
    settings = db.query(models.Setting).filter(models.Setting.name == "allowlist").all()
    if settings:
        emails_allowed = settings[0].value.split(",")
        if user.email not in emails_allowed:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email not allowed")

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

    return new_user
