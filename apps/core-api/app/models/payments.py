import uuid
from sqlalchemy import Column, String, ForeignKey, Text, Date, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    external_id = Column(String(255), unique=True)
    date = Column(Date, nullable=False)
    amount = Column(Numeric(18, 2), nullable=False)
    label = Column(Text)
    status = Column(String(20))
    category = Column(String(50))

    company = relationship("Company", back_populates="transactions")
    payments = relationship("Payment", back_populates="transaction")

class Payment(Base):
    __tablename__ = "payments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    invoice_id = Column(UUID(as_uuid=True), ForeignKey("invoices.id"), nullable=False)
    transaction_id = Column(UUID(as_uuid=True), ForeignKey("transactions.id"), nullable=True)
    amount = Column(Numeric(18, 2), nullable=False)
    date = Column(Date, nullable=False)
    method = Column(String(20)) # TRANSFER, CARD, CHECK, CASH

    invoice = relationship("Invoice", back_populates="payments")
    transaction = relationship("Transaction", back_populates="payments")
