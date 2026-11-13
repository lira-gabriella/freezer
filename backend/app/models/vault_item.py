"""
Vault Item Model
================
Represents a folder that has been compressed into the Cryo-Vault.
Tracks the archive path, original path, size, and integrity hash.
"""
from __future__ import annotations

import os
from datetime import datetime
from typing import Optional

from sqlalchemy import Column, DateTime, Integer, String, Text

from backend.database import Base


class VaultItem(Base):
    __tablename__ = "vault_items"

    id = Column(Integer, primary_key=True, index=True)
    # Original absolute path of the folder that was archived.
    original_path = Column(Text, nullable=False, index=True)
    # Where the compressed archive lives (e.g. ~/.cryoguard_vault/xxx.zst)
    archive_path = Column(Text, nullable=False, unique=True, index=True)
    # Display name for the UI (basename of the original folder).
    name = Column(String(255), nullable=False)
    # Original size on disk in bytes (before compression).
    original_size_bytes = Column(Integer, nullable=False, default=0)
    # Compressed size in bytes (after compression).
    archive_size_bytes = Column(Integer, nullable=False, default=0)
    # SHA-256 of the archive file, used to verify integrity on thaw.
    sha256 = Column(String(64), nullable=False, index=True)
    # When the item was archived.
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    # When the item was last restored (thawed). NULL if still archived.
    restored_at: Optional[datetime] = Column(DateTime, nullable=True)

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return (
            f"<VaultItem id={self.id} name={self.name!r} "
            f"archived={self.restored_at is None}>"
        )

    @property
    def is_archived(self) -> bool:
        """True when the folder is currently in the vault (not restored)."""
        return self.restored_at is None

    @property
    def saved_bytes(self) -> int:
        """How much disk space was saved by archiving this folder."""
        return max(0, self.original_size_bytes - self.archive_size_bytes)