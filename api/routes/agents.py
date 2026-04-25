from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from models.schemas import Agent, AgentStatus
import asyncio
import json
import random
from datetime import datetime

router = APIRouter()

MOCK_AGENTS = [
    Agent(id=1, name="// 01 — Analyzer", role="Sage", codename="sage",
          status=AgentStatus.analyzing, task="Embedding 14k query patterns from JOBS_TIMELINE", active=True),
    Agent(id=2, name="// 02 — Optimizer", role="Forge", codename="forge",
          status=AgentStatus.planning, task="Ranking 23 candidate index strategies", active=True),
    Agent(id=3, name="// 03 — Simulator", role="Echo", codename="echo",
          status=AgentStatus.dry_run, task="Replaying 50 queries on shadow clone", active=True),
    Agent(id=4, name="// 04 — Applier", role="Wright", codename="wright",
          status=AgentStatus.awaiting_approval, task="2 DDL statements queued", active=False),
    Agent(id=5, name="// 05 — Historian", role="Codex", codename="codex",
          status=AgentStatus.indexing, task="Writing decision lineage to graph", active=True),
]

SYNTHETIC_EVENTS = [
    {"agent": "sage", "action": "analyzing", "details": "Scanning INFORMATION_SCHEMA.JOBS_TIMELINE for high-scan patterns"},
    {"agent": "sage", "action": "analyzing", "details": "Found 23 queries scanning >1TB on events_raw"},
    {"agent": "forge", "action": "planning", "details": "Evaluating composite index on orders(customer_id, status)"},
    {"agent": "forge", "action": "planning", "details": "Cost model estimates $12.4K/month savings from partitioning"},
    {"agent": "echo", "action": "dry-run", "details": "Shadow clone created: events_raw_shadow (2% sample, 84M rows)"},
    {"agent": "echo", "action": "dry-run", "details": "Replay complete: 47/50 queries improved, avg -73% bytes"},
    {"agent": "wright", "action": "awaiting approval", "details": "DDL staged: CREATE OR REPLACE TABLE with partitioning"},
    {"agent": "codex", "action": "indexing", "details": "Decision node created: REC-001 → events_raw repartition"},
    {"agent": "codex", "action": "indexing", "details": "Cross-referenced 4 prior repartitions — all positive outcomes"},
    {"agent": "sage", "action": "analyzing", "details": "Detected feature drift on churn_predictor_v3: PSI = 0.184"},
]


@router.get("/agents")
async def list_agents():
    return MOCK_AGENTS


@router.get("/agents/stream")
async def agent_stream():
    async def event_generator():
        idx = 0
        while True:
            event = SYNTHETIC_EVENTS[idx % len(SYNTHETIC_EVENTS)]
            now = datetime.utcnow()
            data = {
                "ts": now.strftime("%H:%M:%S"),
                "agent": event["agent"],
                "action": event["action"],
                "details": event["details"],
                "status": event["action"],
            }
            yield f"data: {json.dumps(data)}\n\n"
            idx += 1
            await asyncio.sleep(4 + random.random() * 2)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
