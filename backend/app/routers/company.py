"""Company route"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app import models, database, schemas, oauth2
from app.routers.utils import _get_all_entries, _get_entry_by_id, _update_entry, _create_entry, _delete_entry

router = APIRouter(prefix="/companies", tags=["companies"])


@router.get("/", response_model=list[schemas.CompanyOut])
def get_all_companies(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(oauth2.get_current_user),
    limit: int = 10,
):
    """Get all companies for the current user.
    :param db: The database session.
    :param current_user: The current user.
    :param limit: The maximum number of companies to return.
    :returns: A list of companies."""

    return _get_all_entries(
        table=models.Company,
        db=db,
        current_user=current_user,
        limit=limit,
    )


@router.get("/{company_id}", response_model=schemas.CompanyOut)
def get_company(
    company_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(oauth2.get_current_user),
):
    """Get a company by ID.
    :param company_id: The company ID.
    :param db: The database session.
    :param current_user: The current user.
    :returns: The company if found."""

    return _get_entry_by_id(
        table=models.Company,
        entry_id=company_id,
        db=db,
        current_user=current_user,
        not_found_message="Company not found",
    )


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.CompanyOut)
def create_company(
    company: schemas.Company,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(oauth2.get_current_user),
):
    """Create a new company.
    :param company: The company data.
    :param db: The database session.
    :param current_user: The current user.
    :returns: The created company."""

    return _create_entry(
        table=models.Company,
        entry_data=company,
        db=db,
        current_user=current_user,
    )


@router.delete("/{company_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_company(
    company_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(oauth2.get_current_user),
):
    """Delete a company by ID.
    :param company_id: The company ID.
    :param db: The database session.
    :param current_user: The current user.
    :returns: Dict with deletion status message."""

    return _delete_entry(
        table=models.Company,
        entry_id=company_id,
        db=db,
        current_user=current_user,
        not_found_message="Company not found",
    )


@router.put("/{company_id}", response_model=schemas.CompanyOut)
def update_company(
    company_id: int,
    updated_company: schemas.CompanyUpdate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(oauth2.get_current_user),
):
    """Update a company by ID.
    :param company_id: The company ID.
    :param updated_company: The updated company data.
    :param db: The database session.
    :param current_user: The current user.
    :returns: The updated company."""

    return _update_entry(
        table=models.Company,
        entry_id=company_id,
        updated_data=updated_company,
        db=db,
        current_user=current_user,
        not_found_message="Company not found",
    )
