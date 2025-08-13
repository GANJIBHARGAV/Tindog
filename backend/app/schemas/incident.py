from __future__ import annotations
from typing import Optional
from pydantic import BaseModel
from datetime import datetime
from ..models.incident import IncidentStatus


class IncidentRead(BaseModel):
    id: int
    sla_id: int
    status: IncidentStatus
    severity: str
    started_at: datetime
    acknowledged_at: Optional[datetime]
    resolved_at: Optional[datetime]

    class Config:
        from_attributes = True
