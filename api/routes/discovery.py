import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from agents.tools.alloydb_tools import get_connection

router = APIRouter()


class DatabaseSelection(BaseModel):
    project_id: Optional[str] = None
    instance_id: str
    database_name: str
    db_type: str
    target_schema: Optional[str] = "public"
    ip: Optional[str] = None


@router.get("/gcp/current-database")
async def get_current_database():
    """Returns the active DB connection info derived from environment variables."""
    return {
        "host": os.getenv("DB_HOST", "localhost"),
        "port": int(os.getenv("DB_PORT", "5432")),
        "database": os.getenv("DB_NAME", "postgres"),
        "user": os.getenv("DB_USER", "postgres"),
        "target_schema": os.getenv("TARGET_SCHEMA", "public"),
        "db_type": "postgresql",
        "display": f"{os.getenv('DB_HOST', 'localhost')}:{os.getenv('DB_PORT', '5432')}/{os.getenv('DB_NAME', 'postgres')}",
    }


@router.get("/gcp/projects")
async def list_projects():
    """Returns distinct project_ids from monitored_databases, plus the env-configured host."""
    try:
        conn = get_connection()
        rows = conn.run(
            "SELECT DISTINCT project_id FROM evo_state.monitored_databases WHERE project_id IS NOT NULL ORDER BY project_id;"
        )
        conn.close()
        projects = [{"id": row[0], "name": row[0]} for row in rows if row[0]]
    except Exception as e:
        print(f"Failed to list projects: {e}")
        projects = []

    # Always include the env-configured host as a selectable project
    default_host = os.getenv("DB_HOST", "localhost")
    default_entry = {"id": default_host, "name": f"Current DB ({default_host})"}
    if not any(p["id"] == default_host for p in projects):
        projects.insert(0, default_entry)

    return projects


@router.get("/gcp/databases")
async def list_databases(project_id: Optional[str] = None):
    """Lists monitored databases registered in evo_state.monitored_databases."""
    try:
        conn = get_connection()
        if project_id:
            rows = conn.run(
                """SELECT db_id, project_id, instance_id, database_name, db_type,
                          target_schema, ip, created_at
                   FROM evo_state.monitored_databases
                   WHERE project_id = $1
                   ORDER BY created_at DESC;""",
                (project_id,)
            )
        else:
            rows = conn.run(
                """SELECT db_id, project_id, instance_id, database_name, db_type,
                          target_schema, ip, created_at
                   FROM evo_state.monitored_databases
                   ORDER BY created_at DESC;"""
            )
        conn.close()

        databases = []
        for row in rows:
            db_id, proj_id, instance_id, database_name, db_type, target_schema, ip, created_at = row
            databases.append({
                "db_id": db_id,
                "project_id": proj_id or "",
                "instance_id": instance_id,
                "database_name": database_name,
                "db_type": db_type,
                "target_schema": target_schema or "public",
                "ip": ip or "",
                "status": "registered",
                "created_at": str(created_at),
            })

        # If no registered databases, expose the env-configured connection
        if not databases:
            databases.append({
                "db_id": None,
                "project_id": os.getenv("DB_HOST", "localhost"),
                "instance_id": os.getenv("DB_HOST", "localhost"),
                "database_name": os.getenv("DB_NAME", "postgres"),
                "db_type": "postgresql",
                "target_schema": os.getenv("TARGET_SCHEMA", "public"),
                "ip": os.getenv("DB_HOST", "localhost"),
                "status": "active (env)",
                "created_at": None,
            })

        return databases
    except Exception as e:
        print(f"Failed to list databases: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/gcp/select-database")
async def select_database(selection: DatabaseSelection):
    """Registers a database as a monitoring target in evo_state.monitored_databases."""
    try:
        conn = get_connection()
        query = """
        INSERT INTO evo_state.monitored_databases
            (project_id, instance_id, database_name, db_type, target_schema, ip)
        VALUES ($1, $2, $3, $4, $5, $6)
        RETURNING db_id;
        """
        result = conn.run(query, (
            selection.project_id or "",
            selection.instance_id,
            selection.database_name,
            selection.db_type,
            selection.target_schema or "public",
            selection.ip or "",
        ))
        conn.close()
        return {"status": "success", "db_id": result[0][0]}
    except Exception as e:
        print(f"Failed to save selection: {e}")
        raise HTTPException(status_code=500, detail=str(e))
