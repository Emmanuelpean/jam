"""Authentication route"""

from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app import utils, models, database, schemas, oauth2

router = APIRouter(tags=["Authentication"])


@router.post("/login", status_code=status.HTTP_200_OK, response_model=schemas.Token)
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

    # Update the user last login
    user.last_login = datetime.now(timezone.utc)
    db.commit()

    # Create an access token and return it
    access_token = oauth2.create_access_token(data={"user_id": user.id})
    return {"access_token": access_token, "token_type": "bearer"}
