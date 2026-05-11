"""Utility functions for token management and email verification."""

import secrets
from typing import Callable

from sqlalchemy.orm import Session
from starlette import status

from app import utils, models, base_schemas
from app.core.models import TokenType
from app.config import settings
from app.emails.email_service import email_service


def get_token(
    token: str,
    token_type: TokenType,
    db: Session,
) -> models.UserToken | None:
    """Retrieve a user token by token string and token type.
    :param token: The token string.
    :param token_type: The type of the token (e.g., 'verification', 'password_reset').
    :param db: The database session.
    :return: The UserToken object if found, else None."""

    return (
        db.query(models.UserToken)
        .filter(
            models.UserToken.token == token,
            models.UserToken.token_type == token_type,
        )
        .first()
    )


def generate_token(
    user_id: int,
    token_type: TokenType,
    db: Session,
    pending_email: str | None = None,
) -> tuple[str, models.UserToken]:
    """Generate a secure random token and delete old tokens of the same type.
    :param user_id: ID of the user for whom the token is generated
    :param token_type: Type of the token (e.g., 'verification', 'password_reset', 'email_change')
    :param db: Database session
    :param pending_email: Optional pending email for email_change tokens
    :return: Tuple of (plain_token, UserToken object)"""

    # Delete all existing tokens of this type for this user
    db.query(models.UserToken).filter(
        models.UserToken.owner_id == user_id,
        models.UserToken.token_type == token_type,
    ).delete()

    # Generate new token
    plain_token = secrets.token_urlsafe(32)
    hashed_token = utils.hash_token(plain_token)

    # noinspection PyArgumentList
    new_token = models.UserToken(
        owner_id=user_id,
        token=hashed_token,
        token_type=token_type,
        pending_email=pending_email,
    )
    db.add(new_token)
    db.commit()
    db.refresh(new_token)

    return plain_token, new_token


def send_verification_with_rate_limit(
    token_type: TokenType,
    user: models.User,
    db: Session,
    send_email_function: Callable,
    endpoint: str,
    name: str,
    pending_email: str | None = None,
) -> base_schemas.GenericResponse:
    """Send verification email with rate limiting.
    :param token_type: Type of the token (e.g., 'verification')
    :param user: user entry
    :param db: database session
    :param send_email_function: Function to send the email
    :param endpoint: Frontend endpoint for the verification link
    :param name: Name of the token type for messaging
    :param pending_email: Optional pending email for email_change tokens
    :return: Dictionary with success status, message and error code"""

    # Check if enough time has passed since last token was generated
    existing_token = (
        db.query(models.UserToken)
        .filter(models.UserToken.owner_id == user.id)
        .filter(models.UserToken.token_type == token_type)
        .order_by(models.UserToken.created_at.desc())
        .first()
    )
    if existing_token:
        seconds_remaining = existing_token.remaining_seconds
        if float(str(seconds_remaining)) > 0:
            return base_schemas.GenericResponse(
                success=False,
                message=f"Please wait {seconds_remaining} seconds before requesting another {name} email.",
                error_code=status.HTTP_429_TOO_MANY_REQUESTS,
            )

    # Generate new verification token and delete the old ones
    plain_token, hashed_token_obj = generate_token(user.id, token_type, db, pending_email)

    try:
        # Send the email to the user with the plain token
        verification_url = f"{settings.frontend_url}/{endpoint}/?token={plain_token}"
        send_email_function(user.email, verification_url, user.first_name)
        return base_schemas.GenericResponse(
            success=True,
            message=f"{name} email sent successfully.",
            error_code=None,
        )

    except Exception as e:
        return base_schemas.GenericResponse(
            success=False,
            message=f"Error sending {token_type} email: {e}",
            error_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


def send_email_verification_email(
    user: models.User,
    db: Session,
) -> base_schemas.GenericResponse:
    """Send email verification email with rate limiting.
    :param user: user entry
    :param db: database session
    :return: Dictionary with success status, message and error code"""

    return send_verification_with_rate_limit(
        token_type=TokenType.VERIFICATION,
        user=user,
        db=db,
        send_email_function=email_service.send_verification_email,
        endpoint="verify-email",
        name="Verification",
    )


def send_password_reset_email(
    user: models.User,
    db: Session,
) -> base_schemas.GenericResponse:
    """Send password reset email with rate limiting.
    :param user: user entry
    :param db: database session
    :return: Dictionary with success status, message and error code"""

    return send_verification_with_rate_limit(
        token_type=TokenType.PASSWORD_RESET,
        user=user,
        db=db,
        send_email_function=email_service.send_password_reset_email,
        endpoint="reset-password",
        name="Password reset",
    )


def send_email_change_email(
    user: models.User,
    new_email: str,
    db: Session,
) -> base_schemas.GenericResponse:
    """Send new email verification email with rate limiting.
    :param user: user entry
    :param new_email: new email address to verify
    :param db: database session
    :return: Dictionary with success status, message and error code"""

    return send_verification_with_rate_limit(
        token_type=TokenType.EMAIL_CHANGE,
        user=user,
        db=db,
        send_email_function=lambda _, url, name: email_service.send_email_change_verification(new_email, url, name),
        endpoint="verify-new-email",
        pending_email=new_email,
        name="Email change verification",
    )
