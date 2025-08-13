from __future__ import annotations
from celery import shared_task
from sqlalchemy.orm import Session
from ..db import SessionLocal
from ..models.sla import SLA
from ..services.evaluator import evaluate_sla
from ..services.notifications import send_email, send_slack


@shared_task(name="app.tasks.evaluation.evaluate_all_slas")
def evaluate_all_slas() -> None:
    db: Session = SessionLocal()
    try:
        slas = db.query(SLA).filter(SLA.is_deleted == False).all()  # noqa: E712
        for sla in slas:
            _, alert = evaluate_sla(db, sla)
            if alert:
                db.flush()
                rules = sla.notification_rules or {}
                emails = rules.get("email", [])
                channels = rules.get("slack", [])
                if emails:
                    send_email(db, emails, subject=f"SLA {alert.state.value}: {sla.name}", body=alert.message)
                if channels:
                    send_slack(db, channels, message=alert.message)
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
