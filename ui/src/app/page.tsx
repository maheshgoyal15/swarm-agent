"use client";
import Topbar from "@/components/Topbar";
import Link from "next/link";
import { postJSON, fetchJSON } from "@/lib/api";
import { useState, useEffect } from "react";
import Hero from "@/components/Hero";
import StatsRow from "@/components/StatsRow";
import AgentSwarm from "@/components/AgentSwarm";
import RecommendationsFeed from "@/components/RecommendationsFeed";
import ImpactChart from "@/components/ImpactChart";
import ChatPanel from "@/components/ChatPanel";
import MemoryStats from "@/components/MemoryStats";
import ActivityFeed from "@/components/ActivityFeed";
import { SwarmStatus, CurrentDatabase } from "@/lib/types";

export default function Home() {
  const [scanning, setScanning] = useState(false);
  const [currentDb, setCurrentDb] = useState<CurrentDatabase | null>(null);
  const [cycleId, setCycleId] = useState<number | null>(null);

  useEffect(() => {
    fetchJSON<CurrentDatabase>("/gcp/current-database")
      .then(setCurrentDb)
      .catch(() => {});

    fetchJSON<SwarmStatus>("/swarm/status")
      .then((s) => setCycleId(s.cycle_id))
      .catch(() => {});
  }, []);

  const handleScan = async () => {
    setScanning(true);
    try {
      const res = await postJSON<{ status: string; cycle_id: number; target_schema: string }>("/scan", {});
      alert(`Scan triggered! Cycle #${res.cycle_id} — schema: ${res.target_schema}`);
      setCycleId(res.cycle_id);
    } catch (err) {
      console.error("Failed to trigger scan:", err);
      alert("Failed to trigger scan. Check that the API is running and the DB is reachable.");
    } finally {
      setTimeout(() => setScanning(false), 2000);
    }
  };

  const dbDisplay = currentDb
    ? `${currentDb.db_type.toUpperCase()} (${currentDb.display})`
    : "Connecting…";

  return (
    <div className="relative z-[1] min-h-screen flex flex-col">
      <Topbar />

      <main
        className="flex-1 w-full mx-auto px-8 py-8"
        style={{ maxWidth: "1640px" }}
      >
        <div className="flex flex-col gap-6">
          {/* Connection bar */}
          <div className="flex justify-between items-center p-4 bg-[#131927] border border-white/5 rounded-lg">
            <div className="text-[14px]">
              <span style={{ color: "var(--text-muted)" }}>Monitoring: </span>
              <span style={{ color: "var(--accent)", fontFamily: "var(--font-mono)" }}>
                {dbDisplay}
              </span>
              {currentDb && (
                <span
                  className="ml-2 text-[11px]"
                  style={{ color: "var(--text-dim)", fontFamily: "var(--font-mono)" }}
                >
                  schema: {currentDb.target_schema}
                </span>
              )}
              <Link
                href="/database-selection"
                className="ml-3 text-[12px] hover:underline"
                style={{ color: "var(--text-dim)" }}
              >
                (Change)
              </Link>
            </div>
            <button
              onClick={handleScan}
              disabled={scanning}
              className={`px-4 py-2 rounded-md text-[13px] font-medium transition-colors ${
                scanning
                  ? "bg-[#8a93a6] text-[#0a0e16] cursor-not-allowed"
                  : "bg-[#7df9a9] text-[#0a0e16] hover:bg-[#7df9a9]/80"
              }`}
            >
              {scanning ? "Scanning…" : "Scan Now"}
            </button>
          </div>

          <Hero />
          <StatsRow />

          {/* Two-column layout */}
          <div className="grid gap-6 grid-cols-1 xl:grid-cols-[1fr_360px]">
            {/* Left Column */}
            <div className="flex flex-col gap-6">
              <AgentSwarm />
              <div className="stagger-4">
                <RecommendationsFeed />
              </div>
              <ImpactChart />
            </div>

            {/* Right Column */}
            <div className="flex flex-col gap-6">
              <ChatPanel />
              <MemoryStats />
              <ActivityFeed />
            </div>
          </div>
        </div>

        {/* Footer */}
        <footer
          className="text-center py-4 mt-6"
          style={{
            fontFamily: "var(--font-mono)",
            fontSize: "10px",
            color: "var(--text-dim)",
            textTransform: "uppercase",
            letterSpacing: "0.15em",
            borderTop: "1px solid var(--border)",
          }}
        >
          EvoAgent{cycleId ? ` · Cycle #${cycleId.toLocaleString()}` : ""} · Powered by ADK + Vertex AI + MCP
        </footer>
      </main>
    </div>
  );
}
