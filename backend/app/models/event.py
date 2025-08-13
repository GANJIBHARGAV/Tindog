from __future__ import annotations
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, DateTime, Index, UniqueConstraint
from ..db import Base
from .common import TimestampMixin


class Event(Base, TimestampMixin):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True)
    service = Column(String(255), nullable=False, index=True)
    metric_type = Column(String(128), nullable=False, index=True)
    value = Column(Float, nullable=False)
    event_ts = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), index=True)
    idempotency_key = Column(String(255), nullable=True)

    __table_args__ = (
        Index("idx_events_service_metric_ts", "service", "metric_type", "event_ts"),
        UniqueConstraint("idempotency_key", name="uq_events_idempotency_key"),
    )
