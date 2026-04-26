from fastapi import APIRouter
from models.schemas import SwarmStatus
from agents.tools.alloydb_tools import get_connection

router = APIRouter()


@router.get("/status")
async def get_swarm_status():
    try:
        conn = get_connection()

        cycle_res = conn.run(
            "SELECT cycle_id FROM evo_state.evo_cycles ORDER BY cycle_id DESC LIMIT 1;"
        )
        cycle_id = cycle_res[0][0] if cycle_res else 0

        active_res = conn.run(
            "SELECT count(*) FROM evo_state.agent_status WHERE status != 'idle';"
        )
        active_count = int(active_res[0][0]) if active_res else 0

        total_res = conn.run("SELECT count(*) FROM evo_state.agent_status;")
        total_count = int(total_res[0][0]) if total_res else 5

        conn.close()

        return SwarmStatus(
            active=active_count > 0,
            agentCount=total_count,
            cycle_id=cycle_id,
        )
    except Exception as e:
        print(f"Failed to get swarm status: {e}")
        return SwarmStatus(active=False, agentCount=5, cycle_id=0)
