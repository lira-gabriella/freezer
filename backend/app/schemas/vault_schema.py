"""
Vault Schemas
=============
Pydantic v2 schemas for the Cryo-Vault endpoints.
Includes strict path sanitization to prevent directory traversal attacks
and blocking of critical OS system directories.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import List, Optional

from pydantic import BaseModel, field_validator

# Directories that CryoGuard will NEVER archive or delete — these are
# critical OS locations whose loss would brick the machine.
CRITICAL_DIRS = {
    "C:\\Windows",
    "C:\\Program Files",
    "C:\\Program Files (x86)",
    "C:\\ProgramData",
    "/bin",
    "/boot",
    "/dev",
    "/etc",
    "/lib",
    "/lib64",
    "/proc",
    "/root",
    "/run",
    "/sbin",
    "/sys",
    "/System",
    "/usr",
    "/var",
}


def sanitize_path(raw: str) -> str:
    """
    Sanitize a user-supplied folder path:
    - Reject null bytes.
    - Reject path traversal (`../`).
    - Resolve to an absolute path.
    - Reject if it points inside a critical OS directory.
    Returns the resolved absolute path as a string.
    """
    if not isinstance(raw, str):
        raise ValueError("Path must be a string")

    # Null-byte injection check.
    if "\x00" in raw:
        raise ValueError("Path contains null bytes")

    # Strip surrounding whitespace.
    raw = raw.strip()
    if not raw:
        raise ValueError("Path cannot be empty")

    # Block obvious traversal attempts before resolution.
    if ".." in raw.split(os.sep) or ".." in raw.split("/"):
        raise ValueError("Path traversal (../) is not allowed")

    # Resolve to absolute real path (follows symlinks).
    try:
        resolved = Path(raw).resolve(strict=False)
    except (OSError, RuntimeError) as exc:
        raise ValueError(f"Cannot resolve path: {exc}")

    resolved_str = str(resolved)

    # Block critical OS directories.
    for critical in CRITICAL_DIRS:
        try:
            critical_resolved = str(Path(critical).resolve(strict=False))
        except (OSError, RuntimeError):
            critical_resolved = critical
        if resolved_str == critical_resolved or resolved_str.startswith(
            critical_resolved + os.sep
        ):
            raise ValueError(
                f"Refusing to operate on critical system directory: {critical}"
            )

    return resolved_str


class ArchiveRequest(BaseModel):
    """Request body for archiving a folder into the Cryo-Vault."""
    model_config = {"extra": "forbid"}

    path: str

    @field_validator("path")
    @classmethod
    def _validate_path(cls, v: str) -> str:
        return sanitize_path(v)


class RestoreRequest(BaseModel):
    """Request body for restoring (thawing) a vault item."""
    model_config = {"extra": "forbid"}

    item_id: int

    @field_validator("item_id")
    @classmethod
    def _validate_item_id(cls, v: int) -> int:
        if not isinstance(v, int) or v <= 0:
            raise ValueError("item_id must be a positive integer")
        return v


class VaultItemResponse(BaseModel):
    """Response shape for a vault item — matches the frontend contract."""
    model_config = {"extra": "allow"}

    id: int
    name: str
    original_path: str
    archive_path: str
    original_size_bytes: int
    archive_size_bytes: int
    sha256: str
    is_archived: bool
    saved_bytes: int
    created_at: Optional[str] = None
    restored_at: Optional[str] = None


class ArchiveResponse(BaseModel):
    """Result of an archive operation."""
    model_config = {"extra": "forbid"}

    success: bool
    message: str
    item: Optional[VaultItemResponse] = None