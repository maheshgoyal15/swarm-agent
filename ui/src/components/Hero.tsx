export default function Hero() {
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
          Coordinator · Cycle #1,247 · Started 04:00 UTC
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
          WORKLOAD ·{" "}
          <strong style={{ color: "var(--text)", fontWeight: 500 }}>
            analytics-prod
          </strong>
        </div>
        <div>
          REGION ·{" "}
          <strong style={{ color: "var(--text)", fontWeight: 500 }}>
            us-central1
          </strong>
        </div>
        <div>
          DATABASES ·{" "}
          <strong style={{ color: "var(--text)", fontWeight: 500 }}>
            BigQuery, AlloyDB, Spanner
          </strong>
        </div>
      </div>
    </section>
  );
}
