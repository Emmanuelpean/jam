"""User route"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app import database, schemas
from app import utils, models, oauth2

user_router = APIRouter(prefix="/users", tags=["users"])


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
    new_user = models.User(**user.model_dump())

    # Add the user to the database, commit it and refresh to get the user ID
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


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


@user_router.get("/", response_model=list[schemas.UserOut])
def get_user(db: Session = Depends(database.get_db)):
    """Get all users.
    :param db: The database session."""

    user = db.query(models.User).all()
    return user


auth_router = APIRouter(tags=["Authentication"])


@auth_router.post("/login", status_code=status.HTTP_200_OK, response_model=schemas.Token)
def login(
    user_credentials: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(database.get_db),
) -> dict:
    """Login a user.
    :param user_credentials: The user credentials (note: username is the email field).
    :param db: The database session.
    :returns: The access token."""

    # Find the user in the list based on the email provided
    user = db.query(models.User).filter(user_credentials.username.strip() == models.User.email).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User not found")

    # Check that the password correspond to that user
    if not utils.verify_password(user_credentials.password, user.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Incorrect password")

    # Create an access token and return it
    access_token = oauth2.create_access_token(data={"user_id": user.id})
    return {"access_token": access_token, "token_type": "bearer"}
