from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.auth import CompanyResponse
from app.models.auth import Company, User
from app.utils.dependencies import get_current_active_user

router = APIRouter(prefix="/companies", tags=["Companies"])

@router.get("/me", response_model=CompanyResponse)
def get_my_company(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get the current user's company information."""
    return current_user.company

@router.put("/me", response_model=CompanyResponse)
def update_my_company(
    company_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update the current user's company information."""
    company = current_user.company
    
    # Update allowed fields
    allowed_fields = ["name", "siret", "vat_number", "address", "settings"]
    for key, value in company_data.items():
        if key in allowed_fields:
            setattr(company, key, value)
    
    db.commit()
    db.refresh(company)
    return company
