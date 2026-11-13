"""
Vault Repository
=================
Pure DB CRUD operations for VaultItem.
No business logic here — just queries.
"""
from __future__ import annotations

from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models.vault_item import VaultItem


class VaultRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, item: VaultItem) -> VaultItem:
        """Insert a new vault item and refresh it to get server defaults."""
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def get_by_id(self, item_id: int) -> Optional[VaultItem]:
        """Fetch a vault item by primary key, or None if missing."""
        return self.db.get(VaultItem, item_id)

    def get_by_original_path(self, original_path: str) -> Optional[VaultItem]:
        """Find an existing (non-restored) item by its original folder path."""
        stmt = select(VaultItem).where(
            VaultItem.original_path == original_path,
            VaultItem.restored_at.is_(None),
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def list_all(self, archived_only: bool = True) -> List[VaultItem]:
        """List all vault items, optionally only those still archived."""
        stmt = select(VaultItem)
        if archived_only:
            stmt = stmt.where(VaultItem.restored_at.is_(None))
        stmt = stmt.order_by(VaultItem.created_at.desc())
        return list(self.db.execute(stmt).scalars().all())

    def mark_restored(self, item: VaultItem) -> VaultItem:
        """Mark an item as restored (thawed) and persist the timestamp."""
        from datetime import datetime
        item.restored_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(item)
        return item

    def delete(self, item: VaultItem) -> None:
        """Permanently delete a vault item row (used after successful thaw)."""
        self.db.delete(item)
        self.db.commit()