import os
import pg8000.native
import sys

def get_columns():
    try:
        conn = pg8000.native.Connection(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "5432")),
        database=os.getenv("DB_NAME", "postgres"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", ""),
    )
        
        query = """
        SELECT table_name, column_name 
        FROM information_schema.columns 
        WHERE table_schema = 'perfagent_heavy'
        ORDER BY table_name;
        """
        rows = conn.run(query)
        for row in rows:
            print(row)
            
        conn.close()
    except Exception as e:
        print(f"Failed: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    get_columns()
