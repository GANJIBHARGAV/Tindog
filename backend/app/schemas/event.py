from __future__ import annotations
from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime


class EventIngest(BaseModel):
    service: str
    metric_type: str
    value: float
    event_ts: Optional[datetime] = None
    idempotency_key: Optional[str] = None


class EventIngestBulk(BaseModel):
    events: List[EventIngest]
