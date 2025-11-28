import uuid
from sqlalchemy import Column, String, Boolean, ForeignKey, Text, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.database import Base

class Customer(Base):
    __tablename__ = "customers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    name = Column(Text, nullable=False)
    email = Column(String(255))
    siret = Column(String(14))
    vat_number = Column(String(20))
    address = Column(JSONB)
    is_individual = Column(Boolean, default=False)
    payment_terms = Column(Integer, default=30)

    company = relationship("Company", back_populates="customers")
    invoices = relationship("Invoice", back_populates="customer")

class Supplier(Base):
    __tablename__ = "suppliers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    name = Column(Text, nullable=False)
    siret = Column(String(14))
    iban = Column(String(34))
    default_category = Column(String(50))

    company = relationship("Company", back_populates="suppliers")
    invoices = relationship("Invoice", back_populates="supplier")
