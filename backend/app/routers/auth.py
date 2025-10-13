"""Authentication route"""

import hashlib
from datetime import datetime, timezone, timedelta
from random import randbytes
from starlette.requests import Request
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app import utils, models, database, schemas, oauth2
from app.emails.email_service import email_service

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
async def create_user(
    request: Request,
    user: schemas.UserRegister,
    db: Session = Depends(database.get_db),
):
    """Create a new user.
    :param request: The request object to build the verification URL.
    :param user: The user data.
    :param db: The database session."""

    # Check the user can be created
    settings = db.query(models.Setting).filter(models.Setting.name == "allowlist").first()
    if settings:
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

    # Email verification
    token = randbytes(10)
    hashedCode = hashlib.sha256()
    hashedCode.update(token)
    verification_code = hashedCode.hexdigest()

    # Create user with verification code
    user_data = user.model_dump()
    user_data["verification_code"] = verification_code
    user_data["is_verified"] = False  # Explicitly set

    new_user = models.User(**user_data)  # noqa
    db.add(new_user)
    db.commit()
    db.refresh(new_user)  # Get the ID and updated fields

    try:
        # Construct verification URL with proper base URL
        base_url = f"{request.url.scheme}://{request.headers.get('host', request.client.host)}"
        url = f"{base_url}/verify-email/{token.hex()}"

        await email_service.send_verification_email(new_user.email, url)

        # Return user data, not a message
        return new_user
    except Exception as e:
        # Roll back the user creation if email fails
        db.delete(new_user)
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error sending verification email: {str(e)}"
        )


@register_router.get("/verify-email/{token}")
def verify_email(
    token: str,
    db: Session = Depends(database.get_db),
) -> dict:
    """Verify a user's email address using the provided token.
    :param token: The verification token from the email.
    :param db: The database session."""

    hashedCode = hashlib.sha256()
    hashedCode.update(bytes.fromhex(token))
    verification_code = hashedCode.hexdigest()

    user = db.query(models.User).filter(models.User.verification_code == verification_code).first()

    if not user:
        raise HTTPException(status_code=403, detail="Invalid or expired token")

    # Check if token is expired (e.g., 24 hours)
    if user.verification_code_created_at:
        expiration_time = user.verification_code_created_at + timedelta(hours=24)  # TODO expirition
        if datetime.now(timezone.utc) > expiration_time:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Verification token has expired")

    user.verification_code = None
    user.verification_code_created_at = None
    user.is_verified = True
    db.commit()

    return {"message": "Account verified successfully"}
