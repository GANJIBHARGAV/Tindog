from __future__ import annotations
from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..models.sla import SLA, SLAStatus, SLAStatusState, Comparator
from ..models.event import Event
from ..models.incident import Incident, IncidentStatus
from ..models.alert import Alert, AlertState


AT_RISK_MARGIN = 0.9


def _compare(comparator: Comparator, value: float, threshold: float) -> bool:
    if comparator == Comparator.gt:
        return value > threshold
    if comparator == Comparator.gte:
        return value >= threshold
    if comparator == Comparator.lt:
        return value < threshold
    if comparator == Comparator.lte:
        return value <= threshold
    raise ValueError("Unsupported comparator")


def _at_risk(comparator: Comparator, value: float, threshold: float) -> bool:
    if comparator in (Comparator.gt, Comparator.gte):
        return value > threshold * AT_RISK_MARGIN
    else:
        return value < threshold / AT_RISK_MARGIN


def evaluate_sla(db: Session, sla: SLA) -> Tuple[SLAStatus, Optional[Alert]]:
    now = datetime.now(timezone.utc)
    window_start = now - timedelta(minutes=sla.window_minutes)

    agg_value = (
        db.query(func.avg(Event.value))
        .filter(Event.service == sla.service)
        .filter(Event.metric_type == sla.metric_type)
        .filter(Event.event_ts >= window_start)
        .scalar()
    )

    status = db.query(SLAStatus).filter(SLAStatus.sla_id == sla.id).first()
    if not status:
        status = SLAStatus(sla_id=sla.id)
        db.add(status)
        db.flush()

    previous_state = status.state

    new_state = SLAStatusState.normal
    alert_state: Optional[AlertState] = None

    if agg_value is None:
        agg_value = status.last_value or 0.0
    else:
        breached = _compare(sla.comparator, agg_value, sla.threshold)
        if breached:
            new_state = SLAStatusState.breached
            alert_state = AlertState.breached if previous_state != SLAStatusState.breached else None
        elif _at_risk(sla.comparator, agg_value, sla.threshold):
            new_state = SLAStatusState.at_risk
            alert_state = AlertState.at_risk if previous_state == SLAStatusState.normal else None
        else:
            if previous_state in (SLAStatusState.at_risk, SLAStatusState.breached):
                new_state = SLAStatusState.recovered
                alert_state = AlertState.recovered
            else:
                new_state = SLAStatusState.normal

    status.state = new_state
    status.last_value = float(agg_value) if agg_value is not None else None

    alert: Optional[Alert] = None

    if alert_state:
        incident = (
            db.query(Incident)
            .filter(Incident.sla_id == sla.id)
            .filter(Incident.status != IncidentStatus.resolved)
            .order_by(Incident.created_at.desc())
            .first()
        )
        if not incident and alert_state in (AlertState.at_risk, AlertState.breached):
            incident = Incident(sla_id=sla.id, severity=sla.severity.value)
            db.add(incident)
            db.flush()
        if incident and alert_state == AlertState.recovered:
            incident.status = IncidentStatus.resolved
            incident.resolved_at = now

        alert = Alert(
            incident_id=incident.id if incident else None,
            sla_id=sla.id,
            state=alert_state,
            message=f"SLA '{sla.name}' is {alert_state.value} (avg={agg_value:.2f}, threshold={sla.threshold})",
            severity=sla.severity.value,
            routing=sla.notification_rules,
        )
        db.add(alert)

    db.flush()
    return status, alert
