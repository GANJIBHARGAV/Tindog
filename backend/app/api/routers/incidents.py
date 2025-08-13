from __future__ import annotations
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ...db import get_db
from ...schemas.incident import IncidentRead
from ...models.incident import Incident, IncidentStatus
from ...auth.security import require_role
from ...models.user import UserRole

router = APIRouter(prefix="/api/incidents", tags=["incidents"])


@router.get("/", response_model=List[IncidentRead])
def list_incidents(db: Session = Depends(get_db)):
    q = db.query(Incident).order_by(Incident.created_at.desc())
    return q.all()


@router.post("/{incident_id}/ack", dependencies=[Depends(require_role(UserRole.admin, UserRole.manager))])
def acknowledge_incident(incident_id: int, db: Session = Depends(get_db)):
    incident = db.query(Incident).get(incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Not found")
    incident.status = IncidentStatus.acknowledged
    db.add(incident)
    db.commit()
    return {"ok": True}


@router.post("/{incident_id}/resolve", dependencies=[Depends(require_role(UserRole.admin, UserRole.manager))])
def resolve_incident(incident_id: int, db: Session = Depends(get_db)):
    incident = db.query(Incident).get(incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Not found")
    incident.status = IncidentStatus.resolved
    db.add(incident)
    db.commit()
    return {"ok": True}
