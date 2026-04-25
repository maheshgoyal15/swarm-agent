# Vibe Coding Prompts — EvoAgent

Copy these prompts directly into your vibe coding tool of choice (Cursor, v0, Lovable, Bolt, Claude Code, etc.). Prompts are ordered so each builds on the last.

---

## Prompt 0 — Project Setup (use first)

```
I'm building "EvoAgent" — an autonomous database optimization platform for Google
Cloud. It's a multi-agent system that watches BigQuery / AlloyDB / Spanner
workloads and recommends schema, index, and partitioning changes.

Stack:
- Frontend: Next.js 14 (App Router) + TypeScript + Tailwind + shadcn/ui + Recharts
- Backend: FastAPI (Python 3.11) on Cloud Run
- Agents: Google ADK (Agent Development Kit), Vertex AI, Gemini 2.5
- DB: AlloyDB (operational state) + BigQuery (telemetry)
- Real-time: Server-Sent Events for agent activity

Design system (CRITICAL — match exactly):
- Background: #0a0e16 (deep blue-black)
- Surface: #0f1420
- Card surface: #131927
- Accent (signature): #7df9a9 (CRT phosphor green)
- Warning: #fbbf24, Critical: #ef5a6f, Info: #6ea8ff
- Text primary: #e6e9f0, muted: #8a93a6, dim: #5a6478
- Display font: 'Instrument Serif' (Google Fonts), italics for emphasis
- Body font: 'Manrope' (Google Fonts)
- Mono font: 'JetBrains Mono' (Google Fonts) — used for labels, code, technical metadata
- 1px hairline borders using rgba(255,255,255,0.06)
- Subtle 32px grid texture on body background
- Card border-radius: 12px, button border-radius: 6px

Set up the Next.js project with these dependencies and create a layout.tsx that
loads the three Google Fonts and applies the dark theme to <body>.
Build a single shared <Card> component matching the spec above.
```

---

## Prompt 1 — Topbar + Navigation

```
Build the Topbar component for EvoAgent (see attached HTML for visual reference).

Requirements:
- Sticky at top, blurred glass effect (backdrop-filter: blur(20px) on rgba(10,14,22,0.7))
- Left: brand logo (32px rounded square, #7df9a9 gradient, animated pulse ring around it)
  with text "Evo<em>Agent</em>" where 'Agent' is in italic accent color
- Center nav links: Overview, Recommendations, Agents, Knowledge, Audit, Settings
  - Active link: accent text color + accent-glow background (rgba(125,249,169,0.15))
- Right side:
  1. Search box (280px wide, mono font, with ⌘K kbd hint)
  2. Status pill: "Swarm Active · 5 agents" with a blinking dot
  3. User avatar (32px circle, gradient background, initials)
- Use lucide-react for any icons needed
- Status pill should poll /api/swarm/status every 5s (mock the endpoint for now,
  always returning {active: true, agentCount: 5})
```

---

## Prompt 2 — Hero + Stats Row

```
Build two components that sit at the top of the Overview page.

1. <Hero> component:
   - Large editorial heading using Instrument Serif at 56px, line-height 1
   - Text: "Your data estate, <em>self-tuning.</em>" with italic accent on the second part
   - Subline in JetBrains Mono 12px, dim color, uppercase, letter-spacing 0.1em:
     "Coordinator · Cycle #1247 · Started 04:00 UTC"
   - Right-aligned metadata block (mono, 11px) showing workload, region, databases

2. <StatsRow> component:
   - 4-column grid (1.4fr 1fr 1fr 1fr) with 1px gap, looking like a single
     bordered card with internal dividers
   - First card "feature" stat: Optimization Score
     - Custom circular gauge SVG (110×110), 8px stroke
     - Use linearGradient from #4ac788 to #7df9a9
     - Stroke-dasharray 314, dashoffset proportional to value
     - Center shows the score number (Instrument Serif 36px, accent color) + grade
       below it ("B+ · Healthy" in mono 9px)
     - To the right: explanation text + trend pill "↑ +14 pts · 30d"
   - Three other stats: Cost Saved MTD, Avg Query Speedup, Pending Review
     - Each: mono uppercase label, then huge number in Instrument Serif (44px),
       trend indicator below in mono with arrow (↑ green, ↓ red)
   - Pull data from /api/metrics/optimization-score (mock returns: score=85,
     cost_saved=28400, speedup=3.7, pending=8, pending_high=3)
```

