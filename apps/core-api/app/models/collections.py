import uuid
from sqlalchemy import Column, String, ForeignKey, Text, Integer, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.base import TimestampMixin

class CollectionCase(Base):
    __tablename__ = "collection_cases"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    invoice_id = Column(UUID(as_uuid=True), ForeignKey("invoices.id"), unique=True, nullable=False)
    status = Column(String(30), nullable=False) # OPEN, IN_PROGRESS, PROMISE_TO_PAY, DISPUTE, CLOSED_PAID, CLOSED_LOST
    strategy = Column(String(30), default='STANDARD')
    next_action_at = Column(DateTime(timezone=True))
    level = Column(Integer, default=0)
    ai_context = Column(JSONB)

    invoice = relationship("Invoice", back_populates="collection_case")
    events = relationship("CollectionEvent", back_populates="case")

class CollectionEvent(Base, TimestampMixin):
    __tablename__ = "collection_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    case_id = Column(UUID(as_uuid=True), ForeignKey("collection_cases.id"), nullable=False)
    type = Column(String(30), nullable=False) # EMAIL_SENT, EMAIL_RECEIVED, NOTE, STATUS_CHANGE
    channel = Column(String(20)) # EMAIL, PHONE, SYSTEM
    content = Column(Text)
    metadata_ = Column("metadata", JSONB) # 'metadata' is reserved in SQLAlchemy sometimes, using metadata_ mapped to metadata column

    case = relationship("CollectionCase", back_populates="events")
