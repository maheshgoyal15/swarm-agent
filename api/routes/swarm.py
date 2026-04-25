from fastapi import APIRouter
from models.schemas import SwarmStatus

router = APIRouter()


@router.get("/status")
async def get_swarm_status():
    return SwarmStatus(
        active=True,
        agentCount=5,
        cycle_id=1247,
    )
