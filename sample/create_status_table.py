import pg8000.native
import sys

def create_table():
    print("Connecting to AlloyDB...")
    try:
        conn = pg8000.native.Connection(
            host="35.223.127.94",
            port=5432,
            database="postgres",
            user="postgres",
            password="Password"
        )
        print("Connection successful!")
        
        # Create table
        query = """
        CREATE TABLE IF NOT EXISTS evo_state.agent_status (
          agent_codename TEXT PRIMARY KEY,
          status TEXT,
          task TEXT,
          updated_at TIMESTAMPTZ DEFAULT NOW()
        );
        """
        print("Creating table...")
        conn.run(query)
        
        # Initialize rows
        query = """
        INSERT INTO evo_state.agent_status (agent_codename, status, task) VALUES
        ('sage', 'idle', 'Idle'),
        ('forge', 'idle', 'Idle'),
        ('echo', 'idle', 'Idle'),
        ('wright', 'idle', 'Idle'),
        ('codex', 'idle', 'Idle')
        ON CONFLICT (agent_codename) DO NOTHING;
        """
        print("Initializing rows...")
        conn.run(query)
        
        print("Table created and initialized successfully!")
        conn.close()
    except Exception as e:
        print(f"Failed: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    create_table()
