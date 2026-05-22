import json
from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from core.cache_manager import CacheManager
from core.event_bus import EventBus
from core.security_proxy import SecurityProxy, VanguardSystem
from core.tactics_engine import (
    MAPS, MAP_CALLOUTS, CALLOUT_GUIDES, S_TIER_AGENTS,
    stream_tactics, get_tactics,
)

router = APIRouter(prefix="/api/tactics", tags=["tactics"])
cache = CacheManager()
bus = EventBus()
_proxy = SecurityProxy(VanguardSystem())


class SelectMapRequest(BaseModel):
    map_id: str


@router.post("/select-map")
async def select_map(payload: SelectMapRequest):
    map_id = payload.map_id.lower()
    if map_id not in MAPS:
        return {"status": "error", "message": f"Unknown map: {map_id}"}

    previous = cache.get("active_map")
    cache.set("active_map", {"map_id": map_id, **MAPS[map_id]}, ttl=3600)

    prev_name = previous["name"] if previous else None
    new_name = MAPS[map_id]["name"]
    msg = (f"Active map changed: {prev_name} → {new_name}"
           if prev_name else f"Map selected: {new_name} [{MAPS[map_id]['type']}]")

    await bus.emit(event="map.selected", tag="MAP_INFO", message=msg)
    return {"status": "ok", "map": {"map_id": map_id, **MAPS[map_id]}}


@router.get("/maps")
async def list_maps():
    return {"maps": [{"map_id": k, **v} for k, v in MAPS.items()]}


@router.get("/callouts")
async def get_callouts(map_id: str = Query(...)):
    callouts = MAP_CALLOUTS.get(map_id.lower(), [])
    return {"map_id": map_id.lower(), "callouts": callouts}


@router.get("/callout-info")
async def callout_info(map_id: str = Query(...), zone_id: str = Query(...)):
    map_id = map_id.lower()
    zone_id = zone_id.lower()
    guide = CALLOUT_GUIDES.get(map_id, {}).get(zone_id)
    if not guide:
        return {"status": "error", "message": "Zone not found"}

    map_name = MAPS.get(map_id, {}).get("name", map_id)
    zone_label = next(
        (c["label"] for c in MAP_CALLOUTS.get(map_id, []) if c["id"] == zone_id), zone_id
    )
    await bus.emit(
        event="map.callout_viewed",
        tag="MAP_INFO",
        message=f"Position guide accessed: [{map_name}] {zone_label}",
    )
    return {"status": "ok", "map_id": map_id, "zone_id": zone_id,
            "zone_label": zone_label, "guide": guide}


async def _tactics_stream(
    agent_id: str, map_id: str, side: str, round_type: str, lang: str, token: str
):
    agent_name = agent_id.capitalize()
    map_name = MAPS.get(map_id, {}).get("name", map_id.capitalize())

    # SecurityProxy check: Full Buy for S-Tier agents requires valid Vanguard token
    is_restricted = (round_type == "full" and agent_id in S_TIER_AGENTS)
    if is_restricted:
        scan_result = await _proxy.scan(token)
        if not scan_result.get("authorized"):
            restricted_msg = (
                "// ACCESS RESTRICTED // Provide a valid Vanguard Token for Full-Buy S-Tier strategy analysis."
                if lang == "en" else
                "// ДОСТУП ОБМЕЖЕНО // Надайте дійсний токен Vanguard для аналізу стратегій S-класу Повна Купівля."
            )
            await bus.emit(
                event="tactics.restricted",
                tag="SECURITY",
                message=f"Full-Buy strategy for {agent_name} ({agent_id.upper()}-Tier) requires Vanguard token.",
            )
            yield f"data: {json.dumps({'chunk': restricted_msg})}\n\n"
            yield f"data: {json.dumps({'done': True, 'restricted': True})}\n\n"
            return

    econ_tag = {"eco": "ECONOMY", "semi": "ECONOMY", "full": "TACTICS"}.get(round_type, "TACTICS")
    await bus.emit(
        event="tactics.briefing_start",
        tag=econ_tag,
        message=f"Generating [{round_type.upper()}] briefing: {agent_name} on {map_name} [{side.upper()}]",
    )

    async for chunk in stream_tactics(agent_id, map_id, side, round_type, lang):
        yield f"data: {json.dumps({'chunk': chunk})}\n\n"

    await bus.emit(
        event="tactics.briefing_complete",
        tag="TACTICS",
        message=f"Briefing complete: {agent_name} // {map_name} // {round_type.upper()}",
    )
    yield f"data: {json.dumps({'done': True})}\n\n"


@router.get("/stream")
async def stream_tactics_route(
    agent_id: str = Query(...),
    map_id: str = Query(...),
    side: str = Query("attack"),
    round_type: str = Query("full"),
    lang: str = Query("en"),
    token: str = Query(""),
):
    return StreamingResponse(
        _tactics_stream(
            agent_id.lower(), map_id.lower(), side.lower(),
            round_type.lower(), lang.lower(), token,
        ),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@router.get("/status")
async def tactics_status():
    return {
        "locked_agent": cache.get("locked_agent"),
        "active_map": cache.get("active_map"),
        "language": cache.get("language") or "en",
        "ready": cache.get("locked_agent") is not None and cache.get("active_map") is not None,
    }
