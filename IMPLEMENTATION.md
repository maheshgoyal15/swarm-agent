# EvoAgent — Implementation Blueprint

**Self-Evolving Database Schema & Query Optimizer Agent**
A production-grade multi-agent system on Google Cloud, built with ADK + MCP + Vertex AI.

---

## 1. The Five Agents (Personalities & Roles)

Giving each agent a distinct name + persona makes the UI more memorable and helps when debugging multi-agent traces.

| # | Name | Role | Primary Job | Key Tools |
|---|------|------|-------------|-----------|
| 01 | **Sage** | Analyzer | Reads telemetry, detects patterns, identifies opportunities | `bigquery_query`, `info_schema_reader`, `embedding_generator` |
| 02 | **Forge** | Optimizer | Generates DDL/DML candidates with rationale | `ddl_generator`, `cost_model`, `best_practice_kb` |
| 03 | **Echo** | Simulator | Validates changes in shadow environment | `dry_run`, `clone_table`, `query_replay` |
| 04 | **Wright** | Applier | Executes approved changes safely | `ddl_executor`, `rollback_manager`, `migration_runner` |
| 05 | **Codex** | Historian | Records decisions, builds knowledge graph | `graph_writer`, `vector_index`, `decision_log` |

The **Coordinator** is unnamed — it's the "brain stem" that orchestrates the loop.

---

## 2. Project Structure

```
db-evoagent/
├── agents/
│   ├── coordinator/
│   │   ├── agent.py              # ADK Coordinator agent
│   │   ├── prompts.py            # System prompts
│   │   └── workflow.py           # Cycle orchestration
│   ├── sage/                     # Analyzer
│   │   ├── agent.py
│   │   ├── tools.py              # BigQuery telemetry tools
│   │   └── pattern_detector.py
│   ├── forge/                    # Optimizer
│   │   ├── agent.py
│   │   ├── ddl_generator.py
│   │   └── cost_model.py
│   ├── echo/                     # Simulator
│   │   ├── agent.py
│   │   └── shadow_runner.py
│   ├── wright/                   # Applier
│   │   ├── agent.py
│   │   └── safe_executor.py
│   └── codex/                    # Historian
│       ├── agent.py
│       └── graph_store.py
│
├── mcp/
│   ├── bigquery_mcp.py           # Wrapper around managed MCP
│   ├── alloydb_mcp.py
│   ├── spanner_mcp.py
│   └── custom_tools/
│       ├── telemetry_mcp.py      # Cloud Operations Suite
│       └── cost_mcp.py           # Billing / cost data
│
├── memory/
│   ├── schema.sql                # AlloyDB schema for state
│   ├── graph_schema.cypher       # Knowledge graph schema
│   └── embeddings.py             # Vector store interface
│
├── api/
│   ├── main.py                   # FastAPI backend
│   ├── routes/
│   │   ├── recommendations.py
│   │   ├── agents.py
│   │   ├── chat.py
│   │   └── audit.py
│   └── websocket.py              # Live activity stream
│
├── ui/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Topbar.tsx
│   │   │   ├── Hero.tsx
│   │   │   ├── StatsRow.tsx
│   │   │   ├── AgentSwarm.tsx
│   │   │   ├── RecommendationCard.tsx
│   │   │   ├── ImpactChart.tsx
│   │   │   ├── ChatPanel.tsx
│   │   │   └── ActivityFeed.tsx
│   │   ├── pages/
│   │   │   ├── Overview.tsx
│   │   │   ├── Recommendations.tsx
│   │   │   ├── Agents.tsx
│   │   │   ├── Knowledge.tsx
│   │   │   └── Audit.tsx
│   │   ├── hooks/
│   │   │   ├── useRecommendations.ts
│   │   │   └── useAgentStream.ts
│   │   └── lib/
│   │       ├── api.ts
│   │       └── theme.ts
│   ├── public/
│   └── package.json
│
├── infra/
│   ├── terraform/
│   │   ├── vertex.tf             # Agent Engine
│   │   ├── alloydb.tf
│   │   ├── bigquery.tf
│   │   ├── workflows.tf
│   │   └── iam.tf                # Least-privilege roles
│   ├── cloudbuild.yaml
│   └── docker/
│       ├── coordinator.Dockerfile
│       └── api.Dockerfile
│
├── tests/
│   ├── agents/
│   ├── mcp/
│   └── e2e/
│
└── README.md
```

---

## 3. Tech Stack Summary

