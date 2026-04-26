import os
import pg8000.native
import sys

def query_db():
    print("Connecting to AlloyDB...")
    try:
        conn = pg8000.native.Connection(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "5432")),
        database=os.getenv("DB_NAME", "postgres"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", ""),
    )
        print("Connection successful!")
        
        queries = [
            "SELECT count(*) FROM perfagent_heavy.orders;",
            "SELECT count(*) FROM perfagent_heavy.users;",
            "SELECT count(*) FROM perfagent_heavy.products;",
            "SELECT count(*) FROM perfagent_heavy.order_items;"
        ]
        
        for query in queries:
            print(f"\nRunning query: {query}")
            result = conn.run(query)
            print(f"Result: {result}")
            
        conn.close()
    except Exception as e:
        print(f"Failed to query DB: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    query_db()
