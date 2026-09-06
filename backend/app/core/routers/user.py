"""User route"""

import datetime as dt

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models, database
from app.base_schemas import GenericResponse
from app.core import oauth2, schemas
from app.core.models import TokenType
from app.core.schemas import CheckPendingEmailResponse
from app.core.utils import (
    check_token_rate_limit,
    send_rate_limited_tokenized_email_change_email,
    send_tokenized_password_changed_email_with_rate_limit,
)
from app.demo import is_demo_session
from app.emails.email_service import email_service
from app.emails.release_data import get_release_slides
from app.payments import stripe
from app.routers.utility import generate_data_table_crud_router, assert_admin
from app.utilities import security
from app.utilities.logger import AppLogger

# -------------------------------------------------------- USERS -------------------------------------------------------


def transform_user_data(data: dict, db: Session, entry_data: dict | None = None) -> dict:
    """Transform user data before creating or updating a user.
    :param data: The user data to transform.
    :param db: The database session
    :param entry_data: optional original data of the entry
    :returns: The transformed user data."""

    _ = db, entry_data
    if "password" in data:
        return {"password": security.hash_password(data["password"])}
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


@user_router.post("/invalidate-all-sessions")
def invalidate_all_sessions(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(oauth2.get_current_user),
) -> GenericResponse:
    """Invalidate all user sessions by incrementing token_version for all users.
    This will force all users to log in again.
    :param db: The database session.
    :param current_user: The current authenticated admin user.
    :returns: A message indicating the result of the operation."""

    assert_admin(current_user)

    # Increment token_version for all users
    db.query(models.User).update({models.User.token_version: models.User.token_version + 1})
    db.commit()

    return GenericResponse(message="All user sessions have been invalidated.", success=True)


@user_router.post("/send-release-email/{version}")
def send_release_email(
    version: str,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(oauth2.get_current_user),
) -> GenericResponse:
    """Send a new version announcement email to all active, verified, non-demo users.
    :param version: The version string to announce (e.g. "1.2.0").
    :param db: The database session.
    :param current_user: The current authenticated admin user.
    :returns: A message with the count of emails sent."""

    assert_admin(current_user)

    features = get_release_slides(version)
    if features is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No release data found for version {version}",
        )

    logger = AppLogger.create_service_logger("release_email", "INFO")

    users = db.query(models.User).filter(models.User.is_active, models.User.is_verified).all()

    sent_count = 0
    for user in users:
        try:
            email_service.send_new_version_email(user.email, version, features)
            sent_count += 1
        except Exception as e:
            logger.error("Failed to send release email to user %s: %s", user.id, str(e))

    return GenericResponse(
        message=f"Release email for v{version} sent to {sent_count}/{len(users)} users.",
        success=True,
    )


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
        .order_by(models.UserQualification.modified_at.desc(), models.UserQualification.id.desc())
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
            entry = models.UserQualification(
                **qualification.model_dump(exclude_unset=True, exclude={"id"}), owner_id=user.id
            )
            db.add(entry)
        else:
            for field, value in qualification.model_dump(exclude_unset=True).items():
                setattr(entry, field, value)
    else:
        entry = models.UserQualification(
            **qualification.model_dump(exclude_unset=True, exclude={"id"}), owner_id=user.id
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
) -> schemas.UserOut:
    """Get the current user's profile.
    :param current_user: The current authenticated user.
    :returns: The current user."""

    profile = schemas.UserOut.model_validate(current_user, from_attributes=True)
    return profile.model_copy(update={"is_demo": is_demo_session()})


@current_user_router.post("/heartbeat")
def heartbeat(
    current_user: models.User = Depends(oauth2.get_current_user),
    db: Session = Depends(database.get_db),
) -> GenericResponse:
    """Record that the user has accessed the app.
    :param current_user: The current authenticated user.
    :param db: The database session.
    :returns: A success message."""

    current_user.previous_login = current_user.last_login
    current_user.last_login = dt.datetime.now(dt.timezone.utc)
    db.commit()

    return GenericResponse(message="Last login updated.", success=True)


@current_user_router.put("/")
def update_account(
    user_update: schemas.CurrentUserUpdate,
    current_user: models.User = Depends(oauth2.get_current_user),
    db: Session = Depends(database.get_db),
) -> GenericResponse:
    """Update the current user's non-sensitive profile fields (name, app version, preferences, premium).
    Email and password updates have their own dedicated endpoints.
    :param user_update: The update data.
    :param current_user: The current authenticated user.
    :param db: The database session.
    :returns: A success message."""

    for field, value in user_update.model_dump(exclude_unset=True).items():
        if isinstance(value, dict):
            for k, v in value.items():
                setattr(getattr(current_user, field), k, v)
        else:
            setattr(current_user, field, value)

    db.commit()
    db.refresh(current_user)

    return GenericResponse(message="User has been successfully updated", success=True)


