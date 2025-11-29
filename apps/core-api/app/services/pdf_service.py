from jinja2 import Environment, FileSystemLoader, select_autoescape

import os
from pathlib import Path

class PDFService:
    """Service for generating PDF invoices from HTML templates."""
    
    def __init__(self):
        # Setup Jinja2 environment
        template_dir = Path(__file__).parent.parent / 'templates'
        self.env = Environment(
            loader=FileSystemLoader(str(template_dir)),
            autoescape=select_autoescape(['html', 'xml'])
        )
    
    def generate_invoice_pdf(self, invoice_data: dict, output_path: str = None) -> bytes:
        """
        Generate a PDF for an invoice.
        
        Args:
            invoice_data: Dictionary containing invoice information
            output_path: Optional path to save the PDF file
            
        Returns:
            PDF content as bytes
        """
        # Render HTML template
        template = self.env.get_template('invoice.html')
        html_content = template.render(**invoice_data)
        
        # Generate PDF
        try:
            from weasyprint import HTML
            pdf_bytes = HTML(string=html_content).write_pdf()
        except OSError as e:
            print(f"Error loading WeasyPrint dependencies: {e}")
            raise ImportError("PDF generation failed: Missing system dependencies (pango, libffi). Please install them via 'brew install pango libffi glib'.")
        except ImportError:
             raise ImportError("WeasyPrint not installed.")
        
        # Optionally save to file
        if output_path:
            with open(output_path, 'wb') as f:
                f.write(pdf_bytes)
        
        return pdf_bytes
    
    def prepare_invoice_data(self, invoice, company, customer=None):
        """
        Prepare invoice data dictionary for template rendering.
        
        Args:
            invoice: SQLAlchemy Invoice model instance
            company: SQLAlchemy Company model instance
            customer: SQLAlchemy Customer model instance (optional)
            
        Returns:
            Dictionary with formatted invoice data
        """
        # Format company address
        company_address = ""
        if company.address:
            addr = company.address
            company_address = f"{addr.get('street', '')}, {addr.get('zip', '')} {addr.get('city', '')}, {addr.get('country', '')}"
        
        # Format customer info
        customer_name = customer.name if customer else "N/A"
        customer_siret = customer.siret if customer else None
        customer_vat = customer.vat_number if customer else None
        customer_address = ""
        if customer and customer.address:
            addr = customer.address
            customer_address = f"{addr.get('street', '')}, {addr.get('zip', '')} {addr.get('city', '')}"
        
        # Prepare lines
        lines = []
        for line in invoice.lines:
            lines.append({
                'description': line.description,
                'quantity': float(line.quantity),
                'unit_price': float(line.unit_price),
                'vat_rate': float(line.vat_rate),
                'amount_ht': float(line.amount_ht)
            })
        
        return {
            'company_name': company.name,
            'company_siret': company.siret,
            'company_vat': company.vat_number,
            'company_address': company_address,
            'invoice_number': invoice.number or 'DRAFT',
            'date_issued': invoice.date_issued.strftime('%d/%m/%Y'),
            'date_due': invoice.date_due.strftime('%d/%m/%Y'),
            'customer_name': customer_name,
            'customer_siret': customer_siret,
            'customer_vat': customer_vat,
            'customer_address': customer_address,
            'lines': lines,
            'total_ht': float(invoice.total_ht),
            'total_tva': float(invoice.total_tva),
            'total_ttc': float(invoice.total_ttc),
        }
