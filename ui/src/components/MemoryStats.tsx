import { mockKnowledgeStats } from "@/lib/mock-data";

export default function MemoryStats() {
  const stats = mockKnowledgeStats;

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
        <div>
          <div
            className="mb-1.5 text-[10px] uppercase tracking-widest"
            style={{
              fontFamily: "var(--font-mono)",
              color: "var(--text-dim)",
              letterSpacing: "0.1em",
            }}
          >
            Decisions logged
          </div>
          <div
            className="leading-none"
            style={{
              fontFamily: "var(--font-display)",
              fontSize: "26px",
            }}
          >
            {stats.decisions_logged.toLocaleString()}
          </div>
        </div>

        <div>
          <div
            className="mb-1.5 text-[10px] uppercase tracking-widest"
            style={{
              fontFamily: "var(--font-mono)",
              color: "var(--text-dim)",
              letterSpacing: "0.1em",
            }}
          >
            Patterns learned
          </div>
          <div
            className="leading-none"
            style={{
              fontFamily: "var(--font-display)",
              fontSize: "26px",
            }}
          >
            {stats.patterns_learned}
          </div>
        </div>

        <div>
          <div
            className="mb-1.5 text-[10px] uppercase tracking-widest"
            style={{
              fontFamily: "var(--font-mono)",
              color: "var(--text-dim)",
              letterSpacing: "0.1em",
            }}
          >
            Rollbacks · 90d
          </div>
          <div
            className="leading-none"
            style={{
              fontFamily: "var(--font-display)",
              fontSize: "26px",
              color: "var(--warn)",
            }}
          >
            {stats.rollbacks_90d}
          </div>
        </div>

        <div>
          <div
            className="mb-1.5 text-[10px] uppercase tracking-widest"
            style={{
              fontFamily: "var(--font-mono)",
              color: "var(--text-dim)",
              letterSpacing: "0.1em",
            }}
          >
            Confidence avg
          </div>
          <div
            className="leading-none"
            style={{
              fontFamily: "var(--font-display)",
              fontSize: "26px",
              color: "var(--accent)",
            }}
          >
            {stats.confidence_avg}
            <span
              className="text-sm"
              style={{ color: "var(--text-muted)" }}
            >
              %
            </span>
          </div>
        </div>
      </div>
    </section>
  );
}
