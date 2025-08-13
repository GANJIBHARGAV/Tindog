from __future__ import annotations
import smtplib
from email.mime.text import MIMEText
import httpx
from typing import List
from sqlalchemy.orm import Session
from ..config import settings
from ..models.delivery import DeliveryLog


def send_email(db: Session, to_emails: List[str], subject: str, body: str) -> None:
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = settings.smtp_from_email
    msg["To"] = ", ".join(to_emails)
    try:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=10) as server:
            if settings.smtp_user and settings.smtp_password:
                server.starttls()
                server.login(settings.smtp_user, settings.smtp_password)
            server.sendmail(settings.smtp_from_email, to_emails, msg.as_string())
        status = "success"
        error = None
    except Exception as exc:  # pragma: no cover
        status = "failed"
        error = str(exc)
    log = DeliveryLog(provider="email", status=status, error_message=error, attempts=1, meta={"to": to_emails, "subject": subject})
    db.add(log)


def send_slack(db: Session, channels: List[str], message: str) -> None:
    if not settings.slack_webhook_url:
        log = DeliveryLog(provider="slack", status="failed", error_message="No webhook configured", attempts=1, meta={"channels": channels})
        db.add(log)
        return
    try:
        for _ in channels:
            payload = {"text": message}
            httpx.post(settings.slack_webhook_url, json=payload, timeout=10)
        status = "success"
        error = None
    except Exception as exc:  # pragma: no cover
        status = "failed"
        error = str(exc)
    log = DeliveryLog(provider="slack", status=status, error_message=error, attempts=1, meta={"channels": channels})
    db.add(log)
