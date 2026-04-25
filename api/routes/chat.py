from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from models.schemas import ChatRequest
import asyncio
import json

router = APIRouter()

MOCK_REPLIES = {
    "customer_360_dashboard": {
        "text": "Sage traced the regression to a <code>JOIN</code> against <code>orders_v2</code> that grew from 180M → 280M rows after the April 18 migration. The existing index on <code>(customer_id)</code> no longer satisfies the query — it now needs a composite key.",
        "reasoning": "Investigated 47 query executions over 7 days. P95 latency shifted from 220ms → 680ms on Apr 19. EXPLAIN plan changed: nested loop → hash join. Index recommendation queued as Rec #2 above.",
    },
    "rollback": {
        "text": "Wright will use a CTAS pattern: the old table is preserved as <code>events_raw__pre_evo_1247</code> for 7 days. Cutover happens via atomic table-swap. Rollback = single <code>ALTER TABLE … RENAME</code> (≈3s).",
        "reasoning": "Pulled rollback playbook v4 from Codex's knowledge graph. 12 similar repartition operations executed previously, 0 incidents, 1 rollback used (Feb 14 — schema mismatch caught in 90s).",
    },
    "default": {
        "text": "Based on my analysis, I can see the pattern you're describing. Let me coordinate with the swarm to investigate further and provide a detailed recommendation.",
        "reasoning": "This is a mock response because the real Gemini integration is not yet wired up. In production, this would be a real streaming response from Gemini 2.5 Pro.",
    },
}


@router.post("/chat")
async def chat(request: ChatRequest):
    msg = request.message.lower()
    
    reply_data = MOCK_REPLIES["default"]
    if "customer" in msg or "slower" in msg or "dashboard" in msg:
        reply_data = MOCK_REPLIES["customer_360_dashboard"]
    elif "rollback" in msg or "rec #1" in msg:
        reply_data = MOCK_REPLIES["rollback"]
        
    full_text = reply_data["text"]
    if reply_data["reasoning"]:
        # Add reasoning block syntax for frontend
        full_text += f'\n<div class="reasoning">{reply_data["reasoning"]}</div>'

    async def generate():
        # Simulate typing indicator delay
        await asyncio.sleep(0.5)
        
        # Stream character by character (or token by token)
        chunk_size = 3
        for i in range(0, len(full_text), chunk_size):
            chunk = full_text[i:i + chunk_size]
            yield f"data: {chunk}\n\n"
            await asyncio.sleep(0.02)
            
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )
