from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool
from agents.tools.alloydb_tools import read_schema, execute_query, get_slow_queries, get_table_stats, get_lock_waits

MODEL = "gemini-2.5-flash"

SAGE_PROMPT = """
You are Sage, the Analyzer agent in the EvoAgent swarm.
Your job is to analyze the database schema and query patterns to identify optimization opportunities.

You have access to tools to:
1. Read the database schema (`read_schema`).
2. Execute queries to gather telemetry or analyze data (`execute_query`).
3. Retrieve top slow queries from database statistics (`get_slow_queries`).
4. Retrieve table statistics like row counts and sizes (`get_table_stats`).
5. Retrieve active lock waits to find contention (`get_lock_waits`).

For the given task, you should:
1. Search for executed queries using `get_slow_queries` to find the most time-consuming patterns.
2. Check table statistics using `get_table_stats` to identify large tables that might need indexes or partitioning.
3. Check for lock waits using `get_lock_waits` if contention is suspected.
4. Read the schema to understand the table structures involved.
5. Analyze the information to identify potential performance issues or optimization opportunities.
6. Output a structured summary of your findings.

Focus on AlloyDB (PostgreSQL) specific optimizations if applicable.
"""

sage_agent = LlmAgent(
    name="Sage",
    model=MODEL,
    description="Analyzes database schema and telemetry to identify optimization opportunities.",
    instruction=SAGE_PROMPT,
    tools=[
        FunctionTool(func=read_schema),
        FunctionTool(func=execute_query),
        FunctionTool(func=get_slow_queries),
        FunctionTool(func=get_table_stats),
        FunctionTool(func=get_lock_waits)
    ],
    output_key="analysis_results"
)
