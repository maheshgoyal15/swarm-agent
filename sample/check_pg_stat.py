import os
import pg8000.native
import sys

def check_pg_stat():
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
        
        # Check if extension exists
        query = "SELECT count(*) FROM pg_extension WHERE extname = 'pg_stat_statements';"
        result = conn.run(query)
        print(f"Extension count: {result}")
        
        if result[0][0] > 0:
            print("pg_stat_statements is installed. Trying to query it...")
            # Query top 5 queries by calls or time
            # Note: column names might be total_time or total_exec_time depending on PG version
            # Let's try total_exec_time (PG 13+)
            try:
                query = "SELECT query, calls, total_exec_time FROM pg_stat_statements ORDER BY total_exec_time DESC LIMIT 5;"
                res = conn.run(query)
                print("Top queries by execution time:")
                for row in res:
                    print(row)
            except Exception as e:
                print(f"Failed to query with total_exec_time: {e}")
                # Try fallback to total_time (older PG)
                try:
                    query = "SELECT query, calls, total_time FROM pg_stat_statements ORDER BY total_time DESC LIMIT 5;"
                    res = conn.run(query)
                    print("Top queries by execution time (fallback):")
                    for row in res:
                        print(row)
                except Exception as e2:
                    print(f"Failed to query with total_time: {e2}")
        else:
            print("pg_stat_statements is NOT installed.")
            
        conn.close()
    except Exception as e:
        print(f"Failed: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    check_pg_stat()
