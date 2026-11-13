"use client";

import Link from "next/link";
import { Activity, Archive, BookOpen, Shield, Snowflake } from "lucide-react";

const nav = [
  { href: "/", label: "Dashboard", icon: Activity },
  { href: "#processes", label: "Processes", icon: Snowflake },
  { href: "#vault", label: "Cryo-Vault", icon: Archive },
  { href: "#security", label: "Security", icon: Shield },
];

export default function Sidebar() {
  return (
    <aside className="hidden w-64 flex-col border-r border-slate-800 bg-[#0f172a] p-4 md:flex">
      <div className="mb-8">
        <h1 className="text-xl font-bold text-cyan-400">CryoGuard</h1>
        <p className="text-xs text-slate-400">Deep Midnight Control</p>
      </div>
      <nav className="space-y-1">
        {nav.map((item) => {
          const Icon = item.icon;
          return (
            <Link
              key={item.href}
              href={item.href}
              className="flex items-center gap-2 rounded-md px-3 py-2 text-sm text-slate-300 hover:bg-slate-800 hover:text-cyan-300"
            >
              <Icon size={16} /> {item.label}
            </Link>
          );
        })}
        <a
          href="http://localhost:8000/docs"
          target="_blank"
          rel="noreferrer"
          className="mt-4 flex items-center gap-2 rounded-md px-3 py-2 text-sm text-slate-300 hover:bg-slate-800 hover:text-cyan-300"
        >
          <BookOpen size={16} /> FastAPI Docs
        </a>
      </nav>
      <div className="mt-auto rounded-lg border border-slate-800 bg-slate-900/50 p-3 text-xs text-slate-400">
        Backend: <span className="text-cyan-300">localhost:8000</span>
      </div>
    </aside>
  );
}
