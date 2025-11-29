from sqlalchemy.orm import Session
from app.models.audit import AuditLog
from uuid import UUID
from typing import Optional, Any
import json

def log_audit(
    db: Session,
    company_id: UUID,
    user_id: Optional[UUID],
    entity_type: str,
    entity_id: UUID,
    action: str,
    changes: Optional[dict[str, Any]] = None
):
    """
    Create an audit log entry.
    """
    audit_entry = AuditLog(
        company_id=company_id,
        user_id=user_id,
        entity_type=entity_type,
        entity_id=entity_id,
        action=action,
        changes=changes
    )
    db.add(audit_entry)
    # We don't commit here to allow the caller to commit as part of a transaction
    # But if called independently, caller must commit.
