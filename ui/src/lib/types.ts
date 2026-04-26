// ============== Agent Types ==============
export interface Agent {
  id: number;
  name: string;
  role: string;
  codename: string;
  status: "analyzing" | "planning" | "dry-run" | "awaiting approval" | "indexing" | "idle";
  task: string;
  active: boolean;
}

// ============== Recommendation Types ==============
export interface Recommendation {
  id: string;
  database_type: string;
  recommendation_type: string;
  agents: string;
  severity: "high" | "medium" | "low";
  title: string;
  target: string;
  description: string;
  sql?: string;
  impact: Impact[];
  icon_type: "cost" | "perf" | "warn";
  actions: ActionType[];
}

export interface Impact {
  label: string;
  value: string;
  positive: boolean;
}

export type ActionType = "apply" | "simulate" | "reject" | "plan_migration" | "schedule" | "review" | "snooze";

// ============== Metrics Types ==============
export interface OptimizationScore {
  score: number;
  grade: string;
  trend: string;
  description: string;
  cost_saved: number;
  cost_trend: string;
  speedup: number;
  speedup_trend: string;
  pending: number;
  pending_high: number;
}

export interface ImpactDataPoint {
  date: string;
  bytes_scanned: number;
  avg_latency: number;
  applied?: boolean;
}

// ============== Chat Types ==============
export interface ChatMessage {
  id: string;
  role: "user" | "ai";
  content: string;
  reasoning?: string;
}

// ============== Activity Types ==============
export interface ActivityEvent {
  id: string;
  timestamp: string;
  agent: string;
  content: string;
  dot_type: "accent" | "warn" | "info";
  highlight?: string;
}

// ============== Swarm Status ==============
export interface SwarmStatus {
  active: boolean;
  agentCount: number;
  cycle_id: number;
}

// ============== Current Database (from env-var connection) ==============
export interface CurrentDatabase {
  host: string;
  port: number;
  database: string;
  user: string;
  target_schema: string;
  db_type: string;
  display: string;
}

// ============== Knowledge Stats ==============
export interface KnowledgeStats {
  decisions_logged: number;
  patterns_learned: number;
  rollbacks_90d: number;
  confidence_avg: number;
}
