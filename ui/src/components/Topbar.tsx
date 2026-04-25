"use client";

import { useEffect, useState } from "react";
import { Search, ChevronRight } from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";

const navItems = [
  { name: "Overview", href: "/" },
  { name: "Recommendations", href: "/recommendations" },
  { name: "Agents", href: "/agents" },
  { name: "Knowledge", href: "/knowledge" },
  { name: "Audit", href: "/audit" },
  { name: "Settings", href: "/settings" },
];

export default function Topbar() {
  const pathname = usePathname();
  const [swarmStatus, setSwarmStatus] = useState({
    active: true,
    agentCount: 5,
  });

  useEffect(() => {
    // Poll swarm status every 5s
    const fetchStatus = async () => {
      try {
        const res = await fetch(
          `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api"}/swarm/status`
        );
        if (res.ok) {
          const data = await res.json();
          setSwarmStatus({ active: data.active, agentCount: data.agentCount });
        }
      } catch {
        // Use default mock data
      }
    };

    fetchStatus();
    const interval = setInterval(fetchStatus, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <header
      className="flex items-center justify-between px-8 py-4 sticky top-0 z-50"
      style={{
        borderBottom: "1px solid var(--border)",
        background: "rgba(10,14,22,0.7)",
        backdropFilter: "blur(20px)",
        WebkitBackdropFilter: "blur(20px)",
      }}
    >
      {/* Left: Brand */}
      <div className="flex items-center">
        <div className="flex items-center gap-3">
          <div className="relative">
            <div
              className="w-8 h-8 rounded-lg flex items-center justify-center font-semibold text-sm"
              style={{
                fontFamily: "var(--font-mono)",
                background:
                  "linear-gradient(135deg, var(--accent) 0%, #4d8c6b 100%)",
                color: "var(--bg)",
                boxShadow: "0 0 20px var(--accent-glow)",
              }}
            >
              E
            </div>
            <div
              className="absolute -inset-0.5 rounded-[10px]"
              style={{
                border: "1px solid var(--accent)",
                opacity: 0.3,
                animation: "pulse 2.5s ease-in-out infinite",
              }}
            />
          </div>
          <div>
            <div
              className="text-[22px] tracking-tight"
              style={{ fontFamily: "var(--font-display)" }}
            >
              Evo<em style={{ color: "var(--accent)", fontStyle: "italic" }}>Agent</em>
            </div>
          </div>
          <div
            className="pl-3 ml-3 text-[10px] uppercase tracking-widest"
            style={{
              fontFamily: "var(--font-mono)",
              color: "var(--text-dim)",
              borderLeft: "1px solid var(--border)",
            }}
          >
            v2.4 · prod
          </div>
        </div>
      </div>

      {/* Center: Nav */}
      <nav className="flex gap-1">
        {navItems.map((item) => {
          const isActive = pathname === item.href || (item.href !== "/" && pathname?.startsWith(item.href));
          return (
            <Link
              key={item.name}
              href={item.href}
              className="px-3.5 py-2 rounded-md text-[13px] font-medium transition-all duration-150 cursor-pointer no-underline"
              style={{
                color: isActive ? "var(--accent)" : "var(--text-muted)",
                background: isActive ? "var(--accent-glow)" : "transparent",
                fontFamily: "var(--font-body)",
              }}
            >
              {item.name}
            </Link>
          );
        })}
      </nav>

      {/* Right: Actions */}
      <div className="flex items-center gap-3">
        {/* Search */}
        <div
          className="flex items-center gap-2 px-3 py-[7px] rounded-md w-[280px]"
          style={{
            background: "var(--surface)",
            border: "1px solid var(--border)",
            fontFamily: "var(--font-mono)",
            fontSize: "12px",
            color: "var(--text-muted)",
          }}
        >
          <Search size={14} style={{ opacity: 0.5 }} />
          <span>Search tables, queries, decisions…</span>
          <kbd
            className="ml-auto px-1.5 py-0.5 rounded text-[10px]"
            style={{
              background: "var(--bg)",
              border: "1px solid var(--border)",
              color: "var(--text-dim)",
            }}
          >
            ⌘K
          </kbd>
        </div>

        {/* Status Pill */}
        <div
          className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-full text-[11px] uppercase tracking-wider"
          style={{
            background: "var(--accent-glow)",
            border: "1px solid rgba(125,249,169,0.25)",
            fontFamily: "var(--font-mono)",
            color: "var(--accent)",
          }}
        >
          <span
            className="w-1.5 h-1.5 rounded-full"
            style={{
              background: "var(--accent)",
              boxShadow: "0 0 8px var(--accent)",
              animation: "blink 1.8s ease-in-out infinite",
            }}
          />
          {swarmStatus.active ? "Swarm Active" : "Swarm Idle"} ·{" "}
          {swarmStatus.agentCount} agents
        </div>

        {/* Avatar */}
        <div
          className="w-8 h-8 rounded-full flex items-center justify-center text-xs font-semibold text-white"
          style={{
            background: "linear-gradient(135deg, #6ea8ff, #b794f6)",
          }}
        >
          RK
        </div>
      </div>
    </header>
  );
}
