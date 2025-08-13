from __future__ import annotations
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
from ..db import Base
from .common import TimestampMixin
from datetime import datetime, timezone


class DeliveryLog(Base, TimestampMixin):
    __tablename__ = "delivery_logs"

    id = Column(Integer, primary_key=True)
    alert_id = Column(Integer, ForeignKey("alerts.id"), nullable=False, index=True)
    alert = relationship("Alert")

    provider = Column(String(64), nullable=False)  # email, slack, sms
    status = Column(String(32), nullable=False)  # success, failed
    error_message = Column(String(1000), nullable=True)
    attempts = Column(Integer, default=0, nullable=False)
    next_retry_at = Column(DateTime(timezone=True), nullable=True)
    meta = Column(JSON, nullable=True)
