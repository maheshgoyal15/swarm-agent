import Topbar from "@/components/Topbar";
import Hero from "@/components/Hero";
import StatsRow from "@/components/StatsRow";
import AgentSwarm from "@/components/AgentSwarm";
import RecommendationsFeed from "@/components/RecommendationsFeed";
import ImpactChart from "@/components/ImpactChart";
import ChatPanel from "@/components/ChatPanel";
import MemoryStats from "@/components/MemoryStats";
import ActivityFeed from "@/components/ActivityFeed";

export default function Home() {
  return (
    <div className="relative z-[1] min-h-screen flex flex-col">
      <Topbar />

      <main
        className="flex-1 w-full mx-auto px-8 py-8"
        style={{ maxWidth: "1640px" }}
      >
        {/* Full-width sections */}
        <div className="flex flex-col gap-6">
          <Hero />
          <StatsRow />

          {/* Two-column layout */}
          <div
            className="grid gap-6 grid-cols-1 xl:grid-cols-[1fr_360px]"
          >
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
          EvoAgent · Cycle #1247 · Next scheduled run 25.04 · 04:00 UTC ·
          Powered by ADK + Vertex AI + MCP
        </footer>
      </main>

    </div>
  );
}
