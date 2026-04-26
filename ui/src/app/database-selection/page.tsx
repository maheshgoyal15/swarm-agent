"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { fetchJSON, postJSON } from "@/lib/api";

interface Project {
  id: string;
  name: string;
}

interface Database {
  project_id: string;
  instance_id: string;
  database_name: string;
  db_type: string;
  ip?: string;
  status: string;
}

export default function DatabaseSelectionPage() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [databases, setDatabases] = useState<Database[]>([]);
  const [selectedProject, setSelectedProject] = useState<string>("");
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadProjects() {
      try {
        const data = await fetchJSON<Project[]>("/gcp/projects");
        setProjects(data);
        if (data.length > 0) {
          setSelectedProject(data[0].id);
        }
      } catch (err) {
        console.error("Failed to load projects:", err);
        setError("Failed to load projects. Is the API running?");
      }
    }
    loadProjects();
  }, []);

  useEffect(() => {
    async function loadDatabases() {
      if (!selectedProject) return;
      setLoading(true);
      try {
        const data = await fetchJSON<Database[]>(`/gcp/databases?project_id=${selectedProject}`);
        setDatabases(data);
      } catch (err) {
        console.error("Failed to load databases:", err);
        setError("Failed to load databases.");
      } finally {
        setLoading(false);
      }
    }
    loadDatabases();
  }, [selectedProject]);

  const handleSelect = async (db: Database) => {
    try {
      const result = await postJSON<{ status: string; db_id: number }>("/gcp/select-database", {
        project_id: db.project_id,
        instance_id: db.instance_id,
        database_name: db.database_name,
        db_type: db.db_type,
      });
      alert(`Database selected successfully! ID: ${result.db_id}`);
      // Redirect or update state
    } catch (err) {
      console.error("Failed to select database:", err);
      alert("Failed to select database.");
    }
  };

  return (
    <div className="relative z-[1] min-h-screen flex flex-col bg-[#0a0e16] text-[#e6e9f0]">
      <main className="flex-1 w-full mx-auto px-8 py-8" style={{ maxWidth: "1200px" }}>
        <div className="mb-8">
          <div className="mb-4">
            <Link href="/" className="text-[13px] hover:underline" style={{ color: "var(--accent)", fontFamily: "var(--font-mono)" }}>
              ← Back to Overview
            </Link>
          </div>
          <h1 className="text-[42px] leading-none tracking-tight mb-3" style={{ fontFamily: "var(--font-display)" }}>
            Database <em style={{ fontStyle: "italic", color: "var(--accent)" }}>Selection</em>
          </h1>
          <p className="text-[14px]" style={{ color: "var(--text-muted)" }}>
            Select a GCP project and database instance to monitor and optimize.
          </p>
        </div>

        {error && (
          <div className="mb-6 p-4 rounded-lg bg-[#ef5a6f]/20 border border-[#ef5a6f]/50 text-[#ef5a6f]">
            {error}
          </div>
        )}

        <div className="mb-6">
          <label className="block text-[12px] uppercase tracking-wider mb-2" style={{ fontFamily: "var(--font-mono)", color: "var(--text-dim)" }}>
            Select Project
          </label>
          <select
            value={selectedProject}
            onChange={(e) => setSelectedProject(e.target.value)}
            className="w-full max-w-md bg-[#131927] border border-white/5 rounded-md p-3 text-[14px]"
          >
            {projects.map((p) => (
              <option key={p.id} value={p.id}>
                {p.name} ({p.id})
              </option>
            ))}
          </select>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {loading ? (
            <p className="text-[14px]" style={{ color: "var(--text-muted)" }}>Loading databases...</p>
          ) : (
            databases.map((db) => (
              <div
                key={db.instance_id}
                className="bg-[#131927] border border-white/5 rounded-lg p-6 hover:border-[#7df9a9]/20 transition-colors"
              >
                <div className="flex justify-between items-start mb-4">
                  <div>
                    <h3 className="text-[18px] font-semibold mb-1">{db.instance_id}</h3>
                    <p className="text-[12px]" style={{ color: "var(--text-muted)", fontFamily: "var(--font-mono)" }}>
                      {db.db_type.toUpperCase()} • {db.database_name}
                    </p>
                  </div>
                  <span
                    className={`text-[10px] uppercase tracking-wider px-2 py-1 rounded ${
                      db.status === "connected" ? "bg-[#7df9a9]/20 text-[#7df9a9]" : "bg-[#8a93a6]/20 text-[#8a93a6]"
                    }`}
                    style={{ fontFamily: "var(--font-mono)" }}
                  >
                    {db.status}
                  </span>
                </div>
                {db.ip && (
                  <p className="text-[13px] mb-4" style={{ color: "var(--text-dim)", fontFamily: "var(--font-mono)" }}>
                    IP: {db.ip}
                  </p>
                )}
                <button
                  onClick={() => handleSelect(db)}
                  className="w-full bg-[#131927] border border-[#7df9a9]/50 text-[#7df9a9] hover:bg-[#7df9a9]/10 py-2 rounded-md text-[13px] font-medium transition-colors"
                >
                  Select Database
                </button>
              </div>
            ))
          )}
        </div>
      </main>
    </div>
  );
}
