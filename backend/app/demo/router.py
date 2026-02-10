"""Demo cleanup endpoint."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models, database, base_schemas
from app.core.oauth2 import get_current_user
from app.demo.seed import cleanup_demo_user

demo_router = APIRouter(prefix="/demo", tags=["Demo"])


@demo_router.post("/cleanup", status_code=status.HTTP_200_OK, response_model=base_schemas.GenericResponse)
def demo_cleanup(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(database.get_db),
) -> base_schemas.GenericResponse:
    """Clean up a demo user and all their data.
    Only accessible by demo users.
    :param current_user: The current authenticated demo user
    :param db: The database session (demo schema)
    :returns: Success response"""

    if not current_user.is_demo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This endpoint is only available for demo users.",
        )

    cleanup_demo_user(db, current_user.id)
    return base_schemas.GenericResponse(success=True, message="Demo data cleaned up successfully.")
