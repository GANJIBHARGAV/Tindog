from __future__ import annotations
from datetime import datetime, timezone
from enum import Enum
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum as SAEnum, JSON
from sqlalchemy.orm import relationship
from ..db import Base
from .common import TimestampMixin


class AlertState(str, Enum):
    at_risk = "at_risk"
    breached = "breached"
    recovered = "recovered"


class Alert(Base, TimestampMixin):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True)
    incident_id = Column(Integer, ForeignKey("incidents.id"), nullable=True, index=True)
    incident = relationship("Incident")

    sla_id = Column(Integer, ForeignKey("slas.id"), nullable=False)
    sla = relationship("SLA")

    state = Column(SAEnum(AlertState), nullable=False)
    message = Column(String(1000), nullable=False)
    severity = Column(String(32), nullable=False)
    routing = Column(JSON, nullable=True)
    sent_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
