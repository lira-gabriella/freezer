"""Vault router: archive, restore, and list vault items."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.app.schemas.vault_schema import ArchiveRequest, RestoreRequest, ArchiveResponse
from backend.app.services import vault_service

router = APIRouter(prefix="/vault", tags=["vault"])


@router.get("")
def list_vault(db: Session = Depends(get_db)):
    return vault_service.list_vault(db)


@router.post("/archive", response_model=ArchiveResponse)
def archive(req: ArchiveRequest, db: Session = Depends(get_db)):
    return vault_service.archive_folder(req.path, db)


@router.post("/restore", response_model=ArchiveResponse)
def restore(req: RestoreRequest, db: Session = Depends(get_db)):
    return vault_service.restore_folder(req.item_id, db)
