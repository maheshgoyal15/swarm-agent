import Topbar from "@/components/Topbar";
import RecommendationsFeed from "@/components/RecommendationsFeed";
import { AlertCircle } from "lucide-react";

export default function RecommendationsPage() {
  return (
    <div className="relative z-[1] min-h-screen flex flex-col">
      <Topbar />

      <main
        className="flex-1 w-full mx-auto px-8 py-8"
        style={{ maxWidth: "1200px" }}
      >
        <div className="mb-8">
          <h1
            className="text-[42px] leading-none tracking-tight mb-3"
            style={{ fontFamily: "var(--font-display)" }}
          >
            Human-in-the-Loop <em style={{ fontStyle: "italic", color: "var(--accent)" }}>Approval Queue</em>
          </h1>
          <p className="text-[14px]" style={{ color: "var(--text-muted)" }}>
            Review, simulate, and approve database optimizations identified by the swarm. Changing the database requires explicit manual approval.
          </p>
          
          <div 
            className="mt-6 p-4 rounded-lg flex items-start gap-3"
            style={{ 
              background: "var(--warn-dim)", 
              border: "1px solid rgba(251, 191, 36, 0.2)",
            }}
          >
            <AlertCircle size={18} style={{ color: "var(--warn)", marginTop: "2px" }} />
            <div>
              <div className="text-[13px] font-semibold mb-1" style={{ color: "var(--warn)" }}>
                Strict Manual Intervention Policy
              </div>
              <div className="text-[13px] leading-relaxed" style={{ color: "var(--text-muted)" }}>
                The EvoAgent swarm is configured to assess, simulate, and propose schema changes and index optimizations. 
                However, no DDL statements will be executed against production databases without explicit authorization from an engineer on this page.
              </div>
            </div>
          </div>
        </div>

        <div className="stagger-2">
          <RecommendationsFeed />
        </div>

      </main>

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
        EvoAgent · Human Approval Gate
      </footer>
    </div>
  );
}
