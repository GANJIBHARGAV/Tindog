from __future__ import annotations
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from ...db import get_db
from ...schemas.sla import SLACreate, SLAUpdate, SLARead, SLAStatusRead
from ...models.sla import SLA, SLAStatus
from ...auth.security import require_role
from ...models.user import UserRole
from ...services.audit import record_audit

router = APIRouter(prefix="/api/slas", tags=["slas"])


@router.get("/", response_model=List[SLARead])
def list_slas(
    db: Session = Depends(get_db),
    service: Optional[str] = Query(default=None),
):
    q = db.query(SLA).filter(SLA.is_deleted == False)  # noqa: E712
    if service:
        q = q.filter(SLA.service == service)
    return q.order_by(SLA.created_at.desc()).all()


@router.post("/", response_model=SLARead, dependencies=[Depends(require_role(UserRole.admin, UserRole.manager))])
def create_sla(payload: SLACreate, db: Session = Depends(get_db)):
    sla = SLA(**payload.model_dump())
    db.add(sla)
    db.commit()
    db.refresh(sla)
    record_audit(db, table_name="slas", row_id=sla.id, action="create", changes=payload.model_dump())
    # Initialize status
    status = SLAStatus(sla_id=sla.id)
    db.add(status)
    db.commit()
    return sla


@router.get("/{sla_id}", response_model=SLARead)
def get_sla(sla_id: int, db: Session = Depends(get_db)):
    sla = db.query(SLA).get(sla_id)
    if not sla or sla.is_deleted:
        raise HTTPException(status_code=404, detail="SLA not found")
    return sla


@router.put("/{sla_id}", response_model=SLARead, dependencies=[Depends(require_role(UserRole.admin, UserRole.manager))])
def update_sla(sla_id: int, payload: SLAUpdate, db: Session = Depends(get_db)):
    sla = db.query(SLA).get(sla_id)
    if not sla or sla.is_deleted:
        raise HTTPException(status_code=404, detail="SLA not found")
    data = payload.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(sla, k, v)
    db.add(sla)
    db.commit()
    db.refresh(sla)
    record_audit(db, table_name="slas", row_id=sla.id, action="update", changes=data)
    return sla


@router.delete("/{sla_id}", dependencies=[Depends(require_role(UserRole.admin, UserRole.manager))])
def delete_sla(sla_id: int, db: Session = Depends(get_db)):
    sla = db.query(SLA).get(sla_id)
    if not sla or sla.is_deleted:
        raise HTTPException(status_code=404, detail="SLA not found")
    sla.is_deleted = True
    db.add(sla)
    db.commit()
    record_audit(db, table_name="slas", row_id=sla.id, action="delete", changes={"is_deleted": True})
    return {"ok": True}


@router.get("/{sla_id}/status", response_model=SLAStatusRead)
def get_sla_status(sla_id: int, db: Session = Depends(get_db)):
    status = db.query(SLAStatus).filter(SLAStatus.sla_id == sla_id).first()
    if not status:
        raise HTTPException(status_code=404, detail="SLA status not found")
    return status