| Layer | Choice | Why |
|-------|--------|-----|
| Agent runtime | Vertex AI Agent Engine + ADK (Python) | Managed, autoscaling, native A2A protocol |
| LLM | Gemini 2.5 Pro (reasoning) + Gemini Flash (pattern matching) | Cost/latency split |
| Data access | Managed MCP (BigQuery, AlloyDB, Spanner) + custom MCP on Cloud Run | Standardized tool layer |
| State store | AlloyDB (operational state) + BigQuery (telemetry / logs) | Best-in-class for each workload |
| Vector store | AlloyDB ScaNN extension OR BigQuery vector search | Pattern similarity matching |
| Graph store | BigQuery property graphs OR Neo4j Aura via MCP | Decision lineage |
| Orchestration | Cloud Workflows + Cloud Scheduler | Reliable loop execution + approval gates |
| API | FastAPI on Cloud Run | Fast, typed, easy WebSocket support |
| Frontend | Next.js 14 (App Router) + Tailwind + shadcn/ui + Recharts | Production patterns |
| Real-time | Server-Sent Events (SSE) for agent activity stream | Simpler than WebSockets, perfect fit |
| Auth | Identity Platform / Workload Identity | Standard GCP auth |
| Observability | Cloud Trace + custom agent-decision logging | Track multi-agent reasoning |

---

## 4. Database Schemas

### 4.1 Operational State (AlloyDB)

```sql
-- Tracks every cycle the swarm runs
CREATE TABLE evo_cycles (
  cycle_id BIGSERIAL PRIMARY KEY,
  started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  ended_at TIMESTAMPTZ,
  workload_id TEXT NOT NULL,
  status TEXT CHECK (status IN ('running','succeeded','failed','aborted')),
  trigger_type TEXT,                  -- 'schedule' | 'manual' | 'alert'
  recommendations_generated INT DEFAULT 0,
  recommendations_applied INT DEFAULT 0,
  estimated_savings_usd NUMERIC(12,2)
);

-- Each recommendation produced by the swarm
CREATE TABLE recommendations (
  rec_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  cycle_id BIGINT REFERENCES evo_cycles(cycle_id),
  database_type TEXT,                 -- 'bigquery' | 'alloydb' | 'spanner'
  target_resource TEXT NOT NULL,      -- fully qualified table/index name
  recommendation_type TEXT,           -- 'partition'|'cluster'|'index'|'denormalize'|'ml_refresh'
  severity TEXT,                      -- 'high'|'medium'|'low'
  rationale TEXT NOT NULL,
  generated_sql TEXT,
  estimated_impact JSONB,             -- {bytes_scanned_pct: -87, latency_ms_p95: ...}
  simulation_results JSONB,
  status TEXT DEFAULT 'pending',      -- 'pending'|'approved'|'applied'|'rejected'|'rolled_back'
  agent_trace JSONB,                  -- full multi-agent reasoning trail
  created_at TIMESTAMPTZ DEFAULT NOW(),
  decided_at TIMESTAMPTZ,
  decided_by TEXT
);

-- Audit log of every applied change
CREATE TABLE applied_changes (
  change_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  rec_id UUID REFERENCES recommendations(rec_id),
  applied_at TIMESTAMPTZ DEFAULT NOW(),
  applied_sql TEXT NOT NULL,
  rollback_sql TEXT NOT NULL,
  pre_state JSONB,                    -- snapshot before
  post_state JSONB,                   -- snapshot after
  observed_impact JSONB,              -- measured impact (vs estimated)
  rolled_back_at TIMESTAMPTZ
);

-- Vector embeddings for similar-pattern lookup
CREATE TABLE pattern_embeddings (
  pattern_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  query_fingerprint TEXT,             -- normalized SQL
  embedding VECTOR(768),              -- using google's textembedding-gecko
  workload_id TEXT,
  occurrence_count INT DEFAULT 1,
  last_seen TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX ON pattern_embeddings USING scann (embedding);
```

### 4.2 Knowledge Graph (BigQuery property graph or Neo4j)

```cypher
// Node types
(:Recommendation { rec_id, type, severity, status })
(:Table { name, db_type, size_bytes, row_count })
(:Query { fingerprint, frequency, avg_bytes_scanned })
(:Decision { decided_at, decided_by, outcome })
(:Outcome { metric, before_value, after_value, delta_pct })
(:Agent { name, role })

// Relationships
(:Recommendation)-[:TARGETS]->(:Table)
(:Recommendation)-[:GENERATED_BY]->(:Agent)
(:Recommendation)-[:RESULTED_IN]->(:Decision)
(:Decision)-[:PRODUCED]->(:Outcome)
(:Recommendation)-[:SIMILAR_TO]->(:Recommendation)
(:Query)-[:SCANS]->(:Table)
```

