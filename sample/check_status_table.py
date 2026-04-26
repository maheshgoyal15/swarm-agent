import pg8000.native
import sys

def check_table():
    try:
        conn = pg8000.native.Connection(
            host="35.223.127.94",
            port=5432,
            database="postgres",
            user="postgres",
            password="Password"
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
