from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.billing import Invoice
from app.models.auth import User
from app.utils.dependencies import get_current_active_user
from app.services.pdf_service import PDFService
from app.services.facturx_service import FacturXService
from app.services.facturx_combiner import FacturXCombiner

router = APIRouter(prefix="/export", tags=["Export"])

pdf_service = PDFService()
facturx_service = FacturXService()
combiner = FacturXCombiner()

@router.get("/invoices/{invoice_id}/pdf")
def export_invoice_pdf(
    invoice_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Generate and download invoice as PDF."""
    invoice = db.query(Invoice).filter(
        Invoice.id == invoice_id,
        Invoice.company_id == current_user.company_id
    ).first()
    
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    # Prepare data
    company = current_user.company
    customer = invoice.customer
    
    invoice_data = pdf_service.prepare_invoice_data(invoice, company, customer)
    
    # Generate PDF
    pdf_bytes = pdf_service.generate_invoice_pdf(invoice_data)
    
    # Return as downloadable file
    filename = f"facture_{invoice.number or invoice.id}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )

@router.get("/invoices/{invoice_id}/facturx")
def export_invoice_facturx(
    invoice_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Generate and download invoice as Factur-X (PDF/A-3 with embedded XML)."""
    invoice = db.query(Invoice).filter(
        Invoice.id == invoice_id,
        Invoice.company_id == current_user.company_id
    ).first()
    
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    # Prepare data
    company = current_user.company
    customer = invoice.customer
    
    # Generate PDF
    invoice_data = pdf_service.prepare_invoice_data(invoice, company, customer)
    pdf_bytes = pdf_service.generate_invoice_pdf(invoice_data)
    
    # Generate Factur-X XML
    xml_str = facturx_service.generate_facturx_xml(invoice, company, customer)
    
    # Combine into Factur-X PDF
    facturx_pdf = combiner.combine_pdf_xml(pdf_bytes, xml_str)
    
    # Return as downloadable file
    filename = f"facture-x_{invoice.number or invoice.id}.pdf"
    return Response(
        content=facturx_pdf,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )

@router.get("/invoices/{invoice_id}/xml")
def export_invoice_xml(
    invoice_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Generate and download invoice XML (Factur-X format)."""
    invoice = db.query(Invoice).filter(
        Invoice.id == invoice_id,
        Invoice.company_id == current_user.company_id
    ).first()
    
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    # Generate Factur-X XML
    company = current_user.company
    customer = invoice.customer
    xml_str = facturx_service.generate_facturx_xml(invoice, company, customer)
    
    # Return as downloadable file
    filename = f"facture_{invoice.number or invoice.id}.xml"
    return Response(
        content=xml_str.encode('utf-8'),
        media_type="application/xml",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )
