from fastapi import APIRouter, Query
from models.schemas import OptimizationScore, ImpactDataPoint, KnowledgeStats
from datetime import datetime, timedelta
import random
from agents.tools.alloydb_tools import get_connection

router = APIRouter()

@router.get("/metrics/optimization-score")
async def optimization_score():
    try:
        conn = get_connection()
        
        # Query counts from DB
        pending_res = conn.run("SELECT count(*) FROM evo_state.recommendations WHERE status = 'pending';")
        pending = pending_res[0][0] if pending_res else 0
        
        pending_high_res = conn.run("SELECT count(*) FROM evo_state.recommendations WHERE status = 'pending' AND severity = 'high';")
        pending_high = pending_high_res[0][0] if pending_high_res else 0
        
        applied_res = conn.run("SELECT count(*) FROM evo_state.recommendations WHERE status = 'applied';")
        applied = applied_res[0][0] if applied_res else 0
        
        conn.close()
        
        # Calculate a dummy score based on pending issues
        # Start with 100, subtract for pending issues
        score = 100 - (pending_high * 5) - ((pending - pending_high) * 2)
        score = max(0, score) # Ensure non-negative
        
        grade = "A · Excellent"
        if score < 70:
            grade = "C · Needs Work"
        elif score < 90:
            grade = "B · Healthy"
            
        return OptimizationScore(
            score=score,
            grade=grade,
            trend="↑ +5 pts · 7d",
            description=f"{applied} optimizations applied. {pending} pending review.",
            cost_saved=applied * 1500, # Dummy calc: $1500 per applied change
            cost_trend="↑ based on applied changes",
            speedup=1.0 + (applied * 0.2), # Dummy calc
            speedup_trend="↑ improving",
            pending=pending,
            pending_high=pending_high,
        )
    except Exception as e:
        print(f"Failed to get metrics: {e}")
        # Fallback to mock data if DB fails
        return OptimizationScore(
            score=85,
            grade="B+ · Healthy",
            trend="↑ +14 pts · 30d",
            description="Fallback data due to DB error.",
            cost_saved=28400,
            cost_trend="↑ 32% vs last month",
            speedup=3.7,
            speedup_trend="↑ 0.4× this week",
            pending=8,
            pending_high=3,
        )

@router.get("/metrics/cost-savings")
async def cost_savings(period: str = Query(default="30d")):
    # Still mostly mock/derived until we have real impact data
    try:
        conn = get_connection()
        applied_res = conn.run("SELECT count(*) FROM evo_state.recommendations WHERE status = 'applied';")
        applied = applied_res[0][0] if applied_res else 0
        conn.close()
        
        total_saved = applied * 1500
        return {
            "period": period,
            "total_saved": total_saved,
            "currency": "USD",
            "breakdown": {
                "alloydb": total_saved,
                "bigquery": 0,
                "spanner": 0,
            },
        }
    except:
        return {
            "period": period,
            "total_saved": 28400,
            "currency": "USD",
            "breakdown": {
                "bigquery": 18200,
                "alloydb": 7100,
                "spanner": 3100,
            },
        }

@router.get("/metrics/impact-timeline")
async def impact_timeline(period: str = Query(default="30d")):
    # Generating synthetic data as approved
    days = int(period.replace("d", "")) if period.endswith("d") else 30
    now = datetime.utcnow()
    data = []
    
    # We can check applied changes to mark them on the chart
    applied_days = []
    try:
        conn = get_connection()
        res = conn.run("SELECT applied_at FROM evo_state.applied_changes;")
        conn.close()
        # Map applied dates to days ago
        for row in res:
            applied_at = row[0]
            if isinstance(applied_at, str):
                applied_at = datetime.fromisoformat(applied_at.replace('Z', '+00:00'))
            days_ago = (now - applied_at).days
            if 0 <= days_ago < days:
                applied_days.append(days - 1 - days_ago)
    except:
        applied_days = [5, 12, 20, 26] # Fallback

    for i in range(days - 1, -1, -1):
        date = now - timedelta(days=i)
        progress = (days - i) / days
        data.append(
            ImpactDataPoint(
                date=date.strftime("%b %d"),
                bytes_scanned=round(12.5 - 4.2 * progress + (random.random() - 0.5) * 1.2, 1),
                avg_latency=round(850 - 280 * progress + (random.random() - 0.5) * 80),
                applied=(days - 1 - i) in applied_days,
            )
        )
    return data

@router.get("/knowledge/stats")
async def knowledge_stats():
    try:
        conn = get_connection()
        applied_res = conn.run("SELECT count(*) FROM evo_state.applied_changes;")
        applied = applied_res[0][0] if applied_res else 0
        
        recs_res = conn.run("SELECT count(*) FROM evo_state.recommendations;")
        total_recs = recs_res[0][0] if recs_res else 0
        
        conn.close()
        
        return KnowledgeStats(
            decisions_logged=total_recs,
            patterns_learned=total_recs, # Assuming 1 pattern per rec for now
            rollbacks_90d=0,
            confidence_avg=95,
        )
    except:
        return KnowledgeStats(
            decisions_logged=2841,
            patterns_learned=147,
            rollbacks_90d=3,
            confidence_avg=94,
        )
