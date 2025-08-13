from __future__ import annotations
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ...db import get_db
from ...schemas.alert import AlertRead
from ...models.alert import Alert
from ...services.notifications import send_email, send_slack

router = APIRouter(prefix="/api/alerts", tags=["alerts"])


@router.get("/", response_model=List[AlertRead])
def list_alerts(db: Session = Depends(get_db)):
    q = db.query(Alert).order_by(Alert.created_at.desc())
    return q.all()


@router.post("/{alert_id}/resend")
def resend_alert(alert_id: int, db: Session = Depends(get_db)):
    alert = db.query(Alert).get(alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Not found")
    rules = alert.routing or {}
    emails = rules.get("email", [])
    channels = rules.get("slack", [])
    if emails:
        send_email(db, emails, subject=f"RESEND: SLA {alert.state.value}", body=alert.message)
    if channels:
        send_slack(db, channels, message=alert.message)
    db.commit()
    return {"ok": True}
