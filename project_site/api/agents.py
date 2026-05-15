import json
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from core.agents_data import agent_stream
from core.event_bus import EventBus

router = APIRouter(prefix="/api/agents", tags=["agents"])
bus = EventBus()


async def _stream_agents():
    await bus.emit(
        event="agents.sync_start",
        tag="INFO",
        message="Agent sync initiated. Streaming data from server...",
    )
    count = 0
    async for agent in agent_stream():
        count += 1
        yield f"data: {json.dumps(agent)}\n\n"

    await bus.emit(
        event="agents.sync_complete",
        tag="SUCCESS",
        message=f"Agent sync complete. {count} agents loaded into roster.",
    )
    yield "data: {\"done\": true}\n\n"


@router.get("/stream")
async def stream_agents():
    return StreamingResponse(
        _stream_agents(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
