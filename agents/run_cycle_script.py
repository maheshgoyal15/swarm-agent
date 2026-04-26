import asyncio
import sys
import os
import json

# Add parent directory to path to find agents package
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# API key must be set in the environment before running this script
# e.g. export GOOGLE_API_KEY=your-key-here

from agents.sage.agent import sage_agent
from agents.forge.agent import forge_agent
from agents.tools.alloydb_tools import save_recommendation, update_agent_status, get_target_schema
from google.adk.agents.invocation_context import InvocationContext
from google.adk.agents.run_config import RunConfig
from google.adk.sessions import InMemorySessionService
from google.genai.types import Content, Part, ModelContent
from uuid import uuid4

async def run_custom_cycle():
    print("Starting Custom Agent Cycle...")
    
    session_service = InMemorySessionService()
    session = await session_service.create_session(
        app_name="EvoAgentCustom", user_id="test_user"
    )
    
    # 1. Run Sage
    print("\n--- Running Sage (Analyzer) ---")
    update_agent_status("sage", "analyzing", "Starting analysis")
    
    sage_content = Content(parts=[Part(text=f"Analyze the schema for {get_target_schema()} and identify slow queries.")])
    sage_context = InvocationContext(
        session_service=session_service,
        agent=sage_agent,
        invocation_id=str(uuid4()),
        session=session,
        user_content=sage_content,
        run_config=RunConfig(),
    )
    
    sage_output = ""
    async for event in sage_agent.run_async(parent_context=sage_context):
        if isinstance(event, ModelContent):
            if event.parts:
                sage_output += event.parts[0].text
                
    print(f"Sage Output:\n{sage_output}")
    update_agent_status("sage", "idle", "Analysis complete")
    
    # 2. Run Forge
    print("\n--- Running Forge (Optimizer) ---")
    update_agent_status("forge", "planning", "Generating recommendations")
    
    forge_prompt = f"""
    Based on the following analysis from Sage, generate a specific performance optimization recommendation.
    
    Analysis:
    {sage_output}
    
    You must output a JSON object matching this structure (and nothing else, no markdown code blocks):
    {{
        "target_resource": "table_name or index_name",
        "recommendation_type": "index" or "partition",
        "severity": "high" or "medium" or "low",
        "rationale": "explanation",
        "sql": "CREATE INDEX ...;"
    }}
    """
    
    forge_content = Content(parts=[Part(text=forge_prompt)])
    forge_context = InvocationContext(
        session_service=session_service,
        agent=forge_agent,
        invocation_id=str(uuid4()),
        session=session,
        user_content=forge_content,
        run_config=RunConfig(),
    )
    
    forge_output = ""
    async for event in forge_agent.run_async(parent_context=forge_context):
        if isinstance(event, ModelContent):
            if event.parts:
                forge_output += event.parts[0].text
                
    print(f"Forge Output:\n{forge_output}")
    update_agent_status("forge", "idle", "Recommendations generated")
    
    # 3. Parse and Save
    print("\n--- Saving Recommendation ---")
    try:
        # Clean up potential markdown code blocks if the model didn't follow instructions
        cleaned_output = forge_output.strip()
        if cleaned_output.startswith("```json"):
            cleaned_output = cleaned_output[7:]
        if cleaned_output.endswith("```"):
            cleaned_output = cleaned_output[:-3]
        cleaned_output = cleaned_output.strip()
        
        rec_data = json.loads(cleaned_output)
        
        result = save_recommendation(
            target_resource=rec_data.get("target_resource"),
            rec_type=rec_data.get("recommendation_type"),
            severity=rec_data.get("severity"),
            rationale=rec_data.get("rationale"),
            sql=rec_data.get("sql")
        )
        print(f"Save Result: {result}")
        print("[SUCCESS] E2E Flow complete and saved to DB!")
        
    except Exception as e:
        print(f"[FAILURE] Failed to parse or save recommendation: {e}")
        print(f"Raw Forge Output was:\n{forge_output}")

if __name__ == "__main__":
    asyncio.run(run_custom_cycle())
