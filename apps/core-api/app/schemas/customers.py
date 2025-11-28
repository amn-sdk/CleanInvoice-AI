from pydantic import BaseModel, EmailStr
from typing import Optional
from uuid import UUID

class CustomerCreate(BaseModel):
    name: str
    email: Optional[EmailStr] = None
    siret: Optional[str] = None
    vat_number: Optional[str] = None
    address: Optional[dict] = None
    is_individual: bool = False
    payment_terms: int = 30

class CustomerUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    siret: Optional[str] = None
    vat_number: Optional[str] = None
    address: Optional[dict] = None
    is_individual: Optional[bool] = None
    payment_terms: Optional[int] = None

class CustomerResponse(BaseModel):
    id: UUID
    company_id: UUID
    name: str
    email: Optional[str]
    siret: Optional[str]
    vat_number: Optional[str]
    is_individual: bool
    payment_terms: int

    class Config:
        from_attributes = True
