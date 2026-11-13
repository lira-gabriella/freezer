"""
Security Schemas
================
Pydantic v2 schemas for the security scanner endpoints.
Defines the Safety Score request/response shapes and finding structures.
"""
from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, field_validator

# File extensions considered high-risk / suspicious.
SUSPICIOUS_EXTENSIONS = {
    ".vbs", ".bat", ".cmd", ".scr", ".ps1", ".js", ".jar", ".exe",
    ".msi", ".dll", ".sh", ".bash", ".zsh", ".php", ".pl", ".py",
    ".reg", ".com", ".pif", ".hta", ".cpl", ".msc", ".wsf", ".wsh",
}


class Finding(BaseModel):
    """A single suspicious file detected during a scan."""
    model_config = {"extra": "allow"}

    path: str
    reason: str
    severity: str  # "low", "medium", "high"
    sha256: Optional[str] = None
    file_size: int = 0


class ScanRequest(BaseModel):
    """Request body for running a security scan."""
    model_config = {"extra": "forbid"}

    path: str

    @field_validator("path")
    @classmethod
    def _validate_path(cls, v: str) -> str:
        if not isinstance(v, str) or not v.strip():
            raise ValueError("Path cannot be empty")
        # Basic sanitization — full path checks happen in the service layer.
        if "\x00" in v:
            raise ValueError("Path contains null bytes")
        return v.strip()


class ScanResponse(BaseModel):
    """Result of a security scan."""
    model_config = {"extra": "allow"}

    success: bool
    target_path: str
    safety_score: int  # 0-100
    files_scanned: int
    suspicious_count: int
    findings: List[Finding] = []
    message: str = ""


class ScanHistoryItem(BaseModel):
    """A past scan log entry for the history UI."""
    model_config = {"extra": "allow"}

    id: int
    target_path: str
    safety_score: int
    files_scanned: int
    suspicious_count: int
    created_at: Optional[str] = None