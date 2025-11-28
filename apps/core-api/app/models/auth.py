import uuid
from sqlalchemy import Column, String, Boolean, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.base import TimestampMixin

class Company(Base, TimestampMixin):
    __tablename__ = "companies"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(Text, nullable=False)
    siret = Column(String(14), unique=True, index=True)
    vat_number = Column(String(20))
    address = Column(JSONB)
    settings = Column(JSONB, default={})
    is_active = Column(Boolean, default=True)

    users = relationship("User", back_populates="company")
    customers = relationship("Customer", back_populates="company")
    suppliers = relationship("Supplier", back_populates="company")
    invoices = relationship("Invoice", back_populates="company")
    transactions = relationship("Transaction", back_populates="company")

class User(Base, TimestampMixin):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(Text, nullable=False)
    full_name = Column(Text, nullable=False)
    role = Column(String(50), nullable=False) # ADMIN, ACCOUNTANT, VIEWER

    company = relationship("Company", back_populates="users")
