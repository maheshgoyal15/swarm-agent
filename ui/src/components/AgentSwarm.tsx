"use client";

import { useState, useEffect } from "react";
import { Agent } from "@/lib/types";
import { fetchJSON } from "@/lib/api";

const AGENT_DEFAULTS: Agent[] = [
  { id: 1, name: "// 01 — Analyzer",  role: "Sage",   codename: "sage",   status: "idle", task: "Idle", active: false },
  { id: 2, name: "// 02 — Optimizer", role: "Forge",  codename: "forge",  status: "idle", task: "Idle", active: false },
  { id: 3, name: "// 03 — Simulator", role: "Echo",   codename: "echo",   status: "idle", task: "Idle", active: false },
  { id: 4, name: "// 04 — Applier",   role: "Wright", codename: "wright", status: "idle", task: "Idle", active: false },
  { id: 5, name: "// 05 — Historian", role: "Codex",  codename: "codex",  status: "idle", task: "Idle", active: false },
];

export default function AgentSwarm() {
  const [agents, setAgents] = useState<Agent[]>(AGENT_DEFAULTS);
  const [pulsingId, setPulsingId] = useState<number | null>(null);
  const [fallbackPolling, setFallbackPolling] = useState(false);

  // Fetch initial state from DB
  useEffect(() => {
    fetchJSON<Agent[]>("/agents")
      .then(setAgents)
      .catch((err) => console.error("Failed to load agents:", err));
  }, []);

  // SSE: live updates per agent status change
  useEffect(() => {
    let es: EventSource | null = null;
    try {
      es = new EventSource(
        `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api"}/agents/stream`
      );
      es.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (!data.agent) return;

          setAgents((prev) => {
            const updated = prev.map((a) => {
              if (a.codename !== data.agent.toLowerCase()) return a;
              const active = data.status !== "awaiting approval" && data.status !== "idle";
              // Trigger pulse
              setPulsingId(a.id);
              setTimeout(() => setPulsingId(null), 1000);
              return { ...a, status: data.status, task: data.details, active };
            });
            return updated;
          });
        } catch {
          // ignore parse errors
        }
      };
      es.onerror = () => {
        console.warn("SSE failed in AgentSwarm, falling back to polling.");
        es?.close();
        setFallbackPolling(true);
      };
    } catch {
      console.warn("EventSource not available, falling back to polling.");
      setFallbackPolling(true);
    }
    return () => es?.close();
  }, []);

  // Fallback polling when SSE is unavailable
  useEffect(() => {
    if (!fallbackPolling) return;
    const interval = setInterval(() => {
      fetchJSON<Agent[]>("/agents")
        .then(setAgents)
        .catch((err) => console.error("Polling failed in AgentSwarm:", err));
    }, 3000);
    return () => clearInterval(interval);
  }, [fallbackPolling]);

  return (
    <section
      className="rounded-xl overflow-hidden stagger-3"
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
            The Swarm
          </span>
          <span
            className="text-[11px] uppercase tracking-widest"
            style={{
              fontFamily: "var(--font-mono)",
              color: "var(--text-dim)",
              letterSpacing: "0.1em",
            }}
          >
            · {agents.length} agents · A2A protocol
          </span>
        </div>
        <button
          className="px-3.5 py-[7px] rounded-md text-[12px] font-medium transition-all duration-150 cursor-pointer"
          style={{
            background: "transparent",
            border: "none",
            color: "var(--text-muted)",
            fontFamily: "var(--font-body)",
          }}
        >
          View graph →
        </button>
      </div>

      {/* Agent Grid */}
      <div
        className="grid gap-3 px-6 py-[18px]"
        style={{ gridTemplateColumns: "repeat(5, 1fr)" }}
      >
        {agents.map((agent) => (
          <div
            key={agent.id}
            className="relative overflow-hidden rounded-lg p-3.5 transition-all duration-300"
            style={{
              background: "var(--surface)",
              border: "1px solid var(--border)",
              animation:
                pulsingId === agent.id ? "cardPulse 0.6s ease-out" : undefined,
            }}
            onMouseEnter={(e) => {
              if (agent.active)
                (e.currentTarget as HTMLElement).style.boxShadow =
                  "0 0 16px 2px var(--accent-glow)";
            }}
            onMouseLeave={(e) => {
              (e.currentTarget as HTMLElement).style.boxShadow = "none";
            }}
          >
            {/* Top Bar */}
            <div
              className="absolute top-0 left-0 right-0 h-0.5"
              style={{
                background: agent.active ? "var(--accent)" : "var(--text-dim)",
                boxShadow: agent.active ? "0 0 8px var(--accent)" : "none",
              }}
            />

            {/* Agent Name */}
            <div
              className="mb-2 text-[10px] uppercase tracking-widest"
              style={{
                fontFamily: "var(--font-mono)",
                color: "var(--text-dim)",
                letterSpacing: "0.1em",
              }}
            >
              {agent.name}
            </div>

            {/* Agent Role */}
            <div
              className="mb-2.5 text-[18px] leading-tight"
              style={{ fontFamily: "var(--font-display)" }}
            >
              {agent.role}
            </div>

            {/* Status */}
            <div
              className="flex items-center gap-1.5 text-[10px]"
              style={{
                fontFamily: "var(--font-mono)",
                color: agent.active ? "var(--accent)" : "var(--text-dim)",
              }}
            >
              <span
                className="w-1 h-1 rounded-full"
                style={{
                  background: "currentColor",
                  animation: agent.active
                    ? "blink 1.5s ease-in-out infinite"
                    : undefined,
                }}
              />
              {agent.status}
            </div>

            {/* Task */}
            <div
              className="mt-2 text-[11px] leading-snug min-h-[30px]"
              style={{ color: "var(--text-muted)" }}
            >
              {agent.task}
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}
