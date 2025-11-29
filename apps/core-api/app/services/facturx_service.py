from datetime import datetime
from decimal import Decimal
import xml.etree.ElementTree as ET
from xml.dom import minidom

class FacturXService:
    """Service for generating Factur-X compliant XML (EN 16931 profile)."""
    
    def generate_facturx_xml(self, invoice, company, customer) -> str:
        """
        Generate Factur-X XML for an invoice.
        
        Args:
            invoice: SQLAlchemy Invoice model instance
            company: SQLAlchemy Company model instance
            customer: SQLAlchemy Customer model instance
            
        Returns:
            XML string (pretty formatted)
        """
        # Create root element
        root = ET.Element('rsm:CrossIndustryInvoice')
        root.set('xmlns:rsm', 'urn:un:unece:uncefact:data:standard:CrossIndustryInvoice:100')
        root.set('xmlns:ram', 'urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100')
        root.set('xmlns:udt', 'urn:un:unece:uncefact:data:standard:UnqualifiedDataType:100')
        root.set('xmlns:qdt', 'urn:un:unece:uncefact:data:standard:QualifiedDataType:100')
        
        # Exchange Context
        context = ET.SubElement(root, 'rsm:ExchangedDocumentContext')
        guideline = ET.SubElement(context, 'ram:GuidelineSpecifiedDocumentContextParameter')
        ET.SubElement(guideline, 'ram:ID').text = 'urn:cen.eu:en16931:2017#compliant#urn:factur-x.eu:1p0:minimum'
        
        # Document Header
        header = ET.SubElement(root, 'rsm:ExchangedDocument')
        ET.SubElement(header, 'ram:ID').text = invoice.number or 'DRAFT'
        ET.SubElement(header, 'ram:TypeCode').text = '380'  # Commercial invoice
        
        issue_date = ET.SubElement(header, 'ram:IssueDateTime')
        date_str = invoice.date_issued.strftime('%Y%m%d')
        ET.SubElement(issue_date, 'udt:DateTimeString', format='102').text = date_str
        
        # Supply Chain Transaction
        transaction = ET.SubElement(root, 'rsm:SupplyChainTradeTransaction')
        
        # Line Items
        for idx, line in enumerate(invoice.lines, 1):
            item = ET.SubElement(transaction, 'ram:IncludedSupplyChainTradeLineItem')
            
            doc_line_doc = ET.SubElement(item, 'ram:AssociatedDocumentLineDocument')
            ET.SubElement(doc_line_doc, 'ram:LineID').text = str(idx)
            
            product = ET.SubElement(item, 'ram:SpecifiedTradeProduct')
            ET.SubElement(product, 'ram:Name').text = line.description
            
            agreement = ET.SubElement(item, 'ram:SpecifiedLineTradeAgreement')
            gross_price = ET.SubElement(agreement, 'ram:GrossPriceProductTradePrice')
            ET.SubElement(gross_price, 'ram:ChargeAmount').text = f'{float(line.unit_price):.2f}'
            
            delivery = ET.SubElement(item, 'ram:SpecifiedLineTradeDelivery')
            billed_qty = ET.SubElement(delivery, 'ram:BilledQuantity', unitCode='C62')
            billed_qty.text = f'{float(line.quantity):.2f}'
            
            settlement = ET.SubElement(item, 'ram:SpecifiedLineTradeSettlement')
            trade_tax = ET.SubElement(settlement, 'ram:ApplicableTradeTax')
            ET.SubElement(trade_tax, 'ram:TypeCode').text = 'VAT'
            ET.SubElement(trade_tax, 'ram:CategoryCode').text = 'S'  # Standard rate
            ET.SubElement(trade_tax, 'ram:RateApplicablePercent').text = f'{float(line.vat_rate):.2f}'
            
            monetary = ET.SubElement(settlement, 'ram:SpecifiedTradeSettlementLineMonetarySummation')
            ET.SubElement(monetary, 'ram:LineTotalAmount').text = f'{float(line.amount_ht):.2f}'
        
        # Trade Agreement (Seller & Buyer)
        agreement_header = ET.SubElement(transaction, 'ram:ApplicableHeaderTradeAgreement')
        
        # Seller
        seller = ET.SubElement(agreement_header, 'ram:SellerTradeParty')
        ET.SubElement(seller, 'ram:Name').text = company.name
        if company.vat_number:
            seller_tax = ET.SubElement(seller, 'ram:SpecifiedTaxRegistration')
            tax_id = ET.SubElement(seller_tax, 'ram:ID', schemeID='VA')
            tax_id.text = company.vat_number
        
        # Buyer
        buyer = ET.SubElement(agreement_header, 'ram:BuyerTradeParty')
        ET.SubElement(buyer, 'ram:Name').text = customer.name if customer else 'N/A'
        
        # Trade Delivery
        delivery_header = ET.SubElement(transaction, 'ram:ApplicableHeaderTradeDelivery')
        occurrence = ET.SubElement(delivery_header, 'ram:ActualDeliverySupplyChainEvent')
        occurrence_date = ET.SubElement(occurrence, 'ram:OccurrenceDateTime')
        ET.SubElement(occurrence_date, 'udt:DateTimeString', format='102').text = date_str
        
        # Trade Settlement (Totals & Payment)
        settlement_header = ET.SubElement(transaction, 'ram:ApplicableHeaderTradeSettlement')
        ET.SubElement(settlement_header, 'ram:InvoiceCurrencyCode').text = invoice.currency or 'EUR'
        
        # Tax Total
        tax_total = ET.SubElement(settlement_header, 'ram:ApplicableTradeTax')
        ET.SubElement(tax_total, 'ram:CalculatedAmount').text = f'{float(invoice.total_tva):.2f}'
        ET.SubElement(tax_total, 'ram:TypeCode').text = 'VAT'
        ET.SubElement(tax_total, 'ram:CategoryCode').text = 'S'
        ET.SubElement(tax_total, 'ram:BasisAmount').text = f'{float(invoice.total_ht):.2f}'
        
        # Monetary Summation
        monetary_sum = ET.SubElement(settlement_header, 'ram:SpecifiedTradeSettlementHeaderMonetarySummation')
        ET.SubElement(monetary_sum, 'ram:LineTotalAmount').text = f'{float(invoice.total_ht):.2f}'
        ET.SubElement(monetary_sum, 'ram:TaxBasisTotalAmount').text = f'{float(invoice.total_ht):.2f}'
        ET.SubElement(monetary_sum, 'ram:TaxTotalAmount', currencyID='EUR').text = f'{float(invoice.total_tva):.2f}'
        ET.SubElement(monetary_sum, 'ram:GrandTotalAmount').text = f'{float(invoice.total_ttc):.2f}'
        ET.SubElement(monetary_sum, 'ram:DuePayableAmount').text = f'{float(invoice.total_ttc):.2f}'
        
        # Payment Terms
        payment_terms = ET.SubElement(settlement_header, 'ram:SpecifiedTradePaymentTerms')
        due_date_str = invoice.date_due.strftime('%Y%m%d')
        due_date_elem = ET.SubElement(payment_terms, 'ram:DueDateDateTime')
        ET.SubElement(due_date_elem, 'udt:DateTimeString', format='102').text = due_date_str
        
        # Pretty print XML
        xml_str = ET.tostring(root, encoding='unicode')
        dom = minidom.parseString(xml_str)
        return dom.toprettyxml(indent='  ')
