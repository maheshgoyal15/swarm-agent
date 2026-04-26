L"use client";

import { useState, useEffect } from "react";
import { mockActivityEvents } from "@/lib/mock-data";
import { ActivityEvent } from "@/lib/types";

export default function ActivityFeed() {
  const [events, setEvents] = useState<ActivityEvent[]>(mockActivityEvents);

  // SSE connection for live activity
  useEffect(() => {
    let es: EventSource | null = null;
    try {
      es = new EventSource(
        `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api"}/agents/stream`
      );
      es.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data.ts && data.agent) {
            const newEvent: ActivityEvent = {
              id: `act-${Date.now()}-${Math.random().toString(36).substring(2, 9)}`,
              timestamp: data.ts,
              agent: data.agent.toUpperCase(),
              content: data.details || data.action,
              dot_type:
                data.agent === "echo"
                  ? "info"
                  : data.agent === "codex"
                  ? "warn"
                  : "accent",
            };
            setEvents((prev) => {
              const updated = [newEvent, ...prev];
              return updated.slice(0, 50); // Cap at 50
            });
          }
        } catch {
          // ignore
        }
      };
      es.onerror = () => {
        es?.close();
      };
    } catch {
      // SSE not available
    }
    return () => es?.close();
  }, []);

  return (
    <section
      className="rounded-xl overflow-hidden stagger-6"
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
        <span
          className="text-[22px] tracking-tight"
          style={{ fontFamily: "var(--font-display)" }}
        >
          Live Activity
        </span>
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
          streaming
        </div>
      </div>

      {/* Activity items */}
      <div className="py-1 pb-3">
        {events.map((event, index) => (
          <div
            key={event.id}
            className="grid gap-3 items-start relative"
            style={{
              gridTemplateColumns: "60px 12px 1fr",
              padding: "10px 24px",
              animation:
                index === 0
                  ? "slideInUp 0.3s ease-out"
                  : undefined,
            }}
          >
            {/* Time */}
            <div
              className="text-right pt-0.5 text-[10px]"
              style={{
                fontFamily: "var(--font-mono)",
                color: "var(--text-dim)",
              }}
            >
              {event.timestamp}
            </div>

            {/* Marker */}
            <div className="relative h-full flex justify-center">
              {/* Vertical line */}
              <div
                className="absolute top-0 bottom-0 w-px"
                style={{ background: "var(--border)" }}
              />
              {/* Dot */}
              <div
                className="w-2 h-2 rounded-full mt-1 z-10"
                style={{
                  background:
                    event.dot_type === "warn"
                      ? "var(--warn)"
                      : event.dot_type === "info"
                      ? "var(--info)"
                      : "var(--accent)",
                  boxShadow: `0 0 0 3px var(--bg-elev)`,
                }}
              />
            </div>

            {/* Content */}
            <div
              className="text-[12px] leading-relaxed pb-1"
              style={{ color: "var(--text)" }}
            >
              <span
                className="mr-2 text-[10px] uppercase tracking-wide"
                style={{
                  fontFamily: "var(--font-mono)",
                  color: "var(--text-muted)",
                  letterSpacing: "0.08em",
                }}
              >
                {event.agent} →
              </span>
              {event.content}
              {event.highlight && (
                <>
                  {" "}
                  <em
                    className="not-italic text-[11px]"
                    style={{
                      color: "var(--accent)",
                      fontFamily: "var(--font-mono)",
                    }}
                  >
                    {event.highlight}
                  </em>
                </>
              )}
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}