This lets you answer questions like *"Show all repartitioning recommendations on tables larger than 1TB and their actual measured impact"* in a single Cypher query.

---

## 5. Agent Implementation (ADK Pattern)

### 5.1 Coordinator (the orchestrator)

```python
# agents/coordinator/agent.py
from google.adk.agents import Agent
from google.adk.tools import AgentTool
from .workflow import run_cycle

coordinator = Agent(
    name="coordinator",
    model="gemini-2.5-pro",
    description="Orchestrates the EvoAgent optimization cycle",
    instruction="""
    You are the Coordinator of the EvoAgent swarm. Your job is to:
    1. Trigger Sage to analyze recent telemetry
    2. Pass findings to Forge for optimization recommendations
    3. Have Echo simulate each recommendation
    4. Compile a report for human review
    5. After approval, dispatch to Wright
    6. Record everything via Codex

    Never apply schema changes without explicit approval (unless env=dev).
    Always include rationale and simulated impact in your report.
    """,
    sub_agents=[sage, forge, echo, wright, codex],
    tools=[AgentTool(agent=sage), AgentTool(agent=forge), ...]
)
```

### 5.2 Sage (Analyzer) — example prompt

```python
sage = Agent(
    name="sage",
    model="gemini-2.5-flash",     # cheaper, pattern-heavy work
    description="Analyzes query telemetry to identify optimization opportunities",
    instruction="""
    You are Sage, the Analyzer.

    For the given workload, you will:
    1. Pull last N days of jobs from INFORMATION_SCHEMA.JOBS_BY_PROJECT
       and JOBS_TIMELINE_BY_PROJECT.
    2. Group queries by semantic similarity (use embedding_search tool).
    3. Identify the top 10 high-impact patterns:
       - High-scan queries (> 1TB scanned)
       - Frequent joins on consistent column sets
       - Time-series filters on unpartitioned tables
       - ML model predictions showing drift signals

    Output a structured JSON list of opportunities with:
      { pattern_id, description, frequency, impact_estimate, evidence_queries }

    Cross-reference each finding with Codex's prior decisions before surfacing.
    """,
    tools=[bigquery_query, info_schema_tool, embedding_search]
)
```

### 5.3 Workflow loop (Cloud Workflows YAML)

```yaml
main:
  steps:
    - trigger_cycle:
        call: http.post
        args:
          url: ${COORDINATOR_URL}/cycles
        result: cycle

    - wait_for_recommendations:
        call: events.await_callback
        args:
          server_url: ${cycle.callback_url}
          timeout: 1800
        result: recommendations

    - human_approval:
        switch:
          - condition: ${cycle.env == "prod"}
            steps:
              - send_for_review:
                  call: http.post
                  args:
                    url: ${API_URL}/recommendations/notify
                    body:
                      recs: ${recommendations}
              - await_decisions:
                  call: events.await_callback
                  args:
                    timeout: 86400  # 24h SLA

    - apply_approved:
        for:
          value: rec
          in: ${approved_recs}
          steps:
            - apply:
                call: http.post
                args:
                  url: ${WRIGHT_URL}/apply
                  body: ${rec}
```

---

## 6. API Design

The frontend talks to one FastAPI service that fronts the agent system.

### Key endpoints

```
GET  /api/cycles                     # List recent cycles
GET  /api/cycles/{id}                # Cycle detail with full agent trace
GET  /api/recommendations            # Filterable list
GET  /api/recommendations/{id}       # Detail + simulation results
POST /api/recommendations/{id}/apply
POST /api/recommendations/{id}/reject
POST /api/recommendations/{id}/simulate

GET  /api/agents                     # Live agent statuses
GET  /api/agents/stream              # SSE: live activity feed

POST /api/chat                       # Natural language chat with swarm
                                     # Returns: { answer, reasoning, sources }

GET  /api/metrics/optimization-score
GET  /api/metrics/cost-savings?period=30d
GET  /api/metrics/impact-timeline

GET  /api/audit                      # Full audit trail with filters
GET  /api/knowledge/similar?query=...
```

### Live activity stream (SSE)

