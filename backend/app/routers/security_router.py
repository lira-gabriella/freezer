"""Security router: scan folders and fetch scan history."""
from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.app.schemas.security_schema import ScanRequest, ScanResponse
from backend.app.services import security_service

router = APIRouter(prefix="/security", tags=["security"])


@router.post("/scan", response_model=ScanResponse)
def scan(req: ScanRequest, db: Session = Depends(get_db)):
    return security_service.scan_path(req.path, db)


@router.get("/history")
def history(limit: int = Query(50, ge=1, le=200), db: Session = Depends(get_db)):
    return security_service.scan_history(db, limit)
