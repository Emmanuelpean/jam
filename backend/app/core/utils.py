"""Utility functions for token management and email verification."""

import datetime as dt
import secrets
from typing import Callable

import requests
from sqlalchemy.orm import Session
from starlette import status

from app import models
from app.base_schemas import GenericResponse
from app.config import settings
from app.core.models import TokenType
from app.emails.email_service import email_service
from app.utilities import security


def verify_captcha_token(token: str) -> bool:
    """Verify a Cloudflare Turnstile token with the siteverify endpoint.
    :param token: Token produced by the Turnstile widget on the client.
    :return: True if Cloudflare confirms the token is valid, False otherwise."""

    if not token:
        return False

    try:
        response = requests.post(
            "https://challenges.cloudflare.com/turnstile/v0/siteverify",
            data={"secret": settings.turnstile_secret_key, "response": token},
            timeout=5,
        )
        response.raise_for_status()
        return bool(response.json().get("success"))
    except (requests.RequestException, ValueError):
        return False


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
    created_at: dt.datetime | None = None,
) -> tuple[str, models.UserToken]:
    """Generate a secure random token for the user.
    Existing tokens of the same type are removed by the UserToken before_insert listener.
    :param user_id: ID of the user for whom the token is generated
    :param token_type: Type of the token (e.g., 'verification', 'password_reset', 'email_change')
    :param db: Database session
    :param pending_email: Optional pending email for email_change tokens
    :param created_at: Optional creation timestamp (defaults to now); used to backdate tokens in tests
    :return: Tuple of (plain_token, UserToken object)"""

    plain_token = secrets.token_urlsafe(32)
    hashed_token = security.hash_token(plain_token)

    new_token = models.UserToken(
        owner_id=user_id,
        token=hashed_token,
        token_type=token_type,
        pending_email=pending_email,
    )
    if created_at is not None:
        new_token.created_at = created_at
    db.add(new_token)
    db.commit()
    db.refresh(new_token)

    return plain_token, new_token


def check_token_rate_limit(
    token_type: TokenType,
    user: models.User,
    db: Session,
) -> int:
    """Check if the user has exceeded the rate limit for a given token type.
    :param token_type: Type of the token (e.g., 'verification')
    :param user: user entry
    :param db: Database session
    :return: True if rate limit exceeded, False otherwise"""

    existing_token = (
        db.query(models.UserToken)
        .filter(models.UserToken.owner_id == user.id)
        .filter(models.UserToken.token_type == token_type)
        .order_by(models.UserToken.created_at.desc())
        .first()
    )
    if existing_token:
        seconds_remaining = existing_token.remaining_seconds
        return seconds_remaining
    else:
        return 0


def send_rate_limited_tokenized_email(
    token_type: TokenType,
    user: models.User,
    db: Session,
    send_email_function: Callable,
    endpoint: str,
    name: str,
    pending_email: str | None = None,
) -> GenericResponse:
    """Send verification email with rate limiting.
    :param token_type: Type of the token
    :param user: user entry
    :param db: database session
    :param send_email_function: Function to send the email
    :param endpoint: Frontend endpoint for the verification link
    :param name: Name of the token type for messaging
    :param pending_email: Optional pending email for email_change tokens
    :return: Dictionary with success status, message, and error code"""

    # Check if enough time has passed since last token was generated
    seconds_remaining = check_token_rate_limit(token_type, user, db)
    if seconds_remaining > 0:
        return GenericResponse(
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
        return GenericResponse(
            success=True,
            message=f"{name} email sent successfully.",
            error_code=None,
        )

    except Exception as e:
        return GenericResponse(
            success=False,
            message=f"Error sending {token_type} email: {e}",
            error_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


def send_rate_limited_tokenized_email_verification_email(
    user: models.User,
    db: Session,
) -> GenericResponse:
    """Send email verification email with rate limiting.
    :param user: user entry
    :param db: database session
    :return: Dictionary with success status, message, and error code"""

    return send_rate_limited_tokenized_email(
        token_type=TokenType.EMAIL_VERIFICATION,
        user=user,
        db=db,
        send_email_function=email_service.send_email_verification_email,
        endpoint="verify-email",
        name="Verification",
    )


def send_rate_limited_tokenized_password_reset_email(
    user: models.User,
    db: Session,
) -> GenericResponse:
    """Send password reset email with rate limiting.
    :param user: user entry
    :param db: database session
    :return: Dictionary with success status, message, and error code"""

    return send_rate_limited_tokenized_email(
        token_type=TokenType.PASSWORD_RESET,
        user=user,
        db=db,
        send_email_function=email_service.send_password_reset_email,
        endpoint="reset-password",
        name="Password reset",
    )


def send_rate_limited_tokenized_email_change_email(
    user: models.User,
    new_email: str,
    db: Session,
) -> GenericResponse:
    """Send new email verification email with rate limiting.
    :param user: user entry
    :param new_email: new email address to verify
    :param db: database session
    :return: Dictionary with success status, message, and error code"""

    return send_rate_limited_tokenized_email(
        token_type=TokenType.EMAIL_CHANGE,
        user=user,
        db=db,
        send_email_function=lambda _, url, name: email_service.send_email_change_verification(new_email, url, name),
        endpoint="verify-new-email",
        pending_email=new_email,
        name="Email change verification",
    )


def send_tokenized_password_changed_email_with_rate_limit(
    user: models.User,
    db: Session,
) -> GenericResponse:
    """Send a notification email to the user when their password is changed.
    :param user: user entry
    :param db: database session
    :return: Dictionary with success status, message, and error code"""

    return send_rate_limited_tokenized_email(
        token_type=TokenType.PASSWORD_CHANGE,
        user=user,
        db=db,
        send_email_function=lambda email, b, c: email_service.send_password_changed_notification(email),
        name="Password changed",
        endpoint="",
    )
