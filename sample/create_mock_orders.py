import pg8000.native
import sys
import os
from dotenv import load_dotenv

# Load environment variables from agents/.env
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), "agents/.env"))

def create_table():
    print("Connecting to AlloyDB...")
    try:
        conn = pg8000.native.Connection(
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", "5432")),
            database=os.getenv("DB_NAME", "postgres"),
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD", "postgres")
        )
        print("Connection successful!")
        
        query = """
        CREATE TABLE IF NOT EXISTS mock_orders (
            order_id SERIAL PRIMARY KEY,
            customer_name TEXT,
            order_date TIMESTAMPTZ DEFAULT NOW(),
            amount NUMERIC,
            status TEXT,
            items_count INTEGER,
            metadata JSONB
        );
        """
        print("Creating mock_orders table...")
        conn.run(query)
        print("Table created successfully!")
        conn.close()
    except Exception as e:
        print(f"Failed: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    create_table()
