from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from models.schemas import Agent, AgentStatus
import asyncio
import json
from datetime import datetime
from agents.tools.alloydb_tools import get_connection

router = APIRouter()

AGENT_PROPERTIES = {
    "sage": {"id": 1, "name": "// 01 — Analyzer", "role": "Sage"},
    "forge": {"id": 2, "name": "// 02 — Optimizer", "role": "Forge"},
    "echo": {"id": 3, "name": "// 03 — Simulator", "role": "Echo"},
    "wright": {"id": 4, "name": "// 04 — Applier", "role": "Wright"},
    "codex": {"id": 5, "name": "// 05 — Historian", "role": "Codex"},
}

@router.get("/agents")
async def list_agents():
    try:
        conn = get_connection()
        rows = conn.run("SELECT agent_codename, status, task FROM evo_state.agent_status;")
        conn.close()
        
        agents = []
        for row in rows:
            codename, status, task = row
            props = AGENT_PROPERTIES.get(codename, {"id": 0, "name": "Unknown", "role": "Unknown"})
            agents.append(Agent(
                id=props["id"],
                name=props["name"],
                role=props["role"],
                codename=codename,
                status=status,
                task=task,
                active=status != "idle"
            ))
        return agents
    except Exception as e:
        print(f"Failed to list agents: {e}")
        # Fallback to idle if DB fails
        return [Agent(id=i, name=p["name"], role=p["role"], codename=c, status="idle", task="Idle", active=False) 
                for c, p in AGENT_PROPERTIES.items()]

@router.get("/agents/stream")
async def agent_stream():
    async def event_generator():
        last_status = {}
        
        while True:
            try:
                conn = get_connection()
                rows = conn.run("SELECT agent_codename, status, task FROM evo_state.agent_status;")
                conn.close()
                
                for row in rows:
                    codename, status, task = row
                    
                    # Check if status or task changed
                    key = f"{codename}:{status}:{task}"
                    if key not in last_status:
                        last_status[key] = True
                        
                        # Emit event
                        data = {
                            "ts": datetime.utcnow().strftime("%H:%M:%S"),
                            "agent": codename,
                            "action": status,
                            "details": task,
                            "status": status,
                        }
                        yield f"data: {json.dumps(data)}\n\n"
                        
            except Exception as e:
                print(f"Error in stream: {e}")
                
            await asyncio.sleep(2) # Poll every 2 seconds

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
