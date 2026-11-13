"""Vault service: archive/restore folders with zstandard and track in DB."""
from __future__ import annotations

import hashlib
import os
import shutil
import tarfile
import tempfile
from pathlib import Path

import zstandard as zstd
from sqlalchemy.orm import Session

from backend.app.models.vault_item import VaultItem
from backend.app.repositories.vault_repo import VaultRepository
from backend.app.schemas.vault_schema import ArchiveResponse, VaultItemResponse
from backend.app.services.sanitizer import sanitize_path

VAULT_DIR = Path.home() / ".cryoguard_vault"
VAULT_DIR.mkdir(parents=True, exist_ok=True)


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _dir_size(path: Path) -> int:
    total = 0
    for p in path.rglob("*"):
        if p.is_file():
            try:
                total += p.stat().st_size
            except OSError:
                pass
    return total


def _to_response(item: VaultItem) -> VaultItemResponse:
    return VaultItemResponse(
        id=item.id, name=item.name, original_path=item.original_path,
        archive_path=item.archive_path, original_size_bytes=item.original_size_bytes,
        archive_size_bytes=item.archive_size_bytes, sha256=item.sha256,
        is_archived=item.is_archived, saved_bytes=item.saved_bytes,
        created_at=item.created_at.isoformat() if item.created_at else None,
        restored_at=item.restored_at.isoformat() if item.restored_at else None,
    )


def archive_folder(path: str, db: Session) -> ArchiveResponse:
    src = Path(sanitize_path(path))
    if not src.exists() or not src.is_dir():
        return ArchiveResponse(success=False, message="Folder not found")
    repo = VaultRepository(db)
    existing = repo.get_by_original_path(str(src))
    if existing:
        return ArchiveResponse(success=False, message="Folder already archived")
    archive_path = VAULT_DIR / f"{src.name}-{abs(hash(str(src)))}.tar.zst"
    original_size = _dir_size(src)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".tar") as tmp:
        tmp_tar = Path(tmp.name)
    try:
        with tarfile.open(tmp_tar, "w") as tar:
            tar.add(src, arcname=src.name)
        cctx = zstd.ZstdCompressor(level=3)
        with tmp_tar.open("rb") as fin, archive_path.open("wb") as fout:
            cctx.copy_stream(fin, fout)
        sha = _sha256(archive_path)
        item = VaultItem(
            original_path=str(src), archive_path=str(archive_path), name=src.name,
            original_size_bytes=original_size, archive_size_bytes=archive_path.stat().st_size,
            sha256=sha,
        )
        repo.create(item)
        shutil.rmtree(src)
        return ArchiveResponse(success=True, message="Archived", item=_to_response(item))
    except Exception as exc:
        if archive_path.exists():
            archive_path.unlink()
        raise exc
    finally:
        if tmp_tar.exists():
            tmp_tar.unlink()


def restore_folder(item_id: int, db: Session) -> ArchiveResponse:
    repo = VaultRepository(db)
    item = repo.get_by_id(item_id)
    if not item or not item.is_archived:
        return ArchiveResponse(success=False, message="Vault item not found")
    archive_path = Path(item.archive_path)
    if not archive_path.exists() or _sha256(archive_path) != item.sha256:
        return ArchiveResponse(success=False, message="Archive missing or corrupted")
    dest = Path(item.original_path)
    dest.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".tar") as tmp:
        tmp_tar = Path(tmp.name)
    try:
        dctx = zstd.ZstdDecompressor()
        with archive_path.open("rb") as fin, tmp_tar.open("wb") as fout:
            dctx.copy_stream(fin, fout)
        with tarfile.open(tmp_tar, "r") as tar:
            tar.extractall(dest.parent)
        repo.mark_restored(item)
        archive_path.unlink(missing_ok=True)
        return ArchiveResponse(success=True, message="Restored", item=_to_response(item))
    finally:
        if tmp_tar.exists():
            tmp_tar.unlink()


def list_vault(db: Session):
    return [_to_response(i) for i in VaultRepository(db).list_all(archived_only=True)]