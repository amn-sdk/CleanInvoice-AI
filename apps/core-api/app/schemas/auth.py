from pydantic import BaseModel, EmailStr
from typing import Optional
from uuid import UUID

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    role: str = "ACCOUNTANT"

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class UserResponse(BaseModel):
    id: UUID
    email: str
    full_name: str
    role: str
    company_id: UUID

    class Config:
        from_attributes = True

class CompanyCreate(BaseModel):
    name: str
    siret: Optional[str] = None
    vat_number: Optional[str] = None

class CompanyResponse(BaseModel):
    id: UUID
    name: str
    siret: Optional[str]
    vat_number: Optional[str]
    is_active: bool

    class Config:
        from_attributes = True
