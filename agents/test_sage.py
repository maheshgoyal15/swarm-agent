import sys
from agents.sage.agent import sage_agent

def test():
    print("Running Sage...")
    try:
        # Try synchronous run as seen in some samples or guessed
        result = sage_agent.run("Analyze the schema for perfagent_heavy and identify tables.")
        print(f"Result: {result}")
    except Exception as e:
        print(f"Error running Sage: {e}", file=sys.stderr)

if __name__ == "__main__":
    test()
