"""Authentication route"""

from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app import utils, models, database, schemas, oauth2

login_router = APIRouter(prefix="/login", tags=["Login"])


@login_router.post("/", status_code=status.HTTP_200_OK, response_model=schemas.Token)
def login(
    user_credentials: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(database.get_db),
) -> dict:
    """Login a user.
    :param user_credentials: The user credentials (note: username is the email field).
    :param db: The database session.
    :returns: The access token.
    :raises HTTPException with a 403 status code if the credentials are invalid."""

    # Find the user in the list based on the email provided
    user = db.query(models.User).filter(user_credentials.username.strip() == models.User.email).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid credentials")

    # Check that the user is active
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User account is inactive")

    # Check that the password corresponds to that user
    if not utils.verify_password(user_credentials.password, user.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid credentials")

    # Update the user last login
    user.last_login = datetime.now(timezone.utc)
    db.commit()

    # Create an access token and return it
    access_token = oauth2.create_access_token(data={"user_id": user.id})
    return {"access_token": access_token, "token_type": "bearer"}


register_router = APIRouter(prefix="/register", tags=["Register"])


@register_router.post("/", status_code=201, response_model=schemas.UserOut)
def create_user(
    user: schemas.UserRegister,
    db: Session = Depends(database.get_db),
):
    """Create a new user.
    :param user: The user data.
    :param db: The database session."""

    # Check the user can be created
    settings = db.query(models.Setting).filter(models.Setting.name == "allowlist").first()
    if settings and settings.is_active:
        emails_allowed = settings.value.split(",")
        if user.email not in emails_allowed:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email not allowed")

    # Get all users and check if the email is already registered
    users = db.query(models.User).all()
    emails = [u.email for u in users]
    if user.email in emails:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    # Hash the password and create the user
    user.password = utils.hash_password(user.password)
    new_user = models.User(**user.model_dump())  # noqa
    db.add(new_user)
    db.commit()

    return new_user
