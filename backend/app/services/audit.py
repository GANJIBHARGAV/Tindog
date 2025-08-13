from __future__ import annotations
from sqlalchemy.orm import Session
from ..models.audit import AuditLog
from typing import Any, Dict


def record_audit(db: Session, table_name: str, row_id: int, action: str, changes: Dict[str, Any] | None = None, actor_email: str | None = None) -> None:
    entry = AuditLog(table_name=table_name, row_id=row_id, action=action, changes=changes or {}, actor_email=actor_email)
    db.add(entry)
    db.flush()
