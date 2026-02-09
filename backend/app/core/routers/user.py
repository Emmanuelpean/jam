"""User route"""

import datetime as dt

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import base_schemas
from app import utils, models, database
from app.core import oauth2, schemas
from app.core.utils import send_email_change_email
from app.emails.email_service import email_service
from app.routers import generate_data_table_crud_router, assert_admin
from app.payments import stripe


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


@user_router.post("/invalidate-all-sessions", response_model=base_schemas.GenericResponse)
def invalidate_all_sessions(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(oauth2.get_current_user),
) -> dict[str, str | bool]:
    """Invalidate all user sessions by incrementing token_version for all users.
    This will force all users to log in again.
    :param db: The database session.
    :param current_user: The current authenticated admin user.
    :returns: A message indicating the result of the operation."""

    assert_admin(current_user)

    # Increment token_version for all users
    db.query(models.User).update({models.User.token_version: models.User.token_version + 1})
    db.commit()

    return {"message": "All user sessions have been invalidated.", "success": True}


# ------------------------------------------------- USER QUALIFICATIONS ------------------------------------------------


user_qualification_router = APIRouter(prefix="/user-qualifications", tags=["user-qualifications"])


@user_qualification_router.get("/latest", response_model=schemas.UserQualificationOut)
def get_latest_user_qualification(
    db: Session = Depends(database.get_db),
    user: models.User = Depends(oauth2.get_current_user),
) -> models.UserQualification:
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
) -> models.UserQualification:
    """Create or update a user qualification.
    :param qualification: The user qualification data.
    :param db: The database session
    :param user: The current authenticated user.
    :returns: The created or updated user qualification."""

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


@current_user_router.post("/heartbeat", response_model=base_schemas.GenericResponse)
def heartbeat(
    current_user: models.User = Depends(oauth2.get_current_user),
    db: Session = Depends(database.get_db),
) -> dict[str, str | bool]:
    """Record that the user has accessed the app.
    :param current_user: The current authenticated user.
    :param db: The database session.
    :returns: A success message."""

    current_user.previous_login = current_user.last_login
    current_user.last_login = dt.datetime.now(dt.timezone.utc)
    db.commit()

    return {"message": "Last login updated.", "success": True}


@current_user_router.put("/", response_model=schemas.CurrentUserUpdateResponse)
def update_account(
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
        email_result = send_email_change_email(current_user, new_email, db)
        if not email_result.success:
            raise HTTPException(
                status_code=email_result.error_code,
                detail=email_result.message,
            )
        result["message"] = email_result.message

    # Update other fields normally
    for field, value in user_update_dict.items():
        if isinstance(value, dict):
            for k, v in value.items():
                setattr(getattr(current_user, field), k, v)
        else:
            setattr(current_user, field, value)

    # Increment token version if password was changed
    if password_changed:
        current_user.token_version += 1
        result["message"] = "Account updated successfully. Please log in again."
        result["logged_out"] = True

    db.commit()
    db.refresh(current_user)
    return result


@current_user_router.get("/verify-email/{token}", response_model=base_schemas.GenericResponse)
def verify_email_change(
    token: str,
    db: Session = Depends(database.get_db),
) -> dict[str, str | bool]:
    """Verify email change using the provided token
    :param token: The email change verification token.
    :param db: The database session.
    :returns: A message indicating the result of the email change verification."""

    hashed_token = utils.hash_token(token)

    # Find the token entry
    token_entry = (
        db.query(models.UserToken)
        .filter(
            models.UserToken.token == hashed_token,
            models.UserToken.token_type == "email_change",
        )
        .first()
    )

    if not token_entry:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid or expired token. Please request a new one by logging in and changing your email address.",
        )

    # Check if token is expired
    if not token_entry.is_valid:
        db.delete(token_entry)
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email change token has expired. Please request a new one by logging in and changing your email address.",
        )

    # Get the user
    user = db.query(models.User).filter(models.User.id == token_entry.owner_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User not found.")

    # Check if demo user
    if user.is_demo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Test users cannot change their email address.",
        )

    # Check if email is already taken
    other_users = (
        db.query(models.User)
        .filter(models.User.id != user.id)
        .filter(models.User.email == token_entry.pending_email)
        .first()
    )
    if other_users:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Update email and invalidate all sessions
    old_email = user.email
    user.email = token_entry.pending_email
    user.token_version += 1

    # Delete the token after successful use
    db.delete(token_entry)
    db.commit()
    email_service.send_email_change_notification(user.email, old_email)

    return {"message": "Email address changed successfully. You can now log in with your new email.", "success": True}


@current_user_router.get("/check-pending-email", response_model=schemas.CheckPendingEmailResponse)
def check_email_pending(
    current_user: models.User = Depends(oauth2.get_current_user),
    db: Session = Depends(database.get_db),
) -> dict[str, bool | str | None]:
    """Check if the user has a pending email change.
    :param current_user: The current authenticated user.
    :param db: The database session.
    :returns: Dictionary with pending status and email if exists."""

    # Get the email change token for this user
    token_entry = (
        db.query(models.UserToken)
        .filter(
            models.UserToken.owner_id == current_user.id,
            models.UserToken.token_type == "email_change",
        )
        .first()
    )

    if not token_entry:
        return {"has_pending_email": False, "pending_email": None}

    # Check if token is expired
    if not token_entry.is_valid:
        db.delete(token_entry)
        db.commit()
        return {"has_pending_email": False, "pending_email": None}

    return {"has_pending_email": True, "pending_email": token_entry.pending_email}


@current_user_router.delete("/", response_model=base_schemas.GenericResponse)
def delete_account(
    delete_request: schemas.AccountDeleteRequest,
    current_user: models.User = Depends(oauth2.get_current_user),
    db: Session = Depends(database.get_db),
) -> dict[str, str | bool]:
    """Delete the current user's account permanently.
    :param delete_request: The account deletion request with password.
    :param current_user: The current authenticated user.
    :param db: The database session.
    :returns: A message indicating the result of the account deletion."""

    # Prevent demo users from deleting their account
    if current_user.is_demo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Test users cannot delete their account.",
        )

    # Verify password before deletion
    if not utils.verify_password(delete_request.password, current_user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Failed to delete account. Password is incorrect.",
        )

    # Cancel Stripe subscription if active
    if current_user.stripe_details and current_user.stripe_details.subscription_id:
        try:
            stripe.Subscription.delete(current_user.stripe_details.subscription_id)
        except Exception as e:
            print(f"Failed to cancel Stripe subscription for user {current_user.id}: {e}")

    # Delete the user (cascading deletes will handle related data)
    db.delete(current_user)
    db.commit()

    return {"message": "Account deleted successfully.", "success": True}
