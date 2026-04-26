import pg8000.native
import json
import sys

def get_connection():
    return pg8000.native.Connection(
        host="35.223.127.94",
        port=5432,
        database="postgres",
        user="postgres",
        password="Password"
    )

def update_agent_status(agent_codename: str, status: str, task: str):
    """Updates the status of an agent in the database."""
    try:
        conn = get_connection()
        query = """
        UPDATE evo_state.agent_status 
        SET status = $1, task = $2, updated_at = NOW() 
        WHERE agent_codename = $3
        RETURNING agent_codename;
        """
        res = conn.run(query, [status, task, agent_codename])
        print(f"[DB Tool] Status updated for {agent_codename}. Result: {res}")
        conn.close()
    except Exception as e:
        print(f"Error updating agent status: {e}", file=sys.stderr)

def read_schema() -> str:
    """
    Reads the schema of the AlloyDB database for the 'perfagent_heavy' schema.
    
    Returns:
        str: A JSON string representation of the database schema.
    """
    print("[DB Tool] Reading schema for 'perfagent_heavy'...")
    update_agent_status('sage', 'analyzing', 'Reading schema')
    try:
        conn = get_connection()
        query = """
        SELECT table_name, column_name, data_type 
        FROM information_schema.columns 
        WHERE table_schema = 'perfagent_heavy'
        ORDER BY table_name, ordinal_position;
        """
        rows = conn.run(query)
        
        schema = {"tables": {}}
        for row in rows:
            table_name, column_name, data_type = row
            if table_name not in schema["tables"]:
                schema["tables"][table_name] = {"columns": []}
            schema["tables"][table_name]["columns"].append({"name": column_name, "type": data_type})
            
        conn.close()
        return json.dumps(schema, indent=2)
    except Exception as e:
        print(f"Error reading schema: {e}", file=sys.stderr)
        return json.dumps({"error": str(e)})

def execute_query(sql_query: str) -> str:
    """
    Executes a SQL query against the AlloyDB database and returns the result.
    
    Args:
        sql_query (str): The SQL query to execute.
        
    Returns:
        str: A JSON string containing the query results.
    """
    print(f"[DB Tool] Executing query: {sql_query}")
    try:
        conn = get_connection()
        results = conn.run(sql_query)
        conn.close()
        return json.dumps(results, indent=2, default=str)
    except Exception as e:
        print(f"Error executing query: {e}", file=sys.stderr)
        return json.dumps({"error": str(e)})

def get_slow_queries() -> str:
    """
    Retrieves top slow queries from pg_stat_statements.
    
    Returns:
        str: A JSON string containing the top slow queries.
    """
    print("[DB Tool] Reading slow queries from pg_stat_statements...")
    update_agent_status('sage', 'analyzing', 'Reading slow queries')
    try:
        conn = get_connection()
        query = """
        SELECT query, calls, total_exec_time 
        FROM pg_stat_statements 
        WHERE query NOT LIKE '%pg_%' 
        ORDER BY total_exec_time DESC 
        LIMIT 10;
        """
        rows = conn.run(query)
        conn.close()
        return json.dumps(rows, indent=2, default=str)
    except Exception as e:
        print(f"Error reading slow queries: {e}", file=sys.stderr)
        return json.dumps({"error": str(e)})

def get_table_stats() -> str:
    """
    Retrieves statistics for tables in the 'perfagent_heavy' schema, including size and row counts.
    
    Returns:
        str: A JSON string containing table statistics.
    """
    print("[DB Tool] Reading table statistics for 'perfagent_heavy'...")
    update_agent_status('sage', 'analyzing', 'Reading table stats')
    try:
        conn = get_connection()
        query = """
        SELECT relname as table_name, 
               n_live_tup as row_count,
               pg_total_relation_size(relid) as total_size_bytes
        FROM pg_stat_user_tables 
        WHERE schemaname = 'perfagent_heavy';
        """
        rows = conn.run(query)
        conn.close()
        return json.dumps(rows, indent=2, default=str)
    except Exception as e:
        print(f"Error reading table stats: {e}", file=sys.stderr)
        return json.dumps({"error": str(e)})

def get_lock_waits() -> str:
    """
    Retrieves current lock waits to identify contention.
    
    Returns:
        str: A JSON string containing active lock waits.
    """
    print("[DB Tool] Reading lock waits...")
    update_agent_status('sage', 'analyzing', 'Reading lock waits')
    try:
        conn = get_connection()
        query = """
        SELECT blocked_locks.pid     AS blocked_pid,
               blocked_activity.usename  AS blocked_user,
               blocking_locks.pid    AS blocking_pid,
               blocking_activity.usename AS blocking_user,
               blocked_activity.query    AS blocked_query,
               blocking_activity.query   AS blocking_query
        FROM pg_catalog.pg_locks         blocked_locks
        JOIN pg_catalog.pg_stat_activity blocked_activity  ON blocked_locks.pid = blocked_activity.pid
        JOIN pg_catalog.pg_locks         blocking_locks 
             ON blocking_locks.locktype = blocked_locks.locktype
             AND blocking_locks.DATABASE IS NOT DISTINCT FROM blocked_locks.DATABASE
             AND blocking_locks.relation IS NOT DISTINCT FROM blocked_locks.relation
             AND blocking_locks.page IS NOT DISTINCT FROM blocked_locks.page
             AND blocking_locks.tuple IS NOT DISTINCT FROM blocked_locks.tuple
             AND blocking_locks.virtualxid IS NOT DISTINCT FROM blocked_locks.virtualxid
             AND blocking_locks.transactionid IS NOT DISTINCT FROM blocked_locks.transactionid
             AND blocking_locks.classid IS NOT DISTINCT FROM blocked_locks.classid
             AND blocking_locks.objid IS NOT DISTINCT FROM blocked_locks.objid
             AND blocking_locks.objsubid IS NOT DISTINCT FROM blocked_locks.objsubid
             AND blocking_locks.pid != blocked_locks.pid
        JOIN pg_catalog.pg_stat_activity blocking_activity ON blocking_locks.pid = blocking_activity.pid
        WHERE NOT blocked_locks.granted;
        """
        rows = conn.run(query)
        conn.close()
        return json.dumps(rows, indent=2, default=str)
    except Exception as e:
        print(f"Error reading lock waits: {e}", file=sys.stderr)
        return json.dumps({"error": str(e)})

def save_recommendation(target_resource: str, rec_type: str, severity: str, rationale: str, sql: str) -> str:
    """
    Saves an optimization recommendation generated by the agent to the database.
    
    Args:
        target_resource (str): The table or index targeted.
        rec_type (str): Type of recommendation (e.g., 'index', 'partition').
        severity (str): 'high', 'medium', or 'low'.
        rationale (str): Explanation for the recommendation.
        sql (str): The generated SQL statement to apply.
        
    Returns:
        str: Success or error message.
    """
    print(f"[DB Tool] Saving recommendation for {target_resource}...")
    update_agent_status('forge', 'planning', 'Saving recommendation')
    try:
        conn = get_connection()
        query = """
        INSERT INTO evo_state.recommendations (target_resource, recommendation_type, severity, rationale, generated_sql, status)
        VALUES ($1, $2, $3, $4, $5, 'pending')
        RETURNING rec_id;
        """
        result = conn.run(query, (target_resource, rec_type, severity, rationale, sql))
        conn.close()
        return json.dumps({"status": "success", "rec_id": str(result[0][0])})
    except Exception as e:
        print(f"Error saving recommendation: {e}", file=sys.stderr)
        return json.dumps({"error": str(e)})
