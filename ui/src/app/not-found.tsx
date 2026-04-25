import Link from "next/link";

export default function NotFound() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center gap-6 relative z-[1]">
      {/* Brand mark */}
      <div className="relative">
        <div
          className="w-16 h-16 rounded-xl flex items-center justify-center font-semibold text-2xl"
          style={{
            fontFamily: "var(--font-mono)",
            background:
              "linear-gradient(135deg, var(--accent) 0%, #4d8c6b 100%)",
            color: "var(--bg)",
            boxShadow: "0 0 40px var(--accent-glow)",
          }}
        >
          E
        </div>
        <div
          className="absolute -inset-1 rounded-[14px]"
          style={{
            border: "1px solid var(--accent)",
            opacity: 0.3,
            animation: "pulse 2.5s ease-in-out infinite",
          }}
        />
      </div>

      <h1
        className="text-[42px] leading-none tracking-tight"
        style={{ fontFamily: "var(--font-display)" }}
      >
        This query returned{" "}
        <em style={{ fontStyle: "italic", color: "var(--accent)" }}>
          no results.
        </em>
      </h1>

      <p
        className="text-[13px]"
        style={{
          fontFamily: "var(--font-mono)",
          color: "var(--text-dim)",
          textTransform: "uppercase",
          letterSpacing: "0.1em",
        }}
      >
        404 · The requested resource was not found
      </p>

      <Link
        href="/"
        className="mt-4 px-5 py-2.5 rounded-md text-[13px] font-semibold transition-all duration-150 no-underline"
        style={{
          background: "var(--accent)",
          color: "var(--bg)",
          border: "1px solid var(--accent)",
          fontFamily: "var(--font-body)",
        }}
      >
        ← Back to Overview
      </Link>
    </div>
  );
}
