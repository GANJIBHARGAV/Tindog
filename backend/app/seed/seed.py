from __future__ import annotations
from sqlalchemy.orm import Session
from ..db import SessionLocal
from ..models.user import User, UserRole
from ..auth.security import get_password_hash
from ..models.calendar import Calendar
from ..models.sla import SLA, Comparator, Severity, SLAStatus
from ..models.event import Event
from datetime import datetime, timedelta, timezone


def run_seed() -> None:
    db: Session = SessionLocal()
    try:
        # Admin user
        if not db.query(User).filter(User.email == "admin@demo.dev").first():
            admin = User(email="admin@demo.dev", hashed_password=get_password_hash("Admin!234"), role=UserRole.admin.value)
            db.add(admin)

        # Calendar
        cal = db.query(Calendar).filter(Calendar.name == "Default Business Hours").first()
        if not cal:
            cal = Calendar(name="Default Business Hours", timezone="UTC", business_hours=[{"day": d, "start": "09:00", "end": "17:00"} for d in ["mon","tue","wed","thu","fri"]], holidays=[])
            db.add(cal)
            db.flush()

        # SLA example
        sla = db.query(SLA).filter(SLA.name == "API latency < 200ms").first()
        if not sla:
            sla = SLA(
                name="API latency < 200ms",
                description="Average response time must be below 200ms",
                service="api",
                metric_type="response_time_ms",
                comparator=Comparator.lte,
                threshold=200.0,
                window_minutes=1,
                severity=Severity.high,
                notification_rules={"email": ["alerts@example.local"], "slack": ["#alerts"]},
                calendar_id=cal.id,
            )
            db.add(sla)
            db.flush()
            db.add(SLAStatus(sla_id=sla.id))

        # Seed events that will breach soon
        now = datetime.now(timezone.utc)
        for i in range(0, 10):
            db.add(Event(service="api", metric_type="response_time_ms", value=150.0, event_ts=now - timedelta(seconds=90 - i*5)))
        for i in range(0, 5):
            db.add(Event(service="api", metric_type="response_time_ms", value=350.0, event_ts=now - timedelta(seconds=30 - i*5)))

        db.commit()
        print("Seed completed")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    run_seed()
