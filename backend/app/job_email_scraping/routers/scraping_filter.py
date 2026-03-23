"""FastAPI routers for the job email scraping service endpoints.

Provides REST API endpoints for managing job alert emails, scraped job postings,
and service execution logs with CRUD operations and admin access controls."""

from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status

from app import models
from app.core.oauth2 import get_current_user
from app.database import get_db
from app.job_email_scraping import schemas
from app.routers.utility import generate_data_table_crud_router, NOT_ALLOWED_EXCEPTION

scraping_filter_router = generate_data_table_crud_router(
    table_model=models.ScrapingExclusionFilter,
    create_schema=schemas.ScrapingFilterCreate,
    update_schema=schemas.ScrapingFilterUpdate,
    out_schema=schemas.ScrapingFilterOut,
    endpoint="scraping-exclusion-filters",
    not_found_msg="Scraped Job Filter not found",
    allowed_actions=["get_all", "get_one", "post"],
)


@scraping_filter_router.put("/{filter_id}", status_code=status.HTTP_200_OK, response_model=schemas.ScrapingFilterOut)
def update_scraping_filter(
    filter_id: int,
    update_data: schemas.ScrapingFilterUpdate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update a scraped job filter by ID.
    :param filter_id: ID of the filter to update
    :param update_data: Update data for the filter
    :param current_user: Current authenticated user
    :param db: Database session"""

    # Fetch the filter to ensure it exists and belongs to the current user.
    filter_obj = (
        db.query(models.ScrapingExclusionFilter)
        .filter(models.ScrapingExclusionFilter.id == filter_id)
        .filter(models.ScrapingExclusionFilter.owner_id == current_user.id)
        .first()
    )

    if not filter_obj:
        raise NOT_ALLOWED_EXCEPTION

    # Get the update fields
    update_dict = update_data.model_dump(exclude_unset=True)
    print(filter_obj.filtered_jobs)
    print(filter_obj.id)

    # If the filter previously filtered jobs, only allow is_active updates
    if filter_obj.filtered_jobs:
        # Check if any fields other than is_active are being updated
        non_active_fields = {k: v for k, v in update_dict.items() if k != "is_active"}
        if non_active_fields:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Cannot update filter fields other than is_active when filter has been used",
            )

    # If the filter was never used, update it
    for key, value in update_data.model_dump(exclude_unset=True).items():
        setattr(filter_obj, key, value)

    db.commit()
    db.refresh(filter_obj)
    return filter_obj


@scraping_filter_router.delete("/{filter_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_scraping_filter(
    filter_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a scraped job filter by ID.
    :param filter_id: ID of the filter to delete
    :param current_user: Current authenticated user
    :param db: Database session
    :return: The deleted or deactivated filter object"""

    # Fetch the filter to ensure it exists and belongs to the current user
    filter_obj = (
        db.query(models.ScrapingExclusionFilter)
        .filter(models.ScrapingExclusionFilter.id == filter_id)
        .filter(models.ScrapingExclusionFilter.owner_id == current_user.id)
        .first()
    )

    if not filter_obj:
        raise NOT_ALLOWED_EXCEPTION

    # If the filter has filtered jobs, do not delete it, just deactivate it
    if filter_obj.filtered_jobs:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT)
    else:
        db.delete(filter_obj)
        db.commit()
