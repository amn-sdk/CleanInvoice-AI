from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.billing import Invoice
from app.models.auth import User
from app.utils.dependencies import get_current_active_user
import httpx
import os

router = APIRouter(prefix="/ai", tags=["AI"])

AI_SERVICE_URL = os.getenv("AI_SERVICE_URL", "http://localhost:8001")

@router.post("/invoices/{invoice_id}/extract")
async def extract_invoice_from_upload(
    invoice_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Upload an invoice image and extract data using AI OCR.
    The extracted data is stored in the invoice's ai_metadata field.
    """
    # Verify invoice belongs to user's company
    invoice = db.query(Invoice).filter(
        Invoice.id == invoice_id,
        Invoice.company_id == current_user.company_id
    ).first()
    
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    # Forward file to AI service
    try:
        async with httpx.AsyncClient() as client:
            files = {"file": (file.filename, await file.read(), file.content_type)}
            response = await client.post(
                f"{AI_SERVICE_URL}/ocr/extract",
                files=files,
                timeout=30.0
            )
            response.raise_for_status()
            result = response.json()
        
        # Store AI metadata
        invoice.ai_metadata = result.get("data", {})
        db.commit()
        
        return {
            "success": True,
            "invoice_id": invoice_id,
            "extracted_data": result.get("data"),
            "message": "Invoice data extracted successfully"
        }
    
    except httpx.HTTPError as e:
        raise HTTPException(
            status_code=503,
            detail=f"AI service unavailable: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Extraction failed: {str(e)}"
        )

@router.get("/health")
async def ai_integration_health():
    """Check if AI service integration is working."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{AI_SERVICE_URL}/health", timeout=5.0)
            return {
                "core_api": "ok",
                "ai_service": response.json()
            }
    except Exception as e:
        return {
            "core_api": "ok",
            "ai_service": "unreachable",
            "error": str(e)
        }
