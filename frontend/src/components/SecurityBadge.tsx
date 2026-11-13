"use client";

import { ShieldAlert, ShieldCheck } from "lucide-react";
import type { ScanResponse } from "@/types/cryoguard";

type Props = { scan: ScanResponse | null };

export default function SecurityBadge({ scan }: Props) {
  if (!scan) {
    return (
      <div className="card">
        <h3 className="mb-1 text-sm font-semibold text-cyan-300">Pre-freeze Security</h3>
        <p className="text-xs text-slate-400">No scan run yet. Scan a folder to see SHA-256 findings and safety score.</p>
      </div>
    );
  }

  const safe = scan.safety_score >= 70 && scan.suspicious_count === 0;
  const tone = safe ? "text-emerald-400" : scan.safety_score >= 40 ? "text-yellow-400" : "text-rose-400";
  const Icon = safe ? ShieldCheck : ShieldAlert;

  return (
    <div className="card">
      <div className="mb-2 flex items-center justify-between">
        <h3 className="text-sm font-semibold text-cyan-300">Pre-freeze Security</h3>
        <div className={`flex items-center gap-1 ${tone}`}>
          <Icon size={16} />
          <span className="font-semibold">{scan.safety_score}/100</span>
        </div>
      </div>
      <p className="text-xs text-slate-400 mb-2" title={scan.target_path}>
        {scan.target_path} • {scan.files_scanned} files • {scan.suspicious_count} suspicious
      </p>
      <div className="max-h-40 space-y-1 overflow-auto">
        {scan.findings.slice(0, 6).map((f, i) => (
          <div key={i} className="rounded border border-slate-800 bg-slate-900/40 p-2 text-xs">
            <p className="truncate text-slate-200" title={f.path}>{f.path}</p>
            <p className="text-slate-400">
              {f.reason} • <span className={f.severity === "high" ? "text-rose-400" : f.severity === "medium" ? "text-yellow-400" : "text-slate-300"}>{f.severity}</span>
            </p>
            {f.sha256 && <p className="truncate text-slate-500" title={f.sha256}>SHA-256: {f.sha256}</p>}
          </div>
        ))}
        {scan.findings.length === 0 && <p className="text-xs text-emerald-400">No suspicious files detected.</p>}
      </div>
      <p className="mt-2 text-xs text-slate-400">{scan.message}</p>
    </div>
  );
}
