"""Authentication route"""

import os
import secrets
from datetime import datetime, timezone, timedelta

from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app import utils, models, database, schemas, oauth2
from app.emails.email_service import email_service

load_dotenv()


def send_verification_with_rate_limit(
    user: models.User,
    db: Session,
) -> dict[str, bool | str]:
    """Send verification email with rate limiting.
    :param user: user entry
    :param db: database session
    :return: Dictionary with success status and message
    :raises HTTPException if email sending fails"""

    # Check if enough time has passed since last email
    min_interval_seconds = int(os.getenv("VERIFICATION_EMAIL_MIN_INTERVAL_SECONDS"))
    if user.verification_token_created_at:
        time_since_last_email = datetime.now(timezone.utc) - user.verification_token_created_at
        if time_since_last_email < timedelta(seconds=min_interval_seconds):
            seconds_remaining = min_interval_seconds - int(time_since_last_email.total_seconds())
            return {
                "success": False,
                "message": f"Please wait {seconds_remaining} seconds before requesting another verification email",
                "seconds_remaining": seconds_remaining,
            }

    # Generate new verification token
    token = secrets.token_urlsafe(32)
    verification_code = utils.hash_token(token)

    # Update user with new verification code and timestamp
    user.verification_token = verification_code
    user.verification_token_created_at = datetime.now(timezone.utc)
    db.commit()

    try:
        # Send verification email
        expiration_min = int(os.getenv("VERIFICATION_TOKEN_EXPIRATION_MINUTES"))
        frontend_url = os.getenv("FRONTEND_URL")
        verification_url = f"{frontend_url}/login/?token={token}"
        email_service.send_verification_email(user.email, verification_url, expiration_min)

        return {"success": True, "message": "Verification email sent successfully"}
    except Exception as e:
        return {"success": False, "message": f"Error sending verification email: {str(e)}"}


# -------------------------------------------------------- LOGIN -------------------------------------------------------


login_router = APIRouter(prefix="/login", tags=["Login"])


@login_router.post("/", status_code=status.HTTP_200_OK, response_model=schemas.Token)
def login(
    user_credentials: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(database.get_db),
) -> dict[str, str]:
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
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="This user account is not active")

    # Check that the password corresponds to that user
    if not utils.verify_password(user_credentials.password, user.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid credentials")

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
) -> models.User:
    """Create a new user.
    :param user: The user data.
    :param db: The database session.
    :returns: The created user."""

    # Check the user can be created
    settings = db.query(models.Setting).filter(models.Setting.name == "allowlist").first()
    if settings and settings.is_active:
        emails_allowed = [email.strip().lower() for email in settings.value.split(",")]
        if user.email not in emails_allowed:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="You are not allowed to sign up for now."
            )

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
) -> dict[str, str]:
    """Verify a user's email address using the provided token.
    :param token: The verification token from the email.
    :param db: The database session."""

    expiration_hours = int(os.getenv("VERIFICATION_TOKEN_EXPIRATION_MINUTES"))
    verification_code = utils.hash_token(token)
    print(verification_code)

    user = db.query(models.User).filter(models.User.verification_token == verification_code).first()

    if not user:
        raise HTTPException(status_code=403, detail="Invalid or expired token")

    # Check if token is expired (e.g., 24 hours)
    expiration_time = user.verification_token_created_at + timedelta(hours=expiration_hours)
    if datetime.now(timezone.utc) > expiration_time:
        send_verification_with_rate_limit(user, db)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Verification token has expired. A new one has been sent.",
        )

    user.verification_token = None
    user.verification_token_created_at = None
    user.is_verified = True
    db.commit()

    return {"message": "Account verified successfully"}


# ------------------------------------------------------ PASSWORD ------------------------------------------------------


password_router = APIRouter(prefix="/password", tags=["Password"])