@current_user_router.put("/password")
def update_password(
    payload: schemas.CurrentUserPasswordUpdate,
    current_user: models.User = Depends(oauth2.get_current_user),
    db: Session = Depends(database.get_db),
) -> GenericResponse:
    """Change the current user's password.
    Verifies the current password, updates to the new password, invalidates existing sessions,
    and sends a notification email to confirm the change.
    :param payload: The current and new password.
    :param current_user: The current authenticated user.
    :param db: The database session.
    :returns: A dictionary with the result of the password update."""

    if is_demo_session():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Demo users cannot change their password.",
        )

    seconds_remaining = check_token_rate_limit(TokenType.PASSWORD_CHANGE, current_user, db)
    if seconds_remaining > 0:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"You have changed or attempted to change your password too recently. "
            f"Please wait {seconds_remaining} seconds before retrying.",
        )

    if not security.verify_password(payload.current_password, current_user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="The current password is incorrect.",
        )

    current_user.password = security.hash_password(payload.new_password)
    current_user.token_version += 1

    email_response = send_tokenized_password_changed_email_with_rate_limit(current_user, db)
    if not email_response.success:
        sta = email_response.error_code if email_response.error_code else status.HTTP_500_INTERNAL_SERVER_ERROR
        raise HTTPException(status_code=sta, detail=email_response.message)
    else:
        db.commit()
        return GenericResponse(message=email_response.message, success=True)


@current_user_router.put("/email")
def update_email(
    payload: schemas.CurrentUserEmailUpdate,
    current_user: models.User = Depends(oauth2.get_current_user),
    db: Session = Depends(database.get_db),
) -> GenericResponse:
    """Request a change of the current user's email address.
    Sends a verification email to the new address. The actual update only happens once the
    user clicks the link in that email (handled by /current-user/verify-email/{token}).
    :param payload: The new email address.
    :param current_user: The current authenticated user.
    :param db: The database session.
    :returns: A success message."""

    if is_demo_session():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Demo users cannot change their email address.",
        )

    if not security.verify_password(payload.current_password, current_user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="The current password is incorrect.",
        )

    new_email = payload.email
    if new_email == current_user.email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The new email address must be different from the current one.",
        )

    seconds_remaining = check_token_rate_limit(TokenType.EMAIL_CHANGE, current_user, db)
    if seconds_remaining > 0:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"You have changed or attempted to change your email too recently."
            f" Please wait {seconds_remaining} seconds before retrying.",
        )

    other_user = db.query(models.User).filter(models.User.id != current_user.id, models.User.email == new_email).first()
    if other_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    email_response = send_rate_limited_tokenized_email_change_email(current_user, new_email, db)
    if not email_response.success:
        status_code = email_response.error_code if email_response.error_code else status.HTTP_500_INTERNAL_SERVER_ERROR
        raise HTTPException(status_code=status_code, detail=email_response.message)
    else:
        return GenericResponse(message=email_response.message, success=True)


@current_user_router.get("/verify-email/{token}")
def verify_email_change(
    token: str,
    db: Session = Depends(database.get_db),
) -> GenericResponse:
    """Verify email change using the provided token
    :param token: The email change verification token.
    :param db: The database session.
    :returns: A message indicating the result of the email change verification."""

    hashed_token = security.hash_token(token)

    # Find the token entry
    token_entry = (
        db.query(models.UserToken)
        .filter(
            models.UserToken.token == hashed_token,
            models.UserToken.token_type == TokenType.EMAIL_CHANGE,
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

    return GenericResponse(
        message="Email address has been successfully updated. You can now log in with your new email.",
        success=True,
    )


@current_user_router.get("/check-pending-email")
def check_email_pending(
    current_user: models.User = Depends(oauth2.get_current_user),
    db: Session = Depends(database.get_db),
) -> CheckPendingEmailResponse:
    """Check if the user has a pending email change.
    :param current_user: The current authenticated user.
    :param db: The database session.
    :returns: Dictionary with pending status and email if exists."""

    # Get the email change token for this user
    token_entry = (
        db.query(models.UserToken)
        .filter(
            models.UserToken.owner_id == current_user.id,
            models.UserToken.token_type == TokenType.EMAIL_CHANGE,
        )
        .first()
    )

    if not token_entry:
        return CheckPendingEmailResponse(has_pending_email=False)

    # Check if token is expired
    if not token_entry.is_valid:
        db.delete(token_entry)
        db.commit()
        return CheckPendingEmailResponse(has_pending_email=False)

    return CheckPendingEmailResponse(has_pending_email=True, pending_email=token_entry.pending_email)


@current_user_router.post("/verify-password")
def verify_password_endpoint(
    verify_request: schemas.AccountDeleteRequest,
    current_user: models.User = Depends(oauth2.get_current_user),
) -> GenericResponse:
    """Verify the current user's password without making any changes."""
    if not security.verify_password(verify_request.password, current_user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Password is incorrect.",
        )
    return GenericResponse(message="Password verified.", success=True)


@current_user_router.delete("/")
def delete_account(
    delete_request: schemas.AccountDeleteRequest,
    current_user: models.User = Depends(oauth2.get_current_user),
    db: Session = Depends(database.get_db),
) -> GenericResponse:
    """Delete the current user's account permanently.
    :param delete_request: The account deletion request with password.
    :param current_user: The current authenticated user.
    :param db: The database session.
    :returns: A message indicating the result of the account deletion."""

    # Prevent demo users from deleting their account
    if is_demo_session():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Test users cannot delete their account.",
        )

    # Verify password before deletion
    if not security.verify_password(delete_request.password, current_user.password):
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

    return GenericResponse(message="Account deleted successfully.", success=True)
