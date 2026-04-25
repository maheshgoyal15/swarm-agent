from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum
import uuid


class AgentStatus(str, Enum):
    analyzing = "analyzing"
    planning = "planning"
    dry_run = "dry-run"
    awaiting_approval = "awaiting approval"
    indexing = "indexing"
    idle = "idle"


class Agent(BaseModel):
    id: int
    name: str
    role: str
    codename: str
    status: AgentStatus
    task: str
    active: bool


class Impact(BaseModel):
    label: str
    value: str
    positive: bool


class Recommendation(BaseModel):
    id: str
    database_type: str
    recommendation_type: str
    agents: str
    severity: str  # "high" | "medium" | "low"
    title: str
    target: str
    description: str
    sql: Optional[str] = None
    impact: list[Impact]
    icon_type: str  # "cost" | "perf" | "warn"
    actions: list[str]
    simulation_results: Optional[dict] = None


class ApplyResult(BaseModel):
    status: str
    change_id: str = Field(default_factory=lambda: str(uuid.uuid4()))


class RejectResult(BaseModel):
    status: str


class SimulateResult(BaseModel):
    before_plan: str
    after_plan: str
    bytes_before: int
    bytes_after: int
    latency_before_ms: int
    latency_after_ms: int


class OptimizationScore(BaseModel):
    score: int
    grade: str
    trend: str
    description: str
    cost_saved: int
    cost_trend: str
    speedup: float
    speedup_trend: str
    pending: int
    pending_high: int


class ImpactDataPoint(BaseModel):
    date: str
    bytes_scanned: float
    avg_latency: float
    applied: bool = False


class ChatRequest(BaseModel):
    message: str


class SwarmStatus(BaseModel):
    active: bool
    agentCount: int
    cycle_id: int


class KnowledgeStats(BaseModel):
    decisions_logged: int
    patterns_learned: int
    rollbacks_90d: int
    confidence_avg: int


class AgentStreamEvent(BaseModel):
    ts: str
    agent: str
    action: str
    details: str
