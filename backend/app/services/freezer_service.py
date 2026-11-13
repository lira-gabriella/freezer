"""Freezer service: freeze/thaw processes via psutil."""
from __future__ import annotations

import os
import time
from typing import List, Tuple

import psutil

from backend.app.schemas.process_schema import FreezeResponse, ProcessInfo


def _act(pid: int, suspend: bool) -> Tuple[bool, str]:
    try:
        proc = psutil.Process(pid)
        if suspend:
            proc.suspend()
        else:
            proc.resume()
        action = "Suspended" if suspend else "Resumed"
        return True, f"{action} {pid} ({proc.name()})"
    except psutil.NoSuchProcess:
        return False, f"Process {pid} no longer exists"
    except psutil.AccessDenied:
        return False, f"Access denied for PID {pid}"
    except Exception as exc:
        return False, f"Failed for PID {pid}: {exc}"


def _run(pids: List[int], suspend: bool) -> FreezeResponse:
    affected, failed, messages = [], [], []
    for pid in pids:
        ok, msg = _act(pid, suspend)
        (affected if ok else failed).append(pid)
        messages.append(msg)
    label = "freeze" if suspend else "thaw"
    return FreezeResponse(
        success=not failed,
        message="; ".join(messages) if messages else f"No processes to {label}",
        affected_pids=affected,
        failed_pids=failed,
    )


def freeze_pids(pids: List[int]) -> FreezeResponse:
    return _run(pids, True)


def thaw_pids(pids: List[int]) -> FreezeResponse:
    return _run(pids, False)


def list_processes() -> List[ProcessInfo]:
    results: List[ProcessInfo] = []
    for proc in psutil.process_iter(attrs=["pid", "name", "username", "status"]):
        try:
            info = proc.info
            pid = info["pid"]
            p = psutil.Process(pid)
            suspended = p.status() == psutil.STATUS_STOPPED
            try:
                cpu = p.cpu_percent(interval=None)
                mem = p.memory_info().rss / (1024 * 1024)
                exe = p.exe()
            except (psutil.Error, OSError):
                cpu, mem, exe = 0.0, 0.0, None
            results.append(
                ProcessInfo(
                    pid=pid,
                    name=info["name"] or "unknown",
                    username=info.get("username"),
                    cpu_percent=round(cpu, 2),
                    memory_mb=round(mem, 2),
                    status="suspended" if suspended else (info["status"] or "running"),
                    exe=exe,
                )
            )
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    results.sort(key=lambda x: x.cpu_percent, reverse=True)
    return results


def find_idle_processes(
    idle_timeout_minutes: int, protected_names: List[str] | None = None
) -> List[int]:
    protected = [n.lower() for n in (protected_names or [])]
    idle_pids: List[int] = []
    now = time.time()
    for proc in psutil.process_iter(attrs=["pid", "name"]):
        try:
            pid = proc.info["pid"]
            name = (proc.info["name"] or "").lower()
            if pid == os.getpid() or any(p in name for p in protected):
                continue
            p = psutil.Process(pid)
            if now - p.create_time() < idle_timeout_minutes * 60:
                continue
            if p.cpu_percent(interval=0.05) < 0.5:
                idle_pids.append(pid)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    return idle_pids
