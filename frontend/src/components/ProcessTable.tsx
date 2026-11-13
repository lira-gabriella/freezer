"use client";

import { useMemo, useState } from "react";
import type { ProcessInfo } from "@/types/cryoguard";

type Props = {
  processes: ProcessInfo[];
  onFreeze: (pids: number[]) => void;
  onThaw: (pids: number[]) => void;
  onFocus: (names: string[]) => void;
  busy?: boolean;
};

export default function ProcessTable({ processes, onFreeze, onThaw, onFocus, busy }: Props) {
  const [filter, setFilter] = useState("");
  const rows = useMemo(() => {
    const q = filter.toLowerCase();
    return processes.filter((p) => !q || p.name.toLowerCase().includes(q) || String(p.pid).includes(q)).slice(0, 40);
  }, [processes, filter]);

  return (
    <section id="processes" className="card">
      <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
        <div>
          <h2 className="text-lg font-semibold text-cyan-300">Live Processes</h2>
          <p className="text-xs text-slate-400">Freeze or thaw running apps</p>
        </div>
        <div className="flex flex-wrap gap-2">
          <button className="btn-muted" onClick={() => onFocus(["chrome", "msedge", "firefox"])} disabled={busy}>Focus: Browsers</button>
          <button className="btn-muted" onClick={() => onFocus(["slack", "discord", "teams"])} disabled={busy}>Focus: Chat</button>
          <button className="btn-muted" onClick={() => onFocus(["spotify"])} disabled={busy}>Focus: Media</button>
        </div>
      </div>
      <input className="input mb-3" placeholder="Filter by name or PID..." value={filter} onChange={(e) => setFilter(e.target.value)} />
      <div className="overflow-auto">
        <table className="w-full text-left text-sm">
          <thead className="text-xs uppercase text-slate-400">
            <tr><th className="py-2">PID</th><th>Name</th><th>CPU%</th><th>RAM MB</th><th>Status</th><th>Action</th></tr>
          </thead>
          <tbody>
            {rows.map((p) => {
              const frozen = p.status === "suspended";
              return (
                <tr key={p.pid} className="border-t border-slate-800">
                  <td className="py-2">{p.pid}</td>
                  <td className="max-w-[220px] truncate" title={p.exe || p.name}>{p.name}</td>
                  <td>{p.cpu_percent.toFixed(1)}</td>
                  <td>{p.memory_mb.toFixed(1)}</td>
                  <td><span className={`badge ${frozen ? "bg-cyan-900/50 text-cyan-300" : "bg-emerald-900/50 text-emerald-300"}`}>{p.status}</span></td>
                  <td>
                    {frozen ? (
                      <button className="btn-safe px-2 py-1 text-xs" onClick={() => onThaw([p.pid])} disabled={busy}>Thaw</button>
                    ) : (
                      <button className="btn-primary px-2 py-1 text-xs" onClick={() => onFreeze([p.pid])} disabled={busy}>Freeze</button>
                    )}
                  </td>
                </tr>
              );
            })}
            {rows.length === 0 && <tr><td colSpan={6} className="py-4 text-center text-slate-500">No processes found.</td></tr>}
          </tbody>
        </table>
      </div>
    </section>
  );
}
