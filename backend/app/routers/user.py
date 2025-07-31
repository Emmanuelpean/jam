"""User route"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import utils, models, oauth2, database, schemas, config

user_router = APIRouter(prefix="/users", tags=["users"])


ALPHA_WHITELIST = [
    "emmanuel.pean@gmail.com",
    "jessicaaggood@live.co.uk",
]


def is_email_whitelisted(email: str) -> bool:
    return email.lower() in ALPHA_WHITELIST


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

    if config.settings.signup.lower() == "restricted" and not is_email_whitelisted(user.email):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email not authorised for alpha testing",
        )

    # Hash the password and create the user
    user.password = utils.hash_password(user.password)
    new_user = models.User(**user.model_dump())

    # Add the user to the database, commit it and refresh to get the user ID
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@user_router.get("/me", response_model=schemas.UserOut)
def get_current_user_profile(
    current_user: models.User = Depends(oauth2.get_current_user),
):
    """Get the current user's profile.
    :param current_user: The current authenticated user."""

    return current_user


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

    # Check if email is being updated and if it's already taken
    if "email" in user_update and user_update["email"] != current_user.email:
        existing_user = db.query(models.User).filter(models.User.email == user_update["email"]).first()
        if existing_user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

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

    # Apply updates
    for field, value in user_update.items():
        setattr(current_user, field, value)

    db.commit()
    db.refresh(current_user)
    return current_user


@user_router.get("/{id}", response_model=schemas.UserOut)
def get_user(
    user_id: int,
    db: Session = Depends(database.get_db),
):
    """Get a user by ID.
    :param user_id: The user ID.
    :param db: The database session."""

    user = db.query(models.User).filter(user_id == models.User.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
