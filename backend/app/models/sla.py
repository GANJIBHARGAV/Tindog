from __future__ import annotations
from enum import Enum
from sqlalchemy import Column, Integer, String, Float, ForeignKey, JSON, Enum as SAEnum
from sqlalchemy.orm import relationship
from .common import TimestampMixin, SoftDeleteMixin
from ..db import Base


class Comparator(str, Enum):
    gt = ">"
    gte = ">="
    lt = "<"
    lte = "<="


class Severity(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class SLA(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "slas"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(String(1000), nullable=True)

    service = Column(String(255), nullable=False)
    metric_type = Column(String(128), nullable=False)
    comparator = Column(SAEnum(Comparator), nullable=False)
    threshold = Column(Float, nullable=False)
    window_minutes = Column(Integer, nullable=False, default=5)
    grace_period_seconds = Column(Integer, nullable=False, default=0)

    severity = Column(SAEnum(Severity), nullable=False, default=Severity.medium)
    owner_team = Column(String(255), nullable=True)

    notification_rules = Column(JSON, nullable=False, default=dict)

    calendar_id = Column(Integer, ForeignKey("calendars.id"), nullable=True)
    calendar = relationship("Calendar")

    suppression_seconds = Column(Integer, nullable=False, default=300)


class SLAStatusState(str, Enum):
    normal = "normal"
    at_risk = "at_risk"
    breached = "breached"
    recovered = "recovered"


class SLAStatus(Base, TimestampMixin):
    __tablename__ = "sla_statuses"

    id = Column(Integer, primary_key=True)
    sla_id = Column(Integer, ForeignKey("slas.id"), nullable=False, index=True)
    sla = relationship("SLA")

    state = Column(SAEnum(SLAStatusState), nullable=False, default=SLAStatusState.normal)
    last_value = Column(Float, nullable=True)
    suppression_until_ts = Column(Integer, nullable=True)
