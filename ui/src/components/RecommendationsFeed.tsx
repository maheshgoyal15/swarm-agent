"use client";

import { useState, useCallback, useEffect } from "react";
import confetti from "canvas-confetti";
import { Recommendation } from "@/lib/types";
import { fetchJSON } from "@/lib/api";

function highlightSQL(sql: string): string {
  const keywords = [
    "CREATE OR REPLACE TABLE",
    "PARTITION BY",
    "CLUSTER BY",
    "AS SELECT",
    "FROM",
    "DATE",
    "CREATE",
    "TABLE",
    "INDEX",
    "ON",
    "ALTER",
  ];
  let result = sql;
  // Highlight comments
  result = result.replace(
    /(--[^\n]*)/g,
    '<span style="color:var(--text-dim);font-style:italic">$1</span>'
  );
  // Highlight keywords
  keywords.forEach((kw) => {
    result = result.replace(
      new RegExp(`\\b${kw}\\b`, "gi"),
      `<span style="color:var(--accent)">${kw}</span>`
    );
  });
  // Highlight strings
  result = result.replace(
    /('[^']*')/g,
    '<span style="color:var(--warn)">$1</span>'
  );
  return result;
}

const actionLabels: Record<string, string> = {
  apply: "Apply",
  simulate: "Simulate",
  reject: "Reject",
  plan_migration: "Plan migration",
  schedule: "Schedule",
  review: "Review",
  snooze: "Snooze",
};

const actionStyles: Record<string, string> = {
  apply: "primary",
  schedule: "primary",
  simulate: "default",
  review: "default",
  plan_migration: "default",
  reject: "ghost",
  snooze: "ghost",
};

const iconSymbols: Record<string, string> = {
  cost: "$",
  perf: "⚡",
  warn: "!",
};

