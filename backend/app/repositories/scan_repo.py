"""
Scan Repository
================
Pure DB CRUD operations for ScanLog.
"""
from __future__ import annotations

from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models.scan_log import ScanLog


class ScanRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, log: ScanLog) -> ScanLog:
        """Insert a new scan log entry."""
        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)
        return log

    def list_recent(self, limit: int = 50) -> List[ScanLog]:
        """Return the most recent scan logs, newest first."""
        stmt = select(ScanLog).order_by(ScanLog.created_at.desc()).limit(limit)
        return list(self.db.execute(stmt).scalars().all())

    def get_by_id(self, log_id: int) -> Optional[ScanLog]:
        return self.db.get(ScanLog, log_id)