def send_password_reset_with_rate_limit(
    user: models.User,
    db: Session,
) -> dict[str, bool | str]:
    """Send password reset email with rate limiting.
    :param user: user entry
    :param db: database session
    :return: dictionary with success status and message
    :raises HTTPException if email sending fails"""

    # Check if enough time has passed since last email
    min_interval_seconds = int(os.getenv("VERIFICATION_EMAIL_MIN_INTERVAL_SECONDS"))
    if user.password_reset_token_created_at:
        time_since_last_email = datetime.now(timezone.utc) - user.password_reset_token_created_at
        if time_since_last_email < timedelta(seconds=min_interval_seconds):
            seconds_remaining = min_interval_seconds - int(time_since_last_email.total_seconds())
            return {
                "success": False,
                "message": f"Please wait {seconds_remaining} seconds before requesting another password reset email",
                "seconds_remaining": seconds_remaining,
            }

    # Generate new verification token
    token = secrets.token_urlsafe(32)
    code = utils.hash_token(token)

    # Update user with new verification code and timestamp
    user.password_reset_token = code
    user.password_reset_token_created_at = datetime.now(timezone.utc)
    db.commit()

    try:
        # Send verification email
        expiration_min = int(os.getenv("VERIFICATION_TOKEN_EXPIRATION_MINUTES"))
        frontend_url = os.getenv("FRONTEND_URL")
        url = f"{frontend_url}/password/reset/?token={token}"
        email_service.send_password_reset_email(user.email, url, expiration_min)

        return {"success": True, "message": "Password reset email sent successfully"}
    except Exception as e:
        return {"success": False, "message": f"Error sending password reset email: {str(e)}"}


@password_router.post("/forgot", status_code=status.HTTP_200_OK)
def request_password_reset(
    email_data: schemas.EmailRequest,
    db: Session = Depends(database.get_db),
) -> dict[str, str]:
    """Request a password reset email.
    :param email_data: Schema containing the user's email address
    :param db: The database session
    :return: Success message (always returns success to prevent email enumeration)"""

    # Find user by email
    user = db.query(models.User).filter(models.User.email == email_data.email.strip().lower()).first()

    # Always return success message to prevent email enumeration attacks
    if not user:
        return {"message": "If an account exists with this email, a password reset link has been sent"}

    # Check if user is active
    if not user.is_active:
        return {"message": "If an account exists with this email, a password reset link has been sent"}

    # Send password reset email with rate limiting
    result = send_password_reset_with_rate_limit(user, db)

    if not result["success"]:
        if "seconds_remaining" in result:
            raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=result["message"])

    return {"message": "If an account exists with this email, a password reset link has been sent"}


@password_router.post("/reset", status_code=status.HTTP_200_OK)
def reset_password(
    reset_data: schemas.PasswordReset,
    db: Session = Depends(database.get_db),
) -> dict[str, str]:
    """Reset a user's password using a valid token.
    :param reset_data: Schema containing token and new password
    :param db: The database session
    :return: Success message
    :raises HTTPException if token is invalid or expired"""

    # Hash the token to compare with stored hash
    password_reset_code = utils.hash_token(reset_data.token)

    # Find user with matching token
    user = db.query(models.User).filter(models.User.password_reset_token == password_reset_code).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid or expired password reset token")

    # Check if token is expired
    expiration_minutes = int(os.getenv("VERIFICATION_TOKEN_EXPIRATION_MINUTES"))
    if user.password_reset_token_created_at:
        expiration_time = user.password_reset_token_created_at + timedelta(minutes=expiration_minutes)
        if datetime.now(timezone.utc) > expiration_time:
            db.commit()
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Password reset token has expired. Please request a new one.",
            )

    # Hash the new password
    hashed_password = utils.hash_password(reset_data.new_password)

    # Update user's password and clear reset token
    user.password = hashed_password
    user.password_reset_token = None
    user.password_reset_token_created_at = None
    db.commit()

    # Optional: Send confirmation email
    try:
        email_service.send_password_changed_notification(user.email)
    except Exception as e:
        # Log but don't fail the request if notification fails
        print(f"Failed to send password change notification: {str(e)}")

    return {"message": "Password has been reset successfully"}
