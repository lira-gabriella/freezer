"""
Path Sanitizer
================
Centralized path sanitization utilities used across services.
"""
from __future__ import annotations

import os
import re
from pathlib import Path

# Directories CryoGuard will NEVER archive, delete, or scan for freezing.
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

    if "\x00" in raw:
        raise ValueError("Path contains null bytes")

    raw = raw.strip()
    if not raw:
        raise ValueError("Path cannot be empty")

    # Block traversal attempts before resolution.
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


def is_critical_path(path: str) -> bool:
    """Return True if the resolved path is (or is inside) a critical dir."""
    try:
        resolved = str(Path(path).resolve(strict=False))
    except (OSError, RuntimeError):
        return False
    for critical in CRITICAL_DIRS:
        try:
            critical_resolved = str(Path(critical).resolve(strict=False))
        except (OSError, RuntimeError):
            critical_resolved = critical
        if resolved == critical_resolved or resolved.startswith(
            critical_resolved + os.sep
        ):
            return True
    return False


def sanitize_process_name(name: str) -> str:
    """
    Strip path separators and shell metacharacters from a process name
    so it can only be used as a substring match, not for injection.
    """
    if not isinstance(name, str):
        raise ValueError("Process name must be a string")
    sanitized = re.sub(r"[^\w.\- ]", "", name).strip()
    if not sanitized:
        raise ValueError("Process name contains only invalid characters")
    return sanitized