---

## Prompt 3 — Agent Swarm Panel (the signature component)

```
Build the <AgentSwarm> component — this is the most distinctive piece of the UI.

Layout:
- Card with header "The Swarm · 5 agents · A2A protocol" (display font + mono subtitle)
- 5-column inner grid showing each of the agents

Each agent card:
- Background: #1a2233 with 1px border #1f2937
- Top edge: 2px colored bar — accent (#7df9a9) when active, dim when idle
- Active agents have a subtle glow on the top bar
- Content:
  - Mono label: "// 01 — Analyzer" (dim color)
  - Display font name: "Sage" (18px Instrument Serif)
  - Status row: pulsing dot + status text in mono ("analyzing", "planning",
    "dry-run", "awaiting approval", "indexing")
  - Task description (11px, muted): one-line current activity

The five agents:
1. Sage (Analyzer) — analyzing — "Embedding 14k query patterns from JOBS_TIMELINE"
2. Forge (Optimizer) — planning — "Ranking 23 candidate index strategies"
3. Echo (Simulator) — dry-run — "Replaying 50 queries on shadow clone"
4. Wright (Applier) — awaiting approval (idle) — "2 DDL statements queued"
5. Codex (Historian) — indexing — "Writing decision lineage to graph"

Connect to /api/agents via Server-Sent Events. When a status update arrives,
animate the change (pulse the agent card briefly).

Subscribe with EventSource on mount, clean up on unmount.
```

---

## Prompt 4 — Recommendations Feed

```
Build the <RecommendationsFeed> component — the core interaction surface.

Card with:
- Header: "Pending Recommendations" (display font) + "8 new" badge
  (accent background, accent text, mono 10px)
- Right side: Filter button + Sort dropdown (default "Sort: Impact ↓")

Each recommendation row (separated by 1px borders):
- 3-column grid: [40px icon] [content] [actions]
- Padding 22px 24px, hover background #131927

Icon:
- 40×40 rounded square
- Cost recommendations: accent-glow bg with $ in accent color
- Performance: info-dim bg with ⚡ in info color
- Warning/drift: warn-dim bg with ! in warn color

Content:
- Meta line (mono 10px uppercase, dim): "BigQuery · Partitioning · Sage + Forge"
  with • dots between, ending with severity tag (high/medium/low)
- Title: 15px semi-bold, can include <code> spans in mono+accent
- Target line: full resource path in mono+accent on subtle bg
- Description: 13px muted text, max 2 lines
- Optional SQL block: dark bg #0a0e16, 1px border, mono 11px, syntax-highlighted
  - Keywords in #7df9a9, strings in #fbbf24, comments in dim+italic
- Impact line: mono 11px, multiple metrics like "Bytes scanned: -87% | Est. savings: $12.4K | 4.2× faster"
  - Positive impacts in accent color, negatives in critical color

Actions column (right):
- "Apply" button (primary, accent bg, dark text) for safe recs
- "Simulate" button (default style) — opens modal with before/after EXPLAIN plans
- "Reject" button (ghost style)
- For risky changes, replace "Apply" with "Plan migration"

Mock data: 4 recommendations matching the visual reference (BigQuery repartition,
AlloyDB index, BQ ML drift, Spanner hot-spot).

Endpoint: GET /api/recommendations
Optimistic UI: when Apply is clicked, immediately show "Applying..." state and
remove from list on 200.
```

---

## Prompt 5 — Impact Chart

```
Build the <ImpactChart> component using Recharts.

Card with:
- Header: "Cumulative Impact · last 30 days"
- Right: time-range toggle (7d / 30d / 90d) — three buttons, only one active

Chart specs:
- AreaChart with two series:
  Series 1: bytes_scanned_per_day (TB) — accent color #7df9a9, gradient fill
  Series 2: avg_query_latency (ms) — info color #6ea8ff, dashed line, lighter gradient
- Both should trend DOWN over time (this is good news — optimization working)
- Mark the days when changes were applied with circular dots on the line
- X-axis: dates in mono font, dim color
- Grid lines: very subtle, rgba(255,255,255,0.05)
- Custom tooltip with dark bg #0f1420, 1px accent border

Legend above chart (mono 11px):
  ■ Bytes scanned (TB/day)   ■ Avg query latency (ms)

Endpoint: GET /api/metrics/impact-timeline?period=30d
Mock returns 30 data points with both metrics declining ~30%.
```

---

## Prompt 6 — Chat Panel

```
Build the <ChatPanel> component — the conversational interface to the swarm.

Card with fixed height 540px, displayed in the right column.
- Header: "Ask the Swarm" (display) + "· Gemini 2.5 Pro" (mono dim)

Messages area (scrollable):
- Each message: 26px avatar + bubble
- User avatar: gradient blue-purple, initials
- AI avatar: solid accent #7df9a9, dark "E" letter
- Bubbles: no background color, just text — keep it clean
- AI messages can have a "reasoning" block:
  - Indented, left border 2px accent
  - Background #131927
  - Italic muted text
  - Smaller (12px)

Input area (fixed bottom):
- Background #131927, 1px top border
- Mono "›" prompt character in accent color
- Borderless input
- Send button: 28px square, accent bg, dark arrow icon

Behavior:
- POST /api/chat { message } with streaming response
- Stream chunks into a new AI message bubble as they arrive
- Show typing indicator (3 dots animated) while waiting for first chunk
- Reasoning block expands automatically when complete

Seed with 2 example exchanges showing:
1. User asks why customer_360_dashboard is slow
2. AI explains, with reasoning block citing investigation steps
3. User asks about rollback plan
4. AI describes CTAS pattern with reasoning citing prior similar cases
```

---

## Prompt 7 — Activity Feed

```
Build the <ActivityFeed> component — the live agent activity stream.

Card with:
- Header: "Live Activity" + streaming status pill on right (with blinking dot)

Each entry: 3-column grid [time] [marker] [content]
- Time column: 60px wide, mono 10px, dim, right-aligned, format HH:MM:SS
- Marker column: vertical line through center + 8px colored dot
  - Dots: accent (default), warn (#fbbf24), info (#6ea8ff)
  - 3px ring around dot in card-bg color (creates separation from line)
- Content: 12px text
  - Agent tag in mono uppercase (e.g., "SAGE →") in muted color
  - Body text with technical resources in <em> styled as accent + mono

Behavior:
- Subscribe to /api/agents/stream via EventSource
- Prepend new events at top
- Cap at 50 visible (older fall off with fade animation)
- Smooth slide-in animation for new entries (translateY 8px → 0, opacity 0 → 1)

Mock activity events to seed:
- 04:42:11 SAGE: Identified high-scan pattern on events_raw, 94% temporal-filtered
- 04:42:38 FORGE: Generated 5 candidate strategies, ranked by simulated impact
- 04:43:02 ECHO: Cloned events_raw to shadow dataset (2% sample, 84M rows)
- 04:44:17 ECHO: Replayed 50-query benchmark on shadow · -87% bytes confirmed
- 04:44:51 CODEX: Cross-referenced 4 prior repartitions on similar tables — all positive
- 04:45:09 COORD: Recommendation surfaced for human review · awaiting decision
```

