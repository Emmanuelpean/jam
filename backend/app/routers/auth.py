"""Authentication route"""

import hashlib
import os
import secrets
from datetime import datetime, timezone, timedelta
from random import randbytes

from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app import utils, models, database, schemas, oauth2
from app.emails.email_service import email_service

load_dotenv()

login_router = APIRouter(prefix="/login", tags=["Login"])


def send_verification_with_rate_limit(
    user: models.User,
    db: Session,
) -> dict:
    """Send verification email with rate limiting.
    :param user: user entry
    :param db: database session
    :return: Dictionary with success status and message
    :raises HTTPException if email sending fails"""

    # Check if enough time has passed since last email
    min_interval_seconds = int(os.getenv("VERIFICATION_EMAIL_MIN_INTERVAL_SECONDS"))
    if user.verification_code_created_at:
        time_since_last_email = datetime.now(timezone.utc) - user.verification_code_created_at
        if time_since_last_email < timedelta(seconds=min_interval_seconds):
            seconds_remaining = min_interval_seconds - int(time_since_last_email.total_seconds())
            return {
                "success": False,
                "message": f"Please wait {seconds_remaining} seconds before requesting another verification email",
                "seconds_remaining": seconds_remaining,
            }

    # Generate new verification token
    token = secrets.token_urlsafe(32)
    verification_code = hashlib.sha256(token.encode()).hexdigest()

    # Update user with new verification code and timestamp
    user.verification_code = verification_code
    user.verification_code_created_at = datetime.now(timezone.utc)
    db.commit()

    try:
        # Send verification email
        frontend_url = os.getenv("FRONTEND_URL")
        verification_url = f"{frontend_url}/verify-email/{token}"
        email_service.send_verification_email(user.email, verification_url)

        return {"success": True, "message": "Verification email sent successfully"}
    except Exception as e:
        return {"success": False, "message": f"Error sending verification email: {str(e)}"}


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

    # Check that the user is verified
    if not user.is_verified:
        result = send_verification_with_rate_limit(user, db)

        if result["success"]:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"User account is not verified. A new verification email has been sent to {user.email}.",
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=result["message"],
            )

    # Check that the password corresponds to that user
    if not utils.verify_password(user_credentials.password, user.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid credentials")

    # Update the user last login
    user.last_login = datetime.now(timezone.utc)
    db.commit()

    # Create an access token and return it
    access_token = oauth2.create_access_token(data={"user_id": user.id})
    return {"access_token": access_token, "token_type": "bearer"}


# ------------------------------------------------------ REGISTER ------------------------------------------------------


register_router = APIRouter(prefix="/register", tags=["Register"])


@register_router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.UserOut)
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
        emails_allowed = [email.strip() for email in settings.value.split(",")]
        if user.email not in emails_allowed:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email not allowed")

    # Check if email already exists
    existing_user = db.query(models.User).filter(models.User.email == user.email).first()

    if existing_user:
        # If user exists but is not verified, resend verification email
        if not existing_user.is_verified:
            result = send_verification_with_rate_limit(existing_user, db)

            if result["success"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered but not verified. A new verification email has been sent.",
                )
            else:
                raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=result["message"])
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    # Hash the password and create the user
    user.password = utils.hash_password(user.password)

    # Create user with verification code
    user_data = user.model_dump()
    new_user = models.User(**user_data)  # noqa
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    result = send_verification_with_rate_limit(new_user, db)
    if not result["success"]:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=result["message"])
    return new_user


@register_router.get("/verify-email/{token}")
def verify_email(
    token: str,
    db: Session = Depends(database.get_db),
) -> dict:
    """Verify a user's email address using the provided token.
    :param token: The verification token from the email.
    :param db: The database session."""

    expiration_hours = int(os.getenv("VERIFICATION_TOKEN_EXPIRATION_HOURS"))
    hashedCode = hashlib.sha256()
    hashedCode.update(bytes.fromhex(token))
    verification_code = hashedCode.hexdigest()

    user = db.query(models.User).filter(models.User.verification_code == verification_code).first()

    if not user:
        raise HTTPException(status_code=403, detail="Invalid or expired token")

    # Check if token is expired (e.g., 24 hours)
    if user.verification_code_created_at:
        expiration_time = user.verification_code_created_at + timedelta(hours=expiration_hours)
        if datetime.now(timezone.utc) > expiration_time:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Verification token has expired")

    user.verification_code = None
    user.verification_code_created_at = None
    user.is_verified = True
    db.commit()

    return {"message": "Account verified successfully"}
