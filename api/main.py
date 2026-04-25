from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import recommendations, agents, metrics, chat, swarm

app = FastAPI(title="EvoAgent API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount routes
app.include_router(swarm.router, prefix="/api/swarm", tags=["swarm"])
app.include_router(recommendations.router, prefix="/api", tags=["recommendations"])
app.include_router(agents.router, prefix="/api", tags=["agents"])
app.include_router(metrics.router, prefix="/api/metrics", tags=["metrics"])
app.include_router(metrics.router, prefix="/api", tags=["knowledge"]) # /knowledge/stats
app.include_router(chat.router, prefix="/api", tags=["chat"])


@app.get("/api/health")
async def health_check():
    return {"status": "ok"}