---

## Prompt 8 — Memory / Knowledge Stats

```
Build a small <MemoryStats> card showing the swarm's accumulated knowledge.

- Header: "Memory · self-knowledge graph"
- 2x2 grid of stats:
  - Decisions logged: 2,841
  - Patterns learned: 147
  - Rollbacks · 90d: 3 (in warn color)
  - Confidence avg: 94% (in accent color)
- Each stat: mono uppercase label + Instrument Serif 26px number
- Endpoint: GET /api/knowledge/stats
```

---

## Prompt 9 — Page Composition

```
Now assemble the Overview page (app/page.tsx).

Layout:
- <Topbar /> at top
- Main content: max-width 1640px, padding 32px, gap 24px
- Inside main:
  - <Hero /> full width
  - <StatsRow /> full width
  - 2-column grid below (1fr 360px, gap 24px):
    - Left column (vertical stack, gap 24px):
      - <AgentSwarm />
      - <RecommendationsFeed />
      - <ImpactChart />
    - Right column (vertical stack, gap 24px):
      - <ChatPanel />
      - <MemoryStats />
      - <ActivityFeed />
- <Footer /> with cycle info in mono small text

Responsive: below 1280px, collapse to single column. Swarm grid becomes 3-up.
```

---

## Prompt 10 — Backend Skeleton (FastAPI)

```
Create a FastAPI backend in /api with these routes (mock data is fine for now,
real ADK integration comes later):

main.py:
- CORS for localhost:3000
- All routes prefixed /api

routes/recommendations.py:
- GET /recommendations — return list of 4 recs with the structure shown
- GET /recommendations/{id} — return single rec with full simulation_results
- POST /recommendations/{id}/apply — return {status: "applied", change_id: uuid}
- POST /recommendations/{id}/reject — return {status: "rejected"}
- POST /recommendations/{id}/simulate — return before/after EXPLAIN plans

routes/agents.py:
- GET /agents — return current status of all 5 agents
- GET /agents/stream — SSE endpoint that emits a synthetic event every 4 seconds
  (rotate through SAGE/FORGE/ECHO/WRIGHT/CODEX with realistic activity messages)

routes/metrics.py:
- GET /metrics/optimization-score
- GET /metrics/cost-savings?period=30d
- GET /metrics/impact-timeline?period=30d (return 30 daily points)

routes/chat.py:
- POST /chat — for now, hardcode a streaming response that yields tokens
  with 30ms delay between them
- Use StreamingResponse with text/event-stream content type

routes/swarm.py:
- GET /swarm/status — {active: true, agentCount: 5, cycle_id: 1247}

models/ — Pydantic schemas mirroring the AlloyDB tables in IMPLEMENTATION.md

Use uvicorn with --reload for local dev. Add a Dockerfile for Cloud Run.
```

---

## Prompt 11 — ADK Agents (the real thing)

```
Now wire up the actual agents using google-adk.

Install: pip install google-adk google-cloud-aiplatform

agents/coordinator/agent.py:
Create a Coordinator agent (Gemini 2.5 Pro) that orchestrates the cycle.
It should have sub_agents = [sage, forge, echo, wright, codex] and use AgentTool
to invoke them. The instruction prompt should match the one in IMPLEMENTATION.md
section 5.1.

agents/sage/agent.py:
Sage uses Gemini 2.5 Flash. Tools needed:
- bigquery_query: executes a SQL query against INFORMATION_SCHEMA
- info_schema_reader: shortcut for common metadata pulls
- embedding_search: searches pattern_embeddings table for similar past patterns

The MCP integration: use the managed BigQuery MCP server URL from your project.
Configure with `from google.adk.tools.mcp import MCPToolset`.

agents/forge/agent.py:
Forge uses Gemini 2.5 Pro (needs strong reasoning). Tools:
- ddl_generator: produces validated DDL given a recommendation type
- cost_model: estimates impact based on table stats + query patterns
- best_practice_kb: retrieves relevant patterns from prior cycles

agents/echo/agent.py:
Echo's job is simulation. Tools:
- bigquery_dry_run: gets EXPLAIN plan + bytes-billed estimate
- clone_table: creates a shadow copy at N% sample
- query_replay: runs a query batch against the shadow

agents/wright/agent.py:
Applier with strict guardrails. Tools:
- safe_executor: validates DDL against information_schema before execution
- rollback_manager: pre-generates rollback SQL and stores it
- migration_runner: handles staged rollouts for risky changes

agents/codex/agent.py:
Historian. Tools:
- graph_writer: writes decision nodes/edges
- vector_index: stores pattern embeddings
- decision_log: appends to the audit table

Wire these into FastAPI routes so /api/cycles triggers the Coordinator.
Use Vertex AI Agent Engine for deployment in production.
```

