"""Process control router: list, freeze, thaw, and idle detection."""
from __future__ import annotations

from fastapi import APIRouter

from backend.app.schemas.process_schema import FreezeRequest, FreezeResponse, AutoIdleConfig
from backend.app.services import freezer_service

router = APIRouter(prefix="/processes", tags=["processes"])


@router.get("")
def list_processes():
    return freezer_service.list_processes()


@router.post("/freeze", response_model=FreezeResponse)
def freeze(req: FreezeRequest):
    return freezer_service.freeze_pids(req.pids)


@router.post("/thaw", response_model=FreezeResponse)
def thaw(req: FreezeRequest):
    return freezer_service.thaw_pids(req.pids)


@router.post("/idle")
def find_idle(cfg: AutoIdleConfig):
    pids = freezer_service.find_idle_processes(
        cfg.idle_timeout_minutes, cfg.protected_processes
    )
    return {"idle_pids": pids, "count": len(pids)}
