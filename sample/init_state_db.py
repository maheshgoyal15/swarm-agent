import pg8000.native
import sys
import os
import pathlib

def init_db():
    print("Connecting to database to initialize EvoAgent state tables...")
    try:
        conn = pg8000.native.Connection(
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", "5432")),
            database=os.getenv("DB_NAME", "postgres"),
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD", ""),
        )
        print("Connection successful!")

        sql_path = pathlib.Path(__file__).parent.parent / "agents" / "schema" / "operational_state.sql"
        if not sql_path.exists():
            print(f"Error: SQL file not found at {sql_path}", file=sys.stderr)
            sys.exit(1)

        sql = sql_path.read_text()
        print("Executing SQL schema...")
        for stmt in sql.split(";"):
            stmt = stmt.strip()
            if stmt and not stmt.startswith("--"):
                try:
                    conn.run(stmt)
                except Exception as e:
                    print(f"  Warning (non-fatal): {e}")

        print("Schema initialized successfully!")
        conn.close()
    except Exception as e:
        print(f"Failed to initialize DB: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    init_db()
