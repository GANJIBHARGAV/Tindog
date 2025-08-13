from __future__ import annotations
from datetime import datetime, timezone
from enum import Enum
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum as SAEnum
from sqlalchemy.orm import relationship
from ..db import Base
from .common import TimestampMixin


class IncidentStatus(str, Enum):
    open = "open"
    acknowledged = "acknowledged"
    resolved = "resolved"


class Incident(Base, TimestampMixin):
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True)
    sla_id = Column(Integer, ForeignKey("slas.id"), nullable=False, index=True)
    sla = relationship("SLA")

    status = Column(SAEnum(IncidentStatus), nullable=False, default=IncidentStatus.open)
    severity = Column(String(32), nullable=False)

    started_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    acknowledged_at = Column(DateTime(timezone=True), nullable=True)
    acknowledged_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    owner = Column(String(255), nullable=True)
