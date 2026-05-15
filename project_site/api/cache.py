from fastapi import APIRouter
from pydantic import BaseModel
from core.cache_manager import CacheManager
from core.event_bus import EventBus

router = APIRouter(prefix="/api/cache", tags=["cache"])
cache = CacheManager()
bus = EventBus()


class LockAgentRequest(BaseModel):
    agent_id: str
    agent_name: str
    agent_role: str


@router.post("/lock-agent")
async def lock_agent(payload: LockAgentRequest):
    previous = cache.get("locked_agent")
    cache.set("locked_agent", payload.model_dump(), ttl=600)

    if previous:
        await bus.emit(
            event="cache.update",
            tag="CACHE",
            message=f"Locked agent updated: {previous['agent_name']} -> {payload.agent_name}",
        )
    else:
        await bus.emit(
            event="cache.set",
            tag="CACHE",
            message=f"Agent locked in cache: {payload.agent_name} [{payload.agent_role}]",
        )

    return {"status": "ok", "locked_agent": payload.model_dump()}


@router.get("/status")
async def cache_status():
    locked = cache.get("locked_agent")
    keys = cache.all_keys()
    return {
        "locked_agent": locked,
        "active_keys": keys,
        "total_entries": len(keys),
    }
