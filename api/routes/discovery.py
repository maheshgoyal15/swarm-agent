from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import json
from agents.tools.alloydb_tools import get_connection

router = APIRouter()

class DatabaseSelection(BaseModel):
    project_id: str
    instance_id: str
    database_name: str
    db_type: str

MOCK_PROJECTS = [
    {"id": "my-sample-project-01", "name": "Sample Project 01"},
    {"id": "analytics-prod", "name": "Analytics Production"},
]

MOCK_DATABASES = [
    {
        "project_id": "my-sample-project-01",
        "instance_id": "alloydb-instance-1",
        "database_name": "postgres",
        "db_type": "alloydb",
        "ip": "35.223.127.94",
        "status": "connected"
    },
    {
        "project_id": "analytics-prod",
        "instance_id": "spanner-instance-1",
        "database_name": "orders_db",
        "db_type": "spanner",
        "status": "disconnected"
    }
]

@router.get("/gcp/projects")
async def list_projects():
    return MOCK_PROJECTS

@router.get("/gcp/databases")
async def list_databases(project_id: str):
    filtered = [db for db in MOCK_DATABASES if db["project_id"] == project_id]
    return filtered

@router.post("/gcp/select-database")
async def select_database(selection: DatabaseSelection):
    print(f"Selecting database: {selection}")
    try:
        conn = get_connection()
        # Insert into evo_state.monitored_databases
        query = """
        INSERT INTO evo_state.monitored_databases (project_id, instance_id, database_name, db_type)
        VALUES ($1, $2, $3, $4)
        RETURNING db_id;
        """
        # pg8000 run takes parameters as a tuple or list
        result = conn.run(query, (selection.project_id, selection.instance_id, selection.database_name, selection.db_type))
        conn.close()
        
        return {"status": "success", "db_id": result[0][0]}
    except Exception as e:
        print(f"Failed to save selection: {e}")
        raise HTTPException(status_code=500, detail=str(e))
