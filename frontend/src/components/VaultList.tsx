"use client";

import { useState } from "react";
import type { VaultItemResponse } from "@/types/cryoguard";
import { sanitizePathInput } from "@/lib/sanitize";

type Props = {
  items: VaultItemResponse[];
  onArchive: (path: string) => Promise<void> | void;
  onRestore: (id: number) => Promise<void> | void;
  busy?: boolean;
};

function fmtMb(bytes: number) {
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

export default function VaultList({ items, onArchive, onRestore, busy }: Props) {
  const [path, setPath] = useState("");
  const [err, setErr] = useState<string | null>(null);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    try {
      const clean = sanitizePathInput(path);
      if (!clean) throw new Error("Path is required");
      setErr(null);
      await onArchive(clean);
      setPath("");
    } catch (e: any) {
      setErr(e.message || "Invalid path");
    }
  }

  return (
    <section id="vault" className="card">
      <h2 className="text-lg font-semibold text-cyan-300">Cryo-Vault</h2>
      <p className="mb-3 text-xs text-slate-400">Archive folders to free disk space, restore with 1 click.</p>
      <form onSubmit={submit} className="mb-3 flex flex-col gap-2 sm:flex-row">
        <input className="input" placeholder="Folder path to archive (no ../)" value={path} onChange={(e) => setPath(e.target.value)} />
        <button className="btn-primary sm:w-40" type="submit" disabled={busy}>Archive</button>
      </form>
      {err && <p className="mb-2 text-xs text-rose-400">{err}</p>}
      <div className="space-y-2">
        {items.map((it) => (
          <div key={it.id} className="flex flex-wrap items-center justify-between gap-3 rounded-lg border border-slate-800 bg-slate-900/40 p-3">
            <div className="min-w-0">
              <p className="font-medium text-slate-100">{it.name}</p>
              <p className="truncate text-xs text-slate-400" title={it.original_path}>{it.original_path}</p>
              <p className="text-xs text-emerald-400">Saved {fmtMb(it.saved_bytes)} ({fmtMb(it.original_size_bytes)} → {fmtMb(it.archive_size_bytes)})</p>
            </div>
            <button className="btn-safe" onClick={() => onRestore(it.id)} disabled={busy}>1-click Thaw</button>
          </div>
        ))}
        {items.length === 0 && <p className="text-sm text-slate-500">Vault is empty.</p>}
      </div>
    </section>
  );
}
