"""Utility functions for token management and email verification."""

import secrets
from datetime import datetime, timezone, timedelta

from app import utils
from app.config import settings


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