---

## Prompt 12 — Polish

```
Final polish pass on the EvoAgent UI:

1. Add page-load animation: stagger the entry of cards with animation-delay
   (top to bottom, 100ms apart, fade + 8px Y translate)
2. Add subtle scroll-triggered effects on the impact chart
3. Add hover glow on agent cards that match their status color
4. The Apply button on recommendations: on click, show confetti briefly
   from button center (use canvas-confetti, accent-color particles only)
5. Empty state for recommendations: "Sage is still analyzing... no patterns
   surfaced yet." with a subtle scanning animation
6. 404 page: keep the brand mark, "This query returned no results" headline in
   Instrument Serif italic, link back to overview
7. Make all the buttons keyboard-accessible (focus rings using accent color
   with 2px outline-offset)
8. Make sure tab order is logical
9. Add prefers-reduced-motion media query that disables all decorative animations
   (keep the agent pulse since it conveys real status)
```

---

## Bonus — Single-prompt v0.dev / Lovable shortcut

If you want to spin up the whole thing in one shot in v0.dev or Lovable, paste this:

```
Build a database optimization dashboard called "EvoAgent" with this exact
aesthetic: dark theme (#0a0e16 background), CRT-phosphor-green accent (#7df9a9),
Instrument Serif display font, Manrope body, JetBrains Mono for technical labels.

The page has:
1. Sticky topbar with brand logo (animated pulsing ring), nav (Overview/
   Recommendations/Agents/Knowledge/Audit/Settings), search bar with ⌘K hint,
   "Swarm Active · 5 agents" status pill, user avatar.

2. Hero heading "Your data estate, self-tuning." (last two words italic accent),
   editorial 56px serif. Subline in mono with cycle metadata.

3. 4-column stats row: Optimization Score (with circular SVG gauge showing 85),
   Cost Saved $28.4K, Avg Speedup 3.7×, Pending Review 8.

4. "The Swarm" panel showing 5 agents in a row: Sage, Forge, Echo, Wright,
   Codex — each a small card with name, role, pulsing status dot, current task.
   Active agents have a glowing top bar.

5. "Pending Recommendations" feed with 4 cards. Each has: severity tag,
   database/type meta, title with code spans, target resource path, description,
   highlighted SQL block, impact metrics (e.g., "-87% bytes scanned"), and
   Apply/Simulate/Reject buttons.

6. Right sidebar: "Ask the Swarm" chat (with streaming AI responses and italic
   reasoning blocks), Memory stats card, Live Activity feed (timeline with
   colored dots and agent tags).

7. Cumulative impact area chart (last 30 days) with two declining series.

The vibe: serious tool for senior database engineers, but with the aesthetic
confidence of Linear or Vercel. Subtle 32px grid texture on background.
1px hairline borders. Lots of monospace for technical metadata. Italic serif
for headings. Use Recharts for the chart, lucide-react for icons.

Make it real and interactive — the buttons should feel responsive, the stream
should actually animate, the chat should stream characters.
```
