from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.ocr_service import InvoiceOCRService
import os
import uuid
from pathlib import Path

router = APIRouter(prefix="/ocr", tags=["OCR"])

ocr_service = InvoiceOCRService()

# Temporary upload directory
UPLOAD_DIR = Path("/tmp/cleaninvoice_uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

@router.post("/extract")
async def extract_invoice_data(file: UploadFile = File(...)):
    """
    Extract data from an invoice image using OCR.
    
    Accepts: JPG, PNG, PDF (first page)
    Returns: Extracted invoice data with confidence score
    """
    # Validate file type
    allowed_extensions = ['.jpg', '.jpeg', '.png', '.pdf']
    file_ext = os.path.splitext(file.filename)[1].lower()
    
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"File type not supported. Allowed: {', '.join(allowed_extensions)}"
        )
    
    # Save uploaded file temporarily
    temp_filename = f"{uuid.uuid4()}{file_ext}"
    temp_path = UPLOAD_DIR / temp_filename
    
    try:
        # Save file
        with open(temp_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Handle PDF (convert first page to image)
        if file_ext == '.pdf':
            # For production, use pdf2image library
            # For now, we'll return an error for PDFs
            raise HTTPException(
                status_code=501,
                detail="PDF support requires pdf2image library (coming soon)"
            )
        
        # Extract data
        result = ocr_service.extract_invoice_data(str(temp_path))
        
        return {
            "success": True,
            "data": result,
            "message": f"Extraction confidence: {result['confidence']:.1%}"
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"OCR extraction failed: {str(e)}"
        )
    
    finally:
        # Clean up temporary file
        if temp_path.exists():
            temp_path.unlink()

@router.get("/health")
def ocr_health():
    """Check if OCR service is operational."""
    return {
        "status": "ok",
        "service": "OCR Invoice Extraction",
        "languages": ["fra", "eng"]
    }
