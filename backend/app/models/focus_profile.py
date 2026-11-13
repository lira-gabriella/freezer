"""
Focus Profile Model
===================
Represents a user-defined "Focus Mode" preset (e.g. Coding Mode).
Each profile lists PIDs / process names to freeze automatically when
the mode is activated, plus an idle timeout in minutes.
"""
from __future__ import annotations

from typing import List

from sqlalchemy import Column, Integer, String, Text

from backend.database import Base


class FocusProfile(Base):
    __tablename__ = "focus_profiles"

    id = Column(Integer, primary_key=True, index=True)
    # Display name shown in the UI, e.g. "Coding Mode".
    name = Column(String(128), nullable=False, unique=True, index=True)
    # Short description of what this mode does.
    description = Column(Text, nullable=False, default="")
    # Idle timeout in minutes before auto-freezing idle apps.
    idle_timeout_minutes = Column(Integer, nullable=False, default=15)
    # JSON-encoded list of process name substrings to freeze, e.g. ["chrome", "slack"].
    target_processes_json = Column(Text, nullable=False, default="[]")
    # Whether this profile is active / selected by the user.
    is_active = Column(Integer, nullable=False, default=0)  # 0/1 bool via int

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"<FocusProfile id={self.id} name={self.name!r} active={bool(self.is_active)}>"

    @property
    def target_processes(self) -> List[str]:
        """Parse the stored JSON list into a Python list of strings."""
        import json
        try:
            data = json.loads(self.target_processes_json or "[]")
            return [str(x) for x in data]
        except (json.JSONDecodeError, TypeError):
            return []

    @target_processes.setter
    def target_processes(self, value: List[str]) -> None:
        """Serialize a Python list into the JSON column."""
        import json
        self.target_processes_json = json.dumps(list(value or []))