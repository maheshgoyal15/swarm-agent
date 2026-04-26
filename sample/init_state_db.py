import pg8000.native
import sys
import os

def init_db():
    print("Connecting to AlloyDB to initialize state tables...")
    try:
        conn = pg8000.native.Connection(
            host="35.223.127.94",
            port=5432,
            database="postgres",
            user="postgres",
            password="Password"
        )
        print("Connection successful!")
        
        # Read SQL file
        sql_path = "agents/schema/operational_state.sql"
        if not os.path.exists(sql_path):
            print(f"Error: SQL file not found at {sql_path}", file=sys.stderr)
            sys.exit(1)
            
        with open(sql_path, 'r') as f:
            sql = f.read()
            
        print("Executing SQL schema...")
        # pg8000 run can execute multiple statements separated by semicolon?
        # Let's split by semicolon just to be safe, or run as one block if supported.
        # PostgreSQL supports running multiple statements in one query string usually.
        # Let's try running it as a whole block.
        conn.run(sql)
        print("Schema initialized successfully!")
        
        conn.close()
    except Exception as e:
        print(f"Failed to initialize DB: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    init_db()
