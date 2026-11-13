"use client";

import { Cpu, HardDrive, ShieldCheck, Snowflake } from "lucide-react";

type Props = {
  ramSavedMb: number;
  diskFreedMb: number;
  frozenApps: number;
  securityScore: number | null;
};

function Card({
  title,
  value,
  sub,
  icon: Icon,
  tone = "text-cyan-400",
}: {
  title: string;
  value: string;
  sub: string;
  icon: any;
  tone?: string;
}) {
  return (
    <div className="card flex items-center gap-4">
      <div className={`rounded-lg bg-slate-800 p-3 ${tone}`}>
        <Icon size={20} />
      </div>
      <div>
        <p className="text-xs uppercase tracking-wide text-slate-400">{title}</p>
        <p className="text-xl font-semibold text-slate-100">{value}</p>
        <p className="text-xs text-slate-500">{sub}</p>
      </div>
    </div>
  );
}

export default function StatsCards({ ramSavedMb, diskFreedMb, frozenApps, securityScore }: Props) {
  const scoreTone =
    securityScore == null ? "text-cyan-400" : securityScore >= 70 ? "text-emerald-400" : "text-rose-400";
  return (
    <section className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
      <Card title="RAM Saved" value={`${ramSavedMb.toFixed(1)} MB`} sub="Estimated from frozen apps" icon={Cpu} />
      <Card title="Disk Space Freed" value={`${diskFreedMb.toFixed(1)} MB`} sub="Cryo-Vault savings" icon={HardDrive} />
      <Card title="Frozen Apps" value={`${frozenApps}`} sub="Currently suspended" icon={Snowflake} />
      <Card
        title="Security Score"
        value={securityScore == null ? "—" : `${securityScore}/100`}
        sub="Latest scan result"
        icon={ShieldCheck}
        tone={scoreTone}
      />
    </section>
  );
}
