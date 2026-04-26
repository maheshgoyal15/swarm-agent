-- Schema for EvoAgent Operational State
CREATE SCHEMA IF NOT EXISTS evo_state;

-- Tracks databases selected for monitoring
CREATE TABLE IF NOT EXISTS evo_state.monitored_databases (
  db_id SERIAL PRIMARY KEY,
  project_id TEXT NOT NULL,
  instance_id TEXT NOT NULL,
  database_name TEXT NOT NULL,
  db_type TEXT NOT NULL,                  -- 'alloydb' | 'spanner' | 'bigquery'
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Tracks every cycle the swarm runs
CREATE TABLE IF NOT EXISTS evo_state.evo_cycles (
  cycle_id SERIAL PRIMARY KEY,
  db_id INT REFERENCES evo_state.monitored_databases(db_id),
  started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  ended_at TIMESTAMPTZ,
  status TEXT CHECK (status IN ('running','succeeded','failed','aborted')),
  recommendations_generated INT DEFAULT 0
);

-- Each recommendation produced by the swarm
CREATE TABLE IF NOT EXISTS evo_state.recommendations (
  rec_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  cycle_id INT REFERENCES evo_state.evo_cycles(cycle_id),
  target_resource TEXT NOT NULL,      -- fully qualified table/index name
  recommendation_type TEXT,           -- 'partition'|'cluster'|'index'|'denormalize'
  severity TEXT,                      -- 'high'|'medium'|'low'
  rationale TEXT NOT NULL,
  generated_sql TEXT,
  status TEXT DEFAULT 'pending',      -- 'pending'|'approved'|'applied'|'rejected'
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Audit log of every applied change
CREATE TABLE IF NOT EXISTS evo_state.applied_changes (
  change_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  rec_id UUID REFERENCES evo_state.recommendations(rec_id),
  applied_at TIMESTAMPTZ DEFAULT NOW(),
  applied_sql TEXT NOT NULL,
  status TEXT DEFAULT 'applied'       -- 'applied'|'failed'
);
