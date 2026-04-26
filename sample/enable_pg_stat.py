import pg8000.native
import sys

def enable_pg_stat():
    print("Connecting to AlloyDB as postgres...")
    try:
        conn = pg8000.native.Connection(
            host="35.223.127.94",
            port=5432,
            database="postgres",
            user="postgres",
            password="Password"
        )
        print("Connection successful!")
        
        query = "CREATE EXTENSION IF NOT EXISTS pg_stat_statements;"
        print(f"Running: {query}")
        conn.run(query)
        print("Extension created successfully (or already existed).")
        
        conn.close()
    except Exception as e:
        print(f"Failed to enable extension: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    enable_pg_stat()
