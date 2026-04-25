from fastapi import APIRouter, Query
from models.schemas import OptimizationScore, ImpactDataPoint, KnowledgeStats
from datetime import datetime, timedelta
import random

router = APIRouter()


@router.get("/metrics/optimization-score")
async def optimization_score():
    return OptimizationScore(
        score=85,
        grade="B+ · Healthy",
        trend="↑ +14 pts · 30d",
        description="17 optimizations applied this month. Score up from 71.",
        cost_saved=28400,
        cost_trend="↑ 32% vs last month",
        speedup=3.7,
        speedup_trend="↑ 0.4× this week",
        pending=8,
        pending_high=3,
    )


@router.get("/metrics/cost-savings")
async def cost_savings(period: str = Query(default="30d")):
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
    days = int(period.replace("d", "")) if period.endswith("d") else 30
    now = datetime.utcnow()
    data = []
    applied_days = [5, 12, 20, 26]

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
    return KnowledgeStats(
        decisions_logged=2841,
        patterns_learned=147,
        rollbacks_90d=3,
        confidence_avg=94,
    )
