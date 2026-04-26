import os
import pg8000.native
import sys

def check_schema():
    print("Connecting to AlloyDB to check schema 'perfagent_heavy'...")
    try:
        conn = pg8000.native.Connection(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "5432")),
        database=os.getenv("DB_NAME", "postgres"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", ""),
    )
        print("Connection successful!")
        
        query = "SELECT table_name FROM information_schema.tables WHERE table_schema = 'perfagent_heavy';"
        print(f"Running query: {query}")
        
        tables = conn.run(query)
        print("Tables in 'perfagent_heavy':")
        for row in tables:
            print(row)
            
        conn.close()
    except Exception as e:
        print(f"Failed to check schema: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    check_schema()
