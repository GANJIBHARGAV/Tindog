from __future__ import annotations
from sqlalchemy import Column, Integer, String, JSON
from ..db import Base
from .common import TimestampMixin


class AuditLog(Base, TimestampMixin):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True)
    table_name = Column(String(128), nullable=False)
    row_id = Column(Integer, nullable=False)
    action = Column(String(32), nullable=False)  # create, update, delete
    actor_email = Column(String(255), nullable=True)
    changes = Column(JSON, nullable=True)
