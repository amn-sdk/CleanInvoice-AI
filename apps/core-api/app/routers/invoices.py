from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.invoices import InvoiceCreate, InvoiceResponse
from app.models.billing import Invoice, InvoiceLine
from typing import List
import uuid
from decimal import Decimal

router = APIRouter(prefix="/invoices", tags=["Invoices"])

# TODO: Add proper authentication dependency
# For now, we'll assume company_id is passed or we use a placeholder

@router.post("/", response_model=InvoiceResponse, status_code=status.HTTP_201_CREATED)
def create_invoice(invoice_data: InvoiceCreate, db: Session = Depends(get_db)):
    # TODO: Get company_id from authenticated user
    # For demo, we'll need to pass it or use a test company
    
    # Calculate totals
    total_ht = Decimal("0.00")
    total_tva = Decimal("0.00")
    
    for line in invoice_data.lines:
        line_ht = line.quantity * line.unit_price
        line_tva = line_ht * (line.vat_rate / Decimal("100"))
        total_ht += line_ht
        total_tva += line_tva
    
    total_ttc = total_ht + total_tva
    
    # Create invoice
    new_invoice = Invoice(
        id=uuid.uuid4(),
        # company_id=company_id,  # TODO: from auth
        customer_id=invoice_data.customer_id,
        supplier_id=invoice_data.supplier_id,
        type=invoice_data.type,
        status="DRAFT",
        date_issued=invoice_data.date_issued,
        date_due=invoice_data.date_due,
        total_ht=total_ht,
        total_tva=total_tva,
        total_ttc=total_ttc
    )
    db.add(new_invoice)
    db.flush()
    
    # Create lines
    for line_data in invoice_data.lines:
        amount_ht = line_data.quantity * line_data.unit_price
        line = InvoiceLine(
            id=uuid.uuid4(),
            invoice_id=new_invoice.id,
            description=line_data.description,
            quantity=line_data.quantity,
            unit_price=line_data.unit_price,
            vat_rate=line_data.vat_rate,
            amount_ht=amount_ht
        )
        db.add(line)
    
    db.commit()
    db.refresh(new_invoice)
    
    return new_invoice

@router.get("/", response_model=List[InvoiceResponse])
def list_invoices(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    # TODO: Filter by company_id from auth
    invoices = db.query(Invoice).offset(skip).limit(limit).all()
    return invoices

@router.get("/{invoice_id}", response_model=InvoiceResponse)
def get_invoice(invoice_id: str, db: Session = Depends(get_db)):
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return invoice
