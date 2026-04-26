from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from models.schemas import ChatRequest
import asyncio
import json
from uuid import uuid4

router = APIRouter()


@router.post("/chat")
async def chat(request: ChatRequest):
    user_input = request.message
    print(f"Chat input: {user_input}")

    async def generate():
        try:
            from google.adk.agents.invocation_context import InvocationContext
            from google.adk.agents.run_config import RunConfig
            from google.adk.sessions import InMemorySessionService
            from google.genai.types import Content, Part, ModelContent
            from agents.coordinator.agent import coordinator_agent

            session_service = InMemorySessionService()
            session = await session_service.create_session(
                app_name="EvoAgentChat", user_id="chat_user"
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

            yield "data: ...\n\n"
            await asyncio.sleep(0.5)

            async for event in coordinator_agent.run_async(parent_context=invocation_context):
                if isinstance(event, ModelContent):
                    if event.parts:
                        text = event.parts[0].text
                        yield f"data: {text}\n\n"

            yield "data: [DONE]\n\n"
        except Exception as e:
            print(f"Error in chat agent execution: {e}")
            yield f"data: Error: {str(e)}\n\n"
            yield "data: [DONE]\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