```python
@router.get("/agents/stream")
async def agent_stream():
    async def event_generator():
        async for event in agent_event_bus.subscribe():
            yield {
                "event": "agent_activity",
                "data": json.dumps({
                    "ts": event.timestamp,
                    "agent": event.agent_name,
                    "action": event.action,
                    "details": event.details
                })
            }
    return EventSourceResponse(event_generator())
```

---

## 7. Frontend (UI) Implementation Notes

The HTML mockup I'm providing uses static data for visual reference. For the real Next.js app, mirror this design system:

### Design tokens (copy from the mockup CSS variables)

- **Background:** `#0a0e16` (deep blue-black)
- **Accent:** `#7df9a9` (CRT phosphor green) — this is your signature
- **Fonts:** Instrument Serif (display), Manrope (body), JetBrains Mono (code/labels)

### Component breakdown

| Component | Data source | Notes |
|-----------|-------------|-------|
| `Topbar` | `/api/swarm/status` | Status pill polls every 5s |
| `StatsRow` | `/api/metrics/*` | 4-up grid; gauge is custom SVG |
| `AgentSwarm` | `/api/agents` (SSE) | Real-time status updates |
| `RecommendationCard` | `/api/recommendations` | Action buttons trigger optimistic UI |
| `ImpactChart` | `/api/metrics/impact-timeline` | Recharts area chart, 2 series |
| `ChatPanel` | `/api/chat` (streaming) | Stream Gemini response chunks |
| `ActivityFeed` | `/api/agents/stream` (SSE) | Tail latest 50 events |

### Critical UI behaviors

1. **Approval is the central interaction** — make Apply/Simulate/Reject buttons large and easy to scan. The "Simulate" button should show a modal with before/after EXPLAIN plans side-by-side.
2. **Reasoning is visible** — every AI message and recommendation has a collapsible "reasoning" block. This is what builds trust with DBAs.
3. **Real-time feel** — the agent activity stream and "Swarm Active" pill should feel alive. Subtle pulse animations on active agents.
4. **Code is first-class** — show real SQL with syntax highlighting on every recommendation. DBAs need to verify what will be executed.

---

## 8. Phased Roadmap (recap, with concrete deliverables)

### Phase 1 — MVP (4–6 weeks)
- ✅ Coordinator + Sage + Codex agents working against BigQuery only
- ✅ Recommendations stored in AlloyDB
- ✅ Single dashboard page (Overview)
- ✅ Manual approval via UI button
- ✅ Telemetry: bytes scanned, query latency, slot usage

### Phase 2 — Full swarm (4–6 weeks)
- ✅ Add Forge, Echo, Wright agents
- ✅ Shadow simulation pipeline
- ✅ A2A debate when agents disagree
- ✅ Full UI: Recommendations + Agents + Audit pages
- ✅ Chat panel (Gemini-powered Q&A)

### Phase 3 — Multi-DB + production (6–8 weeks)
- ✅ AlloyDB + Spanner support
- ✅ Knowledge graph in production
- ✅ Vector similarity search ("we tried this before")
- ✅ Approval workflows via Slack / email
- ✅ Cloud Audit Logs integration, VPC-SC, Model Armor

### Phase 4 — Productize
- ✅ Multi-tenant version for managed service
- ✅ Customer-specific policy engine
- ✅ Onboarding wizard
- ✅ Usage-based billing meters

---

## 9. Risks & Mitigations

| Risk | Mitigation |
|------|-----------|
| Bad change applied → outage | Mandatory simulation + rollback SQL pre-generated + 7-day retention of pre-state |
| Agent hallucinates non-existent columns | Every DDL passes through `validate_against_information_schema` before reaching the user |
| LLM costs spiral | Use Gemini Flash for pattern detection, only escalate to Pro for reasoning/explanation |
| Approval fatigue | Configurable auto-apply for low-risk classes (e.g., adding indexes in dev) |
| Multi-agent infinite loops | Hard cycle budget (max 3 A2A rounds), explicit termination conditions |
| Sensitive data in prompts | All telemetry goes through PII scrubber before LLM; Model Armor as belt-and-suspenders |

---

## 10. What makes this different from a static recommender

- **Memory:** Codex remembers every decision and outcome, so suggestions improve over time.
- **Simulation, not prediction:** Echo actually runs the queries before recommending — no "estimated savings" hand-waving.
- **Multi-agent debate:** When Sage and Forge disagree, the trace is logged and visible to the DBA.
- **Business-aware:** Hooks for Jira tickets, BI tool queries, and natural-language workload descriptions mean recommendations align with intent, not just statistics.
