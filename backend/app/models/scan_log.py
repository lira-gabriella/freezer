"""
Scan Log Model
==============
Records every security scan run by CryoGuard.
Stores the target folder, the computed safety score, and a JSON list
of findings so the UI can render a detailed report later.
"""
from __future__ import annotations

from datetime import datetime
from typing import List

from sqlalchemy import Column, DateTime, Integer, String, Text

from backend.database import Base


class ScanLog(Base):
    __tablename__ = "scan_logs"

    id = Column(Integer, primary_key=True, index=True)
    # Absolute path that was scanned.
    target_path = Column(Text, nullable=False, index=True)
    # 0-100 safety score computed by the security service.
    safety_score = Column(Integer, nullable=False)
    # Total number of files examined during the scan.
    files_scanned = Column(Integer, nullable=False, default=0)
    # Number of suspicious files detected.
    suspicious_count = Column(Integer, nullable=False, default=0)
    # JSON-encoded list of finding dicts (path, reason, severity, sha256).
    findings_json = Column(Text, nullable=False, default="[]")
    # When the scan completed.
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return (
            f"<ScanLog id={self.id} target={self.target_path!r} "
            f"score={self.safety_score}>"
        )