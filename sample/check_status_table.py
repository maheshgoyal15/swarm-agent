import os
import pg8000.native
import sys

def check_table():
    try:
        conn = pg8000.native.Connection(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "5432")),
        database=os.getenv("DB_NAME", "postgres"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", ""),
    )
        
        query = "SELECT * FROM evo_state.agent_status;"
        rows = conn.run(query)
        print("Rows in agent_status:")
        for row in rows:
            print(row)
            
        conn.close()
    except Exception as e:
        print(f"Failed: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    check_table()
