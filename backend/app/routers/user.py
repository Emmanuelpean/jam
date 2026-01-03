"""User route"""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import utils, models, oauth2, database, schemas
from app.config import settings
from app.emails.email_service import email_service
from app.routers import generate_data_table_crud_router
from app.routers.utils import get_retry_remaining_seconds, generate_token, check_token_expiration


# -------------------------------------------------------- USERS -------------------------------------------------------


def transform_user_data(data: dict, db: Session) -> dict:
    """Transform user data before creating or updating a user.
    :param data: The user data to transform.
    :param db: The database session
    :returns: The transformed user data."""

    _ = db
    if "password" in data:
        return {"password": utils.hash_password(data["password"])}
    else:
        return {}


user_router = generate_data_table_crud_router(
    table_model=models.User,
    create_schema=schemas.UserCreate,
    update_schema=schemas.UserUpdate,
    out_schema=schemas.UserOut,
    endpoint="users",
    not_found_msg="User not found",
    admin_only=True,
    transform=transform_user_data,
)


# ------------------------------------------------- USER QUALIFICATIONS ------------------------------------------------


user_qualification_router = APIRouter(prefix="/user-qualifications", tags=["user-qualifications"])


@user_qualification_router.get("/latest", response_model=schemas.UserQualificationOut)
def get_latest_user_qualification(
    db: Session = Depends(database.get_db),
    user: models.User = Depends(oauth2.get_current_user),
):
    """Get the latest user qualification for the current user."""

    entry = (
        db.query(models.UserQualification)
        .filter(models.UserQualification.owner_id == user.id)
        .order_by(models.UserQualification.modified_at.desc())
        .first()
    )
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User Qualification not found",
        )
    return entry


@user_qualification_router.post("/", response_model=schemas.UserQualificationOut)
def upsert_user_qualification(
    qualification: schemas.UserQualificationUpsert,
    db: Session = Depends(database.get_db),
    user: models.User = Depends(oauth2.get_current_user),
):
    """Create or update a user qualification."""

    entry = (
        db.query(models.UserQualification)
        .filter(models.UserQualification.owner_id == user.id)
        .filter(models.UserQualification.id == qualification.id)
        .first()
    )
    if entry:
        # Determine if the qualification was used to rate jobs
        if len(entry.job_ratings):
            # noinspection PyArgumentList
            entry = models.UserQualification(
                **qualification.model_dump(exclude_unset=True, exclude=["id"]), owner_id=user.id
            )
            db.add(entry)
        else:
            for field, value in qualification.model_dump(exclude_unset=True).items():
                setattr(entry, field, value)
    else:
        # noinspection PyArgumentList
        entry = models.UserQualification(
            **qualification.model_dump(exclude_unset=True, exclude=["id"]), owner_id=user.id
        )
        db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


# ---------------------------------------------------- CURRENT USER ----------------------------------------------------


current_user_router = APIRouter(prefix="/current-user", tags=["current-user"])


@current_user_router.get("/", response_model=schemas.UserOut)
def get_current_user_profile(
    current_user: models.User = Depends(oauth2.get_current_user),
) -> models.User:
    """Get the current user's profile.
    :param current_user: The current authenticated user.
    :returns: The current user."""

    return current_user


def send_email_change_with_rate_limit(
    user: models.User,
    db: Session,
    email: str,
) -> dict[str, bool | str | int | None]:
    """Send email change email with rate limiting.
    :param user: user entry
    :param db: database session
    :param email: new email address
    :return: dictionary with success status, message and error code"""

    # Check if enough time has passed since last email
    seconds_remaining = get_retry_remaining_seconds(user.email_change_token_created_at)
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
        verification_url = f"{settings.frontend_url}/verify-new-email/?token={token}"
        email_service.send_email_change_verification(email, verification_url)

        # Update user with new verification code and timestamp
        user.pending_email = email
        user.email_change_token = verification_code
        user.email_change_token_created_at = datetime.now(timezone.utc)
        db.commit()

        return {
            "success": True,
            "message": "Verification email sent successfully.",
            "error_code": None,
        }

    except Exception as e:
        db.rollback()
        return {
            "success": False,
            "message": f"Error sending verification email: {str(e)}",
            "error_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
        }


