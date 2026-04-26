"use client";

import { useState, useEffect, useCallback } from "react";
import { fetchJSON } from "@/lib/api";

interface OptimizationScoreData {
  score: number;
  grade: string;
  trend: string;
  description: string;
  cost_saved: number;
  cost_trend: string;
  speedup: number;
  speedup_trend: string;
  pending: number;
  pending_high: number;
}

export default function StatsRow() {
  const [data, setData] = useState<OptimizationScoreData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  const loadStats = useCallback(async () => {
    try {
      const result = await fetchJSON<OptimizationScoreData>("/metrics/optimization-score");
      setData(result);
    } catch (err) {
      console.error("Failed to load stats:", err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadStats();
    const interval = setInterval(loadStats, 10000);
    return () => clearInterval(interval);
  }, [loadStats]);

  if (loading && !data) {
    return (
      <div className="p-6 text-center bg-[#131927] border border-white/5 rounded-xl">
        <p style={{ color: "var(--text-muted)" }}>Loading stats...</p>
      </div>
    );
  }

  if (!data) return null;

  return (
    <section
      className="grid gap-px rounded-xl overflow-hidden stagger-2"
      style={{
        gridTemplateColumns: "1.4fr 1fr 1fr 1fr",
        background: "var(--border)",
        border: "1px solid var(--border)",
      }}
    >
      {/* Optimization Score (feature stat) */}
      <div
        className="p-6 relative overflow-hidden"
        style={{
          background:
            "linear-gradient(135deg, var(--bg-elev) 0%, rgba(125,249,169,0.04) 100%)",
        }}
      >
        <div
          className="flex items-center gap-2 mb-4 text-[10px] uppercase tracking-widest"
          style={{
            fontFamily: "var(--font-mono)",
            color: "var(--text-dim)",
            letterSpacing: "0.12em",
          }}
        >
          <span
            className="w-1.5 h-1.5 rounded-full"
            style={{ background: "var(--accent)" }}
          />
          Optimization Score
        </div>
        <div className="flex items-center gap-6">
          {/* SVG Gauge */}
          <div className="relative w-[110px] h-[110px] shrink-0">
            <svg viewBox="0 0 120 120" className="w-full h-full" style={{ transform: "rotate(-90deg)" }}>
              <defs>
                <linearGradient id="gaugeGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                  <stop offset="0%" stopColor="#4ac788" />
                  <stop offset="100%" stopColor="#7df9a9" />
                </linearGradient>
              </defs>
              <circle
                cx="60"
                cy="60"
                r="50"
                fill="none"
                stroke="var(--border-strong)"
                strokeWidth="8"
              />
              <circle
                cx="60"
                cy="60"
                r="50"
                fill="none"
                stroke="url(#gaugeGradient)"
                strokeWidth="8"
                strokeLinecap="round"
                strokeDasharray="314"
                strokeDashoffset={314 - (314 * data.score) / 100}
                style={{ filter: "drop-shadow(0 0 6px var(--accent-glow))" }}
              />
            </svg>
            <div className="absolute inset-0 flex flex-col items-center justify-center">
              <div
                className="leading-none"
                style={{
                  fontFamily: "var(--font-display)",
                  fontSize: "36px",
                  color: "var(--accent)",
                }}
              >
                {data.score}
              </div>
              <div
                className="mt-0.5 text-[9px] uppercase tracking-widest"
                style={{
                  fontFamily: "var(--font-mono)",
                  color: "var(--text-dim)",
                  letterSpacing: "0.12em",
                }}
              >
                {data.grade}
              </div>
            </div>
          </div>
          <div>
            <div
              className="text-[13px] leading-relaxed mb-2"
              style={{ color: "var(--text-muted)" }}
            >
              {data.description}
            </div>
            <div
              className="inline-flex items-center gap-1 text-[11px]"
              style={{
                fontFamily: "var(--font-mono)",
                color: "var(--accent)",
              }}
            >
              {data.trend}
            </div>
          </div>
        </div>
      </div>

      {/* Cost Saved */}
      <StatCard
        label="Cost Saved · MTD"
        value={`$${(data.cost_saved / 1000).toFixed(1)}`}
        unit="K"
        trend={data.cost_trend}
        trendColor="var(--accent)"
      />

      {/* Avg Query Speedup */}
      <StatCard
        label="Avg Query Speedup"
        value={data.speedup.toFixed(1)}
        unit="×"
        trend={data.speedup_trend}
        trendColor="var(--accent)"
      />

      {/* Pending Review */}
      <StatCard
        label="Pending Review"
        value={data.pending.toString()}
        trend={`${data.pending_high} high priority`}
        trendColor="var(--warn)"
      />
    </section>
  );
}

function StatCard({
  label,
  value,
  unit,
  trend,
  trendColor,
}: {
  label: string;
  value: string;
  unit?: string;
  trend: string;
  trendColor: string;
}) {
  return (
    <div className="p-6 relative overflow-hidden" style={{ background: "var(--bg-elev)" }}>
      <div
        className="mb-4 text-[10px] uppercase tracking-widest"
        style={{
          fontFamily: "var(--font-mono)",
          color: "var(--text-dim)",
          letterSpacing: "0.12em",
        }}
      >
        {label}
      </div>
      <div
        className="leading-none mb-2"
        style={{
          fontFamily: "var(--font-display)",
          fontSize: "44px",
          letterSpacing: "-0.02em",
        }}
      >
        {value}
        {unit && (
          <span
            className="text-lg ml-1"
            style={{ color: "var(--text-muted)" }}
          >
            {unit}
          </span>
        )}
      </div>
      <div
        className="inline-flex items-center gap-1 text-[11px]"
        style={{
          fontFamily: "var(--font-mono)",
          color: trendColor,
        }}
      >
        {trend}
      </div>
    </div>
  );
}
