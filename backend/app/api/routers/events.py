from __future__ import annotations
from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session
from ...db import get_db
from ...schemas.event import EventIngest, EventIngestBulk
from ...models.event import Event
from ...tasks.evaluation import evaluate_all_slas

router = APIRouter(prefix="/api/events", tags=["events"])


@router.post("/ingest")
def ingest_event(payload: EventIngest, db: Session = Depends(get_db), x_idempotency_key: str | None = Header(default=None)):
    key = payload.idempotency_key or x_idempotency_key
    if key:
        existing = db.query(Event).filter(Event.idempotency_key == key).first()
        if existing:
            return {"ok": True, "duplicate": True}
    evt = Event(
        service=payload.service,
        metric_type=payload.metric_type,
        value=payload.value,
        event_ts=payload.event_ts,
        idempotency_key=key,
    )
    db.add(evt)
    db.commit()
    evaluate_all_slas.delay()
    return {"ok": True}


@router.post("/bulk")
def ingest_bulk(payload: EventIngestBulk, db: Session = Depends(get_db)):
    for ev in payload.events:
        if ev.idempotency_key:
            existing = db.query(Event).filter(Event.idempotency_key == ev.idempotency_key).first()
            if existing:
                continue
        evt = Event(
            service=ev.service,
            metric_type=ev.metric_type,
            value=ev.value,
            event_ts=ev.event_ts,
            idempotency_key=ev.idempotency_key,
        )
        db.add(evt)
    db.commit()
    evaluate_all_slas.delay()
    return {"ok": True}
