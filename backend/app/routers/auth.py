"""Authentication route"""

import secrets
from datetime import datetime, timezone, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app import utils, models, database, schemas, oauth2
from app.config import settings
from app.emails.email_service import email_service


def get_retry_remaining_seconds(token_created_at: datetime | None) -> int:
    """Calculate how many seconds remain until the next email can be sent.
    :param token_created_at: datetime when the last token was created
    :return: seconds remaining until next email can be sent"""

    if token_created_at:
        time_since_last_email = int((datetime.now(timezone.utc) - token_created_at).total_seconds())
        return settings.verification_email_min_interval_seconds - time_since_last_email
    return 0


def generate_token() -> tuple[str, str]:
    """Generate a secure random token.
    :return: tuple containing the token and its hashed verification code"""

    token = secrets.token_urlsafe(32)
    verification_code = utils.hash_token(token)
    return token, verification_code


def check_token_expiration(token_created_at: datetime | None) -> bool:
    """Check if the token has expired.
    :param token_created_at: datetime when the token was created
    :return: True if expired, False otherwise"""

    if token_created_at:
        expiration_time = token_created_at + timedelta(minutes=settings.verification_token_expiration_minutes)
        return datetime.now(timezone.utc) > expiration_time
    return True


# -------------------------------------------------------- LOGIN -------------------------------------------------------


login_router = APIRouter(prefix="/login", tags=["Login"])


@login_router.post("/", status_code=status.HTTP_200_OK, response_model=schemas.Token)
def login(
    user_credentials: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(database.get_db),
) -> dict[str, str]:
    """Login a user.
    :param user_credentials: The user credentials (note: username is the email field)
    :param db: The database session
    :returns: The access token dictionary
    :raises HTTPException with a 403 status code if the credentials are invalid
    :raises HTTPException with a 401 status code if the user is not active or not verified
    :raises HTTPException with a 429 status code if verification email rate limit is exceeded"""

    user_email = utils.clean_email(user_credentials.username)

    # Find the user in the list based on the email provided
    user = db.query(models.User).filter(models.User.email == user_email).first()

    # Check that the user exist and verify the password
    if user is None or not utils.verify_password(user_credentials.password, user.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid credentials.")

    # Check that the user is active
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User account is not active.")

    # Check that the user is verified
    if not user.is_verified:
        result = send_verification_with_rate_limit(user, db)

        # Raise appropriate exception based on email sending result
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
    access_token = oauth2.create_access_token(
        data={"user_id": user.id},
        token_version=user.token_version,
    )
    return {"access_token": access_token, "token_type": "bearer"}


# ------------------------------------------------------ REGISTER ------------------------------------------------------


def send_verification_with_rate_limit(
    user: models.User,
    db: Session,
) -> dict[str, bool | str | int | None]:
    """Send verification email with rate limiting.
    :param user: user entry
    :param db: database session
    :return: Dictionary with success status, message and error code"""

    # Check if enough time has passed since last email
    seconds_remaining = get_retry_remaining_seconds(user.verification_token_created_at)
    if seconds_remaining > 0:
        return {
            "success": False,
            "message": f"Please wait {seconds_remaining} seconds before requesting another verification email",
            "error_code": status.HTTP_429_TOO_MANY_REQUESTS,
        }

    # Generate new verification token
    token, verification_code = generate_token()

    try:
        # Send the email to the user
        verification_url = f"{settings.frontend_url}/login/?token={token}"
        email_service.send_verification_email(user.email, verification_url)

        # Update user with new verification code and timestamp
        user.verification_token = verification_code
        user.verification_token_created_at = datetime.now(timezone.utc)
        db.commit()

        return {
            "success": True,
            "message": "Verification email sent successfully",
            "error_code": None,
        }

    except Exception as e:
        db.rollback()
        return {
            "success": False,
            "message": f"Error sending verification email: {str(e)}",
            "error_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
        }


register_router = APIRouter(prefix="/register", tags=["Register"])


@register_router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.VerificationResponse)
def create_user(
    user: schemas.UserRegister,
    db: Session = Depends(database.get_db),
) -> dict[str, str | bool]:
    """Create a new user
    :param user: The user data
    :param db: The database session
    :returns: Dictionary with success status and message
    :raises HTTPException with a 400 status code if the email is already registered
    :raises HTTPException with a 401 status code if the user is not allowed to sign up"""

    # Check the user can be created
    setting = db.query(models.Setting).filter(models.Setting.name == "allowlist", models.Setting.is_active).first()
    if setting:
        emails_allowed = [utils.clean_email(email) for email in setting.value.split(",")]
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
            result = send_verification_with_rate_limit(existing_user, db)
            if result["success"]:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=f"Email already registered but not verified. "
                    f"A new verification email has been sent to {existing_user.email}.",
                )
            else:
                raise HTTPException(status_code=result["error_code"], detail=result["message"])
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    # Hash the password and create the user
    user.password = utils.hash_password(user.password)

    # Create user
    user_data = user.model_dump()
    new_user = models.User(**user_data)  # noqa
    result = send_verification_with_rate_limit(new_user, db)
    if not result["success"]:
        raise HTTPException(status_code=result["error_code"], detail=result["message"])
    else:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

    return result


