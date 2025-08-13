from __future__ import annotations
from celery import Celery
from ..config import settings

celery = Celery(
    settings.app_name,
    broker=settings.celery_broker,
    backend=settings.celery_backend,
)

celery.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    beat_schedule={
        "evaluate-slas-every-30s": {
            "task": "app.tasks.evaluation.evaluate_all_slas",
            "schedule": 30.0,
        }
    },
)
