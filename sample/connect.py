import pg8000.native
import sys

def test_connection():
    print("Attempting to connect to AlloyDB at 35.223.127.94:5432...")
    try:
        conn = pg8000.native.Connection(
            host="35.223.127.94",
            port=5432,
            database="postgres",
            user="postgres",
            password="Password"
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
