import asyncio
import os
from uuid import uuid4

# Set API keys explicitly to ensure background tasks find them
os.environ["GEMINI_API_KEY"] = "AIzaSyAyC2HjTUKS7goHGlJNF3sKU7yRuMRQRqw"
os.environ["GOOGLE_API_KEY"] = "AIzaSyAyC2HjTUKS7goHGlJNF3sKU7yRuMRQRqw"

from google.adk.agents.invocation_context import InvocationContext
from google.adk.agents.run_config import RunConfig
from google.adk.sessions import InMemorySessionService
from google.genai.types import Content, Part, ModelContent

from agents.coordinator.agent import coordinator_agent
from agents.tools.alloydb_tools import update_agent_status, get_connection

async def reset_all_agents_to_idle(status_msg: str = "Idle"):
    """Helper to reset all agents to idle state."""
    agents = ["sage", "forge", "echo", "wright", "codex"]
    for agent in agents:
        update_agent_status(agent, "idle", status_msg)

async def run_agent_cycle(user_input: str, cycle_id: int = None) -> str:
    """
    Programmatically runs a cycle with the Coordinator agent.
    
    Args:
        user_input (str): The prompt or command for the agent.
        cycle_id (int, optional): The ID of the cycle in DB to update status.
        
    Returns:
        str: The final output from the agent.
    """
    print(f"Starting agent cycle with input: {user_input}, cycle_id: {cycle_id}")
    
    # Set Coordinator to active
    update_agent_status("coordinator", "thinking", "Starting cycle...")
    
    session_service = InMemorySessionService()
    session = await session_service.create_session(
        app_name="EvoAgent", user_id="system_user"
    )
    
    user_content = Content(parts=[Part(text=user_input)])
    
    invocation_context = InvocationContext(
        session_service=session_service,
        agent=coordinator_agent,
        invocation_id=str(uuid4()),
        session=session,
        user_content=user_content,
        run_config=RunConfig(),
    )
    
    final_output = ""
    try:
        # Set Coordinator to thinking before LLM call
        update_agent_status("coordinator", "thinking", "Processing with LLM...")
        
        async for event in coordinator_agent.run_async(parent_context=invocation_context):
            if isinstance(event, ModelContent):
                if event.parts:
                    text = event.parts[0].text
                    print(f"Agent: {text}")
                    final_output += text
                    # Update task with snippet of output to show progress
                    update_agent_status("coordinator", "thinking", f"Generating: {text[:20]}...")
                    
        print("Agent cycle completed successfully.")
        await reset_all_agents_to_idle("Completed")
        
        # Update cycle status in DB
        if cycle_id:
            try:
                conn = get_connection()
                conn.run("UPDATE evo_state.evo_cycles SET status = 'succeeded', ended_at = NOW() WHERE cycle_id = $1;", (cycle_id,))
                conn.close()
            except Exception as e:
                print(f"Failed to update cycle status: {e}")
        
    except Exception as e:
        print(f"Error in agent execution: {e}")
        await reset_all_agents_to_idle(f"Failed: {str(e)[:20]}")
        
        # Update cycle status in DB to failed
        if cycle_id:
            try:
                conn = get_connection()
                conn.run("UPDATE evo_state.evo_cycles SET status = 'failed', ended_at = NOW() WHERE cycle_id = $1;", (cycle_id,))
                conn.close()
            except Exception as e2:
                print(f"Failed to update cycle status on error: {e2}")
                
        raise e
        
    return final_output

if __name__ == "__main__":
    # Test run
    async def main():
        prompt = "Analyze the schema for perfagent_heavy and suggest an optimization."
        result = await run_agent_cycle(prompt)
        print(f"\nFinal Result:\n{result}")
        
    asyncio.run(main())
