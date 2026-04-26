import asyncio
import sys
import os

# Add parent directory to path to find agents package
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.sage.agent import sage_agent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.agents.run_config import RunConfig
from google.adk.sessions import InMemorySessionService
from google.genai.types import Content, Part, ModelContent
from uuid import uuid4

async def test_sage():
    print("Starting Sage Direct Test...")
    
    session_service = InMemorySessionService()
    session = await session_service.create_session(
        app_name="TestSage", user_id="test_user"
    )
    
    user_content = Content(parts=[Part(text="Analyze the schema for perfagent_heavy and identify slow queries.")])
    
    invocation_context = InvocationContext(
        session_service=session_service,
        agent=sage_agent,
        invocation_id=str(uuid4()),
        session=session,
        user_content=user_content,
        run_config=RunConfig(),
    )
    
    try:
        async for event in sage_agent.run_async(parent_context=invocation_context):
            if isinstance(event, ModelContent):
                if event.parts:
                    print(f"Sage Output: {event.parts[0].text}")
    except Exception as e:
        print(f"Sage Failed: {e}", file=sys.stderr)

if __name__ == "__main__":
    asyncio.run(test_sage())