export default function RecommendationsFeed() {
  const [recs, setRecs] = useState<Recommendation[]>([]);
  const [applyingId, setApplyingId] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  const loadRecommendations = useCallback(async () => {
    try {
      const data = await fetchJSON<Recommendation[]>("/recommendations");
      setRecs(data);
    } catch (err) {
      console.error("Failed to load recommendations:", err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadRecommendations();
    
    // Auto-refresh every 10 seconds
    const interval = setInterval(loadRecommendations, 10000);
    return () => clearInterval(interval);
  }, [loadRecommendations]);

  const handleApply = useCallback(
    async (id: string, e: React.MouseEvent<HTMLButtonElement>) => {
      // Confetti from button
      const rect = e.currentTarget.getBoundingClientRect();
      confetti({
        particleCount: 40,
        spread: 60,
        origin: {
          x: (rect.left + rect.width / 2) / window.innerWidth,
          y: (rect.top + rect.height / 2) / window.innerHeight,
        },
        colors: ["#7df9a9", "#4ac788", "#a8ffc8"],
        gravity: 1.2,
        scalar: 0.8,
        ticks: 80,
      });

      setApplyingId(id);

      try {
        const res = await fetch(
          `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api"}/recommendations/${id}/apply`,
          { method: "POST" }
        );
        if (res.ok) {
          // Remove from list after brief delay
          setTimeout(() => {
            setRecs((prev) => prev.filter((r) => r.id !== id));
            setApplyingId(null);
          }, 800);
        }
      } catch {
        // Optimistic: still remove
        setTimeout(() => {
          setRecs((prev) => prev.filter((r) => r.id !== id));
          setApplyingId(null);
        }, 800);
      }
    },
    []
  );

  const handleReject = useCallback(async (id: string) => {
    try {
      await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api"}/recommendations/${id}/reject`,
        { method: "POST" }
      );
      setRecs((prev) => prev.filter((r) => r.id !== id));
    } catch (err) {
      console.error("Failed to reject:", err);
      // Still remove optimistically
      setRecs((prev) => prev.filter((r) => r.id !== id));
    }
  }, []);

  if (loading && recs.length === 0) {
    return (
      <div className="px-6 py-16 text-center">
        <p style={{ color: "var(--text-muted)" }}>Loading recommendations...</p>
      </div>
    );
  }

  if (recs.length === 0) {
    return (
      <section
        className="rounded-xl overflow-hidden"
        style={{
          background: "var(--bg-elev)",
          border: "1px solid var(--border)",
        }}
      >
        <div
          className="flex items-center justify-between px-6 py-[18px]"
          style={{ borderBottom: "1px solid var(--border)" }}
        >
          <div className="flex items-center gap-2.5">
            <span
              className="text-[22px] tracking-tight"
              style={{ fontFamily: "var(--font-display)" }}
            >
              Pending Recommendations
            </span>
          </div>
        </div>
        <div className="px-6 py-16 text-center">
          <div
            className="text-[15px] mb-2"
            style={{ color: "var(--text-muted)" }}
          >
            Sage is still analyzing… no patterns surfaced yet.
          </div>
          <div
            className="h-1 rounded-full mx-auto max-w-[200px]"
            style={{
              background:
                "linear-gradient(90deg, transparent, var(--accent-glow), transparent)",
              backgroundSize: "200% 100%",
              animation: "scanning 2s linear infinite",
            }}
          />
        </div>
      </section>
    );
  }

  return (
    <section
      className="rounded-xl overflow-hidden"
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
            Pending Recommendations
          </span>
          <span
            className="px-2 py-0.5 rounded text-[10px] font-medium"
            style={{
              background: "var(--accent-glow)",
              color: "var(--accent)",
              fontFamily: "var(--font-mono)",
            }}
          >
            {recs.length} new
          </span>
        </div>
        <div className="flex gap-2">
          <button
            className="px-3.5 py-[7px] rounded-md text-[12px] font-medium transition-all duration-150 cursor-pointer"
            style={{
              background: "transparent",
              border: "none",
              color: "var(--text-muted)",
            }}
          >
            Filter
          </button>
          <button
            className="px-3.5 py-[7px] rounded-md text-[12px] font-medium transition-all duration-150 cursor-pointer"
            style={{
              background: "transparent",
              border: "none",
              color: "var(--text-muted)",
            }}
          >
            Sort: Impact ↓
          </button>
        </div>
      </div>

      {/* Recommendations List */}
      <div className="flex flex-col">
        {recs.map((rec) => (
          <article
            key={rec.id}
            className="grid gap-[18px] items-start transition-colors duration-150 cursor-pointer"
            style={{
              gridTemplateColumns: "auto 1fr auto",
              padding: "22px 24px",
              borderBottom: "1px solid var(--border)",
            }}
            onMouseEnter={(e) => {
              (e.currentTarget as HTMLElement).style.background = "var(--surface)";
            }}
            onMouseLeave={(e) => {
              (e.currentTarget as HTMLElement).style.background = "transparent";
            }}
          >
            {/* Icon */}
            <div
              className="w-10 h-10 rounded-lg flex items-center justify-center font-semibold text-sm shrink-0"
              style={{
                fontFamily: "var(--font-mono)",
                background:
                  rec.icon_type === "cost"
                    ? "var(--accent-glow)"
                    : rec.icon_type === "perf"
                    ? "var(--info-dim)"
                    : "var(--warn-dim)",
                color:
                  rec.icon_type === "cost"
                    ? "var(--accent)"
                    : rec.icon_type === "perf"
                    ? "var(--info)"
                    : "var(--warn)",
              }}
            >
              {iconSymbols[rec.icon_type]}
            </div>

            {/* Content */}
            <div className="min-w-0">
              {/* Meta */}
              <div
                className="flex items-center gap-2.5 mb-1.5 text-[10px] uppercase tracking-wide"
                style={{
                  fontFamily: "var(--font-mono)",
                  color: "var(--text-dim)",
                  letterSpacing: "0.08em",
                }}
              >
                <span>{rec.database_type}</span>
                <span
                  className="w-[3px] h-[3px] rounded-full"
                  style={{ background: "var(--text-dim)" }}
                />
                <span>{rec.recommendation_type}</span>
                <span
                  className="w-[3px] h-[3px] rounded-full"
                  style={{ background: "var(--text-dim)" }}
                />
                <span>{rec.agents}</span>
                <span
                  className="w-[3px] h-[3px] rounded-full"
                  style={{ background: "var(--text-dim)" }}
                />
                <span
                  className="px-[7px] py-0.5 rounded text-[10px] uppercase tracking-wide font-medium"
                  style={{
                    background:
                      rec.severity === "high"
                        ? "var(--critical-dim)"
                        : rec.severity === "medium"
                        ? "var(--warn-dim)"
                        : "var(--info-dim)",
                    color:
                      rec.severity === "high"
                        ? "var(--critical)"
                        : rec.severity === "medium"
                        ? "var(--warn)"
                        : "var(--info)",
                    letterSpacing: "0.06em",
                  }}
                >
                  {rec.severity === "high"
                    ? "High Impact"
                    : rec.severity === "medium"
                    ? "Medium Impact"
                    : "Low Impact"}
                </span>
              </div>

              {/* Title */}
              <div
                className="text-[15px] font-semibold mb-1.5 leading-snug"
                style={{ color: "var(--text)" }}
                dangerouslySetInnerHTML={{
                  __html: rec.title.replace(
                    /<code>(.*?)<\/code>/g,
                    '<code style="font-family:var(--font-mono);font-size:12px;background:var(--surface);padding:1px 5px;border-radius:3px;color:var(--accent)">$1</code>'
                  ),
                }}
              />

              {/* Target */}
              <div
                className="inline-block mb-2.5 px-1.5 py-0.5 rounded text-[11px]"
                style={{
                  fontFamily: "var(--font-mono)",
                  color: "var(--accent)",
                  background: "rgba(125,249,169,0.06)",
                }}
              >
                {rec.target}
              </div>

              {/* Description */}
              <div
                className="text-[13px] leading-relaxed mb-3"
                style={{ color: "var(--text-muted)" }}
              >
                {rec.description}
              </div>

              {/* SQL Block */}
              {rec.sql && (
                <div
                  className="mb-3 p-2.5 rounded-md text-[11px] leading-relaxed overflow-x-auto"
                  style={{
                    fontFamily: "var(--font-mono)",
                    background: "var(--bg)",
                    border: "1px solid var(--border)",
                    color: "var(--text-muted)",
                  }}
                  dangerouslySetInnerHTML={{
                    __html: highlightSQL(rec.sql).replace(/\n/g, "<br/>"),
                  }}
                />
              )}

              {/* Impact */}
              <div
                className="flex gap-5 text-[11px]"
                style={{ fontFamily: "var(--font-mono)" }}
              >
                {rec.impact.map((imp, i) => (
                  <span key={i} style={{ color: "var(--text-dim)" }}>
                    {imp.label}:{" "}
                    <strong
                      style={{
                        fontWeight: 500,
                        color: imp.positive
                          ? "var(--accent)"
                          : imp.value === "medium"
                          ? "var(--warn)"
                          : imp.value === "high"
                          ? "var(--critical)"
                          : "var(--critical)",
                      }}
                    >
                      {imp.value}
                    </strong>
                  </span>
                ))}
              </div>
            </div>

            {/* Actions */}
            <div className="flex flex-col gap-1.5 items-end">
              {rec.actions.map((action) => (
                <button
                  key={action}
                  className="px-3.5 py-[7px] rounded-md text-[12px] font-medium transition-all duration-150 cursor-pointer whitespace-nowrap"
                  style={{
                    fontFamily: "var(--font-body)",
                    ...(actionStyles[action] === "primary"
                      ? {
                          background:
                            applyingId === rec.id
                              ? "var(--accent-dim)"
                              : "var(--accent)",
                          color: "var(--bg)",
                          border: "1px solid var(--accent)",
                          fontWeight: 600,
                        }
                      : actionStyles[action] === "ghost"
                      ? {
                          background: "transparent",
                          border: "1px solid transparent",
                          color: "var(--text-muted)",
                        }
                      : {
                          background: "var(--surface)",
                          border: "1px solid var(--border-strong)",
                          color: "var(--text)",
                        }),
                  }}
                  onClick={(e) => {
                    if (action === "apply" || action === "schedule") {
                      handleApply(rec.id, e);
                    } else if (action === "reject" || action === "snooze") {
                      handleReject(rec.id);
                    }
                  }}
                  disabled={applyingId === rec.id}
                >
                  {applyingId === rec.id &&
                  (action === "apply" || action === "schedule")
                    ? "Applying..."
                    : actionLabels[action]}
                </button>
              ))}
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}
