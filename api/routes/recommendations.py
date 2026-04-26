from fastapi import APIRouter, HTTPException, BackgroundTasks
from models.schemas import Recommendation, ApplyResult, RejectResult, SimulateResult, Impact
import uuid
from agents.tools.alloydb_tools import get_connection
from agents.runner import run_agent_cycle

router = APIRouter()

def map_row_to_recommendation(row) -> Recommendation:
    # row is a list or tuple from pg8000
    # Schema: rec_id, cycle_id, target_resource, recommendation_type, severity, rationale, generated_sql, status, created_at
    rec_id, cycle_id, target_resource, recommendation_type, severity, rationale, generated_sql, status, created_at = row
    
    # Derive icon type
    icon_type = "perf"
    if recommendation_type and "partition" in recommendation_type.lower():
        icon_type = "cost"
    elif severity == "high":
        icon_type = "warn"
        
    return Recommendation(
        id=str(rec_id),
        database_type="AlloyDB",
        recommendation_type=recommendation_type or "Optimization",
        agents="Sage + Forge",
        severity=severity or "medium",
        title=f"Optimize {target_resource}",
        target=target_resource,
        description=rationale,
        sql=generated_sql,
        impact=[
            Impact(label="Latency", value="TBD", positive=True),
            Impact(label="Cost", value="TBD", positive=True)
        ],
        icon_type=icon_type,
        actions=["apply", "simulate", "reject"] if status == "pending" else []
    )

@router.get("/recommendations")
async def list_recommendations():
    try:
        conn = get_connection()
        query = "SELECT rec_id, cycle_id, target_resource, recommendation_type, severity, rationale, generated_sql, status, created_at FROM evo_state.recommendations WHERE status = 'pending';"
        rows = conn.run(query)
        conn.close()
        
        recs = [map_row_to_recommendation(row) for row in rows]
        return recs
    except Exception as e:
        print(f"Failed to list recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/recommendations/{rec_id}")
async def get_recommendation(rec_id: str):
    try:
        conn = get_connection()
        query = "SELECT rec_id, cycle_id, target_resource, recommendation_type, severity, rationale, generated_sql, status, created_at FROM evo_state.recommendations WHERE rec_id = $1;"
        rows = conn.run(query, (rec_id,))
        conn.close()
        
        if not rows:
            raise HTTPException(status_code=404, detail="Recommendation not found")
            
        return map_row_to_recommendation(rows[0])
    except HTTPException:
        raise
    except Exception as e:
        print(f"Failed to get recommendation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/recommendations/{rec_id}/apply")
async def apply_recommendation(rec_id: str):
    try:
        conn = get_connection()
        query = "UPDATE evo_state.recommendations SET status = 'applied' WHERE rec_id = $1;"
        conn.run(query, (rec_id,))
        
        # Also insert into applied_changes
        query = "INSERT INTO evo_state.applied_changes (rec_id, applied_sql) SELECT rec_id, generated_sql FROM evo_state.recommendations WHERE rec_id = $1;"
        conn.run(query, (rec_id,))
        
        conn.close()
        return ApplyResult(status="applied")
    except Exception as e:
        print(f"Failed to apply recommendation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/recommendations/{rec_id}/reject")
async def reject_recommendation(rec_id: str):
    try:
        conn = get_connection()
        query = "UPDATE evo_state.recommendations SET status = 'rejected' WHERE rec_id = $1;"
        conn.run(query, (rec_id,))
        conn.close()
        return RejectResult(status="rejected")
    except Exception as e:
        print(f"Failed to reject recommendation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/scan")
async def trigger_scan(background_tasks: BackgroundTasks):
    try:
        conn = get_connection()
        # Create a new cycle
        query = "INSERT INTO evo_state.evo_cycles (status) VALUES ('running') RETURNING cycle_id;"
        result = conn.run(query)
        cycle_id = result[0][0]
        conn.close()
        
        prompt = "Analyze the schema for perfagent_heavy and suggest an optimization."
        background_tasks.add_task(run_agent_cycle, prompt, cycle_id)
        
        return {"status": "scan_triggered", "cycle_id": cycle_id, "message": "Scan started in background."}
    except Exception as e:
        print(f"Failed to trigger scan: {e}")
        raise HTTPException(status_code=500, detail=str(e))
