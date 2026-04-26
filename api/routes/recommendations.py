import os
from fastapi import APIRouter, HTTPException, BackgroundTasks
from models.schemas import Recommendation, ApplyResult, RejectResult, Impact
from agents.tools.alloydb_tools import get_connection, get_target_schema
from agents.runner import run_agent_cycle

router = APIRouter()


def map_row_to_recommendation(row) -> Recommendation:
    # Schema: rec_id, cycle_id, target_resource, recommendation_type, severity,
    #         rationale, generated_sql, status, created_at
    rec_id, cycle_id, target_resource, recommendation_type, severity, rationale, generated_sql, status, created_at = row

    icon_type = "perf"
    if recommendation_type and "partition" in recommendation_type.lower():
        icon_type = "cost"
    elif severity == "high":
        icon_type = "warn"

    return Recommendation(
        id=str(rec_id),
        database_type="PostgreSQL/AlloyDB",
        recommendation_type=recommendation_type or "Optimization",
        agents="Sage + Forge",
        severity=severity or "medium",
        title=f"Optimize {target_resource}",
        target=target_resource,
        description=rationale,
        sql=generated_sql,
        impact=[
            Impact(label="Latency", value="TBD", positive=True),
            Impact(label="Cost", value="TBD", positive=True),
        ],
        icon_type=icon_type,
        actions=["apply", "simulate", "reject"] if status == "pending" else [],
    )


@router.get("/recommendations")
async def list_recommendations():
    try:
        conn = get_connection()
        rows = conn.run(
            """SELECT rec_id, cycle_id, target_resource, recommendation_type, severity,
                      rationale, generated_sql, status, created_at
               FROM evo_state.recommendations
               WHERE status = 'pending'
               ORDER BY created_at DESC;"""
        )
        conn.close()
        return [map_row_to_recommendation(row) for row in rows]
    except Exception as e:
        print(f"Failed to list recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/recommendations/{rec_id}")
async def get_recommendation(rec_id: str):
    try:
        conn = get_connection()
        rows = conn.run(
            """SELECT rec_id, cycle_id, target_resource, recommendation_type, severity,
                      rationale, generated_sql, status, created_at
               FROM evo_state.recommendations WHERE rec_id = $1;""",
            (rec_id,)
        )
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
        conn.run(
            "UPDATE evo_state.recommendations SET status = 'applied' WHERE rec_id = $1;",
            (rec_id,)
        )
        conn.run(
            """INSERT INTO evo_state.applied_changes (rec_id, applied_sql)
               SELECT rec_id, generated_sql FROM evo_state.recommendations WHERE rec_id = $1;""",
            (rec_id,)
        )
        conn.close()
        return ApplyResult(status="applied")
    except Exception as e:
        print(f"Failed to apply recommendation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/recommendations/{rec_id}/reject")
async def reject_recommendation(rec_id: str):
    try:
        conn = get_connection()
        conn.run(
            "UPDATE evo_state.recommendations SET status = 'rejected' WHERE rec_id = $1;",
            (rec_id,)
        )
        conn.close()
        return RejectResult(status="rejected")
    except Exception as e:
        print(f"Failed to reject recommendation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/scan")
async def trigger_scan(background_tasks: BackgroundTasks):
    try:
        conn = get_connection()
        result = conn.run(
            "INSERT INTO evo_state.evo_cycles (status) VALUES ('running') RETURNING cycle_id;"
        )
        cycle_id = result[0][0]
        conn.close()

        schema = get_target_schema()
        prompt = (
            f"Analyze the '{schema}' schema in the connected PostgreSQL/AlloyDB database. "
            f"Identify the top performance and cost optimization opportunities based on slow queries, "
            f"table sizes, and index usage. Generate specific SQL recommendations and save each one."
        )
        background_tasks.add_task(run_agent_cycle, prompt, cycle_id)

        return {
            "status": "scan_triggered",
            "cycle_id": cycle_id,
            "target_schema": schema,
            "message": f"Scan started for schema '{schema}' in background.",
        }
    except Exception as e:
        print(f"Failed to trigger scan: {e}")
        raise HTTPException(status_code=500, detail=str(e))
