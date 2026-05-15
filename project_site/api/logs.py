import json
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from core.event_bus import EventBus
import asyncio

router = APIRouter(prefix="/api/logs", tags=["logs"])
bus = EventBus()


async def _log_stream():
    while True:
        logs = await bus.drain_logs()
        if logs:
            for log in logs:
                yield f"data: {json.dumps(log)}\n\n"
        await asyncio.sleep(0.2)


@router.get("/stream")
async def stream_logs():
    return StreamingResponse(
        _log_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
