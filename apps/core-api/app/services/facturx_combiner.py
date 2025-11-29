from facturx import generate_facturx_from_binary
import io

class FacturXCombiner:
    """Service to combine PDF and XML into a Factur-X compliant PDF/A-3 file."""
    
    def combine_pdf_xml(self, pdf_bytes: bytes, xml_str: str) -> bytes:
        """
        Combine a PDF and Factur-X XML into a compliant Factur-X PDF.
        
        Args:
            pdf_bytes: PDF file content as bytes
            xml_str: Factur-X XML as string
            
        Returns:
            Factur-X PDF content as bytes
        """
        # Convert XML string to bytes
        xml_bytes = xml_str.encode('utf-8')
        
        # Generate Factur-X PDF (PDF/A-3 with embedded XML)
        facturx_pdf = generate_facturx_from_binary(
            pdf_content=pdf_bytes,
            xml_content=xml_bytes,
            facturx_level='minimum',  # EN 16931 profile
        )
        
        return facturx_pdf
