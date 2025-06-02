"""User route"""

from fastapi import HTTPException, Depends, APIRouter, status
from sqlalchemy.orm import Session

from app import models, database, schemas, utils

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", status_code=201, response_model=schemas.UserOut)
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


@router.get("/{id}", response_model=schemas.UserOut)
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


@router.get("/", response_model=list[schemas.UserOut])
def get_user(db: Session = Depends(database.get_db)):
    """Get all users.
    :param db: The database session."""

    user = db.query(models.User).all()
    return user
