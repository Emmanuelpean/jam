"""FastAPI routers for the job email scraping service endpoints.

Provides REST API endpoints for managing job alert emails, scraped job postings,
and service execution logs with CRUD operations and admin access controls."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status

from app import models
from app.core.oauth2 import get_current_user
from app.database import get_db
from app.job_email_scraping import schemas

forwarding_confirmation_router = APIRouter(
    prefix="/forwarding-confirmation-links",
    tags=["forwarding-confirmation-links"],
)


@forwarding_confirmation_router.get("/pending", response_model=schemas.ForwardingConfirmationLinkOut | None)
def get_pending_confirmation_links(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> models.ForwardingConfirmationLink | None:
    """Get all unused forwarding confirmation links for the current user.
    :param current_user: Current authenticated user
    :param db: Database session
    :return: List of pending forwarding confirmation links"""

    entry = (
        db.query(models.ForwardingConfirmationLink)
        .filter(models.ForwardingConfirmationLink.owner_id == current_user.id)
        .order_by(models.ForwardingConfirmationLink.created_at.desc())
        .first()
    )
    if entry and entry.is_used:
        return None
    else:
        return entry


@forwarding_confirmation_router.put("/{link_id}", response_model=schemas.ForwardingConfirmationLinkOut)
def update_confirmation_link(
    link_id: int,
    update_data: schemas.ForwardingConfirmationLinkUpdate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> models.ForwardingConfirmationLink:
    """Update a forwarding confirmation link (mark as used).
    :param link_id: ID of the link to update
    :param update_data: Update data
    :param current_user: Current authenticated user
    :param db: Database session
    :return: Updated forwarding confirmation link"""

    link = (
        db.query(models.ForwardingConfirmationLink)
        .filter(models.ForwardingConfirmationLink.id == link_id)
        .filter(models.ForwardingConfirmationLink.owner_id == current_user.id)
        .first()
    )

    if not link:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Confirmation link not found")

    for key, value in update_data.model_dump(exclude_unset=True).items():
        setattr(link, key, value)

    db.commit()
    db.refresh(link)
    return link
