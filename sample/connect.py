import os
import pg8000.native
import sys

def test_connection():
    print(f"Attempting to connect to {os.getenv('DB_HOST','localhost')}:{os.getenv('DB_PORT','5432')}...")
    try:
        conn = pg8000.native.Connection(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "5432")),
        database=os.getenv("DB_NAME", "postgres"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", ""),
    )
        print("Connection successful!")
        
        print("Running sample query...")
        for row in conn.run("SELECT version()"):
            print(f"DB Version: {row}")
            
        conn.close()
    except Exception as e:
        print(f"Connection failed: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    test_connection()
