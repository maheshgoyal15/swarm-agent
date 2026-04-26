from google.adk.agents import LlmAgent
from google.adk.tools.agent_tool import AgentTool
from agents.sage.agent import sage_agent
from agents.forge.agent import forge_agent

MODEL = "gemini-2.5-pro"

COORDINATOR_PROMPT = """
You are the Coordinator of the EvoAgent swarm.
Your job is to orchestrate the optimization process.

You should:
1. Delegate the analysis of the database to Sage.
2. Take the analysis results from Sage and delegate to Forge to generate specific optimization recommendations (DDL/SQL).
3. Combine the findings and recommendations into a final report for the user.

Always use the specialized agents (Sage and Forge) to perform their respective tasks.
"""

coordinator_agent = LlmAgent(
    name="Coordinator",
    model=MODEL,
    description="Orchestrates the EvoAgent optimization cycle by delegating to Sage and Forge.",
    instruction=COORDINATOR_PROMPT,
    tools=[
        AgentTool(agent=sage_agent),
        AgentTool(agent=forge_agent)
    ],
    output_key="final_report"
)

# For running as a standalone script if needed
if __name__ == "__main__":
    import asyncio
    
    async def main():
        print("Starting EvoAgent cycle...")
        # This is a simplified execution. ADK might require a specific runner or context.
        # In the samples, they often use `agent.run(...)` or similar.
        # Let's see how to run it based on samples if possible, or just provide the definition.
        print("Coordinator defined. Ready to run.")
        
    asyncio.run(main())