@current_user_router.put("/", response_model=schemas.CurrentUserUpdateResponse)
def update_current_user_profile(
    user_update: schemas.CurrentUserUpdate,
    current_user: models.User = Depends(oauth2.get_current_user),
    db: Session = Depends(database.get_db),
) -> dict:
    """Update the current user's profile.
    :param user_update: The user update data.
    :param current_user: The current authenticated user.
    :param db: The database session.
    :returns: A dictionary with the result of the update operation."""

    result = {"success": True, "message": "User has been successfully updated"}
    user_update_dict = user_update.model_dump(exclude_unset=True)

    # Track if password or email changed
    password_changed = False

    # Hash password if it's being updated
    transformed_data = transform_user_data(user_update_dict, db)
    user_update_dict.update(transformed_data)

    # Determine if the user is updating the password or email
    requires_password_check = "password" in user_update_dict or "email" in user_update_dict

    # Prevent test users from changing password or email
    if current_user.is_demo and requires_password_check:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Test users cannot change their password or email address.",
        )

    # Update password/email
    current_password = user_update_dict.get("current_password", "")
    if requires_password_check and not utils.verify_password(current_password, current_user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="The current password is incorrect.",
        )

    # Track password change
    if "password" in user_update_dict:
        password_changed = True

    # Handle email change separately
    if "email" in user_update_dict and user_update_dict["email"] != current_user.email:
        new_email = user_update_dict.pop("email")  # Remove from dict to handle separately

        # Validate email is not already associated with another user
        other_users = (
            db.query(models.User)
            .filter(models.User.id != current_user.id)
            .filter(models.User.email == new_email)
            .first()
        )
        if other_users:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

        # Send verification email with rate limiting
        result = send_email_change_with_rate_limit(current_user, db, new_email)
        if not result["success"]:
            return result

    # Update other fields normally
    for field, value in user_update_dict.items():
        setattr(current_user, field, value)

    # Increment token version if password was changed
    if password_changed:
        current_user.token_version += 1
        result["message"] = "User updated successfully. Please log in again."
        result["logged_out"] = True

    db.commit()
    db.refresh(current_user)
    return result


@current_user_router.get("/verify-email/{token}", response_model=schemas.GenericResponse)
def verify_email_change(
    token: str,
    db: Session = Depends(database.get_db),
) -> dict[str, str]:
    """Verify email change using the provided token
    :param token: The email change verification token.
    :param db: The database session.
    :returns: A message indicating the result of the email change verification."""

    verification_code = utils.hash_token(token)
    user = db.query(models.User).filter(models.User.email_change_token == verification_code).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid or expired token. Please request a new one by logging in and changing your email address.",
        )

    # Check if demo user
    if user.is_demo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Test users cannot change their password or email address.",
        )

    # Check if token is expired
    if check_token_expiration(user.email_change_token_created_at):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email change token has expired. Please request a new one by logging in and changing your email address.",
        )

    # Check if user email does not already exist
    other_users = (
        db.query(models.User).filter(models.User.id != user.id).filter(models.User.email == user.pending_email).first()
    )
    if other_users:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Update email and clear pending fields
    old_email = user.email
    user.email = user.pending_email
    user.pending_email = None
    user.email_change_token = None
    user.email_change_token_created_at = None
    user.token_version += 1
    db.commit()
    email_service.send_email_change_notification(user.email, old_email)

    return {"message": "Email address changed successfully. You can now log in with your new email.", "success": True}


@current_user_router.get("/check-pending-email")
def check_email_pending(
    current_user: models.User = Depends(oauth2.get_current_user),
    db: Session = Depends(database.get_db),
) -> bool:
    """Check if the user has a pending email change and clear it if expired.
    :param current_user: The current authenticated user.
    :param db: The database session.
    :returns: False if no pending email or if the token is expired, True otherwise."""

    # Check if token is expired
    if check_token_expiration(current_user.email_change_token_created_at):
        current_user.pending_email = None
        current_user.email_change_token = None
        current_user.email_change_token_created_at = None
        db.commit()
        return False

    return True
