from __future__ import annotations
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from ..models.sla import Comparator, Severity, SLAStatusState


class SLABase(BaseModel):
    name: str
    description: Optional[str] = None
    service: str
    metric_type: str
    comparator: Comparator
    threshold: float
    window_minutes: int = 5
    grace_period_seconds: int = 0
    severity: Severity = Severity.medium
    owner_team: Optional[str] = None
    notification_rules: Dict[str, Any] = Field(default_factory=dict)
    calendar_id: Optional[int] = None
    suppression_seconds: int = 300


class SLACreate(SLABase):
    pass


class SLAUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    service: Optional[str] = None
    metric_type: Optional[str] = None
    comparator: Optional[Comparator] = None
    threshold: Optional[float] = None
    window_minutes: Optional[int] = None
    grace_period_seconds: Optional[int] = None
    severity: Optional[Severity] = None
    owner_team: Optional[str] = None
    notification_rules: Optional[Dict[str, Any]] = None
    calendar_id: Optional[int] = None
    suppression_seconds: Optional[int] = None


class SLARead(SLABase):
    id: int

    class Config:
        from_attributes = True


class SLAStatusRead(BaseModel):
    sla_id: int
    state: SLAStatusState
    last_value: Optional[float] = None
    suppression_until_ts: Optional[int] = None

    class Config:
        from_attributes = True
