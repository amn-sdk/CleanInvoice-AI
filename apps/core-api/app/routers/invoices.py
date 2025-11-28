from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.invoices import InvoiceCreate, InvoiceResponse
from app.models.billing import Invoice, InvoiceLine
from app.models.auth import User
from app.utils.dependencies import get_current_active_user
from typing import List
import uuid
from decimal import Decimal

router = APIRouter(prefix="/invoices", tags=["Invoices"])

@router.post("/", response_model=InvoiceResponse, status_code=status.HTTP_201_CREATED)
def create_invoice(
    invoice_data: InvoiceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new invoice for the current company."""
    
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
        company_id=current_user.company_id,
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
def list_invoices(
    skip: int = 0,
    limit: int = 100,
    type: str = None,
    status: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """List invoices for the current company with optional filters."""
    query = db.query(Invoice).filter(Invoice.company_id == current_user.company_id)
    
    if type:
        query = query.filter(Invoice.type == type)
    if status:
        query = query.filter(Invoice.status == status)
    
    invoices = query.offset(skip).limit(limit).all()
    return invoices

@router.get("/{invoice_id}", response_model=InvoiceResponse)
def get_invoice(
    invoice_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get a specific invoice by ID."""
    invoice = db.query(Invoice).filter(
        Invoice.id == invoice_id,
        Invoice.company_id == current_user.company_id
    ).first()
    
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return invoice

@router.put("/{invoice_id}/status")
def update_invoice_status(
    invoice_id: str,
    new_status: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update invoice status (e.g., DRAFT -> ISSUED)."""
    invoice = db.query(Invoice).filter(
        Invoice.id == invoice_id,
        Invoice.company_id == current_user.company_id
    ).first()
    
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    # Validate status transition (add more logic here)
    allowed_statuses = ["DRAFT", "ISSUED", "PAID", "LATE", "CANCELLED"]
    if new_status not in allowed_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status. Allowed: {allowed_statuses}")
    
    invoice.status = new_status
    db.commit()
    
    return {"message": "Status updated successfully", "new_status": new_status}

@router.delete("/{invoice_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_invoice(
    invoice_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete a draft invoice."""
    invoice = db.query(Invoice).filter(
        Invoice.id == invoice_id,
        Invoice.company_id == current_user.company_id
    ).first()
    
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    # Only allow deletion of draft invoices
    if invoice.status != "DRAFT":
        raise HTTPException(
            status_code=400,
            detail="Can only delete draft invoices"
        )
    
    db.delete(invoice)
    db.commit()
    return None
