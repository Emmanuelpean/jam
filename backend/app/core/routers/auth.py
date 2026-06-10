"""Authentication route"""

import datetime as dt
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app import utils, models, database, base_schemas
from app.config import settings
from app.core import schemas, oauth2
from app.core.models import get_setting_value, TokenType
from app.core.utils import (
    send_rate_limited_tokenized_email_verification_email,
    send_rate_limited_tokenized_password_reset_email,
    get_token,
)
from app.demo.seed import seed_demo_data
from app.emails.email_service import email_service


# -------------------------------------------------------- LOGIN -------------------------------------------------------


def _assert_not_maintenance(db: Session) -> None:
    """Raise 401 if maintenance mode is currently active."""

    maintenance_scheduled_at = get_setting_value(db, "maintenance_scheduled_at", None)
    if maintenance_scheduled_at:
        try:
            scheduled_time = dt.datetime.fromisoformat(maintenance_scheduled_at)
            if scheduled_time.tzinfo is None:
                scheduled_time = scheduled_time.replace(tzinfo=dt.timezone.utc)
            if scheduled_time <= dt.datetime.now(dt.timezone.utc):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Service is currently under maintenance.",
                )
        except ValueError:
            pass


login_router = APIRouter(prefix="/login", tags=["Login"])


@login_router.post("/", status_code=status.HTTP_200_OK, response_model=schemas.Token)
def login(
    user_credentials: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(database.get_db),
    demo_db: Session = Depends(database.get_demo_db),
) -> dict[str, str]:
    """Log in a user.
    :param user_credentials: The user credentials (note: username is the email field)
    :param db: The database session
    :param demo_db: The demo database session
    :returns: The access token dictionary
    :raises HTTPException with a 403 status code if the credentials are invalid
    :raises HTTPException with a 401 status code if the user is not active or not verified
    :raises HTTPException with a 429 status code if verification email rate limit is exceeded"""

    user_email = utils.clean_email(user_credentials.username)

    if settings.test_mode and user_email == "crash@crash.com":
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

    # Find the user in the list based on the email provided
    user = db.query(models.User).filter(models.User.email == user_email).first()

    # Handle demo user login: create a temp user in the demo schema with seeded data
    if user is not None and user.is_demo:
        _assert_not_maintenance(db)
        try:
            demo_email = f"demo-{uuid.uuid4().hex[:12]}@demo.jam"
            demo_user = models.User(
                email=demo_email,
                password=utils.hash_password(uuid.uuid4().hex),
                is_demo=True,
                is_active=True,
                is_verified=True,
                first_name="Demo",
                last_name="User",
                last_login=dt.datetime.now(dt.timezone.utc),
                premium={"is_active": True, "job_scraping_active": True, "job_rating_active": True},
            )
            demo_db.add(demo_user)
            demo_db.commit()
            demo_db.refresh(demo_user)

            seed_demo_data(demo_db, demo_user)

            access_token = oauth2.create_access_token(
                data={"user_id": demo_user.id},
                token_version=demo_user.token_version,
                is_demo=True,
            )
            return {"access_token": access_token, "token_type": "bearer"}
        except Exception:
            demo_db.rollback()
            raise

    # Check that the user exists and verify the password
    if user is None or not utils.verify_password(user_credentials.password, user.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid credentials.")

    # Check that the user is active
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User account is not active.")

    # Check that the user is verified
    if not user.is_verified:
        result = send_rate_limited_tokenized_email_verification_email(user, db)

        # Raise appropriate exception based on email sending result
        if result.success:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"User account is not verified. A new verification email has been sent to {user.email}.",
            )
        else:
            error_code = result.error_code if result.error_code else status.HTTP_500_INTERNAL_SERVER_ERROR
            if error_code == status.HTTP_429_TOO_MANY_REQUESTS:
                message = (
                    "Your account is not verified. Please check your emails for the verification link or "
                    + result.message.lower()
                )
            else:
                message = result.message
            raise HTTPException(status_code=error_code, detail=message)

    # Block non-admin users from logging in during maintenance
    if not user.is_admin:
        _assert_not_maintenance(db)

    # Save the last login date and update the last login date
    user.previous_login = user.last_login
    user.last_login = dt.datetime.now(dt.timezone.utc)
    db.commit()

    # Create an access token and return it
    access_token = oauth2.create_access_token(
        data={"user_id": user.id},
        token_version=user.token_version,
    )
    return {"access_token": access_token, "token_type": "bearer"}


# ------------------------------------------------------ REGISTER ------------------------------------------------------


register_router = APIRouter(prefix="/register", tags=["Register"])


