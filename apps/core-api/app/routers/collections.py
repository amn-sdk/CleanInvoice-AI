from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.billing import Invoice
from app.models.collections import CollectionCase, CollectionEvent
from app.models.auth import User
from app.utils.dependencies import get_current_active_user
from datetime import datetime, date
import httpx
import os
import uuid

router = APIRouter(prefix="/collections", tags=["Collections"])

AI_SERVICE_URL = os.getenv("AI_SERVICE_URL", "http://localhost:8001")

@router.post("/invoices/{invoice_id}/start")
async def start_collection(
    invoice_id: str,
    strategy: str = "STANDARD",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Start collection process for an overdue invoice.
    Creates a collection case and generates first contact email.
    """
    # Get invoice
    invoice = db.query(Invoice).filter(
        Invoice.id == invoice_id,
        Invoice.company_id == current_user.company_id
    ).first()
    
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    if invoice.status not in ["ISSUED", "LATE"]:
        raise HTTPException(
            status_code=400,
            detail="Invoice must be issued or late to start collection"
        )
    
    # Check if collection already exists
    existing = db.query(CollectionCase).filter(
        CollectionCase.invoice_id == invoice_id
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Collection case already exists for this invoice"
        )
    
    # Calculate days overdue
    today = date.today()
    days_overdue = (today - invoice.date_due).days
    
    # Prepare data for AI agent
    customer = invoice.customer
    invoice_data = {
        "id": str(invoice.id),
        "number": invoice.number or "DRAFT",
        "amount": float(invoice.total_ttc),
        "customer_name": customer.name if customer else "Unknown",
        "customer_email": customer.email if customer else "",
        "days_overdue": days_overdue,
        "payment_history": "No history",  # TODO: Calculate from past invoices
        "strategy": strategy
    }
    
    # Call AI service
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{AI_SERVICE_URL}/collections/process",
                json=invoice_data,
                timeout=30.0
            )
            response.raise_for_status()
            ai_result = response.json()
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"AI service unavailable: {str(e)}"
        )
    
    # Create collection case
    collection_case = CollectionCase(
        id=uuid.uuid4(),
        invoice_id=invoice.id,
        status="OPEN",
        strategy=strategy,
        level=1,
        ai_context=ai_result.get("result", {})
    )
    db.add(collection_case)
    
    # Create first event
    event = CollectionEvent(
        id=uuid.uuid4(),
        case_id=collection_case.id,
        type="EMAIL_SENT",
        channel="EMAIL",
        content=ai_result["result"]["email"]["body"],
        metadata_=ai_result["result"]["email"]
    )
    db.add(event)
    
    db.commit()
    
    return {
        "success": True,
        "case_id": str(collection_case.id),
        "email_generated": ai_result["result"]["email"]
    }

@router.get("/invoices/{invoice_id}/timeline")
def get_collection_timeline(
    invoice_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get the collection timeline for an invoice."""
    # Verify invoice access
    invoice = db.query(Invoice).filter(
        Invoice.id == invoice_id,
        Invoice.company_id == current_user.company_id
    ).first()
    
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    # Get collection case
    case = db.query(CollectionCase).filter(
        CollectionCase.invoice_id == invoice_id
    ).first()
    
    if not case:
        return {
            "has_case": False,
            "timeline": []
        }
    
    # Get events
    events = db.query(CollectionEvent).filter(
        CollectionEvent.case_id == case.id
    ).order_by(CollectionEvent.created_at.desc()).all()
    
    return {
        "has_case": True,
        "case_id": str(case.id),
        "status": case.status,
        "strategy": case.strategy,
        "level": case.level,
        "timeline": [
            {
                "id": str(e.id),
                "type": e.type,
                "channel": e.channel,
                "content": e.content,
                "metadata": e.metadata_,
                "created_at": e.created_at.isoformat()
            }
            for e in events
        ]
    }

@router.put("/cases/{case_id}/close")
def close_collection_case(
    case_id: str,
    reason: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Close a collection case."""
    case = db.query(CollectionCase).filter(
        CollectionCase.id == case_id
    ).first()
    
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    # Verify access through invoice
    invoice = db.query(Invoice).filter(
        Invoice.id == case.invoice_id,
        Invoice.company_id == current_user.company_id
    ).first()
    
    if not invoice:
        raise HTTPException(status_code=404, detail="Access denied")
    
    # Update case
    case.status = "CLOSED_PAID" if reason == "paid" else "CLOSED_LOST"
    
    # Add event
    event = CollectionEvent(
        id=uuid.uuid4(),
        case_id=case.id,
        type="STATUS_CHANGE",
        channel="SYSTEM",
        content=f"Case closed: {reason}"
    )
    db.add(event)
    
    db.commit()
    
    return {"success": True, "new_status": case.status}
