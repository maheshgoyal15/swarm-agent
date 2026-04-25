"use client";

import { useState, useMemo } from "react";
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  ReferenceDot,
} from "recharts";
import { generateImpactTimeline } from "@/lib/mock-data";

type Period = "7d" | "30d" | "90d";

export default function ImpactChart() {
  const [period, setPeriod] = useState<Period>("30d");

  const data = useMemo(() => {
    const days = period === "7d" ? 7 : period === "30d" ? 30 : 90;
    return generateImpactTimeline(days);
  }, [period]);

  const appliedPoints = data.filter((d) => d.applied);

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
            Cumulative Impact
          </span>
          <span
            className="text-[11px] uppercase tracking-widest"
            style={{
              fontFamily: "var(--font-mono)",
              color: "var(--text-dim)",
              letterSpacing: "0.1em",
            }}
          >
            · last {period}
          </span>
        </div>
        <div className="flex gap-2">
          {(["7d", "30d", "90d"] as Period[]).map((p) => (
            <button
              key={p}
              onClick={() => setPeriod(p)}
              className="px-3.5 py-[7px] rounded-md text-[12px] font-medium transition-all duration-150 cursor-pointer"
              style={{
                background:
                  period === p ? "var(--surface)" : "transparent",
                border:
                  period === p
                    ? "1px solid var(--border-strong)"
                    : "1px solid transparent",
                color:
                  period === p ? "var(--text)" : "var(--text-muted)",
                fontFamily: "var(--font-body)",
              }}
            >
              {p}
            </button>
          ))}
        </div>
      </div>

      {/* Chart */}
      <div className="px-6 py-6">
        {/* Legend */}
        <div
          className="flex gap-5 mb-5 text-[11px]"
          style={{
            fontFamily: "var(--font-mono)",
            color: "var(--text-muted)",
          }}
        >
          <span className="flex items-center gap-2">
            <span
              className="w-2.5 h-2.5 rounded-sm inline-block"
              style={{ background: "var(--accent)" }}
            />
            Bytes scanned (TB/day)
          </span>
          <span className="flex items-center gap-2">
            <span
              className="w-2.5 h-2.5 rounded-sm inline-block"
              style={{ background: "var(--info)" }}
            />
            Avg query latency (ms)
          </span>
        </div>

        <ResponsiveContainer width="100%" height={200}>
          <AreaChart
            data={data}
            margin={{ top: 5, right: 5, left: -20, bottom: 0 }}
          >
            <defs>
              <linearGradient id="chartGradAccent" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#7df9a9" stopOpacity={0.3} />
                <stop offset="100%" stopColor="#7df9a9" stopOpacity={0} />
              </linearGradient>
              <linearGradient id="chartGradInfo" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#6ea8ff" stopOpacity={0.2} />
                <stop offset="100%" stopColor="#6ea8ff" stopOpacity={0} />
              </linearGradient>
            </defs>
            <XAxis
              dataKey="date"
              tick={{
                fill: "#5a6478",
                fontSize: 10,
                fontFamily: "var(--font-mono)",
              }}
              axisLine={false}
              tickLine={false}
              interval="preserveStartEnd"
            />
            <YAxis
              tick={{
                fill: "#5a6478",
                fontSize: 10,
                fontFamily: "var(--font-mono)",
              }}
              axisLine={false}
              tickLine={false}
            />
            <Tooltip
              content={({ active, payload, label }) => {
                if (!active || !payload?.length) return null;
                return (
                  <div
                    className="px-3 py-2 rounded-lg text-[11px]"
                    style={{
                      background: "var(--bg-elev)",
                      border: "1px solid var(--accent)",
                      fontFamily: "var(--font-mono)",
                    }}
                  >
                    <div
                      className="mb-1 font-medium"
                      style={{ color: "var(--text)" }}
                    >
                      {label}
                    </div>
                    {payload.map((p, i) => (
                      <div key={i} style={{ color: p.color }}>
                        {p.name === "bytes_scanned"
                          ? "Bytes"
                          : "Latency"}
                        : {p.value}
                        {p.name === "bytes_scanned" ? " TB" : " ms"}
                      </div>
                    ))}
                  </div>
                );
              }}
            />
            <Area
              type="monotone"
              dataKey="bytes_scanned"
              stroke="#7df9a9"
              strokeWidth={1.5}
              fill="url(#chartGradAccent)"
              dot={false}
            />
            <Area
              type="monotone"
              dataKey="avg_latency"
              stroke="#6ea8ff"
              strokeWidth={1.5}
              strokeDasharray="3 3"
              fill="url(#chartGradInfo)"
              dot={false}
            />
            {/* Applied change markers */}
            {appliedPoints.map((point, i) => (
              <ReferenceDot
                key={i}
                x={point.date}
                y={point.bytes_scanned}
                r={4}
                fill="#7df9a9"
                stroke="none"
              />
            ))}
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </section>
  );
}
