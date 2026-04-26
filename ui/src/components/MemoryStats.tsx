"use client";

import { useState, useEffect } from "react";
import { KnowledgeStats } from "@/lib/types";
import { fetchJSON } from "@/lib/api";

export default function MemoryStats() {
  const [stats, setStats] = useState<KnowledgeStats | null>(null);

  useEffect(() => {
    fetchJSON<KnowledgeStats>("/knowledge/stats")
      .then(setStats)
      .catch((err) => console.error("Failed to load knowledge stats:", err));

    const interval = setInterval(() => {
      fetchJSON<KnowledgeStats>("/knowledge/stats")
        .then(setStats)
        .catch(() => {});
    }, 15000);
    return () => clearInterval(interval);
  }, []);

  if (!stats) {
    return (
      <section
        className="rounded-xl overflow-hidden stagger-5"
        style={{ background: "var(--bg-elev)", border: "1px solid var(--border)" }}
      >
        <div className="px-6 py-[18px]" style={{ borderBottom: "1px solid var(--border)" }}>
          <span className="text-[22px] tracking-tight" style={{ fontFamily: "var(--font-display)" }}>
            Memory
          </span>
        </div>
        <div className="px-6 py-10 text-center text-[13px]" style={{ color: "var(--text-dim)", fontFamily: "var(--font-mono)" }}>
          Loading…
        </div>
      </section>
    );
  }

  return (
    <section
      className="rounded-xl overflow-hidden stagger-5"
      style={{
        background: "var(--bg-elev)",
        border: "1px solid var(--border)",
      }}
    >
      {/* Header */}
      <div
        className="flex items-center justify-between px-6 py-[18px]"
        style={{ borderBottom: "1px solid var(--border)" }}
      >
        <div className="flex items-center gap-2.5">
          <span
            className="text-[22px] tracking-tight"
            style={{ fontFamily: "var(--font-display)" }}
          >
            Memory
          </span>
          <span
            className="text-[11px] uppercase tracking-widest"
            style={{
              fontFamily: "var(--font-mono)",
              color: "var(--text-dim)",
              letterSpacing: "0.1em",
            }}
          >
            · self-knowledge graph
          </span>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-2 gap-4 px-6 py-5">
        <StatCell label="Decisions logged" value={stats.decisions_logged.toLocaleString()} />
        <StatCell label="Patterns learned" value={stats.patterns_learned.toString()} />
        <StatCell
          label="Rollbacks · 90d"
          value={stats.rollbacks_90d.toString()}
          valueColor="var(--warn)"
        />
        <StatCell
          label="Confidence avg"
          value={stats.confidence_avg.toString()}
          suffix="%"
          valueColor="var(--accent)"
        />
      </div>
    </section>
  );
}

function StatCell({
  label,
  value,
  suffix,
  valueColor,
}: {
  label: string;
  value: string;
  suffix?: string;
  valueColor?: string;
}) {
  return (
    <div>
      <div
        className="mb-1.5 text-[10px] uppercase tracking-widest"
        style={{
          fontFamily: "var(--font-mono)",
          color: "var(--text-dim)",
          letterSpacing: "0.1em",
        }}
      >
        {label}
      </div>
      <div
        className="leading-none"
        style={{
          fontFamily: "var(--font-display)",
          fontSize: "26px",
          color: valueColor,
        }}
      >
        {value}
        {suffix && (
          <span className="text-sm" style={{ color: "var(--text-muted)" }}>
            {suffix}
          </span>
        )}
      </div>
    </div>
  );
}
