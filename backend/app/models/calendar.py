from __future__ import annotations
from sqlalchemy import Column, Integer, String, JSON
from ..db import Base
from .common import TimestampMixin


class Calendar(Base, TimestampMixin):
    __tablename__ = "calendars"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    timezone = Column(String(64), nullable=False, default="UTC")
    business_hours = Column(JSON, nullable=False, default=list)
    holidays = Column(JSON, nullable=False, default=list)
