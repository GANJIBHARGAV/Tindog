from __future__ import annotations
from fastapi import APIRouter

router = APIRouter(tags=["system"]) 


@router.get("/api/health")
def health():
    return {"status": "ok"}


@router.get("/api/version")
def version():
    return {"version": "0.1.0"}
