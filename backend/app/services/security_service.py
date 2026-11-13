"""Security service: scan folders for suspicious files and compute safety score."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import List

from sqlalchemy.orm import Session

from backend.app.models.scan_log import ScanLog
from backend.app.repositories.scan_repo import ScanRepository
from backend.app.schemas.security_schema import (
    Finding, ScanResponse, ScanHistoryItem, SUSPICIOUS_EXTENSIONS,
)
from backend.app.services.sanitizer import sanitize_path


def _sha256(path: Path) -> str | None:
    try:
        h = hashlib.sha256()
        with path.open("rb") as f:
            for chunk in iter(lambda: f.read(1024 * 1024), b""):
                h.update(chunk)
        return h.hexdigest()
    except OSError:
        return None


def _severity(ext: str, size: int) -> str:
    if ext in {".exe", ".dll", ".scr", ".msi", ".ps1", ".vbs"}:
        return "high"
    if ext in {".bat", ".cmd", ".js", ".jar", ".sh"}:
        return "medium"
    return "low" if size < 1024 * 1024 else "medium"


def scan_path(path: str, db: Session) -> ScanResponse:
    target = Path(sanitize_path(path))
    if not target.exists() or not target.is_dir():
        return ScanResponse(
            success=False, target_path=str(target), safety_score=0,
            files_scanned=0, suspicious_count=0, findings=[], message="Folder not found",
        )
    findings: List[Finding] = []
    files_scanned = 0
    for root, _, files in os.walk(target):
        for name in files:
            files_scanned += 1
            p = Path(root) / name
            ext = p.suffix.lower()
            if ext in SUSPICIOUS_EXTENSIONS:
                try:
                    size = p.stat().st_size
                except OSError:
                    size = 0
                findings.append(
                    Finding(
                        path=str(p), reason=f"Suspicious extension: {ext}",
                        severity=_severity(ext, size), sha256=_sha256(p), file_size=size,
                    )
                )
    suspicious = len(findings)
    penalty = sum({"low": 3, "medium": 7, "high": 15}.get(f.severity, 5) for f in findings)
    score = max(0, 100 - penalty)
    log = ScanLog(
        target_path=str(target), safety_score=score, files_scanned=files_scanned,
        suspicious_count=suspicious, findings_json=json.dumps([f.model_dump() for f in findings]),
    )
    ScanRepository(db).create(log)
    msg = "Scan complete" if suspicious == 0 else f"Found {suspicious} suspicious file(s)"
    return ScanResponse(
        success=True, target_path=str(target), safety_score=score,
        files_scanned=files_scanned, suspicious_count=suspicious, findings=findings, message=msg,
    )


def scan_history(db: Session, limit: int = 50):
    logs = ScanRepository(db).list_recent(limit)
    return [
        ScanHistoryItem(
            id=l.id, target_path=l.target_path, safety_score=l.safety_score,
            files_scanned=l.files_scanned, suspicious_count=l.suspicious_count,
            created_at=l.created_at.isoformat() if l.created_at else None,
        )
        for l in logs
    ]