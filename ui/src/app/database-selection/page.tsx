"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { fetchJSON, postJSON } from "@/lib/api";

interface RegisteredDatabase {
  db_id: number | null;
  project_id: string;
  instance_id: string;
  database_name: string;
  db_type: string;
  target_schema: string;
  ip: string;
  status: string;
  created_at: string | null;
}

interface CurrentDatabase {
  host: string;
  port: number;
  database: string;
  target_schema: string;
  db_type: string;
  display: string;
}

export default function DatabaseSelectionPage() {
  const [currentDb, setCurrentDb] = useState<CurrentDatabase | null>(null);
  const [registered, setRegistered] = useState<RegisteredDatabase[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  // Form state for registering a new monitoring target
  const [form, setForm] = useState({
    instance_id: "",
    database_name: "",
    db_type: "postgresql",
    target_schema: "public",
    ip: "",
    project_id: "",
  });
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    async function load() {
      try {
        const [cur, regs] = await Promise.all([
          fetchJSON<CurrentDatabase>("/gcp/current-database"),
          fetchJSON<RegisteredDatabase[]>("/gcp/databases"),
        ]);
        setCurrentDb(cur);
        setRegistered(regs);
      } catch (err) {
        setError("Failed to load database info. Is the API running?");
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.instance_id || !form.database_name) {
      setError("Instance ID and database name are required.");
      return;
    }
    setSubmitting(true);
    setError(null);
    setSuccess(null);
    try {
      const result = await postJSON<{ status: string; db_id: number }>("/gcp/select-database", form);
      setSuccess(`Registered successfully (ID: ${result.db_id}). The agent will use this target on the next scan.`);
      // Refresh list
      const regs = await fetchJSON<RegisteredDatabase[]>("/gcp/databases");
      setRegistered(regs);
      setForm({ instance_id: "", database_name: "", db_type: "postgresql", target_schema: "public", ip: "", project_id: "" });
    } catch (err) {
      setError("Failed to register database. Check that the API is running.");
      console.error(err);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="relative z-[1] min-h-screen flex flex-col bg-[#0a0e16] text-[#e6e9f0]">
      <main className="flex-1 w-full mx-auto px-8 py-8" style={{ maxWidth: "1200px" }}>
        <div className="mb-8">
          <div className="mb-4">
            <Link
              href="/"
              className="text-[13px] hover:underline"
              style={{ color: "var(--accent)", fontFamily: "var(--font-mono)" }}
            >
              ← Back to Overview
            </Link>
          </div>
          <h1
            className="text-[42px] leading-none tracking-tight mb-3"
            style={{ fontFamily: "var(--font-display)" }}
          >
            Database{" "}
            <em style={{ fontStyle: "italic", color: "var(--accent)" }}>Selection</em>
          </h1>
          <p className="text-[14px]" style={{ color: "var(--text-muted)" }}>
            Manage monitoring targets for the EvoAgent swarm.
          </p>
        </div>

        {error && (
          <div className="mb-6 p-4 rounded-lg bg-[#ef5a6f]/20 border border-[#ef5a6f]/50 text-[#ef5a6f] text-[13px]">
            {error}
          </div>
        )}
        {success && (
          <div className="mb-6 p-4 rounded-lg bg-[#7df9a9]/10 border border-[#7df9a9]/30 text-[#7df9a9] text-[13px]">
            {success}
          </div>
        )}

        {/* Active connection (from env vars) */}
        <div className="mb-8">
          <h2
            className="text-[12px] uppercase tracking-wider mb-3"
            style={{ fontFamily: "var(--font-mono)", color: "var(--text-dim)" }}
          >
            Active Connection (from environment)
          </h2>
          {loading ? (
            <p className="text-[13px]" style={{ color: "var(--text-muted)" }}>Loading…</p>
          ) : currentDb ? (
            <div className="bg-[#131927] border border-[#7df9a9]/20 rounded-lg p-5">
              <div className="grid grid-cols-2 gap-4 text-[13px]" style={{ fontFamily: "var(--font-mono)" }}>
                <div>
                  <span style={{ color: "var(--text-dim)" }}>Host: </span>
                  <strong style={{ color: "var(--accent)" }}>{currentDb.host}:{currentDb.port}</strong>
                </div>
                <div>
                  <span style={{ color: "var(--text-dim)" }}>Database: </span>
                  <strong>{currentDb.database}</strong>
                </div>
                <div>
                  <span style={{ color: "var(--text-dim)" }}>Type: </span>
                  <strong>{currentDb.db_type.toUpperCase()}</strong>
                </div>
                <div>
                  <span style={{ color: "var(--text-dim)" }}>Target Schema: </span>
                  <strong style={{ color: "var(--accent)" }}>{currentDb.target_schema}</strong>
                </div>
              </div>
              <p className="mt-3 text-[11px]" style={{ color: "var(--text-dim)", fontFamily: "var(--font-mono)" }}>
                Configure via DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD, TARGET_SCHEMA environment variables.
              </p>
            </div>
          ) : (
            <p className="text-[13px]" style={{ color: "var(--text-muted)" }}>Unable to reach API.</p>
          )}
        </div>

        {/* Registered monitoring targets */}
        <div className="mb-8">
          <h2
            className="text-[12px] uppercase tracking-wider mb-3"
            style={{ fontFamily: "var(--font-mono)", color: "var(--text-dim)" }}
          >
            Registered Monitoring Targets
          </h2>
          {loading ? (
            <p className="text-[13px]" style={{ color: "var(--text-muted)" }}>Loading…</p>
          ) : registered.length === 0 ? (
            <p className="text-[13px]" style={{ color: "var(--text-muted)" }}>
              No targets registered yet. Use the form below to add one.
            </p>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {registered.map((db, i) => (
                <div
                  key={db.db_id ?? i}
                  className="bg-[#131927] border border-white/5 rounded-lg p-5 hover:border-[#7df9a9]/20 transition-colors"
                >
                  <div className="flex justify-between items-start mb-3">
                    <div>
                      <h3 className="text-[16px] font-semibold mb-1">{db.instance_id}</h3>
                      <p
                        className="text-[11px]"
                        style={{ color: "var(--text-muted)", fontFamily: "var(--font-mono)" }}
                      >
                        {db.db_type.toUpperCase()} · {db.database_name} · schema: {db.target_schema}
                      </p>
                    </div>
                    <span
                      className="text-[10px] uppercase tracking-wider px-2 py-1 rounded bg-[#7df9a9]/20 text-[#7df9a9]"
                      style={{ fontFamily: "var(--font-mono)" }}
                    >
                      {db.status}
                    </span>
                  </div>
                  {db.ip && (
                    <p
                      className="text-[12px] mb-1"
                      style={{ color: "var(--text-dim)", fontFamily: "var(--font-mono)" }}
                    >
                      IP: {db.ip}
                    </p>
                  )}
                  {db.created_at && (
                    <p className="text-[11px]" style={{ color: "var(--text-dim)", fontFamily: "var(--font-mono)" }}>
                      Registered: {new Date(db.created_at).toLocaleString()}
                    </p>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Register new monitoring target */}
        <div>
          <h2
            className="text-[12px] uppercase tracking-wider mb-3"
            style={{ fontFamily: "var(--font-mono)", color: "var(--text-dim)" }}
          >
            Register New Monitoring Target
          </h2>
          <form
            onSubmit={handleRegister}
            className="bg-[#131927] border border-white/5 rounded-lg p-6 grid grid-cols-1 md:grid-cols-2 gap-5"
          >
            <Field
              label="Instance ID / Hostname *"
              value={form.instance_id}
              placeholder="e.g. my-alloydb-instance or 10.0.0.1"
              onChange={(v) => setForm((f) => ({ ...f, instance_id: v }))}
            />
            <Field
              label="Database Name *"
              value={form.database_name}
              placeholder="e.g. postgres"
              onChange={(v) => setForm((f) => ({ ...f, database_name: v }))}
            />
            <div>
              <label
                className="block text-[11px] uppercase tracking-wider mb-1.5"
                style={{ fontFamily: "var(--font-mono)", color: "var(--text-dim)" }}
              >
                Database Type
              </label>
              <select
                value={form.db_type}
                onChange={(e) => setForm((f) => ({ ...f, db_type: e.target.value }))}
                className="w-full bg-[#0a0e16] border border-white/10 rounded-md p-2.5 text-[13px] text-[#e6e9f0]"
              >
                <option value="postgresql">PostgreSQL</option>
                <option value="alloydb">AlloyDB</option>
                <option value="spanner">Spanner</option>
                <option value="bigquery">BigQuery</option>
              </select>
            </div>
            <Field
              label="Target Schema"
              value={form.target_schema}
              placeholder="e.g. public"
              onChange={(v) => setForm((f) => ({ ...f, target_schema: v }))}
            />
            <Field
              label="IP Address (optional)"
              value={form.ip}
              placeholder="e.g. 10.0.0.2"
              onChange={(v) => setForm((f) => ({ ...f, ip: v }))}
            />
            <Field
              label="Project / Label (optional)"
              value={form.project_id}
              placeholder="e.g. my-gcp-project-id"
              onChange={(v) => setForm((f) => ({ ...f, project_id: v }))}
            />
            <div className="md:col-span-2">
              <button
                type="submit"
                disabled={submitting}
                className="w-full py-2.5 rounded-md text-[13px] font-semibold transition-colors"
                style={{
                  background: submitting ? "var(--text-dim)" : "var(--accent)",
                  color: "var(--bg)",
                  border: "none",
                  cursor: submitting ? "not-allowed" : "pointer",
                }}
              >
                {submitting ? "Registering…" : "Register Monitoring Target"}
              </button>
            </div>
          </form>
        </div>
      </main>
    </div>
  );
}

function Field({
  label,
  value,
  placeholder,
  onChange,
}: {
  label: string;
  value: string;
  placeholder?: string;
  onChange: (v: string) => void;
}) {
  return (
    <div>
      <label
        className="block text-[11px] uppercase tracking-wider mb-1.5"
        style={{ fontFamily: "var(--font-mono)", color: "var(--text-dim)" }}
      >
        {label}
      </label>
      <input
        type="text"
        value={value}
        placeholder={placeholder}
        onChange={(e) => onChange(e.target.value)}
        className="w-full bg-[#0a0e16] border border-white/10 rounded-md p-2.5 text-[13px] text-[#e6e9f0] placeholder-[#5a6478] outline-none focus:border-[#7df9a9]/40 transition-colors"
      />
    </div>
  );
}
