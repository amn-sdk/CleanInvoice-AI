from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from datetime import date
from decimal import Decimal

class InvoiceLineCreate(BaseModel):
    description: str
    quantity: Decimal = Decimal("1.0")
    unit_price: Decimal
    vat_rate: Decimal

class InvoiceLineResponse(BaseModel):
    id: UUID
    description: str
    quantity: Decimal
    unit_price: Decimal
    vat_rate: Decimal
    amount_ht: Decimal

    class Config:
        from_attributes = True

class InvoiceCreate(BaseModel):
    customer_id: Optional[UUID] = None
    supplier_id: Optional[UUID] = None
    type: str  # OUT_INVOICE, IN_INVOICE
    date_issued: date
    date_due: date
    lines: List[InvoiceLineCreate]

class InvoiceResponse(BaseModel):
    id: UUID
    type: str
    status: str
    number: Optional[str]
    date_issued: date
    date_due: date
    total_ht: Decimal
    total_tva: Decimal
    total_ttc: Decimal
    lines: List[InvoiceLineResponse]

    class Config:
        from_attributes = True
