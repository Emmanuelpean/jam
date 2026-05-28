"""Router for testing email functionalities in test mode."""

import re

from fastapi import APIRouter, HTTPException
from starlette import status

from app.config import settings
from app.emails.email_service import email_service

email_test_router = APIRouter(prefix="/test", tags=["testing"])


@email_test_router.get("/emails/{email_address}")
def get_test_emails(email_address: str) -> dict:
    """Get all test emails sent to a specific address."""

    if not settings.test_mode:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Test mode not enabled")

    emails = email_service.get_test_emails(email_address)
    return {"emails": emails}


@email_test_router.get("/verification-link/{email_address}")
def get_verification_link(email_address: str) -> dict:
    """Extract verification link from the most recent email."""

    if not settings.test_mode:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Test mode not enabled")

    emails = email_service.get_test_emails(email_address)
    if not emails:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No emails found")

    # Get most recent email
    latest_email = emails[-1]

    # Extract verification URL from HTML body
    base_url = re.escape(settings.frontend_url + "/") + r"[^/]+"
    pattern = base_url + r"/\?token=([A-Za-z0-9_\-]+)"
    match = re.search(pattern, latest_email["body"])

    if match:
        return {"verification_url": match.group(0)}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No verification link found")


@email_test_router.get("/reset-link/{email_address}")
def get_reset_link(email_address: str) -> dict:
    """Extract password reset link from the most recent email."""

    if not settings.test_mode:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Test mode not enabled")

    emails = email_service.get_test_emails(email_address)
    if not emails:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No emails found")

    latest_email = emails[-1]

    # Extract reset URL from HTML body
    base_url = settings.frontend_url + "/reset-password/?token="
    pattern = re.escape(base_url) + r"([A-Za-z0-9_\-]+)"  # Capture the token (assuming token format)
    match = re.search(pattern, latest_email["body"])

    if match:
        return {"reset_url": base_url + match.group(1)}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No reset link found")


@email_test_router.delete("/emails")
def clear_test_emails() -> dict:
    """Clear all test emails."""

    if not settings.test_mode:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Test mode not enabled")

    email_service.clear_test_emails()
    return {"status": "cleared"}
