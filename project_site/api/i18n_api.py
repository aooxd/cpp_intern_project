from fastapi import APIRouter, Query
from pydantic import BaseModel
from core.i18n import get_ui_strings
from core.cache_manager import CacheManager
from core.event_bus import EventBus

router = APIRouter(prefix="/api/i18n", tags=["i18n"])
cache = CacheManager()
bus = EventBus()

SUPPORTED_LANGS = {"en", "uk"}


class SetLangRequest(BaseModel):
    lang: str


@router.get("/strings")
async def get_strings(lang: str = Query("en")):
    lang = lang.lower() if lang.lower() in SUPPORTED_LANGS else "en"
    return {"lang": lang, "strings": get_ui_strings(lang)}


@router.post("/set-lang")
async def set_language(payload: SetLangRequest):
    lang = payload.lang.lower() if payload.lang.lower() in SUPPORTED_LANGS else "en"
    cache.set("language", lang, ttl=86400)

    lang_label = "English" if lang == "en" else "Українська"
    await bus.emit(
        event="i18n.lang_changed",
        tag="INFO",
        message=f"Language switched to: {lang_label}",
    )
    return {"lang": lang, "strings": get_ui_strings(lang)}
