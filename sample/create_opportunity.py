import os
import pg8000.native
import sys
import time

def create_opportunity():
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
        
        query = """
        SELECT p.category, sum(oi.quantity * oi.price) as total_sales 
        FROM perfagent_heavy.order_items oi 
        JOIN perfagent_heavy.products p ON oi.product_id = p.id 
        GROUP BY p.category;
        """
        
        print(f"Running slow query to create opportunity:\n{query}")
        start_time = time.time()
        
        # Run it
        result = conn.run(query)
        
        end_time = time.time()
        print(f"Query completed in {end_time - start_time:.2f} seconds.")
        print(f"Result rows: {len(result)}")
        
        conn.close()
    except Exception as e:
        print(f"Failed: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    create_opportunity()
