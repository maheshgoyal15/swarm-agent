import pathlib
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import recommendations, agents, metrics, chat, swarm, discovery

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
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