@register_router.get("/verify-email/{token}")
def verify_email(
    token: str,
    db: Session = Depends(database.get_db),
) -> dict[str, str]:
    """Verify a user's email address using the provided token
    :param token: The verification token from the email
    :param db: The database session
    :raises HTTPException with a 403 status code if the token does not exist
    :raises HTTPException with a 403 status code if the token has expired
    :return: Success message upon successful verification"""

    verification_code = utils.hash_token(token)
    user = db.query(models.User).filter(models.User.verification_token == verification_code).first()

    if not user:
        raise HTTPException(status_code=403, detail="Invalid or expired token. Please request a new one by logging in.")

    # Check if token is expired (e.g., 24 hours)
    if check_token_expiration(user.verification_token_created_at):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Verification token has expired. Please request a new one by logging in.",
        )

    # Clear the stored token and mark the user as verified
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
    :return: dictionary with success status, message and error code"""

    # Check if enough time has passed since last email
    seconds_remaining = get_retry_remaining_seconds(user.password_reset_token_created_at)
    if seconds_remaining > 0:
        return {
            "success": False,
            "message": f"Please wait {seconds_remaining} seconds before requesting another password reset email",
            "error_code": status.HTTP_429_TOO_MANY_REQUESTS,
        }

    # Generate new verification token
    token, code = generate_token()

    try:
        # Send verification email
        url = f"{settings.frontend_url}/reset-password/?token={token}"
        email_service.send_password_reset_email(user.email, url)

        # Update user with new verification code and timestamp
        user.password_reset_token = code
        user.password_reset_token_created_at = datetime.now(timezone.utc)
        db.commit()

        return {
            "success": True,
            "message": "Password reset email sent successfully",
            "error_code": None,
        }
    except Exception as e:
        db.rollback()
        return {
            "success": False,
            "message": f"Error sending password reset email: {str(e)}",
            "error_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
        }


@password_router.post("/forgot", status_code=status.HTTP_200_OK)
def request_password_reset(
    email_data: schemas.EmailRequest,
    db: Session = Depends(database.get_db),
) -> dict[str, str | bool]:
    """Request a password reset email.
    :param email_data: Schema containing the user's email address
    :param db: The database session
    :return: Success message
    :raises HTTPException with a 404 status code if user does not exist
    :raises HTTPException with a 401 status code if user account is not active
    :raises HTTPException with send_password_reset_with_rate_limit error details"""

    # Find user by email
    user = db.query(models.User).filter(models.User.email == email_data.email).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User with this email does not exist.")

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User account is not active.")

    # Send password reset email with rate limiting
    result = send_password_reset_with_rate_limit(user, db)
    if result["error_code"]:
        raise HTTPException(status_code=result["error_code"], detail=result["message"])
    else:
        return {"success": True, "message": result["message"]}


@password_router.post("/reset", status_code=status.HTTP_200_OK)
def reset_password(
    reset_data: schemas.PasswordReset,
    db: Session = Depends(database.get_db),
) -> dict[str, str | bool]:
    """Reset a user's password using a valid token.
    :param reset_data: Schema containing token and new password
    :param db: The database session
    :return: Success message
    :raises HTTPException with code 403 if token is invalid or expired
    :raises HTTPException with code 500 if there is an error resetting the password"""

    # Hash the token to compare with stored hash
    password_reset_code = utils.hash_token(reset_data.token)

    # Find user with matching token
    user = db.query(models.User).filter(models.User.password_reset_token == password_reset_code).first()

    if not user or check_token_expiration(user.password_reset_token_created_at):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid or expired password reset token")

    # Hash the new password
    hashed_password = utils.hash_password(reset_data.new_password)

    # Update user's password and clear reset token
    try:
        email_service.send_password_changed_notification(user.email)
        user.password = hashed_password
        user.password_reset_token = None
        user.password_reset_token_created_at = None
        db.commit()
    except:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error resetting password")

    return {"success": True, "message": "Password has been reset successfully"}
