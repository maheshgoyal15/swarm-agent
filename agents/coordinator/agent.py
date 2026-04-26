from google.adk.agents import LlmAgent
from google.adk.tools.agent_tool import AgentTool
from google.adk.tools import FunctionTool
from agents.sage.agent import sage_agent
from agents.forge.agent import forge_agent
from agents.tools.alloydb_tools import save_recommendation

MODEL = "gemini-2.5-pro"

COORDINATOR_PROMPT = """
You are the Coordinator of the EvoAgent swarm.
Your job is to orchestrate the optimization process.

You should:
1. Delegate the analysis of the database to Sage.
2. Take the analysis results from Sage and delegate to Forge to generate specific optimization recommendations (DDL/SQL).
3. **CRITICAL**: Once you receive the recommendation from Forge, you MUST use the `save_recommendation` tool to save it to the database. Do not just return it as text.
4. Combine the findings and recommendations into a final report for the user.

Always use the specialized agents (Sage and Forge) to perform their respective tasks.
"""

coordinator_agent = LlmAgent(
    name="Coordinator",
    model=MODEL,
    description="Orchestrates the EvoAgent optimization cycle by delegating to Sage and Forge and saving results.",
    instruction=COORDINATOR_PROMPT,
    tools=[
        AgentTool(agent=sage_agent),
        AgentTool(agent=forge_agent),
        FunctionTool(func=save_recommendation)
    ],
    output_key="final_report"
)

if __name__ == "__main__":
    import asyncio
    
    async def main():
        print("Starting EvoAgent cycle...")
        print("Coordinator defined. Ready to run.")
        
    asyncio.run(main())
