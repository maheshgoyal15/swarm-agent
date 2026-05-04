import pathlib
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import recommendations, agents, metrics, chat, swarm, discovery
from dotenv import load_dotenv
import os

# Load environment variables from agents/.env
load_dotenv("../agents/.env")

from logging.handlers import TimedRotatingFileHandler

log_dir = "../logs"
os.makedirs(log_dir, exist_ok=True)

log_handler = TimedRotatingFileHandler(
    os.path.join(log_dir, "api.log"),
    when="D",
    interval=1,
    backupCount=7
)
log_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
log_handler.setFormatter(formatter)

logger = logging.getLogger()
logger.addHandler(log_handler)
logger.setLevel(logging.DEBUG)

logger.info("API logger initialized with daily rotation.")


def init_db():
    """Run the operational_state.sql schema to create tables if they don't exist."""
    try:
        from agents.tools.alloydb_tools import get_connection
        sql_path = pathlib.Path(__file__).parent.parent / "agents" / "schema" / "operational_state.sql"
        if not sql_path.exists():
            logger.warning(f"Schema file not found at {sql_path}, skipping DB init.")
            return

        sql = sql_path.read_text()
        conn = get_connection()
        for stmt in sql.split(";"):
            stmt = stmt.strip()
            if stmt and not stmt.startswith("--"):
                try:
                    conn.run(stmt)
                except Exception as e:
                    # Warn but continue — some ALTER TABLE stmts fail harmlessly on fresh DBs
                    logger.debug(f"Init SQL warning (non-fatal): {e}")
        conn.close()
        logger.info("DB schema initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize DB schema: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="EvoAgent API", lifespan=lifespan)

from pydantic import BaseModel
import json

class LogMessage(BaseModel):
    level: str
    message: str
    data: dict = None

@app.post("/api/log")
async def log_from_frontend(msg: LogMessage):
    level = msg.level.upper()
    message = f"[UI] {msg.message}"
    if msg.data:
        message += f" | Data: {json.dumps(msg.data)}"
        
    if level == "DEBUG":
        logger.debug(message)
    elif level == "INFO":
        logger.info(message)
    elif level == "WARNING":
        logger.warning(message)
    elif level == "ERROR":
        logger.error(message)
    elif level == "CRITICAL":
        logger.critical(message)
    else:
        logger.info(message)
        
    return {"status": "logged"}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(swarm.router, prefix="/api/swarm", tags=["swarm"])
app.include_router(discovery.router, prefix="/api", tags=["discovery"])
app.include_router(recommendations.router, prefix="/api", tags=["recommendations"])
app.include_router(agents.router, prefix="/api", tags=["agents"])
app.include_router(metrics.router, prefix="/api", tags=["metrics", "knowledge"])
app.include_router(chat.router, prefix="/api", tags=["chat"])


@app.get("/api/health")
async def health_check():
    return {"status": "ok"}


@app.get("/api/dashboard")
async def dashboard():
    """Single endpoint that aggregates all monitor data to avoid CORS/multi-fetch issues."""
    from agents.tools.alloydb_tools import get_connection, get_target_schema
    import json as _json

    result = {
        "agents": [],
        "table_stats": [],
        "slow_queries": [],
        "cycle_id": 0,
        "swarm_active": False,
        "recommendations": [],
    }
    try:
        conn = get_connection()

        # Agent status
        rows = conn.run("SELECT agent_codename, status, task, updated_at FROM evo_state.agent_status ORDER BY agent_codename;")
        result["agents"] = [{"codename": r[0], "status": r[1], "task": r[2], "updated_at": str(r[3])} for r in rows]

        # Active agents count
        active = sum(1 for a in result["agents"] if a["status"] != "idle")
        result["swarm_active"] = active > 0

        # Latest cycle
        cy = conn.run("SELECT cycle_id, status, started_at FROM evo_state.evo_cycles ORDER BY cycle_id DESC LIMIT 1;")
        if cy:
            result["cycle_id"] = cy[0][0]
            result["cycle_status"] = cy[0][1]

        # Table stats — look for mock_orders specifically + all tables
        schema = get_target_schema()
        ts = conn.run(
            "SELECT relname, n_live_tup, pg_total_relation_size(relid), n_dead_tup "
            "FROM pg_stat_user_tables WHERE schemaname = :s ORDER BY pg_total_relation_size(relid) DESC;",
            s=schema,
        )
        result["table_stats"] = [{"table": r[0], "live_rows": r[1], "size_bytes": r[2], "dead_rows": r[3]} for r in ts]

        # Slow queries from pg_stat_statements
        try:
            sq = conn.run(
                "SELECT query, calls, total_exec_time, mean_exec_time "
                "FROM pg_stat_statements "
                "WHERE query NOT LIKE '%pg_%' AND query NOT LIKE '%evo_state%' "
                "ORDER BY total_exec_time DESC LIMIT 10;"
            )
            result["slow_queries"] = [{"query": r[0], "calls": r[1], "total_ms": float(r[2]), "avg_ms": float(r[3])} for r in sq]
        except Exception:
            result["slow_queries"] = []

        # Pending recommendations
        recs = conn.run(
            "SELECT rec_id, target_resource, recommendation_type, severity, rationale, status, created_at "
            "FROM evo_state.recommendations WHERE status = 'pending' ORDER BY created_at DESC LIMIT 10;"
        )
        result["recommendations"] = [
            {"id": str(r[0]), "target": r[1], "type": r[2], "severity": r[3], "rationale": r[4], "status": r[5]}
            for r in recs
        ]

        conn.close()
    except Exception as e:
        result["error"] = str(e)

    return result
