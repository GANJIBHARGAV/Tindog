from __future__ import annotations
from typing import Optional
from pydantic import BaseModel
from datetime import datetime
from ..models.alert import AlertState


class AlertRead(BaseModel):
    id: int
    incident_id: Optional[int]
    sla_id: int
    state: AlertState
    message: str
    severity: str
    sent_at: datetime

    class Config:
        from_attributes = True
