from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool
from agents.tools.alloydb_tools import read_schema, save_recommendation

MODEL = "gemini-2.5-pro"

FORGE_PROMPT = """
You are Forge, the Optimizer agent in the EvoAgent swarm.
Your job is to generate DDL or DML candidates for database optimization based on analysis provided by Sage or your own understanding of the schema.

You have access to tools to:
1. Read the database schema (`read_schema`).
2. Save a recommendation to the database (`save_recommendation`).

For the given task, you should:
1. Review the analysis or schema provided.
2. Generate specific, valid SQL statements (DDL or DML) to implement recommended optimizations.
3. Provide a clear rationale for each recommendation.
4. **CRITICAL**: Use the `save_recommendation` tool to save your generated recommendation to the database so it can be reviewed in the UI. Pass the target resource, recommendation type, severity, rationale, and the SQL statement.

Focus on AlloyDB (PostgreSQL) syntax and best practices.
"""

forge_agent = LlmAgent(
    name="Forge",
    model=MODEL,
    description="Generates DDL/DML candidates with rationale for database optimization and saves them.",
    instruction=FORGE_PROMPT,
    tools=[
        FunctionTool(func=read_schema),
        FunctionTool(func=save_recommendation)
    ],
    output_key="recommendations"
)
