from __future__ import annotations
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from asgi_correlation_id import CorrelationIdMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
from .config import settings
from .utils.logging import setup_logging
from .api.routers import auth as auth_router
from .api.routers import slas as slas_router
from .api.routers import events as events_router
from .api.routers import incidents as incidents_router
from .api.routers import alerts as alerts_router
from .api.routers import health as health_router


setup_logging()

app = FastAPI(title="SLA Breach Warning System", version="0.1.0")

app.add_middleware(CORSMiddleware, allow_origins=[origin.strip() for origin in settings.cors_origins.split(",")], allow_credentials=True, allow_methods=["*"], allow_headers=["*"],)
app.add_middleware(CorrelationIdMiddleware)

app.include_router(health_router.router)
app.include_router(auth_router.router)
app.include_router(slas_router.router)
app.include_router(events_router.router)
app.include_router(incidents_router.router)
app.include_router(alerts_router.router)

Instrumentator().instrument(app).expose(app, include_in_schema=False, endpoint="/api/metrics")


if __name__ == "__main__":
    uvicorn.run("app.main:app", host=settings.host, port=settings.port, reload=False)
