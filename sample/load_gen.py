"""
Load generator for mock_orders table.
Runs mixed read/write workload to produce interesting pg_stat_statements data.
Usage: python3 sample/load_gen.py [--duration 120] [--workers 4]
"""
import os
import sys
import time
import random
import argparse
import threading
import pg8000.native
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from agents/.env
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), "agents/.env"))

DB = dict(
    host=os.getenv("DB_HOST", "localhost"),
    port=int(os.getenv("DB_PORT", "5432")),
    database=os.getenv("DB_NAME", "postgres"),
    user=os.getenv("DB_USER", "postgres"),
    password=os.getenv("DB_PASSWORD", "postgres")
)

STATUSES = ["pending", "shipped", "cancelled"]
BROWSERS = ["chrome", "firefox", "safari"]


def conn():
    return pg8000.native.Connection(**DB)


def workload(worker_id: int, stop_event: threading.Event, counters: dict, lock: threading.Lock):
    c = conn()
    ops = 0
    errors = 0
    while not stop_event.is_set():
        try:
            choice = random.random()

            if choice < 0.40:
                # Sequential scan — no index on status
                rows = c.run(
                    "SELECT order_id, customer_name, amount FROM mock_orders WHERE status = $1 LIMIT 100;",
                    (random.choice(STATUSES),)
                )

            elif choice < 0.60:
                # Range scan on order_date (no index)
                rows = c.run(
                    "SELECT order_id, amount, status FROM mock_orders "
                    "WHERE order_date > NOW() - INTERVAL '30 days' ORDER BY order_date DESC LIMIT 50;"
                )

            elif choice < 0.70:
                # Aggregation — intentionally slow without index
                rows = c.run(
                    "SELECT status, COUNT(*), AVG(amount), SUM(items_count) "
                    "FROM mock_orders GROUP BY status;"
                )

            elif choice < 0.80:
                # JSONB field filter (unindexed)
                browser = random.choice(BROWSERS)
                rows = c.run(
                    "SELECT order_id, customer_name FROM mock_orders "
                    "WHERE metadata->>'browser' = $1 LIMIT 20;",
                    (browser,)
                )

            elif choice < 0.88:
                # Single-row lookup by customer_name (no index)
                n = random.randint(1, 10000)
                rows = c.run(
                    "SELECT * FROM mock_orders WHERE customer_name = $1;",
                    (f"Customer_{n}",)
                )

            elif choice < 0.95:
                # INSERT new order
                c.run(
                    "INSERT INTO mock_orders (customer_name, order_date, amount, status, items_count, metadata) "
                    "VALUES ($1, NOW(), $2, $3, $4, $5);",
                    (
                        f"LoadGen_{worker_id}_{ops}",
                        round(random.uniform(10, 500), 2),
                        random.choice(STATUSES),
                        random.randint(1, 10),
                        f'{{"browser":"{random.choice(BROWSERS)}","promo_used":{str(random.random() > 0.8).lower()}}}',
                    )
                )

            else:
                # UPDATE — touch a random row
                c.run(
                    "UPDATE mock_orders SET status = $1 WHERE order_id = ("
                    "  SELECT order_id FROM mock_orders OFFSET $2 LIMIT 1"
                    ");",
                    (random.choice(STATUSES), random.randint(0, 9999))
                )

            ops += 1

        except Exception as e:
            errors += 1
            try:
                c = conn()
            except Exception:
                time.sleep(0.5)

        time.sleep(random.uniform(0.005, 0.03))

    with lock:
        counters["ops"] += ops
        counters["errors"] += errors
    c.close()


def main():
    parser = argparse.ArgumentParser(description="Load generator for mock_orders")
    parser.add_argument("--duration", type=int, default=120, help="Seconds to run (default 120)")
    parser.add_argument("--workers", type=int, default=4, help="Concurrent workers (default 4)")
    args = parser.parse_args()

    print(f"Starting load: {args.workers} workers for {args.duration}s against mock-postgres")
    print("Queries: status filter | date range | GROUP BY | JSONB filter | name lookup | INSERT | UPDATE")
    print("-" * 70)

    stop_event = threading.Event()
    counters = {"ops": 0, "errors": 0}
    lock = threading.Lock()
    start = time.time()

    threads = [
        threading.Thread(target=workload, args=(i, stop_event, counters, lock), daemon=True)
        for i in range(args.workers)
    ]
    for t in threads:
        t.start()

    try:
        while time.time() - start < args.duration:
            elapsed = time.time() - start
            with lock:
                ops = counters["ops"]
                errors = counters["errors"]
            qps = ops / elapsed if elapsed > 0 else 0
            print(f"  [{elapsed:5.0f}s] ops={ops:,}  errors={errors}  qps={qps:.1f}", end="\r")
            time.sleep(2)
    except KeyboardInterrupt:
        print("\nInterrupted by user")

    stop_event.set()
    for t in threads:
        t.join(timeout=3)

    elapsed = time.time() - start
    print(f"\n\nDone. {counters['ops']:,} ops in {elapsed:.1f}s ({counters['ops']/elapsed:.1f} qps), {counters['errors']} errors")
    print("pg_stat_statements should now show slow queries. Trigger a scan from the UI.")


if __name__ == "__main__":
    main()
