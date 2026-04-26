"use client";

import { useState, useEffect } from "react";
import { fetchJSON } from "@/lib/api";
import { SwarmStatus, CurrentDatabase } from "@/lib/types";

export default function Hero() {
  const [swarm, setSwarm] = useState<SwarmStatus | null>(null);
  const [db, setDb] = useState<CurrentDatabase | null>(null);

  useEffect(() => {
    fetchJSON<SwarmStatus>("/swarm/status")
      .then(setSwarm)
      .catch(() => {});

    fetchJSON<CurrentDatabase>("/gcp/current-database")
      .then(setDb)
      .catch(() => {});
  }, []);

  const cycleLabel = swarm
    ? `Cycle #${swarm.cycle_id.toLocaleString()}`
    : "Cycle —";

  const dbLabel = db
    ? `${db.db_type.toUpperCase()} (${db.host}:${db.port}/${db.database})`
    : "—";

  const schemaLabel = db?.target_schema || "—";

  return (
    <section className="flex items-end justify-between mb-2 stagger-1">
      <div>
        <h1
          className="text-[56px] leading-none tracking-tight font-normal"
          style={{ fontFamily: "var(--font-display)", letterSpacing: "-0.02em" }}
        >
          Your data estate,{" "}
          <em style={{ fontStyle: "italic", color: "var(--accent)" }}>
            self-tuning.
          </em>
        </h1>
        <div
          className="mt-3 text-[12px] uppercase tracking-widest"
          style={{
            fontFamily: "var(--font-mono)",
            color: "var(--text-dim)",
            letterSpacing: "0.1em",
          }}
        >
          Coordinator · {cycleLabel} · {swarm?.active ? "Running" : "Idle"}
        </div>
      </div>
      <div
        className="text-right leading-[1.8]"
        style={{
          fontFamily: "var(--font-mono)",
          fontSize: "11px",
          color: "var(--text-dim)",
        }}
      >
        <div>
          DATABASE ·{" "}
          <strong style={{ color: "var(--text)", fontWeight: 500 }}>
            {dbLabel}
          </strong>
        </div>
        <div>
          TARGET SCHEMA ·{" "}
          <strong style={{ color: "var(--text)", fontWeight: 500 }}>
            {schemaLabel}
          </strong>
        </div>
        <div>
          AGENTS ·{" "}
          <strong style={{ color: "var(--text)", fontWeight: 500 }}>
            {swarm ? `${swarm.agentCount} active` : "—"}
          </strong>
        </div>
      </div>
    </section>
  );
}
