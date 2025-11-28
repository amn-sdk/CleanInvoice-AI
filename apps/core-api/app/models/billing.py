import uuid
from sqlalchemy import Column, String, ForeignKey, Text, Date, Numeric, CHAR
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.base import TimestampMixin

class Invoice(Base, TimestampMixin):
    __tablename__ = "invoices"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id"), nullable=True)
    supplier_id = Column(UUID(as_uuid=True), ForeignKey("suppliers.id"), nullable=True)
    
    type = Column(String(20), nullable=False) # OUT_INVOICE, IN_INVOICE, CREDIT_NOTE
    status = Column(String(20), nullable=False) # DRAFT, ISSUED, PAID, LATE, CANCELLED
    number = Column(String(50))
    
    date_issued = Column(Date, nullable=False)
    date_due = Column(Date, nullable=False)
    currency = Column(CHAR(3), default='EUR')
    
    total_ht = Column(Numeric(18, 2), nullable=False)
    total_tva = Column(Numeric(18, 2), nullable=False)
    total_ttc = Column(Numeric(18, 2), nullable=False)
    
    file_path = Column(Text)
    facturx_xml_path = Column(Text)
    ai_metadata = Column(JSONB)

    # Compliance / Factur-X fields
    pdp_status = Column(String(50))
    lifecycle_status = Column(String(50))
    transmission_id = Column(String(255))

    company = relationship("Company", back_populates="invoices")
    customer = relationship("Customer", back_populates="invoices")
    supplier = relationship("Supplier", back_populates="invoices")
    lines = relationship("InvoiceLine", back_populates="invoice", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="invoice")
    collection_case = relationship("CollectionCase", uselist=False, back_populates="invoice")

class InvoiceLine(Base):
    __tablename__ = "invoice_lines"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    invoice_id = Column(UUID(as_uuid=True), ForeignKey("invoices.id"), nullable=False)
    description = Column(Text, nullable=False)
    quantity = Column(Numeric(12, 3), default=1)
    unit_price = Column(Numeric(18, 2), nullable=False)
    vat_rate = Column(Numeric(5, 2), nullable=False)
    amount_ht = Column(Numeric(18, 2), nullable=False)

    invoice = relationship("Invoice", back_populates="lines")
