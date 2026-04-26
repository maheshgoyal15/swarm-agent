import asyncio
import sys
import os

# Add parent directory to path to find agents package
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.runner import run_agent_cycle
from agents.tools.alloydb_tools import get_connection

async def test_e2e():
    print("Starting E2E Test...")
    
    # 1. Clear old recommendations for testing
    try:
        conn = get_connection()
        conn.run("DELETE FROM evo_state.recommendations WHERE target_resource LIKE '%perfagent_heavy%';")
        print("Cleared old recommendations for testing.")
        conn.close()
    except Exception as e:
        print(f"Warning: Failed to clear old recommendations: {e}")
        
    # 2. Run agent cycle
    prompt = "Please analyze the database schema for perfagent_heavy and suggest at least one specific performance optimization recommendation. You MUST save the recommendation using the save_recommendation tool."
    
    try:
        result = await run_agent_cycle(prompt)
        print(f"\nAgent Cycle Result:\n{result}")
    except Exception as e:
        print(f"Agent Cycle Failed: {e}", file=sys.stderr)
        sys.exit(1)
        
    # 3. Verify recommendations in DB
    try:
        conn = get_connection()
        rows = conn.run("SELECT rec_id, target_resource, status FROM evo_state.recommendations WHERE status = 'pending';")
        print(f"\nFound {len(rows)} pending recommendations in DB.")
        for row in rows:
            print(row)
        conn.close()
        
        if len(rows) > 0:
            print("\n[SUCCESS] E2E Test PASSED: Recommendations were generated and saved!")
        else:
            print("\n[FAILURE] E2E Test FAILED: No recommendations saved to DB.")
            sys.exit(1)
            
    except Exception as e:
        print(f"Failed to verify recommendations: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(test_e2e())