@register_router.post("/", status_code=status.HTTP_201_CREATED, response_model=base_schemas.GenericResponse)
def create_user(
    user: schemas.UserRegister,
    db: Session = Depends(database.get_db),
) -> base_schemas.GenericResponse:
    """Create a new user
    :param user: The user data
    :param db: The database session
    :returns: Dictionary with success status and message
    :raises HTTPException with a 400 status code if the email is already registered
    :raises HTTPException with a 401 status code if the user is not allowed to sign up"""

    _assert_not_maintenance(db)

    # Check the user can be created
    allowlist = models.get_setting_value(db, "allowlist", None)
    if allowlist is not None:
        emails_allowed = [utils.clean_email(email) for email in allowlist.split(",")]
        if user.email not in emails_allowed:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="You are not allowed to sign up for now.",
            )

    # Check if email already exists
    existing_user = db.query(models.User).filter(models.User.email == user.email).first()

    if existing_user:
        # If user exists but is not verified, resend verification email
        if not existing_user.is_verified:
            result = send_rate_limited_tokenized_email_verification_email(existing_user, db)
            if result.success:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=f"Email already registered but not verified. "
                    f"A new verification email has been sent to {existing_user.email}.",
                )
            else:
                error_code = result.error_code if result.error_code else status.HTTP_500_INTERNAL_SERVER_ERROR
                raise HTTPException(status_code=error_code, detail=result.message)
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    # Hash the password and create the user
    user.password = utils.hash_password(user.password)

    # Create user with related tables
    user_data = user.model_dump()
    new_user = models.User(**user_data)  # noqa
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Send verification email
    result = send_rate_limited_tokenized_email_verification_email(new_user, db)
    if not result.success:
        # Rollback user creation if email fails
        db.delete(new_user)
        db.commit()
        error_code = result.error_code if result.error_code else status.HTTP_500_INTERNAL_SERVER_ERROR
        raise HTTPException(status_code=error_code, detail=result.message)

    return result


@register_router.get("/verify-email/{token}", response_model=base_schemas.GenericResponse)
def verify_email(
    token: str,
    db: Session = Depends(database.get_db),
) -> dict[str, str | bool]:
    """Verify a user's email address using the provided token
    :param token: The verification token from the email
    :param db: The database session
    :raises HTTPException with a 403 status code if the token does not exist
    :raises HTTPException with a 403 status code if the token has expired
    :return: Success message upon successful verification"""

    _assert_not_maintenance(db)

    verification_code = utils.hash_token(token)
    token_entry = get_token(verification_code, TokenType.EMAIL_VERIFICATION, db)

    if not token_entry:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid or expired token. Please request a new one by logging in.",
        )

    # Check if token is expired
    if not token_entry.is_valid:
        # Delete expired token
        db.delete(token_entry)
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Verification token has expired. Please request a new one by logging in.",
        )

    # Get the user
    user = db.query(models.User).filter(models.User.id == token_entry.owner_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User not found.")

    # Mark user as verified and delete the token
    user.is_verified = True
    db.delete(token_entry)
    db.commit()

    return {"message": "Account verified successfully", "success": True}


# --------------------------------------------------- PASSWORD RESET ---------------------------------------------------


password_router = APIRouter(prefix="/password", tags=["Password"])


@password_router.post("/forgot", status_code=status.HTTP_200_OK, response_model=base_schemas.GenericResponse)
def request_password_reset(
    email_data: schemas.PasswordResetRequest,
    db: Session = Depends(database.get_db),
) -> base_schemas.GenericResponse:
    """Request a password reset email.
    :param email_data: Schema containing the user's email address
    :param db: The database session
    :return: Success message
    :raises HTTPException with a 404 status code if user does not exist
    :raises HTTPException with a 401 status code if user account is not active
    :raises HTTPException with a 403 status code if user is a test user
    :raises HTTPException with send_password_reset_with_rate_limit error details"""

    _assert_not_maintenance(db)

    # Find user by email
    user = db.query(models.User).filter(models.User.email == email_data.email).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User with this email does not exist.")

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User account is not active.")

    # Prevent test users from resetting password
    if user.is_demo:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Test users cannot reset their password.")

    # Send password reset email with rate limiting
    result = send_rate_limited_tokenized_password_reset_email(user, db)
    if not result.success:
        error_code = result.error_code if result.error_code else status.HTTP_500_INTERNAL_SERVER_ERROR
        raise HTTPException(status_code=error_code, detail=result.message)
    else:
        return result


@password_router.post("/reset", status_code=status.HTTP_200_OK, response_model=base_schemas.GenericResponse)
def reset_password(
    reset_data: schemas.PasswordReset,
    db: Session = Depends(database.get_db),
) -> dict[str, str | bool]:
    """Reset a user's password using a valid token.
    :param reset_data: Schema containing token and new password
    :param db: The database session
    :return: Success message
    :raises HTTPException with code 403 if token is invalid or expired
    :raises HTTPException with code 403 if user is a test user
    :raises HTTPException with code 500 if there is an error resetting the password"""

    _assert_not_maintenance(db)

    # Hash the token to compare with stored hash
    password_reset_code = utils.hash_token(reset_data.token)

    # Find token entry with matching hash
    token_entry = get_token(password_reset_code, TokenType.PASSWORD_RESET, db)

    if not token_entry or not token_entry.is_valid:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid or expired password reset token")

    # Get the user
    user = db.query(models.User).filter(models.User.id == token_entry.owner_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User not found")

    # Prevent test users from resetting password
    if user.is_demo:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Test users cannot reset their password.")

    # Hash the new password
    hashed_password = utils.hash_password(reset_data.new_password)

    # Update user's password and mark token as used
    try:
        email_service.send_password_changed_notification(user.email)
        user.password = hashed_password
        db.delete(token_entry)
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error resetting password")

    return {"success": True, "message": "Password has been reset successfully"}
