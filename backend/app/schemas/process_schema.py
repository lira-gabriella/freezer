"""
Process Schemas
===============
Pydantic v2 schemas for process control endpoints.
Includes strict validation of PIDs and process names to prevent injection.
"""
from __future__ import annotations

import re
from typing import List, Optional

from pydantic import BaseModel, field_validator


# Reusable config: allow population by field name (so aliases work) and
# forbid extra fields so typos in JSON are caught immediately.
CFG = {"extra": "forbid"}


class ProcessInfo(BaseModel):
    """Snapshot of a running process for the UI."""
    model_config = {"extra": "allow"}

    pid: int
    name: str
    username: Optional[str] = None
    cpu_percent: float = 0.0
    memory_mb: float = 0.0
    status: str = "running"  # running, suspended, etc.
    exe: Optional[str] = None


class FreezeRequest(BaseModel):
    """Request body for freezing one or more processes."""
    pids: List[int] = []
    process_names: List[str] = []

    @field_validator("pids")
    @classmethod
    def _validate_pids(cls, v: List[int]) -> List[int]:
        cleaned: List[int] = []
        for pid in v:
            if not isinstance(pid, int) or pid <= 0:
                raise ValueError(f"Invalid PID: {pid!r} — must be a positive integer")
            # Reject absurdly high PIDs that would never exist.
            if pid > 4194304:  # max pid on most OSes
                raise ValueError(f"PID {pid} is out of range")
            cleaned.append(pid)
        return cleaned

    @field_validator("process_names")
    @classmethod
    def _validate_names(cls, v: List[str]) -> List[str]:
        cleaned: List[str] = []
        for name in v:
            if not isinstance(name, str) or not name.strip():
                raise ValueError("Process name must be a non-empty string")
            # Strip any path separators or shell metacharacters.
            sanitized = re.sub(r"[^\w.\- ]", "", name).strip()
            if not sanitized:
                raise ValueError(f"Process name {name!r} contains only invalid chars")
            cleaned.append(sanitized)
        return cleaned


class FreezeResponse(BaseModel):
    """Result of a freeze/thaw operation."""
    model_config = CFG

    success: bool
    message: str
    affected_pids: List[int] = []
    failed_pids: List[int] = []


class AutoIdleConfig(BaseModel):
    """User settings for the auto-idle watchdog."""
    model_config = CFG

    enabled: bool = True
    idle_timeout_minutes: int = 15
    # Process name substrings that should NEVER be auto-frozen.
    protected_processes: List[str] = []

    @field_validator("idle_timeout_minutes")
    @classmethod
    def _validate_timeout(cls, v: int) -> int:
        if not isinstance(v, int) or v < 1:
            raise ValueError("idle_timeout_minutes must be a positive integer")
        if v > 1440:  # 24h cap
            raise ValueError("idle_timeout_minutes cannot exceed 1440 (24h)")
        return v


class FocusModeRequest(BaseModel):
    """Request to activate a focus mode by profile id or name."""
    model_config = CFG

    profile_id: Optional[int] = None
    profile_name: Optional[str] = None

    @field_validator("profile_name")
    @classmethod
    def _validate_profile_name(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        sanitized = re.sub(r"[^\w\- ]", "", v).strip()
        return sanitized or None