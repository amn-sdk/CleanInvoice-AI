from PIL import Image
import pytesseract
import re
from typing import Dict, Optional
from datetime import datetime

class InvoiceOCRService:
    """Service for extracting text and data from invoice images using OCR."""
    
    def __init__(self):
        # Configuration for pytesseract
        # On some systems, you may need to set: pytesseract.pytesseract.tesseract_cmd = r'/usr/bin/tesseract'
        pass
    
    def extract_text(self, image_path: str) -> str:
        """
        Extract raw text from an invoice image.
        
        Args:
            image_path: Path to the invoice image file
            
        Returns:
            Extracted text as string
        """
        image = Image.open(image_path)
        text = pytesseract.image_to_string(image, lang='fra')  # French language
        return text
    
    def extract_invoice_data(self, image_path: str) -> Dict:
        """
        Extract structured data from an invoice image.
        
        Args:
            image_path: Path to the invoice image file
            
        Returns:
            Dictionary with extracted invoice data
        """
        # Extract text
        text = self.extract_text(image_path)
        
        # Initialize result
        result = {
            'confidence': 0.0,
            'raw_text': text,
            'invoice_number': None,
            'date': None,
            'total_amount': None,
            'supplier_name': None,
            'vat_number': None,
            'lines': []
        }
        
        # Extract invoice number (patterns: FA-2024-001, FACT 001, Invoice #123, etc.)
        invoice_patterns = [
            r'(?:facture|invoice|fact\.?)\s*[:#]?\s*([A-Z0-9\-]+)',
            r'n[°o]?\s*(?:facture|invoice)?\s*[:#]?\s*([A-Z0-9\-]+)',
        ]
        for pattern in invoice_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                result['invoice_number'] = match.group(1).strip()
                break
        
        # Extract dates (DD/MM/YYYY, DD-MM-YYYY, YYYY-MM-DD)
        date_patterns = [
            r'(\d{1,2}[/-]\d{1,2}[/-]\d{4})',
            r'(\d{4}[/-]\d{1,2}[/-]\d{1,2})',
        ]
        for pattern in date_patterns:
            match = re.search(pattern, text)
            if match:
                result['date'] = match.group(1)
                break
        
        # Extract total amount
        # Patterns: 1 234,56 €, 1234.56 EUR, Total: 1234,56, etc.
        total_patterns = [
            r'(?:total|montant|amount)\s*(?:ttc|ht)?\s*:?\s*([0-9\s]+[,.]?\d{2})\s*€?',
            r'([0-9\s]+[,.]\d{2})\s*(?:€|EUR|euros?)',
        ]
        for pattern in total_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                # Take the last (usually the grand total)
                amount_str = matches[-1].replace(' ', '').replace(',', '.')
                try:
                    result['total_amount'] = float(amount_str)
                except ValueError:
                    pass
                break
        
        # Extract VAT number
        vat_pattern = r'(?:tva|vat)\s*(?:intra)?\.?\s*:?\s*([A-Z]{2}\s*\d[\dA-Z\s]+)'
        match = re.search(vat_pattern, text, re.IGNORECASE)
        if match:
            result['vat_number'] = match.group(1).strip().replace(' ', '')
        
        # Extract supplier name (usually at the top, first non-empty line)
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        if lines:
            result['supplier_name'] = lines[0][:100]  # First line, max 100 chars
        
        # Calculate confidence score based on extracted fields
        fields_found = sum([
            1 if result['invoice_number'] else 0,
            1 if result['date'] else 0,
            1 if result['total_amount'] else 0,
            1 if result['supplier_name'] else 0,
        ])
        result['confidence'] = fields_found / 4.0  # 0.0 to 1.0
        
        return result
