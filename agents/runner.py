import asyncio
import os
import sys
from uuid import uuid4

# Remove API keys from environment to force Vertex AI (ADC)
os.environ.pop("GOOGLE_API_KEY", None)
os.environ.pop("GEMINI_API_KEY", None)

# Add parent directory to path to find agents package
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables from agents/.env
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

import logging
from logging.handlers import TimedRotatingFileHandler

log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
os.makedirs(log_dir, exist_ok=True)

log_handler = TimedRotatingFileHandler(
    os.path.join(log_dir, "agents.log"),
    when="D",
    interval=1,
    backupCount=7
)
log_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
log_handler.setFormatter(formatter)

logger = logging.getLogger("agents")
logger.addHandler(log_handler)
logger.setLevel(logging.DEBUG)

logger.info("Agents logger initialized with daily rotation.")

# Monkey patch google.adk.models.google_llm to use Vertex AI
try:
    import google.adk.models.google_llm
    from google.genai import Client
    
    original_Client = Client
    
    def mocked_Client(**kwargs):
        print("[Monkey Patch] Creating Client with Vertex AI enabled")
        kwargs['vertexai'] = True
        kwargs['project'] = os.getenv("GCP_PROJECT", "my-sample-project-01-338917")
        kwargs['location'] = os.getenv("GCP_LOCATION", "us-central1")
        # Remove API key if present to force ADC
        kwargs.pop('api_key', None)
        return original_Client(**kwargs)
        
    google.adk.models.google_llm.Client = mocked_Client
    print("[Monkey Patch] Successfully patched google.adk.models.google_llm.Client")
except Exception as e:
    print(f"[Monkey Patch] Failed to patch: {e}")

from google.adk.agents.invocation_context import InvocationContext
from google.adk.agents.run_config import RunConfig
from google.adk.sessions import InMemorySessionService
from google.genai.types import Content, Part, ModelContent

from agents.coordinator.agent import coordinator_agent
from agents.tools.alloydb_tools import update_agent_status, get_connection, get_target_schema

async def reset_all_agents_to_idle(status_msg: str = "Idle"):
    """Helper to reset all agents to idle state."""
    agents = ["sage", "forge", "echo", "wright", "codex"]
    for agent in agents:
        update_agent_status(agent, "idle", status_msg)

async def run_agent_cycle(user_input: str, cycle_id: int = None) -> str:
    """
    Programmatically runs a cycle with the Coordinator agent.
    """
    print(f"Starting agent cycle with input: {user_input}, cycle_id: {cycle_id}")
    
    update_agent_status("sage", "analyzing", "Thinking...")
    
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
        update_agent_status("coordinator", "thinking", "Processing with LLM...")
        
        async for event in coordinator_agent.run_async(parent_context=invocation_context):
            if isinstance(event, ModelContent):
                if event.parts:
                    text = event.parts[0].text
                    print(f"Agent: {text}")
                    final_output += text
                    update_agent_status("coordinator", "thinking", f"Generating: {text[:20]}...")
                    
        print("Agent cycle completed successfully.")
        await reset_all_agents_to_idle("Completed")
        
        if cycle_id:
            try:
                conn = get_connection()
                conn.run("UPDATE evo_state.evo_cycles SET status = 'succeeded', ended_at = NOW() WHERE cycle_id = $1;", [None, cycle_id])
                conn.close()
            except Exception as e:
                print(f"Failed to update cycle status: {e}")
        
    except Exception as e:
        print(f"Error in agent execution: {e}")
        await reset_all_agents_to_idle(f"Failed: {str(e)[:20]}")
        
        if cycle_id:
            try:
                conn = get_connection()
                conn.run("UPDATE evo_state.evo_cycles SET status = 'failed', ended_at = NOW() WHERE cycle_id = $1;", [None, cycle_id])
                conn.close()
            except Exception as e2:
                print(f"Failed to update cycle status on error: {e2}")
                
        raise e
        
    return final_output

if __name__ == "__main__":
    async def main():
        schema = get_target_schema()
        prompt = f"Analyze the schema for {schema} and suggest an optimization."
        result = await run_agent_cycle(prompt)
        print(f"\nFinal Result:\n{result}")
        
    asyncio.run(main())
