from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from models.schemas import Agent, AgentStatus
import asyncio
import json
from datetime import datetime
from agents.tools.alloydb_tools import get_connection

router = APIRouter()

AGENT_PROPERTIES = {
    "sage":   {"id": 1, "name": "// 01 — Analyzer",  "role": "Sage"},
    "forge":  {"id": 2, "name": "// 02 — Optimizer", "role": "Forge"},
    "echo":   {"id": 3, "name": "// 03 — Simulator", "role": "Echo"},
    "wright": {"id": 4, "name": "// 04 — Applier",   "role": "Wright"},
    "codex":  {"id": 5, "name": "// 05 — Historian", "role": "Codex"},
}

# Only statuses declared in the AgentStatus enum
_VALID_STATUSES = {s.value for s in AgentStatus}

def _safe_status(raw: str) -> str:
    return raw if raw in _VALID_STATUSES else "idle"


@router.get("/agents")
async def list_agents():
    try:
        conn = get_connection()
        # Only fetch the 5 known display agents; coordinator is internal
        codenames = list(AGENT_PROPERTIES.keys())
        placeholders = ", ".join(f"${i+1}" for i in range(len(codenames)))
        rows = conn.run(
            f"SELECT agent_codename, status, task FROM evo_state.agent_status WHERE agent_codename IN ({placeholders});",
            codenames,
        )
        conn.close()

        agents = []
        for row in rows:
            codename, status, task = row
            props = AGENT_PROPERTIES[codename]
            safe = _safe_status(status)
            agents.append(Agent(
                id=props["id"],
                name=props["name"],
                role=props["role"],
                codename=codename,
                status=safe,
                task=task,
                active=safe != "idle",
            ))
        return agents
    except Exception as e:
        print(f"Failed to list agents: {e}")
        return [
            Agent(
                id=p["id"],
                name=p["name"],
                role=p["role"],
                codename=c,
                status="idle",
                task="Idle",
                active=False,
            )
            for c, p in AGENT_PROPERTIES.items()
        ]


@router.get("/agents/stream")
async def agent_stream():
    async def event_generator():
        # Track CURRENT state per agent (not an ever-growing seen-set)
        current_state: dict[str, tuple[str, str]] = {}
        conn = None

        try:
            while True:
                try:
                    if conn is None:
                        conn = get_connection()

                    rows = conn.run(
                        "SELECT agent_codename, status, task FROM evo_state.agent_status;"
                    )

                    for row in rows:
                        codename, status, task = row
                        prev = current_state.get(codename)
                        new_state = (status, task)

                        if prev != new_state:
                            current_state[codename] = new_state
                            data = {
                                "ts": datetime.utcnow().strftime("%H:%M:%S"),
                                "agent": codename,
                                "action": status,
                                "details": task,
                                "status": status,
                            }
                            yield f"data: {json.dumps(data)}\n\n"

                except GeneratorExit:
                    return
                except Exception as e:
                    print(f"Error in SSE stream: {e}")
                    # Close and let the next iteration reconnect
                    if conn:
                        try:
                            conn.close()
                        except Exception:
                            pass
                    conn = None

                await asyncio.sleep(2)
        finally:
            if conn:
                try:
                    conn.close()
                except Exception:
                    pass

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
