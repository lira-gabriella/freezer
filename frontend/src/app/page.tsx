"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import StatsCards from "@/components/StatsCards";
import ProcessTable from "@/components/ProcessTable";
import VaultList from "@/components/VaultList";
import SecurityBadge from "@/components/SecurityBadge";
import { api } from "@/lib/api";
import { sanitizePathInput } from "@/lib/sanitize";
import type { ProcessInfo, ScanResponse, VaultItemResponse } from "@/types/cryoguard";

export default function Home() {
  const [processes, setProcesses] = useState<ProcessInfo[]>([]);
  const [vault, setVault] = useState<VaultItemResponse[]>([]);
  const [scan, setScan] = useState<ScanResponse | null>(null);
  const [scanPath, setScanPath] = useState("");
  const [busy, setBusy] = useState(false);
  const [msg, setMsg] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    try {
      const [p, v] = await Promise.all([api.listProcesses(), api.listVault()]);
      setProcesses(p);
      setVault(v);
    } catch (e: any) {
      setMsg(e.message || "Failed to load data");
    }
  }, []);

  useEffect(() => { refresh(); }, [refresh]);

  const frozen = useMemo(() => processes.filter((p) => p.status === "suspended"), [processes]);
  const ramSavedMb = frozen.reduce((a, p) => a + p.memory_mb, 0);
  const diskFreedMb = vault.reduce((a, i) => a + i.saved_bytes, 0) / (1024 * 1024);

  async function run<T>(fn: () => Promise<T>) {
    setBusy(true); setMsg(null);
    try { return await fn(); } catch (e: any) { setMsg(e.message || "Action failed"); }
    finally { setBusy(false); }
  }

  async function freeze(pids: number[]) { await run(() => api.freeze({ pids })); await refresh(); }
  async function thaw(pids: number[]) { await run(() => api.thaw({ pids })); await refresh(); }
  async function focus(names: string[]) {
    const targets = processes.filter((p) => p.status !== "suspended" && names.some((n) => p.name.toLower().includes(n))).map((p) => p.pid);
    if (targets.length) await freeze(targets); else setMsg("No matching running processes found.");
  }
  async function archive(path: string) { await run(() => api.archive(path)); await refresh(); }
  async function restore(id: number) { await run(() => api.restore(id)); await refresh(); }
  async function doScan() {
    await run(async () => {
      const clean = sanitizePathInput(scanPath);
      if (!clean) throw new Error("Scan path is required");
      setScan(await api.scan(clean));
    });
  }

  return (
    <div className="space-y-6">
      <header>
        <h1 className="text-2xl font-bold text-cyan-300">CryoGuard Dashboard</h1>
        <p className="text-sm text-slate-400">Freeze apps, vault folders, and scan for threats.</p>
      </header>
      {msg && <div className="rounded-md border border-slate-700 bg-slate-900 p-3 text-sm text-slate-200">{msg}</div>}
      <StatsCards ramSavedMb={ramSavedMb} diskFreedMb={diskFreedMb} frozenApps={frozen.length} securityScore={scan?.safety_score ?? null} />
      <ProcessTable processes={processes} onFreeze={freeze} onThaw={thaw} onFocus={focus} busy={busy} />
      <div className="grid grid-cols-1 gap-6 xl:grid-cols-2">
        <VaultList items={vault} onArchive={archive} onRestore={restore} busy={busy} />
        <section id="security" className="space-y-4">
          <div className="card">
            <h2 className="text-lg font-semibold text-cyan-300">Security Scanner</h2>
            <p className="mb-3 text-xs text-slate-400">Pre-freeze SHA-256 & malware risk scan.</p>
            <div className="flex flex-col gap-2 sm:flex-row">
              <input className="input" placeholder="Folder path to scan" value={scanPath} onChange={(e) => setScanPath(e.target.value)} />
              <button className="btn-primary sm:w-32" onClick={doScan} disabled={busy}>Scan</button>
            </div>
          </div>
          <SecurityBadge scan={scan} />
        </section>
      </div>
    </div>
  );
}
